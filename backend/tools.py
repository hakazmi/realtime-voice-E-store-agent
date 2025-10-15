import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, List, Dict, Any
from salesforce.client import (
    list_active_products,
    get_standard_pricebook,
    upsert_account,
    create_order,
    create_order_item,
    get_order_status,
    sf
)
from salesforce.schema import Order, OrderItem
from backend.state import Product, CartItem, Customer
from datetime import datetime
from openai import OpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json




# Tool JSON schemas for OpenAI Realtime API
TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "search_products",
        "description": "Search for products in the catalog by category, price range, color, or size",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Free-text search query (e.g., 'shoes', 'wallet')"
                },
                "category": {
                    "type": "string",
                    "description": "Product category",
                    "enum": ["Accessories", "Footwear", "Watches"]
                },
                "price_max": {
                    "type": "number",
                    "description": "Maximum price in USD"
                },
                "price_min": {
                    "type": "number",
                    "description": "Minimum price in USD"
                },
                "color": {
                    "type": "string",
                    "description": "Product color preference"
                },
                "size": {
                    "type": "string",
                    "description": "Product size or size range"
                }
            },
            "required": []
        }
    },
    {
        "type": "function",
        "name": "add_to_cart",
        "description": "Add a product to the shopping cart. First search for products, then use the product_id from search results.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": "Name of the product to add (e.g., 'Men's Sports Running Shoes - Grey')"
                },
                "quantity": {
                    "type": "integer",
                    "description": "Quantity to add",
                    "minimum": 1,
                    "default": 1
                }
            },
            "required": ["product_name"]
        }
    },
    {
        "type": "function",
        "name": "place_salesforce_order",
        "description": "Create an order in Salesforce with cart items. MUST confirm with customer before calling.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Customer full name"
                        },
                        "email": {
                            "type": "string",
                            "description": "Customer email address"
                        },
                        "phone": {
                            "type": "string",
                            "description": "Customer phone number"
                        }
                    },
                    "required": ["name", "email"]
                },
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "pricebook_entry_id": {
                                "type": "string",
                                "description": "PricebookEntry ID"
                            },
                            "quantity": {
                                "type": "integer",
                                "minimum": 1
                            }
                        },
                        "required": ["pricebook_entry_id", "quantity"]
                    }
                },
                "checkout_source": {
                    "type": "string",
                    "enum": ["Voice", "Web"],
                    "default": "Voice"
                }
            },
            "required": ["customer", "items"]
        }
    },
    {
        "type": "function",
        "name": "lookup_order_status",
        "description": "Look up order status by order number or customer email",
        "parameters": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "Salesforce order number (e.g., 00000103)"
                },
                "email": {
                    "type": "string",
                    "description": "Customer email to find their orders"
                }
            },
            "required": []
        }
    }
]


# Tool implementation functions
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, openai_api_key=os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define structured schema
class ProductQuery(BaseModel):
    query: str = Field(..., description="Main product keyword or name")
    category: Optional[str] = Field(None, description="General category like Footwear, Accessories, Watches")
    color: Optional[str] = Field(None, description="Color name if mentioned")
    size: Optional[str] = Field(None, description="Product size if relevant")
    price_min: Optional[float] = Field(None, description="Minimum price")
    price_max: Optional[float] = Field(None, description="Maximum price")

# Create LangChain parser for structured JSON output
parser = PydanticOutputParser(pydantic_object=ProductQuery)

