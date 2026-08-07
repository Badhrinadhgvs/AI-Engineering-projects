import os
from openai import OpenAI
from .scraper import fetch_website_contents, fetch_website_links

class LLM:
    def __init__(self):
        self.openai = OpenAI(base_url="http://localhost:11434/v1", api_key='ollama')

    def get_relevent_links(self, name, url, model):
        links = fetch_website_links(url)
        links_sys_pro = """You are given with the set of links. Analyze all the links which you got and select the best links which can be placed in a Brochure. The Brochure is for Marketing and Business purposes. Make sure you are picking best links. The output should in JSON like:
           {
             'links':[
               {'link-type':'about-page','link':'https://example.com/about'},
               {'link-type':'home-page','link':'https://home.example.com'}
             ]
           }
        """
        links_user_pro = f"""
        You are given with the links of the Website/Company {name}, Pick the Best links for Creating Brochure, The Links are {links}
        """
        res = self.openai.chat.completions.create(
            model=model,
            messages=[
                {'role': 'system', 'content': links_sys_pro},
                {'role': 'user', 'content': links_user_pro}
            ],
            response_format={'type': 'json_object'}
        )
        return res.choices[0].message.content

    def get_system_prompt(self):
        return """You are a Professional Brochure maker... (unchanged)"""

    def get_user_prompt(self, name, url, model):
        return f"""You are given with the Contents, links of the Website: {name}

The Contents of the Website are: {fetch_website_contents(url)}

The Relevant Links (In JSON format):
{self.get_relevent_links(name, url, model)}

Now, go through the contents of the website and links, understand the Business, and make a comprehensive detailed Brochure for this.
"""

    def create_brochure(self, name, url, model):
        message = [
            {'role': 'system', 'content': self.get_system_prompt()},
            {'role': 'user', 'content': self.get_user_prompt(name, url, model)}
        ]
        response = self.openai.chat.completions.create(
            model=model,
            messages=message,
            stream=True
        )
        res = ""
        for chunk in response:
            res += chunk.choices[0].delta.content or ''
            yield res   # streamed straight to Gradio, no IPython needed