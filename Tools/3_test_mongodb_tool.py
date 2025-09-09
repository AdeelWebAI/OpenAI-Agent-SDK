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

client = AsyncOpenAI(api_key=gemini_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

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
    try:
        parsed_date = datetime.strptime(due_date, "%d %B %Y").isoformat()
    except ValueError:
        parsed_date = due_date
    doc = {
        "title": title,
        "description": description,
        "due_date": parsed_date,
        "created_at": datetime.utcnow().isoformat() + 'Z'
    }
    try:
        result = mongo_client['todo']['todo'].insert_one(doc)
        return f"Todo added: {description} (ID: {result.inserted_id})."
    except Exception as e:
        raise Exception(f"Failed to create todo: {str(e)}")

@function_tool
def fetch_todos():
    """
    goal:
        fetch todos from mongodb and return as a list.
    """
    try:
        todos = list(mongo_client['todo']['todo'].find())
        for todo in todos:
            todo['_id'] = str(todo['_id'])
        return todos
    except Exception as e:
        raise Exception(f"Failed to fetch todos: {str(e)}")

# Test the fetch_todos function directly
print("Testing fetch_todos function...")
try:
    todos = fetch_todos()
    print(f"Found {len(todos)} todos:")
    for todo in todos:
        print(f"- {todo.get('title', 'No title')}: {todo.get('description', 'No description')}")
except Exception as e:
    print(f"Error: {e}")

mongo_client.close()
