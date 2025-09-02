from pymongo import MongoClient
from pymongo.server_api import ServerApi
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

uri = os.getenv("MONGODB_URI")
gemini_api_key = os.getenv("GEMINI_API_KEY")

mongo_client = MongoClient(uri, server_api=ServerApi('1'))

try:
    mongo_client.admin.command('ping')
    print("Connected to MongoDB!")
except Exception as e:
    print(f"Connection failed: {e}")
    # Exit or handle

client = AsyncOpenAI(api_key=gemini_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")  # Verify URL

@function_tool
def create_todo(title: str, description: str, due_date: str):
    """
    goal:
        create a todo in mongodb.
    args:
        title: the title of the todo.
        description: the description of the todo.
        due_date: the due date of the todo.
    
    """
    if not title or not description:
        raise ValueError("Title and description required.")
    # Optional: Parse due_date to ISO
    try:
        parsed_date = datetime.strptime(due_date, "%d %B %Y").isoformat()  # e.g., "4 september 2025" -> "2025-09-04T00:00:00"
    except ValueError:
        parsed_date = due_date  # Fallback
    doc = {
        "title": title,
        "description": description,
        "due_date": parsed_date,
        "created_at": datetime.utcnow().isoformat() + 'Z'
    }
    try:
        result = mongo_client['todo']['todo'].insert_one(doc)  # Use correct client and names
        return f"Todo added: {description} (ID: {result.inserted_id})."
    except Exception as e:
        raise Exception(f"Failed to create todo: {str(e)}")

# Agent definition (update instructions to match title/desc)
agent = Agent(
    name="Todo Agent",
    instructions="""(updated instructions with title as required, align schema)""",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    tools=[create_todo]
)

query = input("Enter the prompt: ")
result = Runner.run_sync(agent, query)
print(result.final_output)

mongo_client.close()