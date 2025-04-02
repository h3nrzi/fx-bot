import requests

BOT_TOKEN = "token"
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"


res = requests.get(url=url).json()
print(res)
