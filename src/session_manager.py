from dataclasses import dataclass, field

@dataclass
class Session:
  active: bool = False # VAi ser pra verificar se o usurio deu /start, se não o bot não deve responder
  pdf_text: str = "" # Se tiver recebido algum pdf ele vai ser armazenado aqui
  history: list[dict] = [field(default_factory=list)]
  
  def reset(self): #Pra reiniciar ou iniciar uma sessão, vai servir pra não confundir a AI com o novo sistema de historico que coloquei
    self.active = True
    self.pdf_text = ""
    self.history = []

  def set_pdf(self, text): # O texto do pdf recebido vai ser armazenado aqui futuramente, e depois limpa o historico de perguntas
    self.pdf_text = text
    self.history = [] 
    
  def has_pdf(self): #Usar pro bot saber se já pode consultar o pdf
    return bool(self.pdf_text)
  
  def add_to_history(self, role, content): #Adicionei porque da ultima vez o modelo só respondia de forma engessada, vai ser pra armazernar as mensagens
    self.history.append({"role": role, "content": content})