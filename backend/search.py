from tavily import TavilyClient
from config import TAVILY_API_KEY

client = TavilyClient(api_key=TAVILY_API_KEY)

def search_web(query):
    try:
        results = client.search(query=query, max_results=3)
        output = ""
        for r in results["results"]:
            output += f"- {r['title']}: {r['content']}\n"
        return output
    except Exception as e:
        return f"Search unavailable: {str(e)}"
