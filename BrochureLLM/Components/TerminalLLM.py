import os
from openai import OpenAI
from .scraper import fetch_website_contents,fetch_website_links
from IPython.display import display,Markdown,update_display

class LLM:
  def __init__(self):
    self.openai = OpenAI(base_url="http://localhost:11434/v1",api_key='ollama')
    self.markdown=None
    
  def __call__(self,name,url,model):
    self.name = name
    self.url = url
    self.model = model
    yield from self.create_brochure()
    
  def get_relevent_links(self):
    links = fetch_website_links(self.url)
    links_sys_pro = """You are given with the set of links. Analyze all the links which you got and select the best links which can be placed in a Brochure. The Brochure is for Marketing and Business purposes. Make sure you are picking best links. The output should in JSON like:
           {
             'links':[
               {'link-type':'about-page','link':'https://example.com/about'},
               {'link-type':'home-page','link':'https://home.example.com'},
               
             ]
           }
    """
    links_user_pro = f"""
    You are given with the links of the Website/Company {self.name}, Pic the Best links for Creating Brochure, The Links are{links}
    """
    res = self.openai.chat.completions.create(
      model = self.model,
      messages=[{'role':'system','content':links_sys_pro},
                {'role':'user','content':links_user_pro}
                ],
      response_format={'type':'json_object'}
    )
    return res.choices[0].message.content
    
    
  def get_system_prompt(self):
    pro = f"""You are an Professional Brochure maker, The Brochures you are going to make are used by top companies for their Marketing and Business Purposes. You will be provided the relevant links of the Business and the web contents os the Business. The Web Contents are scraped from the original website. The links will be provided in JSON format. Provide the Brochure in Markdown only. Points to remember while making brochures:
    Key Design and Content PointsKnow your audience: Tailor your tone, images, and language to fit the people you want to reach.Write short text: Use bullet points and brief sentences instead of long paragraphs.Make a great cover: Use a clear headline and a strong image to grab attention right away.Use consistent branding: Stick to your company logo colors and limit yourself to two or three fonts.Add a call to action: Tell the reader what to do next, like visit a website or call a number.
    """
    return pro
  
  def get_user_prompt(self):
    user = f"""You are given with the Contents,links of the Website:{self.name}\n\n
    The Contents of the Website are: {fetch_website_contents(self.url)}
    \n\n
    The Relevant Links(In JSON format):
    {self.get_relevent_links()}\n\n
    Now, Go through the contents of the website, links understand about the Business and Make a Comprehensive detailed Brochure for this.
    """
    return user
    
  def create_brochure(self):
    message = [
      {'role':'system','content':self.get_system_prompt()},
      {'role':'user','content':self.get_user_prompt()}
    ]
    response = self.openai.chat.completions.create(
      model=self.model,
      messages=message,
      stream=True
    )
    res = ""
    for chunk in response:
      res+=chunk.choices[0].delta.content or ''
      yield res
      
    self.markdown = res
    
  def print_brochure(self):
    return display(Markdown(self.markdown))
    
    
    

    
  



