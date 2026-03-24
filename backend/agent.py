from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from config import ANTHROPIC_API_KEY
from search import search_web as _search_web
from memory import add_conversation, get_memory_summary
from flowise import get_flowise_memory

@tool
def search_web(query: str) -> str:
    """Search the web for current information about a topic."""
    return _search_web(query)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are Ruby, an advanced AI assistant with a sleek, space-themed personality. You were built by Callum, a developer based in Melbourne, Australia.

Your personality:
- You are intelligent, warm, and slightly futuristic in your tone
- You speak with confidence but never arrogance
- You are helpful, practical, and always focused on giving real value
- You occasionally use subtle space metaphors but never overdo it
- You remember everything the user tells you and refer back to it naturally

Your capabilities:
- You can answer questions, help with research, analyse documents, and assist with business tasks
- You help Callum build and grow his AI business
- You use the search_web tool when you need current information or facts you don't know
- You are aware you are part of a larger system that includes automation workflows

Important rules:
- Always introduce yourself as Ruby if asked who you are
- Never say you are Claude or mention Anthropic
- Keep responses clear and concise unless detail is specifically needed
- Always be honest if you don't know something

{memory_summary}"""),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    api_key=ANTHROPIC_API_KEY,
    temperature=0.7
)
agent = create_tool_calling_agent(llm, [search_web], prompt)
agent_executor = AgentExecutor(agent=agent, tools=[search_web], verbose=True)

chat_history = []

def chat(user_message, image_data=None, image_media_type=None):
    memory_summary = get_memory_summary()
    flowise_context = get_flowise_memory(user_message)
    memory_summary = memory_summary + flowise_context

    if image_data and image_media_type:
        multimodal_message = HumanMessage(content=[
            {
                "type": "image_url",
                "image_url": {"url": f"data:{image_media_type};base64,{image_data}"}
            },
            {"type": "text", "text": user_message}
        ])
        from langchain_core.messages import SystemMessage
        system_message = SystemMessage(content=f"""You are Ruby, an advanced AI assistant with a sleek, space-themed personality built by Callum, a developer based in Melbourne, Australia. You are intelligent, warm, and slightly futuristic. Never say you are Claude or mention Anthropic. Always introduce yourself as Ruby if asked.

{memory_summary}""")
        response = llm.invoke([system_message] + chat_history + [multimodal_message])
        content = response.content
        if isinstance(content, list):
            response_text = "".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )
        else:
            response_text = content
        chat_history.append(multimodal_message)
        chat_history.append(AIMessage(content=response_text))
    else:
        result = agent_executor.invoke({
            "input": user_message,
            "chat_history": chat_history,
            "memory_summary": memory_summary,
        })
        output = result["output"]
        if isinstance(output, list):
            response_text = "".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in output
            )
        else:
            response_text = output
        chat_history.append(HumanMessage(content=user_message))
        chat_history.append(AIMessage(content=response_text))

    add_conversation("user", user_message)
    add_conversation("assistant", response_text)

    return response_text