from ..logger import log_single_message

def greet():
    """
    Output: Tuple(hello message, info code)
    """
    print(f"Controller: Greeting user with a message")
    log_single_message("INFO", "Greeting endpoint was called.")

    message_dict = {
        "message": "Welcome to the SUSTech Merch Store!"
    }
    return message_dict, 200
    