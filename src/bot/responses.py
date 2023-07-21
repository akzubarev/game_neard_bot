def handle_response(text: str):
    processed_text = text.lower()
    match processed_text:
        case "hello":
            response_text = "Сам иди"
        case _:
            response_text = "Че?"
    return response_text
