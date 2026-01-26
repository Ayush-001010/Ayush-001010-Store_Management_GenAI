from fastapi import FastAPI
from dotenv import load_dotenv
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from system_prompt import System_Prompt_Welcome_Message , System_Prompt_Home_Page , System_Prompt_ShopOwner_Dashboard
from pydantic import BaseModel
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Table.Base import Base  # Import the shared Base
from Table.Store import Store
from Table.PurchasingTracking import PurchasingTrackingTable
from Table.Selling import Selling
from Table.Orginization import Orginization
from Table.Inventory import Inventory
from sqlalchemy import func,and_
from datetime import datetime, timedelta
import json;


load_dotenv()

### Database Connection and Testing
username = "root"
password = "Ayush%4010"
hostname = "localhost"
port = 3306
database = "store_management_store"
engine = create_engine(f"mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}")

Session = sessionmaker(bind=engine)  # `engine` is your database connection
session = Session()

try:
    records = session.query(PurchasingTrackingTable).all()  # Fetch all rows
    if not records:
        print("No records found in purchasingTrackingTables.")
    else:
        for record in records:
            print(f"Month: {record.month}, Year: {record.year}, Revenue: {record.revenue}, Loss: {record.loss}")
except Exception as e:
    print(f"Error querying purchasingTrackingTables: {e}")
finally:
    session.close()

try:
    with engine.connect() as connection:
        print("Connection to MySQL successful!")
except Exception as e:
    print("Failed to connect to MySQL:", e)
###



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React frontend in development
    ],
    allow_credentials=True,  # Allow credentials for cookie-based auth
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

client = OpenAI()


class UserInput(BaseModel):
    user_query: str
    type: str

class AnalyticNewPaperInput(BaseModel):
    organization_id : int

 
from decimal import Decimal
import json

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        # Check for Decimal type and convert to float
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)  # Default behavior for other types

class SellingItemObj:
    itemName: str
    totalSoldQuantity: int
    totalProfitGenrated: Decimal  # It might be Decimal from database

    def to_dict(self):
        return {
            "itemName": self.itemName,
            "totalSoldQuantity": self.totalSoldQuantity,
            # Convert Decimal to float
            "totalProfitGenrated": float(self.totalProfitGenrated),
        }

class LowStockItemObj:
    itemName: str
    currentStockQuantity: Decimal  # It might be Decimal from database
    lowAlertLimit: Decimal  # It might be Decimal from database

    def to_dict(self):
        return {
            "itemName": self.itemName,
            # Convert all Decimal values to float
            "currentStockQuantity": float(self.currentStockQuantity),
            "lowAlertLimit": float(self.lowAlertLimit),
        }

class InventoryStatus:
    itemName: str
    currentStockQuantity: Decimal
    isInStock: bool
    lowAlertLimit: Decimal

    def to_dict(self):
        return {
            "itemName": self.itemName,
            "currentStockQuantity": float(self.currentStockQuantity),
            "isInStock": self.isInStock,
            "lowAlertLimit": float(self.lowAlertLimit),
        }


class StoreAnalyticObj:
    shopId: int
    shopName: str
    last24hrsRevenue: Decimal
    last24hrsLoss: Decimal
    last7DaysRevenue: Decimal
    last7DaysLoss: Decimal
    sellingItemsOverLast7Days: list[SellingItemObj]
    lowStockItemList: list[LowStockItemObj]
    currentInventoryStatus: list[InventoryStatus]

    def to_dict(self):
        return {
            "shopId": self.shopId,
            "shopName": self.shopName,
            # Convert Decimal to float
            "last24hrsRevenue": float(self.last24hrsRevenue),
            "last24hrsLoss": float(self.last24hrsLoss),
            "last7DaysRevenue": float(self.last7DaysRevenue),
            "last7DaysLoss": float(self.last7DaysLoss),
            # Serialize nested objects
            "sellingItemsOverLast7Days": [item.to_dict() for item in self.sellingItemsOverLast7Days],
            "lowStockItemList": [item.to_dict() for item in self.lowStockItemList],
            "currentInventoryStatus": [item.to_dict() for item in self.currentInventoryStatus],
        }

@app.get("/")
def read_root():
    return {"Start": "Hello World"}

