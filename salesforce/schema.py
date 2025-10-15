from dataclasses import dataclass

@dataclass
class Product2:
    Name: str
    ProductCode: str
    IsActive: bool
    Description: str = ""
    SKU__c: str = ""
    Color__c: str = ""
    Size__c: str = ""
    StorefrontProductUrl__c: str = ""

@dataclass
class Pricebook2:
    Name: str
    IsActive: bool = True
    IsStandard: bool = False

@dataclass
class PricebookEntry:
    Pricebook2Id: str
    Product2Id: str
    UnitPrice: float
    UseStandardPrice: bool = False
    IsActive: bool = True
    CompareAtPrice__c: float = 0.0

@dataclass
class Account:
    Name: str
    Email: str = ""
    Phone: str = ""

@dataclass
class Order:
    AccountId: str
    Pricebook2Id: str
    EffectiveDate: str
    Status: str
    CheckoutSource__c: str = "Voice"
    StorefrontCartId__c: str = ""

@dataclass
class OrderItem:
    OrderId: str
    PricebookEntryId: str
    Quantity: int
    UnitPrice: float
    VariantId__c: str = ""
    SelectedOptions__c: str = ""
