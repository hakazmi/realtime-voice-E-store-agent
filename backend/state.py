from typing import TypedDict, Annotated, Sequence, Optional, List, Dict, Any
from operator import add
from dataclasses import dataclass, asdict

@dataclass
class Product:
    id: str
    name: str
    price: float
    description: str
    color: str = ""
    size: str = ""
    url: str = ""
    product_code: str = ""
    pricebook_entry_id: str = ""

@dataclass
class CartItem:
    product: Product
    quantity: int
    
    def to_dict(self):
        return {
            "product": asdict(self.product),
            "quantity": self.quantity
        }

@dataclass
class Customer:
    name: str
    email: str
    phone: str = ""

class AgentState(TypedDict):
    """State for the voice shopping agent"""
    
    # Conversation flow
    messages: Annotated[Sequence[dict], add]
    intent: str  # search_products | refine | confirm_purchase | place_order | order_status | wrap_up
    
    # Search context
    search_query: Optional[str]
    search_filters: Dict[str, Any]  # category, price_min, price_max, color, size
    search_results: List[Product]
    
    # Shopping cart
    cart: List[CartItem]
    
    # Customer info
    customer: Optional[Customer]
    
    # Order tracking
    order_number: Optional[str]
    order_status: Optional[Dict[str, Any]]
    
    # Session metadata
    session_id: str
    conversation_history: Annotated[Sequence[str], add]