@app.post("/chat")
def chat_endpoint(user_input: str):
    message_history = [
    {
        "role":"system",
        "content": System_Prompt_Home_Page
    }
    ]
    message_history.append({"role" : "user" , "content":user_input})
    while True :
        response = client.chat.completions.create(
        model="gpt-4o",
        messages=message_history
        )
        result = json.loads(response.choices[0].message.content)
        message_history.append({ "role" : "assistant" , "content" : response.choices[0].message.content})

        if result.get("step") == "Output":
            print(f"Output 👉🏻 {result.get("content")}")
            return {"data": result.get("content") , "success" : True}
            break
        elif result.get("step") == "Plan":
            print(f"Response 🤖 ",response.choices[0].message.content)
        else:
            print(f"Starting.... ",response.choices[0].message.content)

    return {"response": "Something Went Wrong"}

@app.post("/welcome-message")
def welcome_message_endpoint(req: UserInput):
    message_history = [
    {
        "role":"system",
        "content": System_Prompt_Welcome_Message
    }
    ]
    message_history.append({"role" : "user" , "content":req.user_query})
    while True :
        response = client.chat.completions.create(
        model="gpt-4o",
        messages=message_history
        )
        result = json.loads(response.choices[0].message.content)
        message_history.append({ "role" : "assistant" , "content" : response.choices[0].message.content})

        if result.get("step") == "Output":
            print(f"Output 👉🏻 {result.get("content")}")
            return {"data": result.get("content") , "success" : True}
            break
        elif result.get("step") == "Plan":
            print(f"Response 🤖 ",response.choices[0].message.content)
        else:
            print(f"Starting.... ",response.choices[0].message.content)

    return {"response": "Something Went Wrong"}


