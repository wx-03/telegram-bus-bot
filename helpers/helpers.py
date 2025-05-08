from datetime import datetime

def format_timing(str):
    if str == '':
        return ''
    dt = datetime.fromisoformat(str)
    formatted = dt.strftime('%I:%M %p')
    return formatted