import asyncio
import pickle
import regex as re
import json_repair
import json
from tenacity import AsyncRetrying, RetryError, stop_after_attempt
from modules.chatbox import chatbox
from modules.helper import Doc

INDEX = 0
GEM_ID = 'df8f12a87dcc'
FILE_PATH = "./restored/restored.json"
PROMPT_PATH = './instructions/Trans/init_prompt.txt'
SESSION_PATH = './previous_chat/session'
OUT_PATH = "./out/"
QUERY_SIZE = 20000

async def main():
    # --- 1. Read files ---
    try: 
        with open(SESSION_PATH, 'rb') as f:
            metadata = pickle.load(f)
    except FileNotFoundError:
        metadata = None
        print("No existed session found")

    with open(PROMPT_PATH ,"r") as f:
        prompt = f.read()

    # Use 'utf-8' encoding for broad compatibility
    with open(f"{FILE_PATH}", 'r', encoding='utf-8') as f:
        doc = Doc(json.load(f))
    
    text = json.dumps(doc.document, indent=2, ensure_ascii=False)

    # --- 3. Initialize Client with init_prompt ---
    s = await chatbox.init(gem=GEM_ID, metadata=metadata)
    r = await s.send_message(prompt)
    r = await s.send_message(text)
    blocks = re.findall(r'(?<=```markdown\n)[\s\S]*?(?=\n```)', r.text) 
    if len(blocks) == 2:
        with open(f"{OUT_PATH}Glossary.md", "w") as f: f.write(blocks[0])
        with open(f"{OUT_PATH}ToC.md", "w") as f: f.write(blocks[1])
    else:
        raise ValueError("Server initial response is in wrong format")

    # Switch model to save cost

    # Translating
    queries = doc.generate_queries(QUERY_SIZE)
    for i, query_text in enumerate(queries, start=INDEX):
        try:
            async for attempt in AsyncRetrying(stop=stop_after_attempt(3), after=s.restart):
                with attempt: 
                    print(f"Processing chunk {i}")
                    r = await s.send_message(query_text)
                    if not isinstance( patches := json_repair.loads(r.text), dict):
                        with open(f"{OUT_PATH}error_response.txt", 'w', encoding='utf-8') as f: f.write(r.text)
                        raise TypeError("Server Response is not dict")
                    doc.patch_trans(patches)
        except RetryError as e:
            print(e)
            break

        with open(f"{OUT_PATH}translated.json", "w", encoding='utf-8') as f:
            json.dump(doc.document, f, indent=2, ensure_ascii=False)
        md = doc.to_markdown()
        with open('./out/translated.md', 'w', encoding='utf-8') as f:
            f.write(md)
        # if i == 0:
        #     s.model = 'gemini-2.5-flash'
        #     await s.restart()
        
    if ep := doc.err_patchs:
        with open(f"{OUT_PATH}error_patch.json", 'w', encoding='utf-8') as f: json.dump(ep, f, indent=2, ensure_ascii=False)
    if session:= await s.close():
        with open(SESSION_PATH, 'wb') as s: pickle.dump(session, s)
    print("Client closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")



