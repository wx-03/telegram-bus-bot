from flask import Flask, request
from telegram_utils.messaging import send_message
from telegram_utils.message_handling import handle_message

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
	data = request.get_json()
	try:
		handle_message(data)
	except Exception as e:
		send_message(data['message']['chat']['id'], str(e))
	return "OK", 200

if __name__ == "__main__":
	app.run(debug=True)
