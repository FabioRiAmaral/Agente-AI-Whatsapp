from whatsapp import WhatsappClient
from pdf_handler import PdfHandler
from ai_handler import AiHandler
from session_manager import SessionManager
from logger import logger
import json

bot_number = "5562996223115@c.us"

class Bot:
  def __init__(self):
    self.wa = WhatsappClient()
    self.pdf = PdfHandler(self.wa)
    self.ai = AiHandler()
    self.sessions = SessionManager()
  
  def handleStart(self, phone_number): #Vai receber o /start do chat e começar a conversa
    self.sessions.start(phone_number)
    logger.info(f"Sessão iniciada para {phone_number}")
    self.wa.sendMessage(phone_number, "Envie um PDF que irei responder sobre qualquer assunto que tem dentro dele")
  
  def handleText(self,phone_number, text):
    session = self.sessions.get(phone_number)
    if not session.has_pdf():
      logger.info(f"Pergunta feita sem PDF em {phone_number}")
      self.wa.sendMessage(phone_number, "Só consigo responder se eu receber um PDF")
      return
    
    logger.info(f"Pergunta de {phone_number}: {text}")
    answer = self.ai.getAnswer(session, text)
    logger.info(f"Resposta gerada para {phone_number}: {answer}")
    self.wa.sendMessage(phone_number, answer)
  
  def handleDocument(self, phone_number, media_url):
    session = self.sessions.get(phone_number)
    logger.info(f"PDF recebido em {phone_number}")
    pdf_text = self.pdf.fetch(media_url)
    session.set_pdf(pdf_text)
    logger.info(f"PDF indexado com sucesso para {phone_number}")
    self.wa.sendMessage(phone_number, "Recebi o PDF, faça sua pergunta e eu te responderei")
    
  def handleEvent(self, data): # Vai garantir que só funcione da maneira que eu quero
    event = data.get("event")
    if event != "message":
      return
    
    payload = data.get("payload", {})
    phone_number = payload.get("from", "")
    to_number = payload.get("to", "")
    message_type = payload.get("_data", {}).get("type", "")
    message_body = payload.get("body", "").strip()
    from_me = payload.get("fromMe", False)
    logger.info(f"Mensagem recebida | de: {phone_number} | type: {message_type} | body: {message_body}")
    
    if from_me and to_number != bot_number:
      logger.info("Ignorado -- fromMe para outro número")
      return
    
    if not phone_number.endswith(("@c.us", "@lid")):
      logger.info(f"Ignorado -- não é chat privado: {phone_number}")
      return  
    
    if message_type == "chat" and message_body.lower() == "/start":
      logger.info(f"/start detectado para {phone_number}")
      self.handleStart(phone_number)
    
    elif not self.sessions.is_active(phone_number):
      logger.info(f"Ignorado -- sessão não ativa para {phone_number}")  
    
    elif message_type == "chat":
      self.handleText(phone_number, payload.get("body"))  
      
    elif message_type == "document":
      media_url = (payload.get("media") or {}).get("url")
      if media_url:
        self.handleDocument(phone_number, media_url)
      else:
        logger.warning(f"PDF sem URL de mídia para {phone_number}")
        self.wa.sendMessage(phone_number, "Não consegui acessar o PDF, tente enviar novamente.")