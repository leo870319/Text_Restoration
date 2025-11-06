import asyncio
import json_repair
import sys
import regex as re
from linerange_GMM import findPhyLRange
from gemini_webapi import GeminiClient

def splitArticles(txt: str):
    r = findPhyLRange(txt)
    min = r[0]
    max = r[1]
    print(min, max)
    # Split by paragraphs (period + newline followed by uppercase letter)
    chunks = re.split(rf'(?<=.{{{min},{max}}}\n.{{1,{min}}}\.\d*)\n(?=[A-Z].?[a-z].{{{min},{max}}})', txt)
    return chunks

def generateQueries(chunks: list, num: int):
    queries = []
    t = ''
    char_limit = num  # Define limit clearly
    for x in chunks:
        if len(t) + len(x) > char_limit and t:
            queries.append(t+'\n\n')
            t = x
        else:
            t += x
    
    # Add the last remaining chunk
    if t:
        queries.append(t+'\n\n')

    print(f"Split text into {len(queries)} chunks.")
    return queries


async def main():

    # --- 1. Read and Chunk Text ---
    try:
        # Use 'utf-8' encoding for broad compatibility
        with open("text3.txt", 'r', encoding='utf-8') as f:
            txt = f.read()
    except FileNotFoundError:
        print("Error: text.txt not found. Please create the file.", file=sys.stderr)
        return
    except Exception as e:
        print(f"Error reading text.txt: {e}", file=sys.stderr)
        return
    
    if not txt:
        print("text.txt is empty. Exiting.", file=sys.stderr)
        return


    # 2. Group chunks into queries up to a character limit
    chunks = splitArticles(txt)
    with open("chunks.txt", "w") as f:
        f.write(("\n----\n").join(chunks))
    queries = generateQueries(chunks, 10000)
    with open("queries.txt", "w") as f:
        f.write(("\n").join(queries))

    # --- 3. Initialize Client ---
    client = GeminiClient()
    chat = None
    # Set a reasonable timeout for initialization
    await client.init(timeout=3000, auto_close=False, close_delay=300, auto_refresh=True)

    # --- 4. Select Gem/Agent ---
    await client.fetch_gems(include_hidden=False)
    gems = client.gems
    # This ID is specific to your setup.
    agent_id = '257091e4e465'
    agent = gems.get(id=agent_id)

    if not agent:
        print(f"Error: Could not find Gem with ID {agent_id}", file=sys.stderr)
        return

    print(f"Using Gem: {agent.name}")
    chat = client.start_chat(model='gemini-2.5-pro', gem=agent)
    # 5. Process all queries
    for i, query_text in enumerate(queries):
        print(f"Sending chunk {i + 1}/{len(queries)}...")
        try:
            r = await chat.send_message(query_text)
            jdict = json_repair.loads(r.text)
            maintext = jdict.get("maintext") + "\n\n"
            footnote = jdict.get("footnotes") + "\n"
            with open("body.txt", "a") as b, open("footnotes.txt", "a") as f:
                b.write(maintext)
                f.write(footnote)
        except Exception as e:
            print(f"Error sending chunk {i + 1}: {e}", file=sys.stderr)
            # Decide whether to continue or stop
            # continue 
            break # Stop on first error

    # --- 6. Close Client ---
    if client.running:
        print("Closing client connection...")
        await client.close()
        print("Client closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")


