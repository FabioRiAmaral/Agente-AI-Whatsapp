from whatsapp import WhatsappClient
from pdf_handler import PdfHandler
from ai_handler import AiHandler
from session_manager import SessionManager

class Bot:
  def __init__(self):
    self.wa = WhatsappClient()
    self.pdf = PdfHandler(self.wa)
    self.ai = AiHandler()
    self.sessions = SessionManager()
  
  def handleStart(self, phoneNumber): #Vai receber o /start do chat e começar a conversa
    self.sessions.start(phoneNumber)
    self.wa.sendMessage(phoneNumber, "Olá, envie um PDF que irei responder sobre qualquer assunto que tem dentro dele")
  
  def handleText(self,phoneNumber, text):
    session = self.sessions.get(phoneNumber)
    if not session.has_pdf():
      self.wa.sendMessage(phoneNumber, "Só consigo responder se eu receber um PDF")
      return
    answer = self.ai.getAnswer(session, text)
    self.wa.sendMessage(phoneNumber, answer)
  
  def handleDocument(self, phoneNumber, media_url):
    session = self.sessions.get(phoneNumber)
    pdf_text = self.pdf.fetch(media_url)
    session.set_pdf(pdf_text)
    self.wa.sendMessage(phoneNumber, "Recebi o PDF, faça sua pergunta e eu te responderei")
    
  def handleEvent(self, data): # Vai garantir que só funcione da maneira que eu quero
    if data.get("event") != "message":
      return
    payload = data.get("payload", {})
    phone_number = payload.get("from", "")
    message_type = payload.get("type", "")
    message_body = payload.get("body", "").strip()
    if payload.get("fromMe"):
      return
    if not phone_number.endswith("@c.us"):
      return
    if message_type == "text" and message_body.lower() == "/start":
      self.handleStart(phone_number)
      return
    if not self.sessions.is_active(phone_number):
      return
    elif message_type == "document":
      self.handleDocument(phone_number, payload.get("body"))