import os
from simple_salesforce import Salesforce
from dotenv import load_dotenv

load_dotenv()

# --- Connect directly for demo ---
sf = Salesforce(
    username=os.getenv("SALESFORCE_USERNAME"),
    password=os.getenv("SALESFORCE_PASSWORD"),
    security_token=os.getenv("SALESFORCE_SECURITY_TOKEN"),
    domain=os.getenv("SALESFORCE_DOMAIN", "test")
)
print("✅ Connected to Salesforce demo org")

# ---- Product2 ----
def create_product(product_data):
    """Create a Product2 record with both standard and custom fields"""
    allowed_fields = {
        "Name",
        "ProductCode",
        "Description",
        "Family",
        "IsActive",
        "SKU__c",
        "Color__c",
        "Size__c",
        "StorefrontProductUrl__c"
    }

    data = {k: v for k, v in product_data.__dict__.items() if k in allowed_fields}

    try:
        res = sf.Product2.create(data)
        print(f"✅ Created Product in Salesforce: {res}")
        return res
    except Exception as e:
        print(f"⚠️ Error creating product: {e}")
        return None


def list_active_products(max_price=None):
    """List active products under a max price."""
    query = f"""
    SELECT Id, Name, ProductCode, Description, Color__c, Size__c, StorefrontProductUrl__c,
        (SELECT UnitPrice FROM PricebookEntries WHERE IsActive = true)
    FROM Product2
    WHERE IsActive = true
      AND Id IN (
          SELECT Product2Id FROM PricebookEntry
          WHERE UnitPrice <= {max_price} AND IsActive = true
      )
    """
    try:
        results = sf.query(query)
        print(f"✅ Found {len(results['records'])} products under ${max_price}")
        return results['records']
    except Exception as e:
        print(f"⚠️ Error listing products: {e}")
        return []

# ---- Pricebook ----
def get_standard_pricebook():
    result = sf.query("SELECT Id FROM Pricebook2 WHERE IsStandard = true LIMIT 1")
    return result['records'][0]['Id']

# ---- Account ----
def upsert_account(email, name, phone=None):
    existing = sf.query(f"SELECT Id FROM Account WHERE Name = '{name}' LIMIT 1")
    if existing['records']:
        return existing['records'][0]['Id']
    res = sf.Account.create({"Name": name, "Phone": phone})
    return res['id']

# ---- Order ----
def create_order(order_data):
    allowed_fields = {
        "AccountId",
        "Pricebook2Id",
        "EffectiveDate",
        "Status",
        "Description"
    }
    data = {k: v for k, v in order_data.__dict__.items() if k in allowed_fields}

    try:
        res = sf.Order.create(data)
        print(f"✅ Order created successfully: {res}")
        return res
    except Exception as e:
        print(f"⚠️ Error creating order: {e}")
        return None


def create_order_item(item_data):
    try:
        res = sf.OrderItem.create(item_data.__dict__)
        print(f"✅ Created OrderItem: {res}")
        return res
    except Exception as e:
        print(f"⚠️ Error creating order item: {e}")
        return None


def get_order_status(order_number):
    query = f"SELECT Id, OrderNumber, Status, EffectiveDate, TotalAmount FROM Order WHERE OrderNumber = '{order_number}' LIMIT 1"
    return sf.query(query)

