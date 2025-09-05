from dotenv import load_dotenv
load_dotenv()
from tavily import TavilyClient
import os

client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))