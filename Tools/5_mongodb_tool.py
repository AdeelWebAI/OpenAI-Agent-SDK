from pymongo import MongoClient
from pymongo.server_api import ServerApi
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional, Union
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

# fetch todos from mongodb and return as a list
@function_tool
def fetch_todos():
    """
    goal:
        fetch todos from mongodb and return as a list.
    """
    try:
        todos = list(mongo_client['todo']['todo'].find())
        # Convert ObjectId to string for JSON serialization
        for todo in todos:
            todo['_id'] = str(todo['_id'])
        return todos
    except Exception as e:
        raise Exception(f"Failed to fetch todos: {str(e)}")

# update todos in mongodb by title match
@function_tool
def update_todo(title: str, new_title: str = "", description: str = "", due_date: str = ""):
    """
    goal:
        update the todos in mongodb by title match.
    args:
        title: the current title of the todo to update.
        new_title: the new title of the todo (leave empty to not change).
        description: the new description of the todo (leave empty to not change).
        due_date: the new due date of the todo (leave empty to not change).
    """
    try:
        # Validate title
        if not title:
            raise ValueError("Title is required to find the todo to update.")
        
        # Build update document with only provided fields
        update_doc = {}
        if new_title and new_title.strip():
            update_doc["title"] = new_title
        if description and description.strip():
            update_doc["description"] = description
        if due_date and due_date.strip():
            try:
                parsed_date = datetime.strptime(due_date, "%d %B %Y").isoformat()
            except ValueError:
                parsed_date = due_date
            update_doc["due_date"] = parsed_date
        
        # Add updated timestamp
        update_doc["updated_at"] = datetime.utcnow().isoformat() + 'Z'
        
        if not update_doc:
            raise ValueError("At least one field must be provided to update.")
        
        # Update the todo by title match
        result = mongo_client['todo']['todo'].update_one(
            {"title": title},
            {"$set": update_doc}
        )
        
        if result.matched_count == 0:
            return f"No todo found with title: '{title}'"
        elif result.modified_count == 0:
            return f"Todo with title '{title}' found but no changes were made"
        else:
            return f"Todo with title '{title}' updated successfully"
            
    except Exception as e:
        raise Exception(f"Failed to update todo: {str(e)}")
        
# delete todos in mongodb by title match
@function_tool
def delete_todo(title: str):
    """
    goal:
        delete todos in mongodb by title match.
    """
    mongo_client['todo']['todo'].delete_one({"title": title})
    return f"Todo with title '{title}' deleted successfully"


# Agent definition (update instructions to match title/desc)
agent = Agent(
    name="Todo Agent",
    instructions="""You are a helpful todo management agent. You can:
1. Create new todos with title, description, and due date
2. Fetch and display all existing todos
3. Update existing todos by title match with new title, description, due date, or completion status

When displaying todos, format them nicely with:
- Title
- Description  
- Due Date
- Created Date
- ID

When updating todos, you need the current title of the todo. If the user wants to update a todo but doesn't provide the title, first fetch all todos to show them the available options with their titles.

Always use the fetch_todos tool when the user asks to see their todos, list todos, or show todos.""",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    tools=[create_todo, fetch_todos, update_todo, delete_todo]
)

query = input("Enter the prompt: ")
result = Runner.run_sync(agent, query)
print(result.final_output)

mongo_client.close()