from flask import Flask, request

from telegram_utils.message_handling import handle_message
from telegram_utils.messaging import send_message

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
	data = request.get_json()
	handle_message(data)
	return "OK", 200

if __name__ == "__main__":
	app.run(debug=False)
