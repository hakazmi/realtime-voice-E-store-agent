from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Import your existing modules
from salesforce.client import (
    sf,
    list_active_products,
    get_standard_pricebook,
    upsert_account,
    create_order,
    create_order_item,
    get_order_status
)
from salesforce.schema import Order, OrderItem
from backend.voice_client import RealtimeVoiceClient
from backend.tools import tool_search_products, tool_place_order, tool_lookup_order

load_dotenv()

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

# Initialize FastAPI app
app = FastAPI(
    title="Voice E-Commerce API",
    description="Voice-driven shopping assistant with Salesforce integration",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Pydantic Models ====================

class ProductResponse(BaseModel):
    id: str
    name: str
    price: float
    description: str
    color: str
    size: str
    product_code: str
    category: str
    image_url: str
    pricebook_entry_id: str

class SearchFilters(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    color: Optional[str] = None
    size: Optional[str] = None

class CartItemRequest(BaseModel):
    product_id: str
    quantity: int

class CustomerInfo(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

class OrderRequest(BaseModel):
    customer: CustomerInfo
    items: List[Dict[str, Any]]
    checkout_source: str = "Web"

class ChatMessage(BaseModel):
    message: str
    type: str = "text"  # "text" or "voice"

# ==================== In-Memory Storage ====================
# In production, use Redis or database
active_sessions: Dict[str, Dict] = {}

# ==================== Product Endpoints ====================

@app.get("/")
async def root():
    return {
        "message": "Voice E-Commerce API",
        "status": "running",
        "endpoints": {
            "products": "/api/products",
            "search": "/api/products/search",
            "cart": "/api/cart",
            "orders": "/api/orders",
            "chat": "/ws/chat/{session_id}"
        }
    }

@app.get("/api/products", response_model=List[ProductResponse])
async def get_all_products(
    category: Optional[str] = None,
    limit: int = 50
):
    """Get all products from Salesforce"""
    try:
        query = """
        SELECT Id, Name, ProductCode, Description, Color__c, Size__c, Family, Image_URL__c,
               (SELECT Id, UnitPrice FROM PricebookEntries WHERE IsActive = true LIMIT 1)
        FROM Product2
        WHERE IsActive = true
        """
        
        if category:
            query += f" AND Family = '{category}'"
        
        query += f" LIMIT {limit}"
        
        results = sf.query(query)
        products = []
        
        for record in results['records']:
            pbe = record.get('PricebookEntries', {}).get('records', [])
            if pbe:
                products.append(ProductResponse(
                    id=record['Id'],
                    name=record['Name'],
                    price=pbe[0]['UnitPrice'],
                    description=record.get('Description', ''),
                    color=record.get('Color__c', ''),
                    size=record.get('Size__c', ''),
                    product_code=record.get('ProductCode', ''),
                    category=record.get('Family', ''),
                    image_url=record.get('Image_URL__c', ''),
                    pricebook_entry_id=pbe[0]['Id']
                ))
        
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products/search", response_model=List[ProductResponse])
async def search_products(filters: SearchFilters):
    """Search products with filters"""
    try:
        results = tool_search_products(
            query=filters.query,
            category=filters.category,
            price_min=filters.price_min,
            price_max=filters.price_max,
            color=filters.color,
            size=filters.size
        )
        
        products = []
        for item in results:
            # Fetch image URL from Salesforce
            prod = sf.query(f"SELECT Image_URL__c FROM Product2 WHERE Id = '{item['id']}' LIMIT 1")
            image_url = prod['records'][0].get('Image_URL__c', '') if prod['records'] else ''
            
            products.append(ProductResponse(
                id=item['id'],
                name=item['name'],
                price=item['price'],
                description=item['description'],
                color=item['color'],
                size=item['size'],
                product_code=item['product_code'],
                category='',
                image_url=image_url,
                pricebook_entry_id=item['pricebook_entry_id']
            ))
        
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """Get single product by ID"""
    try:
        query = f"""
        SELECT Id, Name, ProductCode, Description, Color__c, Size__c, Family, Image_URL__c,
               (SELECT Id, UnitPrice FROM PricebookEntries WHERE IsActive = true LIMIT 1)
        FROM Product2
        WHERE Id = '{product_id}' AND IsActive = true
        LIMIT 1
        """
        
        result = sf.query(query)
        if not result['records']:
            raise HTTPException(status_code=404, detail="Product not found")
        
        record = result['records'][0]
        pbe = record['PricebookEntries']['records'][0]
        
        return ProductResponse(
            id=record['Id'],
            name=record['Name'],
            price=pbe['UnitPrice'],
            description=record.get('Description', ''),
            color=record.get('Color__c', ''),
            size=record.get('Size__c', ''),
            product_code=record.get('ProductCode', ''),
            category=record.get('Family', ''),
            image_url=record.get('Image_URL__c', ''),
            pricebook_entry_id=pbe['Id']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    """Get all product categories"""
    try:
        query = "SELECT Family FROM Product2 WHERE IsActive = true AND Family != null GROUP BY Family"
        results = sf.query(query)
        categories = [record['Family'] for record in results['records']]
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Cart Endpoints ====================

@app.post("/api/cart/{session_id}/add")
async def add_to_cart(session_id: str, item: CartItemRequest):
    """Add item to cart"""
    try:
        if session_id not in active_sessions:
            active_sessions[session_id] = {"cart": [], "voice_mode": False}
        
        # Get product details
        product = await get_product(item.product_id)
        
        # Check if item already in cart
        cart = active_sessions[session_id]["cart"]
        for cart_item in cart:
            if cart_item["product"]["id"] == item.product_id:
                cart_item["quantity"] += item.quantity
                return {"message": "Cart updated", "cart": cart}
        
        # Add new item
        cart.append({
            "product": product.dict(),
            "quantity": item.quantity
        })
        
        return {"message": "Item added to cart", "cart": cart}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cart/{session_id}")
async def get_cart(session_id: str):
    """Get cart contents"""
    if session_id not in active_sessions:
        return {"cart": [], "total": 0}
    
    cart = active_sessions[session_id].get("cart", [])
    total = sum(item["product"]["price"] * item["quantity"] for item in cart)
    
    return {"cart": cart, "total": total}

@app.delete("/api/cart/{session_id}/item/{product_id}")
async def remove_from_cart(session_id: str, product_id: str):
    """Remove item from cart"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart = active_sessions[session_id]["cart"]
    active_sessions[session_id]["cart"] = [
        item for item in cart if item["product"]["id"] != product_id
    ]
    
    return {"message": "Item removed from cart"}

@app.delete("/api/cart/{session_id}")
async def clear_cart(session_id: str):
    """Clear entire cart"""
    if session_id in active_sessions:
        active_sessions[session_id]["cart"] = []
    return {"message": "Cart cleared"}

@app.put("/api/cart/{session_id}/item/{product_id}")
async def update_cart_quantity(session_id: str, product_id: str, quantity: int):
    """Update item quantity in cart"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart = active_sessions[session_id]["cart"]
    
    if quantity <= 0:
        # Remove item if quantity is 0 or less
        active_sessions[session_id]["cart"] = [
            item for item in cart if item["product"]["id"] != product_id
        ]
    else:
        # Update quantity
        for cart_item in cart:
            if cart_item["product"]["id"] == product_id:
                cart_item["quantity"] = quantity
                break
    
    return {"message": "Cart updated"}

# ==================== Order Endpoints ====================

@app.post("/api/orders")
async def place_order(order_request: OrderRequest):
    """Place an order in Salesforce"""
    try:
        print(f"📋 Order request received:")
        print(f"   Customer: {order_request.customer.name} ({order_request.customer.email})")
        print(f"   Items: {order_request.items}")
        print(f"   Checkout source: {order_request.checkout_source}")
        
        result = tool_place_order(
            customer={
                "name": order_request.customer.name,
                "email": order_request.customer.email,
                "phone": order_request.customer.phone or ""
            },
            items=order_request.items,
            checkout_source=order_request.checkout_source
        )
        
        print(f"📋 Order result: {result}")
        
        if result["success"]:
            return {
                "success": True,
                "order_number": result["order_number"],
                "order_id": result["order_id"],
                "total_amount": result["total_amount"],
                "message": "Order placed successfully"
            }
        else:
            error_msg = result.get("message", "Order failed")
            print(f"❌ Order failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Exception in place_order: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/customer/{email}")
async def get_customer_orders(email: str):
    """Get all orders for a customer by email"""
    try:
        result = tool_lookup_order(email=email)
        
        if result["success"]:
            return result
        else:
            return {"orders": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== WebSocket Chat/Voice Endpoint ====================

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.voice_clients: Dict[str, RealtimeVoiceClient] = {}
        self.voice_mode_active: Dict[str, bool] = {}  # Track voice mode per session
    
    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.voice_mode_active[session_id] = False  # Start in text mode
        
        # Initialize session cart if not exists
        if session_id not in active_sessions:
            active_sessions[session_id] = {"cart": [], "voice_mode": False}
        
        # Initialize voice client for this session
        voice_client = RealtimeVoiceClient()
        
        # Link voice client's cart to the session cart
        voice_client.state["cart"] = active_sessions[session_id]["cart"]
        voice_client.session_id = session_id
        
        self.voice_clients[session_id] = voice_client
        
        try:
            await voice_client.connect()
            
            # Start listening for OpenAI events
            asyncio.create_task(self.listen_to_voice_client(session_id))
            
            await websocket.send_json({
                "type": "system",
                "message": "Connected to shopping assistant",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            print(f"❌ Failed to connect voice client: {e}")
            import traceback
            traceback.print_exc()
            await websocket.send_json({
                "type": "error",
                "message": f"Failed to connect assistant: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
    
    async def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        
        if session_id in self.voice_clients:
            await self.voice_clients[session_id].close()
            del self.voice_clients[session_id]
        
        if session_id in self.voice_mode_active:
            del self.voice_mode_active[session_id]
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)
    
    async def listen_to_voice_client(self, session_id: str):
        """Listen to OpenAI Realtime API events and forward to WebSocket"""
        voice_client = self.voice_clients.get(session_id)
        if not voice_client or not voice_client.ws:
            return
        
        try:
            async for message in voice_client.ws:
                event = json.loads(message)
                await self.handle_voice_event(session_id, event)
        except Exception as e:
            print(f"❌ Error in voice client listener: {e}")
            import traceback
            traceback.print_exc()
    
    async def handle_voice_event(self, session_id: str, event: Dict[str, Any]):
        """Handle OpenAI Realtime API events"""
        event_type = event.get("type")
        
        # Ignore these to reduce noise
        if event_type in [
            "response.audio_transcript.delta", 
            "response.output_item.added", 
            "response.content_part.added", 
            "input_audio_buffer.committed",
            "response.output_item.done",
            "response.content_part.done",
            "response.done",
            "session.created",
            "session.updated",
            "response.created",
            "rate_limits.updated"
        ]:
            return
        
        # User started speaking - trigger interruption
        if event_type == "input_audio_buffer.speech_started":
            print(f"🎤 User started speaking - interrupting assistant")
            # Notify frontend to stop audio playback
            await self.send_message(session_id, {
                "type": "user_speaking",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        # User stopped speaking
        if event_type == "input_audio_buffer.speech_stopped":
            print(f"🎤 User stopped speaking")
            return
        
        # User speech transcription
        if event_type == "conversation.item.input_audio_transcription.completed":
            await self.send_message(session_id, {
                "type": "user_message",
                "content": event["transcript"],
                "timestamp": datetime.now().isoformat(),
                "mode": "voice"
            })
        
        # Assistant response (text) - always send text to chat
        elif event_type == "response.audio_transcript.done":
            await self.send_message(session_id, {
                "type": "assistant_message",
                "content": event["transcript"],
                "timestamp": datetime.now().isoformat(),
                "mode": "voice"
            })
        
        # Response cancelled (user interrupted)
        elif event_type == "response.cancelled":
            print(f"🛑 Response cancelled for session {session_id}")
            # Frontend already stopped audio when user started speaking
            return
        
        # Assistant audio (for playback) - ONLY send if voice mode is active
        elif event_type == "response.audio.delta":
            # Check if voice mode is active for this session
            is_voice_mode = self.voice_mode_active.get(session_id, False)
            
            if is_voice_mode:
                # Send audio for playback
                await self.send_message(session_id, {
                    "type": "audio_delta",
                    "audio": event["delta"],
                    "timestamp": datetime.now().isoformat()
                })
        
        # Tool calls
        elif event_type == "response.function_call_arguments.done":
            call_id = event["call_id"]
            name = event["name"]
            arguments = json.loads(event["arguments"])
            
            print(f"🔧 Executing tool: {name} with args: {arguments}")
            
            # Execute tool
            voice_client = self.voice_clients.get(session_id)
            if voice_client:
                result = await voice_client.handle_tool_call(name, arguments)
                
                print(f"🔧 Tool result for {name}: {result}")
                
                # Handle search_products tool result
                if name == "search_products" and result.get("success"):
                    products = result.get("products", [])
                    print(f"📦 Sending {len(products)} products to frontend")
                    
                    # Send products directly - frontend will attach to next assistant message
                    await self.send_message(session_id, {
                        "type": "tool_result",
                        "tool": "search_products",
                        "result": products,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Send tool response to OpenAI
                await voice_client.send_tool_response(call_id, result)
                
                # CRITICAL: Sync cart after add_to_cart tool
                if name == "add_to_cart" and result.get("success"):
                    print(f"🔄 Syncing cart for session {session_id}")
                    # Notify frontend to refresh cart
                    await self.send_message(session_id, {
                        "type": "cart_updated",
                        "cart": active_sessions[session_id]["cart"],
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Clear cart after successful order
                if name == "place_salesforce_order" and result.get("success"):
                    print(f"🧹 Clearing cart for session {session_id}")
                    active_sessions[session_id]["cart"] = []
                    voice_client.state["cart"] = []
                    await self.send_message(session_id, {
                        "type": "cart_cleared",
                        "timestamp": datetime.now().isoformat()
                    })
        
        # Errors - only REAL errors that user should see
        elif event_type == "error":
            error_msg = event.get("error", {}).get("message", "")
            error_code = event.get("error", {}).get("code", "")
            
            # Ignore these common non-critical errors
            ignore_errors = [
                "buffer too small",
                "Buffer is empty",
                "No speech detected",
                "Audio buffer is empty",
                "buffer_cleared",
                "response_cancelled"
            ]
            
            if not any(ignore in str(error_msg) or ignore in str(error_code) for ignore in ignore_errors):
                await self.send_message(session_id, {
                    "type": "error",
                    "message": error_msg,
                    "timestamp": datetime.now().isoformat()
                })

manager = ConnectionManager()

@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for chat and voice interaction"""
    await manager.connect(session_id, websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "text":
                # Text message from user - voice mode OFF
                content = data.get("content")
                
                # Set voice mode to FALSE for this session
                manager.voice_mode_active[session_id] = False
                
                # Echo user message back
                await manager.send_message(session_id, {
                    "type": "user_message",
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                    "mode": "text"
                })
                
                # Send to OpenAI Realtime API
                voice_client = manager.voice_clients.get(session_id)
                if voice_client:
                    await voice_client.send_text(content)
                    await asyncio.sleep(0.1)
            
            elif message_type == "audio":
                # Audio chunk from user - voice mode ON
                audio_data = data.get("audio")
                
                # Set voice mode to TRUE for this session
                manager.voice_mode_active[session_id] = True
                
                # Send to OpenAI Realtime API
                voice_client = manager.voice_clients.get(session_id)
                if voice_client:
                    import base64
                    audio_bytes = base64.b64decode(audio_data)
                    await voice_client.send_audio(audio_bytes)
            
            elif message_type == "audio_commit":
                # Commit audio buffer (when user stops speaking)
                voice_client = manager.voice_clients.get(session_id)
                if voice_client:
                    await voice_client.commit_audio()
            
            elif message_type == "voice_mode_off":
                # User explicitly turned off voice mode
                manager.voice_mode_active[session_id] = False
                print(f"🔇 Voice mode OFF for session {session_id}")
            
            elif message_type == "voice_mode_on":
                # User explicitly turned on voice mode
                manager.voice_mode_active[session_id] = True
                print(f"🎤 Voice mode ON for session {session_id}")
            
            elif message_type == "ping":
                # Keepalive ping
                await manager.send_message(session_id, {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        await manager.disconnect(session_id)
        print(f"Client {session_id} disconnected")
    except Exception as e:
        print(f"WebSocket error for {session_id}: {e}")
        import traceback
        traceback.print_exc()
        await manager.disconnect(session_id)

# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Salesforce connection
        sf.query("SELECT Id FROM Product2 LIMIT 1")
        sf_status = "connected"
    except:
        sf_status = "disconnected"
    
    return {
        "status": "healthy",
        "salesforce": sf_status,
        "openai": "configured" if os.getenv("OPENAI_API_KEY") else "not configured",
        "timestamp": datetime.now().isoformat()
    }

# ==================== Run Server ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )