import os
from openai import OpenAI
from dotenv import load_dotenv
from IPython.display import Markdown, display

load_dotenv(override=True)


class CodeGen:
    def __init__(self, code: str, lang: str):
        self.code = code
        self.lang = lang
        self.reasoning = ""
        self.final = ""

    def understand(self):
        sys_pr = f"""
        You are an expert software engineer specializing in Python
and {self.lang} code translation, you will be provided with a piece of code in python.
    Understand the code line by line and what i want as an output from you is How this particular code can be converted to the {self.lang},
    Strictly donot generate the code, Provide a list of points and suggestions which are provided to another one helping it to convert this code effectively and efficiently.
    """
        user_pr = f"""
    Here is the python code you have to understand:
    ```Python
    {self.code}
    ```
    """
        thinker = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        res = thinker.chat.completions.create(
            messages=[
                {"role": "system", "content": sys_pr},
                {"role": "user", "content": user_pr},
            ],
            model="gpt-oss:20b-cloud",
        )

        self.reasoning = res.choices[0].message.content

    def generate(self):
        sys_pr = f"""
      You are an Helpful Coding expert, whoes job is to convert the given python code to {self.lang} here the main objective is to make the code in {self.lang} such that the overall execution time will be reduced and the code will run and perform efficiently. You will be provided with the code and a set of points which you can consider them while writing the code, Make sure you write the code properly and ***Strictly Only Generate the code*** in {self.lang}. No Extra text,backticks,commas etc. Again I only need code no explanation etc it is mandatory to follow
      """
        user_pr = f"""
      Here is the Python code which you have to convert it into {self.lang}.
      ```Python
      {self.code}
      ```
      Here are few points which you may consider while writing the code in {self.lang}
      {self.reasoning}
      Again **Strictly Only Generate the code***
      """

        """ coder = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=os.environ.get("GEMINI_KEY"),
        )"""

        coder = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        res = coder.chat.completions.create(
            messages=[
                {"role": "system", "content": sys_pr},
                {"role": "user", "content": user_pr},
            ],
            model="gemma4:cloud",
        )
        self.final = res.choices[0].message.content

    def evaluate(self):
        sys_pr = f"""
      You are an Expert code evaluator, think just like an working compiler(Persona), You will be given a piece of code and you have to check whether the code works well or if any issues are present, **Strictly** you have to reply in either Good/Not Good.
      If there is any syntax error, any issues in the code return as Not Good.
      If it is good and ok for compiling simply return Good.
      """
        user_pr = f"Here is the generated code in the {self.lang} Programming language:\n {self.final}"
        evaluator = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        res = evaluator.chat.completions.create(
            messages=[
                {"role": "system", "content": sys_pr},
                {"role": "user", "content": user_pr},
            ],
            model="gpt-oss:20b-cloud",
        )
        lst = str(res.choices[0].message.content)
        print(lst)
        return lst.strip().lower() == "good"

    def main(self):
        self.understand()
        MAX_RETRIES = 5
        self.understand()
        for attempt in range(MAX_RETRIES):
            self.generate()
            if self.evaluate():
                break
            else:
                print("Generation failed after maximum attempts.")
        self.final = self.final.replace(f"```", "")
        return self.final
