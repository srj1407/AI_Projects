from openai import OpenAI
from dotenv import load_dotenv
from transcripts import get_transcripts
import os

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

system_prompt = """You are given the transcripts of a You Tube video
You have to summarize that video and give key takeaways."""

def summarize(url):
    transcripts = get_transcripts(url)
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role":"system", "content": system_prompt},
            {"role":"user",   "content": f"Summarize this video:\n\n{transcripts}"},
        ],
    )
    return response.choices[0].message.content