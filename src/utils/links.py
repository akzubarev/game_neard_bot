def hlink(text: str, link: str):
    return f"[{text}]({link})"


def apply_markdown(text):
    for char in ['_', '*',
                 # '[', ']', '(', ')',
                 '~', '`', '>', '#', '+', '-',
                 '=', '|', '{', '}', '.', '!']:
        text = text.replace(char, f"\\{char}")
    return text
