import asyncio
import os
import sys
from typing import List, Tuple

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langchain.agents import create_agent

load_dotenv()


def build_conversation_messages(
    session_memory: List[Tuple[str, str]],
    user_prompt: str,
) -> List[Tuple[str, str]]:
    return [*session_memory, ("user", user_prompt)]


def get_assistant_content(message):
    content = getattr(message, "content", "")
    if not isinstance(content, str):
        return ""
    role = getattr(message, "role", None) or getattr(message, "type", None)
    if role in {"assistant", "ai"}:
        return content
    return ""


def extract_last_assistant_response(messages):
    for message in reversed(messages):
        response = get_assistant_content(message)
        if response:
            return response.strip()
    last = messages[-1]
    return getattr(last, "content", "").strip() if hasattr(last, "content") else ""


async def main():
    server_ip = os.getenv("SERVER_IP", "127.0.0.1")

    client = MultiServerMCPClient({
        "servicenow": {
            "url": f"http://{server_ip}:8000/mcp",
            "transport": "streamable_http",
        }
    })

    tools = await client.get_tools()

    llm = ChatOllama(
        model="gemma4",
        temperature=0,
        streaming=True,
    )

    system_prompt = (
        "You are a helpful IT support assistant. Use the available tools to create incidents in ServiceNow when requested. "
        "Only use the create_incident tool for this workflow."
    )

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
    )

    print("\n")
    print("=" * 40)
    print("====  ServiceNow Support Assistant  ====")
    print("=" * 40)

    session_memory: List[Tuple[str, str]] = []

    while True:
        try:
            print("\n" + "-" * 38)
            user_prompt = input("Enter your prompt (or type 'exit' to quit): ").strip()
        except EOFError:
            print("\nNo more input. Exiting.")
            break

        if not user_prompt:
            continue

        if user_prompt.lower() in {"exit", "quit", "bye"}:
            print("Goodbye!")
            break

        print(f"\nUser: {user_prompt}\n")

        conversation_messages = build_conversation_messages(session_memory, user_prompt)

        result = await agent.ainvoke({"messages": conversation_messages})
        assistant_response = extract_last_assistant_response(result["messages"])

        if assistant_response:
            print("Agent: ", end="")
            print(assistant_response)
            session_memory.append(("user", user_prompt))
            session_memory.append(("ai", assistant_response))
        else:
            print("Agent: (no assistant response received)")

        print()


if __name__ == "__main__":
    asyncio.run(main())