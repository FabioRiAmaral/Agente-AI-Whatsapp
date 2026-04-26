from flask import Flask, request
from bot import Bot

app = Flask(__name__)
bot = Bot()

@app.route("/webhook", methods=["POST"]) 
def webhook():
  bot.handleEvent(request.json)
  return "Tudo certo"

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=False) # http://host.docker.internal:5000/webhook