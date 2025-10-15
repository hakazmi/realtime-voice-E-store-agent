import asyncio
from backend.voice_client import RealtimeVoiceClient

async def interactive_voice_test():
    """Interactive test for voice shopping assistant"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║     Voice E-Commerce Shopping Assistant - Backend Test      ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    client = RealtimeVoiceClient()
    
    try:
        # Connect to OpenAI Realtime API
        await client.connect()
        
        # Start listening for events in background
        listen_task = asyncio.create_task(client.listen())
        
        # Wait for session to be ready
        await asyncio.sleep(1)
        
        print("\n✅ Voice assistant is ready!")
        print("\nAvailable commands:")
        print("  - Type your message to chat")
        print("  - Type 'quit' or 'exit' to end session")
        print("\nExample queries:")
        print("  • 'I need shoes under $100'")
        print("  • 'Show me watches'")
        print("  • 'Add the black belt to my cart'")
        print("  • 'Proceed to checkout'")
        print("  • 'Where is my order?'")
        print("\n" + "="*60 + "\n")
        
        # Interactive loop
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye!")
                    break
                
                # Send message to assistant
                await client.send_text(user_input)
                
                # Wait for response
                await asyncio.sleep(3)
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted")
                break
                
        # Cleanup
        listen_task.cancel()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


async def automated_test_flow():
    """Automated test flow for demonstration"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║        Automated Voice Shopping Flow - Demo Test            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    client = RealtimeVoiceClient()
    
    try:
        await client.connect()
        listen_task = asyncio.create_task(client.listen())
        await asyncio.sleep(1.0)
        
        # Test scenarios
        scenarios = [
            {
                "name": "Product Search - Shoes",
                "query": "I need shoes under $100",
                "wait": 5
            },
            {
                "name": "Product Search - Watches",
                "query": "Show me watches in silver color",
                "wait": 5
            },
            {
                "name": "Refine Search",
                "query": "Any watches under $120?",
                "wait": 4
            },
            {
                "name": "Add to Cart",
                "query": "I'll take the chronograph watch",
                "wait": 3
            },
            {
                "name": "View Cart",
                "query": "What's in my cart?",
                "wait": 3
            },
            {
                "name": "Checkout Initiation",
                "query": "Proceed to checkout",
                "wait": 3
            },
            {
                "name": "Provide Details",
                "query": "My name is Sarah Smith, email is sarah.smith@example.com, phone is 555-0123",
                "wait": 4
            },
            {
                "name": "Confirm Order",
                "query": "Yes, place the order",
                "wait": 5
            },
            {
                "name": "Order Status Check",
                "query": "What's the status of my order?",
                "wait": 4
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{'='*60}")
            print(f"Scenario {i}/{len(scenarios)}: {scenario['name']}")
            print(f"{'='*60}")
            print(f"Query: '{scenario['query']}'")
            print()
            
            await client.send_text(scenario['query'])
            await asyncio.sleep(scenario['wait'])
            
            print()
        
        print("\n" + "="*60)
        print("✅ Automated test flow completed!")
        print("="*60)
        
        listen_task.cancel()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


def print_menu():
    """Print main menu"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   Voice E-Commerce Backend - OpenAI Realtime API Test       ║
╚══════════════════════════════════════════════════════════════╝

Choose test mode:

  1. Interactive Mode - Chat with the assistant
  2. Automated Demo - Run predefined test flow
  3. Exit

""")


async def main():
    """Main entry point"""
    
    while True:
        print_menu()
        
        try:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == "1":
                await interactive_voice_test()
            elif choice == "2":
                await automated_test_flow()
            elif choice == "3":
                print("\n👋 Goodbye!")
                break
            else:
                print("\n❌ Invalid choice. Please enter 1, 2, or 3.\n")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")