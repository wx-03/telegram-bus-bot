import logging

from dotenv import load_dotenv
from flask import Flask, request

import set_webhook
from telegram_utils.message_handling import handle_message

logger = logging.getLogger(__name__)

app = Flask(__name__)

set_webhook.main()


@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    handle_message(data)
    return "OK", 200


if __name__ == "__main__":
    logging.basicConfig(filename="bot.log", filemode="w", level=logging.DEBUG)
    app.run(debug=True)
