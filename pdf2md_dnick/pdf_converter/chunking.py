import re


def split_on_h1_h2(markdown_text: str):
    pattern = re.compile(r'(^#{1,2}\s.*$)', re.MULTILINE)
    parts = pattern.split(markdown_text)

    chunks = []
    current = ""

    for part in parts:
        if pattern.match(part):
            if current.strip():
                chunks.append(current.strip())
            current = part
        else:
            current += "\n" + part

    if current.strip():
        chunks.append(current.strip())

    return chunks
