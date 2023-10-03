def hlink(text: str, link: str):
    return f"[{text}]({link})"


def ready_for_links(text):
    for char in ['_', '*', '[', ']', '(', ')',
                 '~', '`', '>', '#', '+', '-',
                 '=', '|', '{', '}', '.', '!']:
        text = text.replace(char, f"\\{char}")
    return text
