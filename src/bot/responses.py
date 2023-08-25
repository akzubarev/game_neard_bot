def handle_response(text: str):
    processed_text = text.lower()
    match processed_text:
        case _:
            response_text = (
                "Команда не распознана, проверьте что ввели данные в правильном формате\n"
                "Если не получается, нажмите /cancel и попробуйте заново"
            )
    return response_text
