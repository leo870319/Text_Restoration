from typing import Iterator, TypedDict
import regex as re
import json

class Footnote(TypedDict):
    pending: bool
    lb: str
    pos: float
    content: str
class Body(TypedDict):
    pos: float
    content: str
class Response(TypedDict):
    bodies: list[Body]
    author_notes: list[Footnote]
    editor_notes: list[Footnote]


class Doc():
    def __init__(self, source: Response|None = None , doc: dict[str, dict]|None = None):

        self.document: dict[str, dict] = {}
        if source:
            self._source = source
            self._nmap: dict[float, list[Footnote]]= {}
            for n in self._source['author_notes'] + self._source['editor_notes']:
                if self._nmap.get(n['pos']): self._nmap[n['pos']].append(n)
                else: self._nmap[n['pos']] = [n]
            self._attach_notes_to_body()
        elif doc:
            self.document = doc
        else:
            raise ValueError("no source or doc")

        self.err_notes: list[Footnote] = []
        self.err_patchs = []

    def _attach_notes_to_body(self):
        t = {"t1": "<Insert T1 English>", "t2": "<Insert T2 Chinese>", "t3": "<Insert T3 Plain>"}
        for b in self._source["bodies"]:
            if notes := self._nmap.get(b["pos"]):
                notes = {n["lb"]: {"content": n["content"], **t} for n in notes}
                d = {str(b["pos"]): { "content": b["content"], **t, "notes": notes}}
            else: d = {str(b["pos"]): { "content": b["content"], **t}}
            self.document.update(d)

    def generate_queries(self, query_size: int = 10000) -> Iterator[str]:
        current_query: dict[str, dict] = {}
        current_length = 0
        
        for pos, body in self.document.items():
            pos = pos
            b_len = len(str(body))
            if b_len > query_size:
                if current_query:
                    yield json.dumps(current_query, indent=2, ensure_ascii=False)
                    current_query = {}
                    current_length = 0 
                yield json.dumps({pos: body}, indent=2, ensure_ascii=False) 
            elif current_length + b_len <= query_size:
                current_query.update({pos: body})
                current_length += b_len
            else:
                yield json.dumps(current_query, indent=2, ensure_ascii=False)
                current_query = {pos: body}
                current_length = b_len
        if current_query:
            yield json.dumps(current_query, indent=2, ensure_ascii=False)



    def patch_trans(self, patches: dict[str, dict]):
        for pos_str, patch in patches.items():
            try:
                target = self.document.get(pos_str)
            except ValueError:
                target = None

            if not target:
                self.err_patchs.append({pos_str: patch})
                print(f"Warning: Patch received have unknown pos: {pos_str}")
                continue

            target.update({k: v for k, v in patch.items() if k != "notes"})
            t_notes = target.get("notes")
            p_notes = patch.get("notes")
            if p_notes and t_notes:
                for nid, _ in t_notes.items():
                    if nid in p_notes:
                        t_notes[nid].update(p_notes[nid])
                    else:
                        self.err_patchs.append({pos_str: patch})
                        print(f"Warning: Patch received {pos_str} missing  note: {nid}")
            elif p_notes or t_notes:
                self.err_patchs.append({pos_str: patch})
                print(f"Warning: Patch received {pos_str} missing all notes")

    def to_markdown(self):
        pb = '\n\n'
        lc = '<br><br>'
        
        blocks_str = []
        for pos, body in self.document.items():
            sc = body["content"]
            t1 = body.get("t1")
            t2 = body.get("t2")
            t3 = body.get("t3")
            if t1 and t2 and t3:
                t1 = re.sub(r'\n', r'<br>', t1)
                t2 = re.sub(r'\n', r'<br>', t2)
                t3 = re.sub(r'\n', r'<br>', t3)
                body_str ='#### ' + pos + pb + '>' + sc + pb + 'T1: ' + pb + '>' + t1 + pb + 'T2: ' + pb + '>' + t2 + pb + 'T3: ' + pb + '>' + t3
            else:
                body_str = pos + pb + sc
            if notes := body.get("notes"):
                notes_str = []
                for lb, note in notes.items():
                    lb = f'[^{lb}]: '
                    sc = note["content"]
                    t1 = note.get('t1')
                    t2 = note.get('t2')
                    t3 = note.get('t3')
                    if t1 and t2 and t3:
                        t1 = re.sub(r'\n', r'<br>', t1)
                        t2 = re.sub(r'\n', r'<br>', t2)
                        t3 = re.sub(r'\n', r'<br>', t3)
                        s = lb + sc + lc + t1 + lc + t2 + lc + t3
                    else:
                        s = lb + sc 
                    notes_str.append(s)
                notes_str = ('\n').join(notes_str)
                block = body_str + pb + notes_str
            else:
                block = body_str
            block = re.sub(r'(?<=\[\^)(.*?)(?=\])', rf'{pos}-\1', block)
            blocks_str.append(block)
        blocks_str = (pb).join(blocks_str)
        return blocks_str
