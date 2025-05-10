def result_message(message, status_code, result):
    result = {
        "Message": message,
        "Status_code": status_code,
        "Result": result,
    }
    return result
