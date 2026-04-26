import os
import tempfile
import fitz
from whatsapp import WhatsappClient

class PdfHandler:
  def __init__(self, whatsappClient: WhatsappClient):
    self.client = whatsappClient
  
  def fetch(self, media_url):
    pdfBytes = self.client.downloadMedia(media_url) # recebe os bytes brutos da URL
    return self.extractText(pdfBytes)
  
  def extractText(self, pdf_bytes):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp: 
      tmp.write(pdf_bytes) #O Pdf é salvo como arquivo temporario, acho melhor que criar o arquivo fisico que nem no ultimo processo
      tmp_path = tmp.name
      
    try:
      doc = fitz.open(tmp_path)
      pages = [doc[i].get_text() for i in range(doc.page_count)]
      return "\n\n".join(pages) # Retorna cada texto de cada pagina em str
    finally:
      doc.close()
      os.unlink(tmp_path) # Descobri que em python o mesmo vindo aparentemente depois do return, o finally ativa antes