@app.post("/analytic-newspaper-shopowner")
def analytic_newspaper_shopowner_endpoint(req:AnalyticNewPaperInput) :
# def analytic_newspaper_shopowner_endpoint() :
    organization_id = req.organization_id
    # organization_id = 1
    shopRecords = session.query(Store).filter(Store.organizationId == organization_id).all()
    arr : list[StoreAnalyticObj]=  []
    for shop in shopRecords :
        obj = StoreAnalyticObj()
        obj.shopId = shop.id
        obj.shopName = shop.name
        obj.last24hrsRevenue=0
        obj.last24hrsLoss=0
        obj.last7DaysLoss=0
        obj.last7DaysRevenue=0
        obj.sellingItemsOverLast7Days = []
        obj.lowStockItemList = []
        obj.currentInventoryStatus = []
        print(f"Shop ID : {shop.id}")
        now = datetime.now()
        last_24_hours = now - timedelta(hours=24)
        last_24hrs_revenue = (
            session.query(
                func.sum(PurchasingTrackingTable.revenue)
            )
            .filter(
                and_(
                    PurchasingTrackingTable.storeId == shop.id,  # Match shop ID
                    PurchasingTrackingTable.createdAt >= last_24_hours,  # Records in the last 24 hours
                )
            )
            .scalar()  # Retrieve the sum value as a scalar
        )
        last_24hrs_loss = (
            session.query(
                func.sum(PurchasingTrackingTable.loss)
            )
            .filter(
                and_(
                    PurchasingTrackingTable.storeId == shop.id,  # Match shop ID
                    PurchasingTrackingTable.createdAt >= last_24_hours,  # Records in the last 24 hours
                )
            )
            .scalar()  # Retrieve the sum value as a scalar
        )
        if type(last_24hrs_revenue) is float and last_24hrs_revenue > 0:
            obj.last24hrsRevenue = last_24hrs_revenue
        if type(last_24hrs_loss) is float and last_24hrs_loss > 0:
            obj.last24hrsLoss = last_24hrs_loss
        
        last_7_days = now - timedelta(days=7)
        last_7_days_revenue = (
            session.query(
                func.sum(PurchasingTrackingTable.revenue)
            )
            .filter(
                and_(
                    PurchasingTrackingTable.storeId == shop.id,  # Match shop ID
                    PurchasingTrackingTable.createdAt >= last_7_days,  # Records in the last 24 hours
                )
            )
            .scalar()  # Retrieve the sum value as a scalar
        )
        last_7_days_loss = (
            session.query(
                func.sum(PurchasingTrackingTable.loss)
            )
            .filter(
                and_(
                    PurchasingTrackingTable.storeId == shop.id,  # Match shop ID
                    PurchasingTrackingTable.createdAt >= last_7_days,  # Records in the last 24 hours
                )
            )
            .scalar()  # Retrieve the sum value as a scalar
        )
        if type(last_7_days_revenue) is float and last_7_days_revenue > 0:
            obj.last7DaysRevenue = last_7_days_revenue
        if type(last_7_days_loss) is float and last_7_days_loss > 0:
            obj.last7DaysLoss = last_7_days_loss
        

        selling_records = session.query(Selling).filter(and_( Selling.storeId == shop.id) and Selling.dateOfSale >= last_7_days).all()
        for selling in selling_records :
            prd_details = session.query(Inventory).filter(Inventory.id == selling.inventoryId).first()
            itemObj = SellingItemObj()
            itemObj.itemName = prd_details.productName
            itemObj.totalSoldQuantity = selling.quantitySold
            itemObj.totalProfitGenrated = selling.unitSellingPrice - (prd_details.costPrice * selling.quantitySold)
            obj.sellingItemsOverLast7Days.append(itemObj)
        
        low_stock_items = session.query(Inventory).filter(and_( Inventory.lowAlertLimit != None , Inventory.lowAlertLimit > Inventory.isInStock , Inventory.id.in_(
            session.query(Selling.inventoryId).filter(Selling.storeId == shop.id)
        ))).all()
        for item in low_stock_items :
            lowStockObj = LowStockItemObj()
            lowStockObj.itemName = item.productName
            total_sold_quantity = session.query(func.sum(Selling.quantitySold)).filter(and_( Selling.storeId == shop.id , Selling.inventoryId == item.id)).scalar()
            if total_sold_quantity is None :
                total_sold_quantity = 0
            current_stock_quantity = max(0, 100 - total_sold_quantity)  # Assuming initial stock of 100 for simplicity
            lowStockObj.currentStockQuantity = current_stock_quantity
            lowStockObj.lowAlertLimit = item.lowAlertLimit
            obj.lowStockItemList.append(lowStockObj)
        
        current_stock_quantity = session.query(Inventory).filter(Inventory.id.in_(
            session.query(Selling.inventoryId).filter(Selling.storeId == shop.id)
        )).all()
        for item in current_stock_quantity :
            inventoryStatusObj = InventoryStatus()
            inventoryStatusObj.itemName = item.productName
            total_sold_quantity = session.query(func.sum(Selling.quantitySold)).filter(and_( Selling.storeId == shop.id , Selling.inventoryId == item.id)).scalar()
            if total_sold_quantity is None :
                total_sold_quantity = 0
            current_stock_quantity = max(0, 100 - total_sold_quantity)  # Assuming initial stock of 100 for simplicity
            inventoryStatusObj.currentStockQuantity = current_stock_quantity
            inventoryStatusObj.isInStock = item.isInStock
            inventoryStatusObj.lowAlertLimit = item.lowAlertLimit
            obj.currentInventoryStatus.append(inventoryStatusObj)
        print(f"Last 24hrs Revenue : {obj.last24hrsRevenue} , Last 24hrs Loss : {obj.last24hrsLoss} , Last 7 Days Revenue : {obj.last7DaysRevenue} , Last 7 Days Loss : {obj.last7DaysLoss} ")
        for sellingItem in obj.sellingItemsOverLast7Days :
            print(f"Selling Item Name : {sellingItem.itemName} , Total Sold Quantity : {sellingItem.totalSoldQuantity} , Total Profit Generated : {sellingItem.totalProfitGenrated} ")
        for lowStockItem in obj.lowStockItemList :
            print(f"Low Stock Item Name : {lowStockItem.itemName} , Current Stock Quantity : {lowStockItem.currentStockQuantity} , Low Alert Limit : {lowStockItem.lowAlertLimit} ")
        for inventoryStatus in obj.currentInventoryStatus :
            print(f"Inventory Item Name : {inventoryStatus.itemName} , Current Stock Quantity : {inventoryStatus.currentStockQuantity} , Is In Stock : {inventoryStatus.isInStock} , Low Alert Limit : {inventoryStatus.lowAlertLimit} ")
        arr.append(obj)

    data_to_serialize = [store_obj.to_dict() for store_obj in arr]
    message_history = [
        {
            "role": "system",
            "content": System_Prompt_ShopOwner_Dashboard,
        }
    ]

    message_history.append({
        "role": "user",
        "content": f"Provide an analytic newspaper for my shop with the following details: {json.dumps(data_to_serialize, cls=DecimalEncoder)}"
    })
    # Add to OpenAI messages
    
    while True :
        response = client.chat.completions.create(
        model="gpt-4o",
        messages=message_history
        )
        result = json.loads(response.choices[0].message.content)
        message_history.append({ "role" : "assistant" , "content" : response.choices[0].message.content})

        if result.get("step") == "Output":
            print(f"Output 👉🏻 {result.get("content")}")
            return {"content": result.get("content") , "success" : True , "data" : result.get("data")}
            break
        elif result.get("step") == "Plan":
            print(f"Response 🤖 ",response.choices[0].message.content)
        else:
            print(f"Starting.... ",response.choices[0].message.content)
 

        


    
    
