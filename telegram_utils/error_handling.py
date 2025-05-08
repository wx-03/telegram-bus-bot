from telegram_utils.messaging import send_message

def send_error_message(chat_id, error):
    send_message(chat_id, error)
