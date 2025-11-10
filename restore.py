import pickle
import asyncio
import json_repair
import sys
import regex as re
from linerange_GMM import findPhyLRange
from gemini_webapi import GeminiClient, ChatSession
from tenacity import AsyncRetrying, RetryError, stop_after_attempt

INDEX = 0
SOURCE_PATH = "./raw/text2.txt"
OUT_PATH = "./restored/"
SESSION_PATH = "./session"
GEMID = 'cd16701d5533'
MODEL = 'gemini-2.5-pro'
QUERY_SIZE = 10000

class session:
    __chat: ChatSession
    
    #Prohibit Instanciation with built-in method
    def __new__(cls):
        raise TypeError( f"Do create instance by calling {cls.__name__}(). Use .init()。")

    #Create new session
    @classmethod
    async def init(cls, gem=None, metadata=None):

        if not (gem or metadata): raise ValueError("No previous chat or gem")

        #Instanciate a session
        instance = object.__new__(cls)

        #Create Gemini client
        client = GeminiClient()
        await client.init(timeout=3000, auto_close=False, auto_refresh=True) 
        await client.fetch_gems(include_hidden=False)

        #Start chat
        if metadata: 
            instance.__chat = client.start_chat(model=MODEL, metadata=metadata)
            print("Resume previous chat")
        elif gem: 
            instance.__chat = client.start_chat(model=MODEL, gem=client.gems.get(id=gem))
            print("Start new chat")

        return instance

    @property
    def __client(self):
        return self.__chat.geminiclient
    @property
    def __gem(self):
        return self.__chat.gem
    @property
    def __metadata(self):
        return self.__chat.metadata
    @property
    def __setting(self):
        #Setup ChatSession using gems or previous chat history
        if self.__metadata: setup = {"metadata": self.__metadata}
        elif self.__gem: setup = {"gem": self.__gem}
        else: raise ValueError
        return setup

    async def send_message(self, message):
        r = await self.__chat.send_message(message)
        return r 
    
    async def close(self):
        if self.__client.running:
            #Backup current session before close
            with open("session", "wb") as f: pickle.dump(self.__metadata, f)
            #Close current client
            await self.__client.close()

    async def restart(self, retry_state=None):
        if retry_state:
            print(retry_state)
        #Retain current setting for new client
        setting=self.__setting 
        await self.close()
        await asyncio.sleep(10.0)

        client = GeminiClient()
        await client.init(timeout=3000, auto_close=False, auto_refresh=True) 
        self.__chat = client.start_chat(model=MODEL, **setting)
def splitArticles(txt: str):
    min, max = findPhyLRange(txt)
    # Split by paragraphs (period + newline followed by uppercase letter)
    chunks = re.split(rf'(?<=\n.{{{min},{max}}}\n.{{1,{min - 1}}}\.\d*)\n(?=\p{{Lu}} ?\p{{Ll}}.{{{min},{max}}}\n)', txt)
    return chunks

def generateQueries(paragraphs: list, num: int):
    queries = []
    t = ''
    char_limit = num  # Define limit clearly
    for x in paragraphs:
        if len(t) + len(x) > char_limit and t:
            queries.append(t+'\n')
            t = x
        else:
            t += x
    
    # Add the last remaining chunk
    if t:
        queries.append(t+'\n')

    return queries


async def main():

    # --- 1. Read files ---
    try:
        # Use 'utf-8' encoding for broad compatibility
        with open(SOURCE_PATH, 'r', encoding='utf-8') as f:
            txt = f.read()
    except FileNotFoundError:
        print(f"Error: {SOURCE_PATH} not found. Please create the file.", file=sys.stderr)
        return
    if not txt:
        print(f"{SOURCE_PATH} is empty. Exiting.", file=sys.stderr)
        return


    # 2. Group chunks into queries up to a character limit
    chunks = splitArticles(txt)
    print(f"Split text into {len(chunks)} chunks.")
    queries = generateQueries(chunks, QUERY_SIZE)
    print(f"Translation will take {len(queries)} queries to complete.")

    try: 
        with open(SESSION_PATH, 'rb') as f:
            metadata = pickle.load(f)
    except FileNotFoundError:
        metadata = None
        print("No existed session found")
        pass

    # await init_gemini()
    s = await session.init(gem=GEMID, metadata=None)
    print("Gemini chat session initiated")
    # 5. Process all queries
    for i, query_text in enumerate(queries, start=INDEX):
        print(f"Translating: {i}/{len(queries)-1}")
        try:
            async for attempt in AsyncRetrying(stop=stop_after_attempt(10), after=s.restart):
                with attempt:
                    # r = await state["chat"].send_message(query_text)
                    r = await s.send_message(query_text)
                    if not isinstance( jdict := json_repair.loads(r.text), dict):
                        print("Server Response is not JSON")
                        raise TypeError
                    if not (
                        isinstance(maintext := jdict.get("main_text"), str) and
                        isinstance(anote := jdict.get("author_footnotes"), list) and
                        isinstance(enote := jdict.get("editor_footnotes"), list)
                    ):
                        print("JSON format error")
                        raise TypeError
                    with (
                        open(f"{OUT_PATH}body.txt", "a") as b, 
                        open(f"{OUT_PATH}author_footnotes.txt", "a") as af, 
                        open(f"{OUT_PATH}editor_footnotes", "a") as ef
                    ):
                        b.write(maintext + "\n")
                        if enote: ef.write("\n".join(enote) + "\n") 
                        if anote: af.write("\n".join(anote) + "\n")
        except RetryError as e:
            print(f"All retries failed: {e}")

    # --- 6. Close Client ---
    await s.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")


