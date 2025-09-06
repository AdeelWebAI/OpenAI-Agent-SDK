import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, OpenAIResponsesModel, Runner, WebSearchTool

# Load environment variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initialize AsyncOpenAI client
client = AsyncOpenAI(api_key=openai_api_key)

# Define the Agent
agent = Agent(
    name="Assistant",
    instructions="You are an expert of agentic AI.",
    model=OpenAIResponsesModel(
        model="gpt-3.5-turbo",
        openai_client=client
    ),
    tools=[WebSearchTool()]
)

# Take input from user
query = input("Enter the query: ")

# Run synchronously
result = Runner.run_sync(agent, query)

# Print final output
print(result.final_output)