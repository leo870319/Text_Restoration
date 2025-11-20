from gemini_webapi import GeminiClient, ChatSession 
import asyncio

MODEL = 'gemini-3.0-pro'


class chatbox:
    __chat: ChatSession
    model: str
    
    #Prohibit Instanciation with built-in method
    def __new__(cls):
        raise TypeError( f"Do create instance by calling {cls.__name__}(). Use .init()。")

    #Create new session
    @classmethod
    async def init(cls, gem=None, metadata=None, model=MODEL):

        if not (gem or metadata): raise ValueError("No previous chat or gem")

        #Instanciate a session
        instance = object.__new__(cls)
        instance.model = model

        #Create Gemini client
        client = GeminiClient()
        await client.init(timeout=3000, auto_close=False, auto_refresh=True) 
        await client.fetch_gems(include_hidden=False)

        #Start chat
        if metadata: 
            instance.__chat = client.start_chat(model=instance.model, metadata=metadata)
            print("Resume previous chat")
        elif gem: 
            instance.__chat = client.start_chat(model=instance.model, gem=client.gems.get(id=gem))
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
            #save chat history
            metadata = self.__metadata
            #Close current client
            await self.__client.close()
            return metadata

    async def restart(self,  retry_state=None):
        #Retain current setting for new client
        setting=self.__setting 
        await self.close()

        if retry_state:
            print(retry_state)
            print("Sleeping...")
            await asyncio.sleep(20.0)

        client = GeminiClient()
        await client.init(timeout=3000, auto_close=False, auto_refresh=True) 
        self.__chat = client.start_chat(model=self.model, **setting)
