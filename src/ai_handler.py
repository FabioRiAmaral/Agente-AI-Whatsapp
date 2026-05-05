import os, requests
from dotenv import load_dotenv
from session_manager import Session

load_dotenv()

api_key = os.getenv("HF_API_KEY", "")
url = "https://api-inference.huggingface.co/models/google/gemma-3-4b-it"

class AiHandler:
  def __init__(self):
    self.headers = { 
      "Authorization": f"Beared {api_key}", # Requisição padrao do hugging face para ver se tem permição
      "Content-Type": "application/json",
    }
  
  def getAnswer(self, session: Session, question):
    prompt = self.buildPrompt(session, question)
    answer = self.callApi(prompt)
    
    session.add_to_history("user", question) #Guarda pro modelo ter contexto das mensagens
    session.add_to_history("assistant", answer)
    return answer
  
  def buildPrompt(self, session: Session, question):
    messages = [
      {"role": "system", "content": self.systemPrompt(session.pdf_text)},
      *session.history,
      {"role": "user", "content": question}
    ]
    
    prompt = ""
    for msg in messages:
      role = msg["role"]
      content = msg["content"]
      prompt = f"<|im_start|>{role}\n{content}<|im_end|>\n"
    prompt += "<|im_start|>assistant\n"
    return prompt
  
  def systemPrompt(self, pdfText):
    return (
      "Você é um assistente que responde perguntas baseadas exclusivamente"
      "no documento que será providenciado abaixo.\n"
      "Regras a seguir:\n"
      "Use APENAS o conteúdo de dentro do documento\n"
      "Se a resposta não estiver no documento apenas diga: 'Essa imformação não está no documento.'\n"
      "Seja direto e objetivo nas respostas\n\n"
      "Abaixo o documento:\n"
      f"{pdfText}"
    )
    
  def callApi(self, prompt):
    response = requests.post(
      url,
      headers=self.headers,
      json={"input": prompt, "parameters": {
        "max_new_tokens": 512,
        "temperature": 0.2, 
        "top_p": 0.8, 
        "repetition_penalty": 1.1, 
        "return_full_text": False,
        } # type: ignore
      }
    )
    
    response.raise_for_status()
    data = response.json()
    
    if isinstance(data, list) and data:
      return data[0].get("generated_text", "Erro ao gerar resposta.")
    return "Erro ao gerar resposta."