from tenacity import AsyncRetrying, RetryError, stop_after_attempt, wait_fixed
import asyncio
import pickle
import sys
import regex as re
from gemini_webapi import GeminiClient
from typing import Dict, Any

INDEX = 0
AGENTID = 'df8f12a87dcc'

def generateQueries(paragraphs: list, num: int):
    queries = []
    t = ''
    char_limit = num  # Define limit clearly
    for x in paragraphs:
        if len(t) + len(x) > char_limit and t:
            queries.append(t + "\n")
            t = x
        else:
            t += x
    
    # Add the last remaining chunk
    if t:
        queries.append(t+"\n")

    print(f"Split text into {len(queries)} chunks.")
    return queries


async def main():

    # --- 1. Read files ---
    try:
        # Use 'utf-8' encoding for broad compatibility
        with open("body.txt", 'r', encoding='utf-8') as f:
            body = f.read()
        with open("footnotes.txt", 'r', encoding='utf-8') as f:
            foot = f.read()
    except FileNotFoundError:
        print("Error: text.txt not found. Please create the file.", file=sys.stderr)
        return
    except Exception as e:
        print(f"Error reading text.txt: {e}", file=sys.stderr)
        return
    if not (body or foot):
        print("text.txt is empty. Exiting.", file=sys.stderr)
        return


    # 2. Group chunks into queries up to a character limit
    text = body + foot
    bodies = body.splitlines()
    foots = foot.splitlines()
    b = generateQueries(bodies, 5000)
    f = generateQueries(foots, 5000)
    queries = b + f

    # --- 3. Initialize Client ---
    state: Dict[str, Any] = {
        "client": None,
        "chat": None,
        "metadata": None
    }

    try: 
        with open('session', 'rb') as f:
            state["metadata"] = pickle.load(f)
    except FileNotFoundError:
        print("No existed session found")
        pass

    async def init_gemini(retry_state=None):
        if state["client"]:
            await state["client"].close()
            print(retry_state)
            await asyncio.sleep(10.0)
        # Set a reasonable timeout for initialization
        state["client"] = GeminiClient()
        await state["client"].init(timeout=3000, auto_close=False, close_delay=300, auto_refresh=True)

        # --- 4. Select Gem/Agent ---
        if state.get('metadata'):
            state["chat"] = state["client"].start_chat(model='gemini-2.5-pro', metadata=state.get('metadata'))
        else:
            await state["client"].fetch_gems(include_hidden=False)
            # This ID is specific to your setup.
            agent = state["client"].gems.get(id=AGENTID)
            # Initialize translation task with entire article
            state["chat"] = state["client"].start_chat(model='gemini-2.5-pro', gem=agent)
            state["metadata"] = state["chat"].metadata
            with open("session", "wb") as f:
                pickle.dump(state["metadata"], f)
            print("New chat initiated, waiting for first response")
            r = await state["chat"].send_message(text)
            p = re.compile(r'(?<=```markdown\n)[\s\S]*?(?=\n```)')
            block = p.findall(r.text) 
            if len(block) == 2:
                with open("ToC.md", "w") as f:
                    f.write(block[0]+ "---\n\n")
                with open("Glossary.md", "w") as f:
                    f.write(block[1]+ "---\n\n")

    await init_gemini()
    # 5. Process all queries
    p = re.compile(r'(?<=```markdown\n)[\s\S]*?(?=\n```)')
    for i, query_text in enumerate(queries, start=INDEX):
        print(f"Processing chunk {i}/{len(queries)-1}")
        try:
            async for attempt in AsyncRetrying(stop=stop_after_attempt(10), after=init_gemini):
                with attempt:
                    r = await state["chat"].send_message(query_text)
                    block = p.findall(r.text) 
                    with open("body_translate.md", "a") as f:
                        f.write(block[0]+ "\n\n---\n\n")
                    # with open("glossary.txt", "a") as f:
                    #     f.write(block[1]+ "---\n\n")
        except RetryError as e:
            print(f"All retries failed: {e}")
        
    # --- 6. Close Client ---
    if state["client"].running:
        print("Closing client connection...")
        await state["client"].close()
        print("Client closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")



