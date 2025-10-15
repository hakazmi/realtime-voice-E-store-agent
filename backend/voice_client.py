import asyncio
import json
import os
from typing import Optional, Dict, Any, Callable
import websockets
from dotenv import load_dotenv
from backend.tools import TOOL_SCHEMAS, tool_search_products, tool_add_to_cart, tool_place_order, tool_lookup_order
from backend.state import AgentState, Customer, CartItem, Product

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REALTIME_API_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"

SYSTEM_INSTRUCTIONS = """You are a helpful voice shopping assistant for an e-commerce store. 

Your personality:
- Friendly, conversational, and professional
- Speak naturally in complete sentences, not word-by-word
- Always ask clarifying follow-up questions to understand user needs better
- Be proactive in suggesting complementary products
- Keep responses concise but complete (10-20 seconds when speaking)

Your capabilities:
- Search products by category (Watches, Footwear, Accessories), price, color, size
- Help customers add items to cart
- Place orders in Salesforce
- Track order status

Important conversation flow rules:

1. PRODUCT SEARCH - Always ask follow-up questions:
   - If user says "show me watches" → Ask: "What color would you prefer? We have silver, gold, black, and more."
   - If user says "shoes under $100" → Ask: "Great! What color are you looking for?"
   - If user says "wallets" → Ask: "Would you like a slim wallet or a larger travel wallet?"
   - Extract filters properly: category, color, price range, size
   - When search_products returns results, say something natural like:
     "I found [X] great options for you. Take a look at these [product type]."
   - DO NOT describe individual products - let the cards speak for themselves

2. ADDING TO CART - Be clear and efficient:
   - If user says "option 1" or "first one", use the EXACT product name from search results
   - After adding, briefly confirm: "Added [product name] to your cart for $[price]."
   - Then ask: "Would you like to keep shopping or proceed to checkout?"

3. CHECKOUT PROCESS - Collect information smoothly:
   - Before calling place_salesforce_order, you MUST:
     * Confirm cart contents: "You have [X] items totaling $[total]"
     * Ask for: name, email, phone (one at a time if needed)
     * Get explicit confirmation: "Shall I place this order?"
   - After successful order: "Your order #[number] is confirmed! You'll receive an email at [email]."

4. ORDER TRACKING:
   - If asked "where's my order", call lookup_order_status
   - Provide status clearly: "Your order #[number] is currently [status]."

5. NATURAL CONVERSATION:
   - Always respond in FULL, COMPLETE sentences
   - Use contractions naturally: "I've found" instead of "I have found"
   - Be warm: "Great choice!", "Perfect!", "I'd be happy to help!"
   - If user speaks in Urdu/another language, politely respond: "I understand! Let me help you in English."

6. FOLLOW-UP QUESTIONS - Be helpful:
   - After showing products: "Which one catches your eye?"
   - After adding to cart: "Would you like to add anything else, or shall we checkout?"
   - If cart is empty: "Your cart is empty. Can I help you find something?"

Product categories:
- Watches: $79-299 (Silver, Gold, Black, Blue, Brown)
- Footwear (Shoes): $70-90 (Various colors and sizes)
- Accessories (Belts, Wallets): $35-60 (Black, Brown, Navy)

Always maintain a helpful, patient, and natural tone. Make shopping feel easy and enjoyable!"""


