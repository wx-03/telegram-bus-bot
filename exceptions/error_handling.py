import logging

from telegram_utils.messaging import send_message

logger = logging.getLogger(__name__)


def handle_error(error, chat_id=None):
    if chat_id:
        send_message(chat_id, str(error))
    logging.error(str(error), exc_info=True)
