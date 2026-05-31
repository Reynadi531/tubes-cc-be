import asyncio
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv(Path(__file__).parent / "yuki" / ".env")
from yuki.agent import root_agent

APP_NAME = "yuki"
USER_ID = "user_1"
SESSION_ID = "session_001"


async def setup_session_and_runner(
    root_agent: Agent = None, session_id: str = SESSION_ID
):
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session_id
    )
    runner = Runner(
        agent=root_agent, app_name=APP_NAME, session_service=session_service
    )
    return session, runner


async def call_agent_async(
    query: str, root_agent: Agent = None, session_id: str = SESSION_ID
) -> str:
    content = types.Content(role="user", parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner(
        root_agent=root_agent, session_id=session_id
    )
    events = runner.run_async(
        user_id=USER_ID, session_id=session_id, new_message=content
    )
    final_response_text = "No response received."
    found_final = False
    async for event in events:
        if event.is_final_response() and not found_final:
            found_final = True
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )

    print(f"<<< Agent Response: {final_response_text}")
    return final_response_text


async def run_agent_pipeline(query: str) -> str:
    return await call_agent_async(
        query=query, root_agent=root_agent, session_id=SESSION_ID
    )


if __name__ == "__main__":
    user_query = "Perkenalkan dirimu"
    asyncio.run(run_agent_pipeline(query=user_query))
