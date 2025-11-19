import regex as re
from typing import Iterator
from modules.linerange_GMM import findPhyLRange

def splitArticles(txt: str):
    min, max = findPhyLRange(txt)
    print(min, max)
    # Split by paragraphs (period + newline followed by uppercase letter)
    chunks = re.split(rf'(?<=\n.{{{min},{max}}}\n.{{1,{min - 1}}}\.\d*)\n(?=\p{{Lu}} ?\p{{Ll}}.{{{min},{max}}}\n)', txt)
    return chunks

def generateQueries(paragraphs: list, query_size: int = 10000) -> list[str]:
    current_length = 0
    current_query = ''
    queries = []

    for p in paragraphs:
        l = len(p)
        if l > query_size:
            if current_query:
                queries.append(current_query)
                current_query = ''
                current_length = 0 
            queries.append(p)
        elif current_length + l <= query_size:
            current_query += (p + '\n')
            current_length += l
        else:
            queries.append(current_query)
            current_query = p
            current_length = l
    if current_query:
        queries.append(current_query)
    return queries
