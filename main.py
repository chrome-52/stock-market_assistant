import os
import sys
import json
import asyncio
import warnings
import contextlib

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

warnings.filterwarnings('ignore')
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = "TRUE"
os.environ['GOOGLE_CLOUD_PROJECT'] = "eci-ugi-digital-ccaipoc"
os.environ['GOOGLE_CLOUD_LOCATION'] = "global"

from agent import root_agent
from trade_utils import print_alerts

async def background_task(session_service, app_name, user_id, session_id):
  try:
    while True:
      await asyncio.sleep(10)

      session = await session_service.get_session(
      app_name=app_name, user_id=user_id, session_id=session_id)
  
      sys.stdout.write("\033[2K\r")  
      sys.stdout.flush()
      print_alerts(session.state)
      sys.stdout.flush()
  except asyncio.CancelledError:
    print("\n[INFO] Background task stopped")
    raise

async def main():
    session_service = InMemorySessionService()
    input_session = PromptSession()
    
    APP_NAME  = "demo"
    USER_ID   = "cr_52"
    SESSION_ID = "session-1"

    try:
        with open("state.json") as f:
            initial_state = json.load(f)
    except:
        initial_state = {"portfolio":dict(), "watchlist":dict()}

    # create the session 
    await session_service.create_session(app_name=APP_NAME, 
                                        user_id=USER_ID, 
                                        session_id=SESSION_ID, 
                                        state=initial_state)
    runner = Runner(agent=root_agent, 
                    app_name=APP_NAME, 
                    session_service=session_service)
    
    try:
        with patch_stdout():
            bg_task = asyncio.create_task(
                background_task(session_service, 
                                APP_NAME, USER_ID, 
                                SESSION_ID))

            while True:
                user_input = await input_session.prompt_async("User: ")
                if user_input.lower().strip() in {"exit", "quit"}:
                    print("Agent: Goodbye!")
                    break

                user_msg = types.Content(role="user", parts=[types.Part(text=user_input)])
                for event in runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=user_msg):
                    if event.is_final_response():
                        print(f"Agent: ", event.content.parts[0].text)

    finally:
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
        with open("state.json", "w") as f:
            json.dump(session.state, f, indent=4)
        bg_task.cancel() 
        with contextlib.suppress(asyncio.CancelledError):
            await bg_task


if __name__ == '__main__':
    asyncio.run(main())

