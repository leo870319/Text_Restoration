import asyncio
import pickle
import regex as re
import json_repair
import json
from tenacity import AsyncRetrying, RetryError, stop_after_attempt
from modules.chatbox import chatbox
from modules.doc import Doc

INDEX = 0
GEM_ID = 'df8f12a87dcc'
FILE_PATH = "./result/Weber/restored.json"
SESSION_PATH = './previous_chat/session'
OUT_PATH = "./out/"
QUERY_SIZE = 5000

async def main():

    # --- 1. Read files ---
    # try: 
    #     with open(SESSION_PATH, 'rb') as f:
    #         metadata = pickle.load(f)
    # except FileNotFoundError:
    #     metadata = None
    #     print("No existed session found")
    #
    # with open("./instructions/init_prompt_trans.txt" ,"r") as f:
    #     prompt = f.read()

    # Use 'utf-8' encoding for broad compatibility
    with open(f"{FILE_PATH}", 'r', encoding='utf-8') as f:
        doc = Doc(source = json.load(f))
    
    # with open('./out/translated.json', 'r', encoding='utf-8') as f:
    #     doucment = json.load(f)
    document = doc.document
    with open('./out/translated.json', 'w', encoding='utf-8') as f:
        json.dump(document, f,indent=4,  ensure_ascii=False)

    # queries = doc.generate_queries(QUERY_SIZE)

    # --- 3. Initialize Client ---
    # s = await chatbox.init(gem=GEM_ID, metadata=metadata)
    # r = await s.send_message(prompt)
    # r = await s.send_message(text)
    # blocks = re.findall(r'(?<=```markdown\n)[\s\S]*?(?=\n```)', r.text) 
    # if len(blocks) == 2:
    #     with open("ToC.md", "w") as f: f.write(blocks[0])
    #     with open("Glossary.md", "w") as f: f.write(blocks[1])
    # else:
    #     raise ValueError("Server initial response is in wrong format")
    #
    # for i, query_text in enumerate(queries, start=INDEX):
    #     print(f"Processing chunk {i}")
    #     print(query_text)

        # try:
        #     async for attempt in AsyncRetrying(stop=stop_after_attempt(3), after=s.restart):
        #         with attempt: r = await s.send_message(query_text)
        # except RetryError as e:
        #     raise e

        # if not isinstance( patches := json_repair.loads(r.text), dict):
        #     raise TypeError("Server Response is invalid")
        # doc.patch_trans(patches)
        # doc.save()

        
    # if session:= await s.close():
    #     with open(SESSION_PATH, 'wb') as s: pickle.dump(session, s)
    # print("Client closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")



