import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("WAHA_API_KEY")
base_url = "http://localhost:3000"

class WhatsappClient:
  def __init__(self):
    self.headers = {
      "Content-Type": "application/json",
      "X-Api-Key": api_key,
    }
    
  def sendMessage(self, phoneNumber, text):
    requests.post(
      f"{base_url}/api/sendText",
      headers=self.headers,
      json={
        "session": "default",
        "chatId": phoneNumber,
        "text": text,
      }
    )
  
  def downloadMedia(self, mediaUrl: str) -> bytes:
    response = requests.get(mediaUrl, headers=self.headers)
    response.raise_for_status()
    return response.content