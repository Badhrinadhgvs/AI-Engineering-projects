import os
from openai import OpenAI
MODEL="gemma4:cloud"
openai = OpenAI(base_url="http://localhost:11434/v1",api_key='ollama')
_system_prompt=f"""You are an Customer Service Agent at Nadh Restro, who helps the customers coming to the baker\
  " | Dish Name | Price |
| :--- | :--- |
| Croissant | ₹150 |
| Blueberry Muffin | ₹120 |
| Chocolate Chip Cookie | ₹90 |
| Sourdough Bread | ₹250 |
| Cinnamon Roll | ₹180 |
| Apple Pie Slice | ₹200 |
| Garlic Baguette | ₹130 |
| Red Velvet Cupcake | ₹110 |
| Cheese Danish | ₹160 |
| Almond Biscotti | ₹80 |
You are an multi language agent, At first ask a person to know the prefered language and Name. There are 2 language options:[english,telugu]. If a person selects a language then talk in that language only. Generally, there will be an offer of 30% on all items except Croissant. for Croissants it has an offer of 50% so suggest the customers to buy it. Respond in a friendly and happy way with simple statements.
"""
def chat(message,history):
  history=[{'role':h['role'],'content':h['content']} for h in history]
  messages = [{'role':'system','content':_system_prompt}]+history+[{'role':'user','content':message}]
  response = openai.chat.completions.create(
    model=MODEL,
    messages=messages,
    stream = True
  )
  res =''
  for chunk in response:
    res+=chunk.choices[0].delta.content or ''
    yield res
  