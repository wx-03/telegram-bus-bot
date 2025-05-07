from flask import Flask, request
import json
from bot_utils import send_message

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
	data = request.get_json()
	print(json.dumps(data, indent=4))
	chatid = data['message']['chat']['id']
	if not 'text' in data['message']:
		send_message(chatid, "I only can understand text :(")
		return "OK", 200
	send_message(chatid, data['message']['text'])
	return "OK", 200

if __name__ == "__main__":
	app.run(debug=True)
