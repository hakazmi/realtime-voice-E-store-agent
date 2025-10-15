from typing import Literal
from langgraph.graph import StateGraph, END
from backend.state import AgentState, CartItem
from backend.tools import (
    tool_search_products,
    tool_add_to_cart,
    tool_place_order,
    tool_lookup_order
)


def route_intent(state: AgentState) -> Literal["search_products", "refine", "confirm_purchase", "place_order", "order_status", "wrap_up"]:
    """Route conversation based on intent"""
    intent = state.get("intent", "search_products")
    return intent


def search_products_node(state: AgentState) -> AgentState:
    """Search for products based on filters"""
    filters = state.get("search_filters", {})
    query = state.get("search_query", "")
    
    print(f"🔍 Searching products: query='{query}', filters={filters}")
    
    products = tool_search_products(
        query=query,
        category=filters.get("category"),
        price_max=filters.get("price_max"),
        price_min=filters.get("price_min"),
        color=filters.get("color"),
        size=filters.get("size")
    )
    
    state["search_results"] = products
    state["intent"] = "refine"
    
    # Create message for conversation history
    if products:
        msg = f"Found {len(products)} products matching your criteria."
    else:
        msg = "No products found matching your criteria. Try adjusting filters."
    
    state["conversation_history"].append(msg)
    
    return state


def refine_node(state: AgentState) -> AgentState:
    """Handle refinement of search or adding to cart"""
    # This node waits for user input to either:
    # - Refine search (update filters)
    # - Add product to cart
    # - Move to checkout
    
    state["intent"] = "confirm_purchase"  # Default next step
    return state


def confirm_purchase_node(state: AgentState) -> AgentState:
    """Confirm purchase details before placing order"""
    cart = state.get("cart", [])
    
    if not cart:
        state["conversation_history"].append("Your cart is empty. Would you like to search for products?")
        state["intent"] = "search_products"
        return state
    
    # Calculate total
    total = sum(item.product.price * item.quantity for item in cart)
    
    # Build confirmation message
    items_summary = ", ".join([f"{item.quantity}x {item.product.name}" for item in cart])
    msg = f"Your cart contains: {items_summary}. Total: ${total:.2f}. Would you like to proceed with checkout?"
    
    state["conversation_history"].append(msg)
    state["intent"] = "place_order"
    
    return state


def place_order_node(state: AgentState) -> AgentState:
    """Place the order in Salesforce"""
    cart = state.get("cart", [])
    customer = state.get("customer")
    
    if not customer:
        state["conversation_history"].append("I need your name and email to complete the order.")
        state["intent"] = "confirm_purchase"
        return state
    
    print(f"📦 Placing order for {customer.name} ({customer.email})")
    
    # Convert cart to order items format
    items = [
        {
            "pricebook_entry_id": item.product.pricebook_entry_id,
            "quantity": item.quantity
        }
        for item in cart
    ]
    
    # Place order
    result = tool_place_order(
        customer={
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone
        },
        items=items,
        checkout_source="Voice"
    )
    
    if result["success"]:
        order_number = result["order_number"]
        total = result["total_amount"]
        
        msg = f"✅ Order {order_number} placed successfully! Total: ${total:.2f}. You'll receive a confirmation email shortly."
        state["order_number"] = order_number
        state["conversation_history"].append(msg)
        state["intent"] = "wrap_up"
    else:
        msg = f"❌ Failed to place order: {result.get('message', 'Unknown error')}"
        state["conversation_history"].append(msg)
        state["intent"] = "confirm_purchase"
    
    return state


def order_status_node(state: AgentState) -> AgentState:
    """Look up order status"""
    order_number = state.get("order_number")
    customer = state.get("customer")
    
    print(f"🔍 Looking up order: {order_number}")
    
    result = tool_lookup_order(
        order_number=order_number,
        email=customer.email if customer else None
    )
    
    if result["success"]:
        if "orders" in result:
            # Multiple orders found
            orders_list = "\n".join([
                f"Order {o['order_number']}: {o['status']} - ${o['total_amount']:.2f}"
                for o in result["orders"]
            ])
            msg = f"Here are your recent orders:\n{orders_list}"
        else:
            # Single order
            msg = f"Order {result['order_number']}: Status is {result['status']}. "
            msg += f"Placed on {result['effective_date']}. Total: ${result['total_amount']:.2f}"
        
        state["order_status"] = result
        state["conversation_history"].append(msg)
    else:
        msg = f"Could not find order. {result.get('message', '')}"
        state["conversation_history"].append(msg)
    
    state["intent"] = "wrap_up"
    return state


def wrap_up_node(state: AgentState) -> AgentState:
    """Wrap up conversation"""
    msg = "Is there anything else I can help you with today?"
    state["conversation_history"].append(msg)
    return state


# Build the graph
def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes (rename 'order_status' to 'handle_order_status' to avoid conflict)
    workflow.add_node("search_products", search_products_node)
    workflow.add_node("refine", refine_node)
    workflow.add_node("confirm_purchase", confirm_purchase_node)
    workflow.add_node("place_order", place_order_node)
    workflow.add_node("handle_order_status", order_status_node)  # Renamed node
    workflow.add_node("wrap_up", wrap_up_node)
    
    # Add edges and conditional routing
    workflow.set_entry_point("search_products")
    
    workflow.add_conditional_edges(
        "search_products",
        route_intent,
        {
            "search_products": "search_products",
            "refine": "refine",
            "confirm_purchase": "confirm_purchase",
            "place_order": "place_order",
            "order_status": "handle_order_status",  # Update edge to new node name
            "wrap_up": "wrap_up"
        }
    )
    
    workflow.add_conditional_edges(
        "refine",
        route_intent,
        {
            "search_products": "search_products",
            "refine": "refine",
            "confirm_purchase": "confirm_purchase",
            "place_order": "place_order",
            "order_status": "handle_order_status",  # Update edge to new node name
            "wrap_up": "wrap_up"
        }
    )
    
    workflow.add_edge("confirm_purchase", "place_order")
    workflow.add_edge("place_order", "wrap_up")
    workflow.add_edge("handle_order_status", "wrap_up")  # Update edge to new node name
    
    return workflow.compile()

agent_graph = create_agent_graph()