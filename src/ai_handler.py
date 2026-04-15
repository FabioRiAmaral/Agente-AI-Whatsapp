import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from session_manager import Session

model_id = "google/gemma-4-E2B-it"

class AiHandler:
  def __init__(self):
    self.tokenizer = AutoTokenizer.from_pretrained(model_id)
    self.model = AutoModelForCausalLM.from_pretrained(
      model_id,
      dtype=torch.bfloat16,
      device_map="auto",
    )
  
  def getAnswer(self, session: Session, question):
    messages = self.buildMessages(session, question)
    prompt = self.apllyTemplate(messages)
    answer = self.generate(prompt)
    session.add_to_history("user", question) #Guarda pro modelo ter contexto das mensagens
    session.add_to_history("assistant", answer)
    return answer
  
  def buildMessages(self, session: Session, question):
    return [
      {"role": "system", "content": self.systemPrompt(session.pdf_text)},
      *session.history,
      {"role": "user", "content": question}
    ]
  
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
    
  def apllyTemplate(self, messages: list[dict]):
    return self.tokenizer.apply_chat_template(
      messages,
      tokenize=False,
      add_generation_prompt=True,
    )
  
  def generate(self, prompt):
    inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
    with torch.inferenceMode():
      outputs = self.model.generate(
        **inputs,
        max_new_tokens=512,
        temperature=0.2, #O tanto que a AI foge do pdf, quando mais proximo de zero mais duro no pdf ele responde, trocar se necessario
        do_sample=True,
        top_p=0.8,
        repetition_penalty=1.1,
      )
    answerIds = outputs[0][inputs["input_ids"].shape[-1]:]#Esses dois é um tratamento necessario para os resultados que o Gemma entrega
    return self.tokenizer.decode(answerIds, skip_special_tokens=True)