# Create a clean, robust prompt
prompt = PromptTemplate(
    template=(
        "You are a product search assistant for an e-commerce store.\n"
        "Extract structured search filters from this natural language query.\n\n"
        "User Query: {user_query}\n\n"
        "{format_instructions}\n"
    ),
    input_variables=["user_query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

def interpret_search_query(user_query: str) -> dict:
    """Use LangChain + OpenAI to extract structured filters from any user query."""
    try:
        chain_input = prompt.format_prompt(user_query=user_query)
        response = llm.invoke(chain_input.to_string())
        filters = parser.parse(response.content)
        return filters.dict()
    except Exception as e:
        print(f"⚠️ Failed to interpret query using LangChain parser: {e}")
        # fallback — use OpenAI raw method
        try:
            response = client.responses.create(
                model="gpt-4o-mini",
                input=f"Extract structured filters as JSON from: {user_query}",
                temperature=0.2,
                max_output_tokens=200,
            )
            return json.loads(response.output_text)
        except Exception as e2:
            print(f"⚠️ Fallback also failed: {e2}")
            return {
                "query": user_query,
                "category": None,
                "color": None,
                "size": None,
                "price_min": None,
                "price_max": None,
            }


def tool_search_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    price_max: Optional[float] = None,
    price_min: Optional[float] = None,
    color: Optional[str] = None,
    size: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search products in Salesforce with filters (now AI-enhanced)"""

    # 🧠 If query exists but seems like a full sentence → interpret with OpenAI
    if query and len(query.split()) > 2:
        print(f"🧠 Interpreting user query with OpenAI: '{query}'")
        filters = interpret_search_query(query)
        query = filters.get("query")
        category = filters.get("category")
        color = filters.get("color")
        size = filters.get("size")
        price_min = filters.get("price_min")
        price_max = filters.get("price_max")

    # Build SOQL query
    base_query = """
    SELECT Id, Name, ProductCode, Description, Color__c, Size__c, Family, 
           (SELECT Id, UnitPrice FROM PricebookEntries WHERE IsActive = true LIMIT 1),
           Image_URL__c
    FROM Product2
    WHERE IsActive = true
    """

    conditions = []

    if category:
        conditions.append(f"Family = '{category}'")

    if color:
        conditions.append(f"Color__c LIKE '%{color}%'")

    if size:
        conditions.append(f"Size__c LIKE '%{size}%'")

    if query:
        conditions.append(f"(Name LIKE '%{query}%' OR Description LIKE '%{query}%')")

    if price_max:
        conditions.append(f"""
            Id IN (SELECT Product2Id FROM PricebookEntry 
                   WHERE UnitPrice <= {price_max} AND IsActive = true)
        """)

    if price_min:
        conditions.append(f"""
            Id IN (SELECT Product2Id FROM PricebookEntry 
                   WHERE UnitPrice >= {price_min} AND IsActive = true)
        """)

    if conditions:
        base_query += " AND " + " AND ".join(conditions)

    base_query += " LIMIT 10"

    try:
        print(f"🔍 Salesforce SOQL: {base_query}")
        results = sf.query(base_query)
        products = []

        for record in results['records']:
            pbe = record.get('PricebookEntries', {}).get('records', [])
            if pbe:
                products.append({
                    "id": record['Id'],
                    "name": record['Name'],
                    "price": pbe[0]['UnitPrice'],
                    "description": record.get('Description', ''),
                    "color": record.get('Color__c', ''),
                    "size": record.get('Size__c', ''),
                    "product_code": record.get('ProductCode', ''),
                    "pricebook_entry_id": pbe[0]['Id'],
                    "category": record.get('Family', ''),
                    "image_url": record.get('Image_URL__c', ''),  # IMPORTANT: Include image_url
                    "url": f"https://store.example.com/product/{record['ProductCode']}"
                })

        return products
    except Exception as e:
        print(f"❌ Error searching products: {e}")
        return []


def tool_add_to_cart(product_name: str, quantity: int, cart: List) -> Dict[str, Any]:
    """Add product to cart - works with both dict and CartItem formats"""
    try:
        # Escape single quotes in product name to prevent SQL injection
        escaped_product_name = product_name.replace("'", "\\'")
        
        # Fetch product details
        product_query = sf.query(f"""
            SELECT Id, Name, ProductCode, Description, Color__c, Size__c,
                   (SELECT Id, UnitPrice FROM PricebookEntries WHERE IsActive = true LIMIT 1),
                   Image_URL__c
            FROM Product2
            WHERE Name = '{escaped_product_name}' AND IsActive = true 
            LIMIT 1
        """)
        
        if not product_query['records']:
            return {"success": False, "message": "Product not found"}
        
        record = product_query['records'][0]
        pbe = record['PricebookEntries']['records'][0]
        
        # Create product as dictionary (compatible with web cart format)
        product_dict = {
            "id": record['Id'],
            "name": record['Name'],
            "price": pbe['UnitPrice'],
            "description": record.get('Description', ''),
            "color": record.get('Color__c', ''),
            "size": record.get('Size__c', ''),
            "product_code": record.get('ProductCode', ''),
            "pricebook_entry_id": pbe['Id'],
            "category": record.get('Family', ''),
            "image_url": record.get('Image_URL__c', '')
        }
        
        # Check if product already exists in cart
        for item in cart:
            # Handle both dict and CartItem formats
            if isinstance(item, dict):
                existing_product_id = item.get('product', {}).get('id')
            else:
                existing_product_id = item.product.id
            
            if existing_product_id == product_dict['id']:
                # Update quantity
                if isinstance(item, dict):
                    item['quantity'] += quantity
                else:
                    item.quantity += quantity
                
                # Calculate cart total
                cart_total = calculate_cart_total(cart)
                
                return {
                    "success": True,
                    "message": f"Updated {product_dict['name']} quantity in cart",
                    "cart_total": cart_total
                }
        
        # Add new item to cart as dict (compatible with web format)
        cart.append({
            "product": product_dict,
            "quantity": quantity
        })
        
        # Calculate cart total
        cart_total = calculate_cart_total(cart)
        
        return {
            "success": True,
            "message": f"Added {quantity}x {product_dict['name']} to cart",
            "cart_total": cart_total
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"Error adding to cart: {str(e)}"}


def calculate_cart_total(cart: List) -> float:
    """Calculate total price of cart - handles both dict and CartItem formats"""
    total = 0.0
    for item in cart:
        try:
            if isinstance(item, dict):
                # Web format: {'product': {...}, 'quantity': 1}
                price = item.get('product', {}).get('price', 0)
                quantity = item.get('quantity', 0)
            else:
                # CartItem format: CartItem(product=Product(...), quantity=1)
                price = item.product.price
                quantity = item.quantity
            
            total += price * quantity
        except Exception as e:
            print(f"⚠️ Error calculating item total: {e}")
            continue
    
    return total



def tool_place_order(customer: Dict, items: List[Dict], checkout_source: str = "Voice") -> Dict[str, Any]:
    """Place order in Salesforce"""
    try:
        # Upsert account
        account_id = upsert_account(
            email=customer['email'],
            name=customer['name'],
            phone=customer.get('phone', '')
        )
        
        # Get standard pricebook
        pricebook_id = get_standard_pricebook()
        
        # Create order
        order_data = Order(
            AccountId=account_id,
            Pricebook2Id=pricebook_id,
            EffectiveDate=datetime.now().strftime("%Y-%m-%d"),
            Status="Draft",
            CheckoutSource__c=checkout_source
        )
        
        order_result = create_order(order_data)
        if not order_result:
            return {"success": False, "message": "Failed to create order"}
        
        order_id = order_result['id']
        
        # Add order items
        order_items = []
        total_amount = 0.0
        
        for item in items:
            # Get price from PricebookEntry
            pbe_query = sf.query(f"""
                SELECT UnitPrice FROM PricebookEntry 
                WHERE Id = '{item['pricebook_entry_id']}' LIMIT 1
            """)
            unit_price = pbe_query['records'][0]['UnitPrice']
            
            order_item_data = OrderItem(
                OrderId=order_id,
                PricebookEntryId=item['pricebook_entry_id'],
                Quantity=item['quantity'],
                UnitPrice=unit_price
            )
            
            item_result = create_order_item(order_item_data)
            if item_result:
                order_items.append(item_result)
                total_amount += unit_price * item['quantity']
        
        # Get order number
        order_query = sf.query(f"SELECT OrderNumber FROM Order WHERE Id = '{order_id}' LIMIT 1")
        order_number = order_query['records'][0]['OrderNumber']
        
        return {
            "success": True,
            "order_number": order_number,
            "order_id": order_id,
            "total_amount": total_amount,
            "items_count": len(order_items)
        }
    except Exception as e:
        print(f"❌ Error placing order: {e}")
        return {"success": False, "message": f"Error placing order: {str(e)}"}


def tool_lookup_order(order_number: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    """Look up order status"""
    try:
        if order_number:
            result = get_order_status(order_number)
            if result['records']:
                order = result['records'][0]
                return {
                    "success": True,
                    "order_number": order.get('OrderNumber'),
                    "status": order.get('Status'),
                    "effective_date": order.get('EffectiveDate'),
                    "total_amount": order.get('TotalAmount', 0.0)
                }
        
        elif email:
            # Find orders by email
            query = f"""
                SELECT Id, OrderNumber, Status, EffectiveDate, TotalAmount
                FROM Order
                WHERE Account.Email = '{email}'
                ORDER BY CreatedDate DESC
                LIMIT 5
            """
            result = sf.query(query)
            
            if result['records']:
                orders = []
                for order in result['records']:
                    orders.append({
                        "order_number": order.get('OrderNumber'),
                        "status": order.get('Status'),
                        "effective_date": order.get('EffectiveDate'),
                        "total_amount": order.get('TotalAmount', 0.0)
                    })
                return {"success": True, "orders": orders}
        
        return {"success": False, "message": "No orders found"}
    except Exception as e:
        return {"success": False, "message": f"Error looking up order: {str(e)}"}