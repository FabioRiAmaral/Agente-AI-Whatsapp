import os
import tempfile
import fitz
from whatsapp import WhatsappClient

class PdfHandler:
  def __init__(self, whatsappClient: WhatsappClient):
    self.client = whatsappClient
  
  def fetch(self, media_url):
    pdfBytes = self.client.downloadMedia(media_url)
    return self.extractText(pdfBytes)
  
  def extractText(self, pdf_bytes):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
      tmp.write(pdf_bytes)
      tmp_path = tmp.name
    try:
      doc = fitz.open(tmp_path)
      pages = [doc[i].get_text() for i in range(doc.page_count)]
      doc.close
      return "\n\n".join(pages)
    finally:
      os.unlink(tmp_path)