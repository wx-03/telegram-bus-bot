from .messaging import send_message

def handle_message(data):
	chatid = data['message']['chat']['id']
	if not 'text' in data['message']:
		raise Exception('Sorry, I can only understand text :(')
	send_message(chatid, data['message']['text'])