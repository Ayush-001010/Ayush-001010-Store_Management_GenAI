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
from Table.PurchasingTrackingDayByDay import PurchasingTrackingDayWiseTable
from Table.Selling import Selling
from Table.Orginization import Orginization
from Table.User import UsersTable
from Table.Inventory import Inventory
from sqlalchemy import func,and_
from datetime import datetime, timedelta
import json;
from sqlalchemy import or_



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

# try:
#     records = session.query(PurchasingTrackingTable).all()  # Fetch all rows
#     if not records:
#         print("No records found in purchasingTrackingTables.")
#     else:
#         for record in records:
#             print(f"Month: {record.month}, Year: {record.year}, Revenue: {record.revenue}, Loss: {record.loss}")
# except Exception as e:
#     print(f"Error querying purchasingTrackingTables: {e}")
# finally:
#     session.close()

# try:
#     with engine.connect() as connection:
#         print("Connection to MySQL successful!")
# except Exception as e:
#     print("Failed to connect to MySQL:", e)
###


monthNameConfig = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

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
    last24hrsProfit: Decimal
    last7DaysRevenue: Decimal
    last7DaysLoss: Decimal
    last7DaysProfit: Decimal
    last30DaysRevenue: Decimal
    last30DaysLoss: Decimal
    last30DaysProfit: Decimal
    lastOneYearRevenue: Decimal
    lastOneYearLoss: Decimal
    lastOneYearProfit: Decimal
    sellingItemsOverLast7Days: list[SellingItemObj]
    lowStockItemList: list[LowStockItemObj]
    currentInventoryStatus: list[InventoryStatus]

    def to_dict(self):
        return {
            "shopId": self.shopId,
            "shopName": self.shopName,
            "last24hrsRevenue": float(self.last24hrsRevenue),
            "last24hrsLoss": float(self.last24hrsLoss),
            "last7DaysRevenue": float(self.last7DaysRevenue),
            "last7DaysLoss": float(self.last7DaysLoss),
            "last30DaysRevenue": float(self.last30DaysRevenue),
            "last30DaysLoss": float(self.last30DaysLoss),
            "lastOneYearRevenue": float(self.lastOneYearRevenue),
            "lastOneYearLoss": float(self.lastOneYearLoss),
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
    storeRecords = session.query(Store).filter(Store.organizationId == organization_id).all()
    arr : list[StoreAnalyticObj]=  []
    message_history = [
        {
            "role": "system",
            "content": System_Prompt_ShopOwner_Dashboard,
        }
    ]
    for store in storeRecords:
        obj = StoreAnalyticObj()
        obj.shopId = store.id
        obj.shopName = store.name
        obj.last24hrsRevenue = Decimal(0)
        obj.last24hrsLoss = Decimal(0)
        obj.last24hrsProfit = Decimal(0)
        obj.last7DaysRevenue = Decimal(0)
        obj.last7DaysLoss = Decimal(0)
        obj.last7DaysProfit = Decimal(0)
        obj.last30DaysRevenue = Decimal(0)
        obj.last30DaysLoss = Decimal(0)
        obj.last30DaysProfit = Decimal(0)
        obj.lastOneYearRevenue = Decimal(0)
        obj.lastOneYearLoss = Decimal(0)
        obj.lastOneYearProfit = Decimal(0)
        obj.sellingItemsOverLast7Days = []
        obj.lowStockItemList = []
        obj.currentInventoryStatus = []

        # 24 hrs revenue , profit and loss
        now = datetime.now()
        last_24_hours = now - timedelta(hours=24)
        day = last_24_hours.day
        month = monthNameConfig[last_24_hours.month]
        year = last_24_hours.year

        last_24_hours_revenu = session.query(func.sum(PurchasingTrackingDayWiseTable.revenue)).filter(and_(PurchasingTrackingDayWiseTable.day == day , PurchasingTrackingDayWiseTable.storeId == store.id , PurchasingTrackingDayWiseTable.month == month , PurchasingTrackingDayWiseTable.year == year )).scalar()
        last_24_hours_loss = session.query(func.sum(PurchasingTrackingDayWiseTable.loss)).filter(and_(PurchasingTrackingDayWiseTable.day == day , PurchasingTrackingDayWiseTable.storeId == store.id , PurchasingTrackingDayWiseTable.month == month , PurchasingTrackingDayWiseTable.year == year )).scalar()

        if type(last_24_hours_revenu) is Decimal | float:
            obj.last24hrsRevenue = last_24_hours_revenu
        if type(last_24_hours_loss) is Decimal | float:
            obj.last24hrsLoss = last_24_hours_loss
        if type(last_24_hours_revenu) is Decimal | float and type(last_24_hours_loss) is Decimal | float:
            obj.last24hrsProfit = last_24_hours_revenu - last_24_hours_loss
        
        # 7 days revenue , profit and loss
        last_7_days = now - timedelta(days=7)
        last_7_days_revenu = session.query(func.sum(PurchasingTrackingDayWiseTable.revenue)).filter(and_(PurchasingTrackingDayWiseTable.storeId == store.id , PurchasingTrackingDayWiseTable.month == month , PurchasingTrackingDayWiseTable.year == year , PurchasingTrackingDayWiseTable.createdAt >= last_7_days)).scalar()
        last_7_days_loss = session.query(func.sum(PurchasingTrackingDayWiseTable.loss)).filter(and_(PurchasingTrackingDayWiseTable.storeId == store.id , PurchasingTrackingDayWiseTable.month == month , PurchasingTrackingDayWiseTable.year == year , PurchasingTrackingDayWiseTable.createdAt >= last_7_days)).scalar() 
        if last_7_days_revenu:
            obj.last7DaysRevenue = last_7_days_revenu
        if last_7_days_loss:
            obj.last7DaysLoss = last_7_days_loss
        if last_7_days_revenu and last_7_days_loss :
            obj.last7DaysProfit = last_7_days_revenu - last_7_days_loss
        
        print(" Profit for last 7 days ",obj.last7DaysProfit , " \n Revenue ", obj.last7DaysRevenue , " \n Loss " , obj.last7DaysLoss, " \n store id ", store.id , " \n date ", last_7_days , " month ", month , " year ", year)
        
        #  30 days revenue , profit and loss
        last_30_date = now - timedelta(days=30)
        last_30_days_revenu = session.query(func.sum(PurchasingTrackingTable.revenue)).filter(and_(PurchasingTrackingTable.storeId == store.id , PurchasingTrackingTable.createdAt >= last_30_date)).scalar()
        last_30_days_loss = session.query(func.sum(PurchasingTrackingTable.loss)).filter(and_(PurchasingTrackingTable.storeId == store.id , PurchasingTrackingTable.createdAt >= last_30_date)).scalar()
        if last_30_days_revenu:
            obj.last30DaysRevenue = last_30_days_revenu
        if last_30_days_loss:
            obj.last30DaysLoss = last_30_days_loss
        if last_30_days_revenu and last_30_days_loss:
            obj.last30DaysProfit = last_30_days_revenu - last_30_days_loss

        #  1 year revenue , profit and loss
        last_one_year_date = now - timedelta(days=365)
        last_one_year_revenu = session.query(func.sum(PurchasingTrackingTable.revenue)).filter(and_(PurchasingTrackingTable.storeId == store.id , PurchasingTrackingTable.createdAt >= last_one_year_date)).scalar()
        last_one_year_loss = session.query(func.sum(PurchasingTrackingTable.loss)).filter(and_(PurchasingTrackingTable.storeId == store.id , PurchasingTrackingTable.createdAt >= last_one_year_date)).scalar()
        print("Last one year revenu ",last_one_year_revenu)
        if last_one_year_revenu:
            obj.lastOneYearRevenue = last_one_year_revenu
        if last_one_year_loss:
            obj.lastOneYearLoss = last_one_year_loss
        if last_one_year_revenu and last_one_year_loss:
            obj.lastOneYearProfit = last_one_year_revenu - last_one_year_loss
       
        # Selling items over last 7 days
        selling_items = session.query(Selling).filter(and_(Selling.storeId == store.id , Selling.dateOfSale >= last_7_days)).all()
        for item in selling_items:
            selling_item_obj = SellingItemObj()
            selling_item_obj.itemName = session.query(Inventory).filter(Inventory.id == item.inventoryId).first().productName
            selling_item_obj.totalSoldQuantity = item.quantitySold
            selling_item_obj.totalProfitGenrated = Decimal(item.unitSellingPrice) * Decimal(item.quantitySold)
            obj.sellingItemsOverLast7Days.append(selling_item_obj)
        
        # Low stock item list
        low_stock_items = session.query(Inventory).filter(and_(Inventory.storeId == store.id , Inventory.isInStock <= Inventory.lowAlertLimit)).all()
        for item in low_stock_items:
            low_stock_item_obj = LowStockItemObj()
            low_stock_item_obj.itemName = item.productName
            low_stock_item_obj.currentStockQuantity = item.isInStock
            low_stock_item_obj.lowAlertLimit = item.lowAlertLimit
            obj.lowStockItemList.append(low_stock_item_obj)
        
        # Current inventory status
        inventory_items = session.query(Inventory).filter(Inventory.storeId == store.id).all()
        for item in inventory_items:
            inventory_status_obj = InventoryStatus()
            inventory_status_obj.itemName = item.productName
            inventory_status_obj.currentStockQuantity = item.isInStock
            inventory_status_obj.isInStock = item.isInStock > 0
            inventory_status_obj.lowAlertLimit = item.lowAlertLimit
            obj.currentInventoryStatus.append(inventory_status_obj)

        arr.append(obj)

    # data_to_serialize = [store_obj.to_dict() for store_obj in arr]
    data_to_serialize = [store_obj.to_dict() for store_obj in arr]
    message_history.append({
        "role": "user",
        "content": f"Provide an analytic newspaper for my shop with the following details: {json.dumps(data_to_serialize, cls=DecimalEncoder)}"
    })

    print("Obj  ",data_to_serialize)
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
    return {"response": "Something Went Wrong"}

from typing import Optional

def getUserDetails(location: Optional[str] = None, name_starts_with: Optional[str] = None):
    """
    Get users by location and/or name pattern
    
    Args:
        location: Location to search (e.g., "Pune")
        name_starts_with: First letter of name (e.g., "P")
    """
    # Start with base query
    query = session.query(UsersTable)
    
    # Apply location filter if provided
    if location:
        query = query.filter(UsersTable.location.ilike(f"%{location}%"))
    
    # Apply name filter if provided
    if name_starts_with:
        query = query.filter(UsersTable.userName.ilike(f"{name_starts_with}%"))
    
    userDetails = query.all()
    
    return [
        {
            "userName": user.userName,
            "userEmail": user.userEmail,
            "location": user.location,
            "id": user.id,
            "userProfileImage": user.userProfileImage if hasattr(user, 'userProfileImage') else None
        }
        for user in userDetails
    ]


@app.post("/chat-group-info")
def chatGroupInfoEndPoint(user_input: str):
    System_Prompt_Group_Info = """
You are an expert AI assistant specialized in finding users based on their location and name.
You work with Start, Plan, Tool, Observe, and Output steps.

Rules:
- Strictly follow JSON output format.
- Only run one step at a time.
- For every tool call, wait for the Observe step (tool output).
- Sequence: Start → Plan → Tool → Observe → Output

Available TOOL:
- getUserDetails: Get user details based on location and/or name pattern.
  Parameters:
  * location (optional): Partial or full location name (e.g., "Pune", "Mumbai")
  * name_starts_with (optional): First letter(s) of username (e.g., "P", "H", "Pa")

Your Capabilities:
1. Find users by LOCATION: "users in Pune"
2. Find users by NAME: "users whose name starts with P"
3. Find users by BOTH: "users in Pune whose name starts with H"

Task Flow:
1. Extract location and/or name pattern from user query
2. Call getUserDetails tool with appropriate parameters
3. Return user details in specified format

Output Format (Success):
[
  {
    "userName": "John Doe",
    "userEmail": "john@example.com",
    "location": "Pune",
    "id": "user123",
    "userProfileImage": "image_url"
  }
]

Output Format (Out of Scope):
[
  {
    "message": "Sorry, I can only provide user information based on location and/or name. Please ask about users in a specific location or with a specific name pattern."
  }
]

Example 1 - Location Query:
User: "Show me users in Pune"

Response Steps:
{
  "step": "Start",
  "content": "User wants to find users in Pune"
}
{
  "step": "Plan",
  "content": "Extract location: 'Pune'. Call getUserDetails with location parameter."
}
{
  "step": "Tool",
  "content": {
    "toolName": "getUserDetails",
    "toolInput": {
      "location": "Pune",
      "name_starts_with": null
    }
  }
}
{
  "step": "Observe",
  "content": [
    {
      "userName": "Ayush Kumar",
      "userEmail": "ayush@example.com",
      "location": "Pune",
      "id": "user1",
      "userProfileImage": "img1.jpg"
    }
  ]
}
{
  "step": "Output",
  "content": [
    {
      "userName": "Ayush Kumar",
      "userEmail": "ayush@example.com",
      "location": "Pune",
      "id": "user1",
      "userProfileImage": "img1.jpg"
    }
  ]
}

Example 2 - Name Query:
User: "Find users whose name starts with P"

Response Steps:
{
  "step": "Start",
  "content": "User wants users whose name starts with P"
}
{
  "step": "Plan",
  "content": "Extract name pattern: 'P'. Call getUserDetails with name_starts_with parameter."
}
{
  "step": "Tool",
  "content": {
    "toolName": "getUserDetails",
    "toolInput": {
      "location": null,
      "name_starts_with": "P"
    }
  }
}
{
  "step": "Observe",
  "content": [
    {
      "userName": "Priya Sharma",
      "userEmail": "priya@example.com",
      "location": "Mumbai",
      "id": "user2",
      "userProfileImage": "img2.jpg"
    }
  ]
}
{
  "step": "Output",
  "content": [
    {
      "userName": "Priya Sharma",
      "userEmail": "priya@example.com",
      "location": "Mumbai",
      "id": "user2",
      "userProfileImage": "img2.jpg"
    }
  ]
}

Example 3 - Combined Query:
User: "Users in Pune whose name starts with H"

Response Steps:
{
  "step": "Start",
  "content": "User wants users in Pune with names starting with H"
}
{
  "step": "Plan",
  "content": "Extract location: 'Pune' and name pattern: 'H'. Call getUserDetails with both parameters."
}
{
  "step": "Tool",
  "content": {
    "toolName": "getUserDetails",
    "toolInput": {
      "location": "Pune",
      "name_starts_with": "H"
    }
  }
}
{
  "step": "Observe",
  "content": [
    {
      "userName": "Harsh Patel",
      "userEmail": "harsh@example.com",
      "location": "Pune",
      "id": "user3",
      "userProfileImage": "img3.jpg"
    }
  ]
}
{
  "step": "Output",
  "content": [
    {
      "userName": "Harsh Patel",
      "userEmail": "harsh@example.com",
      "location": "Pune",
      "id": "user3",
      "userProfileImage": "img3.jpg"
    }
  ]
}

Example 4 - Out of Scope:
User: "What's the weather today?"

Response:
{
  "step": "Start",
  "content": "User asking about weather - out of scope"
}
{
  "step": "Plan",
  "content": "This query is not related to user search. Provide polite out-of-scope message."
}
{
  "step": "Output",
  "content": [
    {
      "message": "Sorry, I can only provide user information based on location and/or name. Please ask about users in a specific location or with a specific name pattern."
    }
  ]
}

Important Notes:
- Always extract both location and name_starts_with from query
- If query has only location, set name_starts_with to null
- If query has only name, set location to null
- If query has both, use both parameters
- Be flexible with phrasing: "starts with", "beginning with", "name like", etc.
    """
    
    message_history = [
        {
            "role": "system",
            "content": System_Prompt_Group_Info
        }
    ]
    
    message_history.append({"role": "user", "content": user_input})
    
    max_iterations = 10  # Prevent infinite loops
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=message_history,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            message_history.append({
                "role": "assistant",
                "content": response.choices[0].message.content
            })
            
            current_step = result.get("step")
            
            if current_step == "Output":
                print(f"✅ Output: {result.get('content')}")
                return {
                    "data": result.get("content"),
                    "success": True
                }
            
            elif current_step == "Plan":
                print(f"🤖 Plan: {result.get('content')}")
            
            elif current_step == "Tool":
                tool_info = result.get("content", {})
                tool_name = tool_info.get("toolName")
                tool_input = tool_info.get("toolInput", {})
                
                print(f"🔧 Calling Tool: {tool_name} with input: {tool_input}")
                
                # Execute the tool
                if tool_name == "getUserDetails":
                    location = tool_input.get("location")
                    name_starts_with = tool_input.get("name_starts_with")
                    
                    # Call the function
                    tool_result = getUserDetails(
                        location=location,
                        name_starts_with=name_starts_with
                    )
                    
                    # Add observe step to history
                    observe_message = {
                        "step": "Observe",
                        "content": tool_result
                    }
                    message_history.append({
                        "role": "user",
                        "content": json.dumps(observe_message)
                    })
                    
                    print(f"📊 Tool Result: {tool_result}")
                else:
                    print(f"⚠️ Unknown tool: {tool_name}")
            
            elif current_step == "Start":
                print(f"🚀 Start: {result.get('content')}")
            
            else:
                print(f"❓ Unknown step: {current_step}")
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Something went wrong"
            }
    
    return {
        "success": False,
        "message": "Max iterations reached"
    }
