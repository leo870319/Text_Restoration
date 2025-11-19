import pickle
import asyncio
import json_repair
import json
from tenacity import AsyncRetrying, RetryError, stop_after_attempt
from modules.helper import splitArticles, generateQueries, Response
from modules.chatbox import chatbox

INDEX = 0
PROMPT_PATH = "instructions/init_prompt.txt"
SOURCE_PATH = "raw/text2.txt"
OUT_PATH = "restored/"
QUERY_SIZE = 10000
SESSION_PATH = "previous_chat/session"
GEMID = 'cd16701d5533'

async def main():

    # --- 1. Read files ---
    try:
        # Use 'utf-8' encoding for broad compatibility
        with open(SOURCE_PATH, 'r', encoding='utf-8') as f, open(PROMPT_PATH, 'r') as p:
            txt = f.read()
            prompt = p.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: {SOURCE_PATH} not found.")
    if not txt:
        raise ValueError(f"{SOURCE_PATH} is empty.")

    try: 
        with open(SESSION_PATH, 'rb') as f:
            metadata = pickle.load(f)
    except FileNotFoundError:
        metadata = None
        print("No existed session found")
        pass


    # 2. Group chunks into queries up to a character limit
    chunks = splitArticles(txt)
    print(f"Split text into {len(chunks)} chunks.")
    queries = generateQueries(chunks, QUERY_SIZE)
    print(f"Restoration will take {len(queries)} queries to complete.")

    # await init_gemini()
    s = await chatbox.init(gem=GEMID, metadata=metadata)
    if not (r := await s.send_message(prompt)):
        raise RuntimeError("Oh....")
    # 5. Process all queries
    response = Response(
        bodies=[],
        author_notes=[],
        editor_notes=[]
    )

    for i, query in enumerate(queries, start=INDEX):
        try:
            async for attempt in AsyncRetrying(stop=stop_after_attempt(10), after=s.restart):
                print(f"Restoring: {i}/{len(queries)-1}")
                with attempt: r = await s.send_message(query)
        except RetryError as e:
            print(f"All retries failed: {e}")
            break

        if not isinstance( jdict := json_repair.loads(r.text), dict):
            raise TypeError("Server Response is not JSON")
        if not (
            isinstance(b := jdict.get("b"), list) and
            isinstance(a := jdict.get("a"), list) and
            isinstance(e := jdict.get("e"), list)
        ):
            raise TypeError("JSON format error")

        response["bodies"] += b
        response["author_notes"] += a
        response["editor_notes"] += e


    with open(f"{OUT_PATH}restored.json", "w", encoding='utf-8') as f:
        json.dump(response, f, indent=4, ensure_ascii=False)

    # --- 6. Close Client ---
    if session:= await s.close():
        with open(SESSION_PATH, 'wb') as s: pickle.dump(session, s)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")


