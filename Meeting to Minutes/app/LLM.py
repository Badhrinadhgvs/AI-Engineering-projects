import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
from logs.logger import logging
from IPython.display import display, Markdown

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logging.error(f"API KEY IS INVALID (OR) NOT PROVIDED")
else:
    logging.info(f"API KEY IS PROVIDED")


openai = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key=api_key
)


class MeetLLM:
    def __init__(self, audio_file: object | None):
        self.speech = "gemini-3.5-flash"
        self.audio = audio_file
        self.base64 = None
        self.content = ""
        self.summ = "gemini-3.5-flash"

    def getInfo(self):
        try:
            with open(self.audio, "rb") as fp:
                abytes = fp.read()
                audio_base64 = base64.b64encode(abytes).decode("utf-8")
                self.base64 = audio_base64
                logging.info("Audio is Found and saved inside the code.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            self.base64 = None

    def getTranscribe(self):
        try:
            result = openai.chat.completions.create(
                model=self.speech,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please provide a word-for-word transcription of this audio.",
                            },
                            {
                                "type": "input_audio",
                                "input_audio": {"data": self.base64, "format": "mp3"},
                            },
                        ],
                    }
                ],
            )
            self.content = result.choices[0].message.content
            logging.info(
                f"Sucessfully Extracted Transcribe from audio {self.content[:5]}..."
            )
        except Exception as e:
            logging.error(f"Unexpected error while getting transcribe : {e}")
            self.content = "No Transcribe"

    def summarize(self):
        try:
            logging.info("Final Task Summarization Started")
            self.getInfo()
            self.getTranscribe()
            sys_prompt = """
    You are an Expert Summarizer, You will be Provide by the Transcript of an Meeting, Analyze it
    and make sure you summarize it appropriately, You should add
    1, What are the Main Points Discussed and some basic things about the meeting
    2, Important points to be noted
    3, Important Details if any
    4, Overall what happened in a clear way.
    Respond in Markdown Only
    """
            Pr = f"""
    Here is the Transcribe of the Entire meeting, Summarize this:
    {self.content}
    """

            res = openai.chat.completions.create(
                model=self.summ,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": Pr},
                ],
            )

            display(Markdown(res.choices[0].message.content))
            logging.info("Successfully Completed Task and rendered")
            return res.choices[0].message.content
        except Exception as e:
            logging.error(f"Error Ocuured during summarizing: {e}")
            return "Sorry!! Cannot perform tasks"
