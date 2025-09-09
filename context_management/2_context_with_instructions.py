from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner
import os
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

hotel_info = """
Welcome to the Grand Aurora Hotel, a prestigious five-star property situated in the vibrant downtown district of New Avalon. Our hotel redefines luxury through personalized service, elegant design, and modern functionality. Designed with both business travelers and leisure guests in mind, the Grand Aurora boasts 250 meticulously designed rooms, including 30 signature suites and 10 extended-stay luxury apartments. Every room features floor-to-ceiling windows, plush king or queen-size beds with premium linens, marble bathrooms, and complimentary high-speed Wi-Fi.
📍 **Address**: 88 Aurora Boulevard, Downtown New Avalon, Avalon City, 55678  
📞 **Phone**: +1 (555) 987-6543  
✉️ **Email**: contact@grandaurorahotel.com  
🌐 **Website**: www.grandaurorahotel.com  
📱 **Social Media**:  
- Instagram: @grandaurorahotel  
- Twitter: @AuroraLuxuryStay  
- Facebook: facebook.com/grandaurorahotel
"""

agent = Agent(
    name="Hotel Assistant",
    instructions="You are Grand Aurora Hotel Assistant" + hotel_info.strip(),
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
)

query = input("Ask your hotel-related question: ")

result = Runner.run_sync(
    agent,
    query,
)

print(result.final_output)