class RealtimeVoiceClient:
    """OpenAI Realtime API client for voice shopping"""
    
    def __init__(self):
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.session_id: Optional[str] = None
        self.state = AgentState(
            messages=[],
            intent="search_products",
            search_query=None,
            search_filters={},
            search_results=[],
            cart=[],
            customer=None,
            order_number=None,
            order_status=None,
            session_id="",
            conversation_history=[]
        )
        self.audio_callback: Optional[Callable] = None
        self.keepalive_task: Optional[asyncio.Task] = None
        self.is_connected = False
        
    async def connect(self):
        """Connect to OpenAI Realtime API with retry logic"""
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        print("🔌 Connecting to OpenAI Realtime API...")
        
        try:
            # Add ping_interval and ping_timeout to keep connection alive
            self.ws = await websockets.connect(
                REALTIME_API_URL, 
                extra_headers=headers,
                ping_interval=20,  # Send ping every 20 seconds
                ping_timeout=10,   # Wait 10 seconds for pong
                close_timeout=10   # Timeout for closing connection
            )
            print("✅ Connected to Realtime API")
            self.is_connected = True
            
            # Configure session
            await self.configure_session()
            
            # Start keepalive task
            self.keepalive_task = asyncio.create_task(self._keepalive())
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.is_connected = False
            raise
        
    async def _keepalive(self):
        """Send periodic keepalive messages to prevent timeout"""
        while self.is_connected and self.ws and not self.ws.closed:
            try:
                await asyncio.sleep(15)  # Send keepalive every 15 seconds
                if self.ws and not self.ws.closed:
                    # Send a session.update as keepalive (doesn't change anything)
                    await self.ws.send(json.dumps({
                        "type": "session.update",
                        "session": {}
                    }))
                    print("💓 Keepalive ping sent")
            except Exception as e:
                print(f"⚠️ Keepalive error: {e}")
                break
        
    async def configure_session(self):
        """Configure the realtime session with tools and instructions"""
        config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": SYSTEM_INSTRUCTIONS,
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 700,  # Reduced for better interruption
                    "create_response": True  # Auto-create response on speech detection
                },
                "tools": TOOL_SCHEMAS,
                "tool_choice": "auto",
                "temperature": 0.7,  # Slightly higher for natural speech
                "max_response_output_tokens": 500  # Ensure complete sentences
            }
        }
        
        await self.ws.send(json.dumps(config))
        print("⚙️ Session configured with tools and instructions")
        
    async def send_audio(self, audio_data: bytes):
        """Send audio input to the API with error handling"""
        if not self.ws or self.ws.closed:
            print("⚠️ WebSocket is closed, cannot send audio")
            return
            
        try:
            import base64
            
            event = {
                "type": "input_audio_buffer.append",
                "audio": base64.b64encode(audio_data).decode()
            }
            await self.ws.send(json.dumps(event))
        except websockets.exceptions.ConnectionClosed:
            print("⚠️ Connection closed while sending audio")
            self.is_connected = False
        except Exception as e:
            print(f"❌ Error sending audio: {e}")
        
    async def commit_audio(self):
        """Commit audio buffer and create response"""
        if not self.ws or self.ws.closed:
            print("⚠️ WebSocket is closed, cannot commit audio")
            return
            
        try:
            await self.ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
        except websockets.exceptions.ConnectionClosed:
            print("⚠️ Connection closed while committing audio")
            self.is_connected = False
        except Exception as e:
            print(f"❌ Error committing audio: {e}")
        
    async def handle_tool_call(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool calls with proper error handling"""
        print(f"🔧 Tool call: {tool_name} with args: {tool_args}")
        
        try:
            if tool_name == "search_products":
                products = tool_search_products(**tool_args)
                print(f"✅ Search returned {len(products)} products")
                return {
                    "success": True,
                    "products": products,
                    "count": len(products)
                }
                
            elif tool_name == "add_to_cart":
                print(f"📦 Current cart before add: {self.state['cart']}")
                print(f"📦 Product name to find: '{tool_args.get('product_name')}'")
                
                result = tool_add_to_cart(
                    product_name=tool_args["product_name"],
                    quantity=tool_args.get("quantity", 1),
                    cart=self.state["cart"]
                )
                
                print(f"📦 Add to cart result: {result}")
                print(f"📦 Current cart after add: {self.state['cart']}")
                
                if not result.get("success"):
                    print(f"❌ Add to cart failed: {result.get('message')}")
                
                return result
                
            elif tool_name == "place_salesforce_order":
                print(f"🛒 Placing order with customer: {tool_args.get('customer')}")
                
                # Store customer info in state
                customer_data = tool_args["customer"]
                self.state["customer"] = Customer(
                    name=customer_data["name"],
                    email=customer_data["email"],
                    phone=customer_data.get("phone", "")
                )
                
                result = tool_place_order(
                    customer=customer_data,
                    items=tool_args["items"],
                    checkout_source=tool_args.get("checkout_source", "Voice")
                )
                
                print(f"🛒 Order result: {result}")
                
                if result["success"]:
                    self.state["order_number"] = result["order_number"]
                    # Clear cart after successful order
                    self.state["cart"] = []
                    print(f"✅ Order placed successfully: {result['order_number']}")
                else:
                    print(f"❌ Order placement failed: {result.get('message')}")
                
                return result
                
            elif tool_name == "lookup_order_status":
                print(f"🔍 Looking up order: {tool_args}")
                
                result = tool_lookup_order(
                    order_number=tool_args.get("order_number"),
                    email=tool_args.get("email")
                )
                
                print(f"🔍 Lookup result: {result}")
                return result
                
            else:
                error_msg = f"Unknown tool: {tool_name}"
                print(f"❌ {error_msg}")
                return {"success": False, "message": error_msg}
        
        except Exception as e:
            error_msg = f"Exception in handle_tool_call: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"Tool execution error: {str(e)}"
            }
    
    async def send_tool_response(self, call_id: str, output: Dict[str, Any]):
        """Send tool execution result back to the API"""
        if not self.ws or self.ws.closed:
            print("⚠️ WebSocket is closed, cannot send tool response")
            return
            
        try:
            event = {
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(output)
                }
            }
            await self.ws.send(json.dumps(event))
            
            # Trigger response generation
            await self.ws.send(json.dumps({"type": "response.create"}))
        except websockets.exceptions.ConnectionClosed:
            print("⚠️ Connection closed while sending tool response")
            self.is_connected = False
        except Exception as e:
            print(f"❌ Error sending tool response: {e}")
    
    async def listen(self):
        """Listen for events from the API with reconnection logic"""
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                if not self.ws or self.ws.closed:
                    print("🔄 Reconnecting to OpenAI...")
                    await self.connect()
                    retry_count = 0  # Reset retry count on successful connection
                
                async for message in self.ws:
                    event = json.loads(message)
                    await self.handle_event(event)
                    
            except websockets.exceptions.ConnectionClosed as e:
                print(f"⚠️ Connection closed: {e.code} {e.reason}")
                self.is_connected = False
                retry_count += 1
                
                if retry_count < max_retries:
                    wait_time = min(2 ** retry_count, 10)  # Exponential backoff, max 10s
                    print(f"🔄 Retrying in {wait_time} seconds... (Attempt {retry_count}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    print("❌ Max retries reached. Connection failed.")
                    break
                    
            except Exception as e:
                print(f"❌ Error in listen loop: {e}")
                import traceback
                traceback.print_exc()
                break
    
    async def handle_event(self, event: Dict[str, Any]):
        """Handle different event types from the API"""
        event_type = event.get("type")
        
        if event_type == "session.created":
            self.session_id = event["session"]["id"]
            print(f"✅ Session created: {self.session_id}")
            
        elif event_type == "session.updated":
            print("✅ Session updated")
            
        elif event_type == "input_audio_buffer.speech_started":
            print("🎤 User started speaking - INTERRUPTING ASSISTANT")
            # Cancel any ongoing response when user starts speaking
            if self.ws and not self.ws.closed:
                try:
                    await self.ws.send(json.dumps({"type": "response.cancel"}))
                    print("🛑 Assistant response cancelled")
                except Exception as e:
                    print(f"⚠️ Failed to cancel response: {e}")
            
        elif event_type == "input_audio_buffer.speech_stopped":
            print("🎤 User stopped speaking")
            
        elif event_type == "conversation.item.input_audio_transcription.completed":
            transcript = event["transcript"]
            print(f"📝 User said: {transcript}")
            self.state["conversation_history"].append(f"User: {transcript}")
            
        elif event_type == "response.audio_transcript.delta":
            delta = event.get("delta", "")
            # Don't print every delta to avoid spam
            pass
            
        elif event_type == "response.audio_transcript.done":
            transcript = event["transcript"]
            print(f"\n✅ Complete response: {transcript}")
            self.state["conversation_history"].append(f"Assistant: {transcript}")
            
        elif event_type == "response.audio.delta":
            # Audio chunk received
            import base64
            audio_chunk = base64.b64decode(event["delta"])
            if self.audio_callback:
                await self.audio_callback(audio_chunk)
                
        elif event_type == "response.function_call_arguments.done":
            # Function call completed
            call_id = event["call_id"]
            name = event["name"]
            arguments = json.loads(event["arguments"])
            
            print(f"\n🔧 Executing function: {name}")
            
            # Execute tool
            result = await self.handle_tool_call(name, arguments)
            
            # Send result back
            await self.send_tool_response(call_id, result)
            
        elif event_type == "response.done":
            print("\n✅ Response complete")
            
        elif event_type == "response.cancelled":
            print("🛑 Response was cancelled (user interrupted)")
            
        elif event_type == "error":
            error = event.get("error", {})
            error_code = error.get("code", "")
            error_message = error.get("message", "Unknown error")
            
            # Ignore certain non-critical errors
            if error_code not in ["buffer_cleared", "response_cancelled"]:
                print(f"❌ Error: {error_message}")
            
    async def send_text(self, text: str):
        """Send text message (for testing without audio)"""
        if not self.ws or self.ws.closed:
            print("⚠️ WebSocket is closed, cannot send text")
            return
            
        try:
            event = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": text
                        }
                    ]
                }
            }
            await self.ws.send(json.dumps(event))
            await self.ws.send(json.dumps({"type": "response.create"}))
        except websockets.exceptions.ConnectionClosed:
            print("⚠️ Connection closed while sending text")
            self.is_connected = False
        except Exception as e:
            print(f"❌ Error sending text: {e}")
        
    async def close(self):
        """Close the connection gracefully"""
        self.is_connected = False
        
        # Cancel keepalive task
        if self.keepalive_task:
            self.keepalive_task.cancel()
            try:
                await self.keepalive_task
            except asyncio.CancelledError:
                pass
        
        # Close WebSocket
        if self.ws and not self.ws.closed:
            await self.ws.close()
            print("👋 Connection closed gracefully")


async def test_voice_session():
    """Test the voice client with text input"""
    client = RealtimeVoiceClient()
    
    try:
        await client.connect()
        
        # Start listening for events
        listen_task = asyncio.create_task(client.listen())
        
        # Wait a bit for session to be ready
        await asyncio.sleep(1)
        
        # Test conversation flow
        print("\n" + "="*50)
        print("Testing: Product Search")
        print("="*50)
        await client.send_text("I need shoes under $100")
        await asyncio.sleep(5)
        
        print("\n" + "="*50)
        print("Testing: Add to Cart")
        print("="*50)
        await client.send_text("Add the white sneakers to my cart")
        await asyncio.sleep(3)
        
        print("\n" + "="*50)
        print("Testing: Checkout")
        print("="*50)
        await client.send_text("Proceed to checkout. My name is John Doe and email is john@example.com")
        await asyncio.sleep(5)
        
        print("\n" + "="*50)
        print("Testing: Order Status")
        print("="*50)
        await client.send_text("What's the status of my order?")
        await asyncio.sleep(3)
        
        # Cancel listen task
        listen_task.cancel()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_voice_session())