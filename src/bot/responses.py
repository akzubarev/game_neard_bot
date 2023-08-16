def handle_response(text: str):
    processed_text = text.lower()
    match processed_text:
        case _:
            response_text = "Команда не распознана, попробуйте заново"
    return response_text
