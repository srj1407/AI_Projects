import gradio as gr
import json
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from openai import OpenAI
from transcripts import get_transcripts
from scraper import fetch_website_contents
import os
from pprint import pprint
load_dotenv()

GLOBAL_MESSAGES = []

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


tools = [{
    "type": "function",                                     
    "function": {
        "name": "get_transcripts",                           
        "description": "Get the transcripts of a youtube video.", 
        "parameters": {                           
            "type": "object",
            "properties": {"url": {"type": "string", "description": "Youtube video url"}},
            "required": ["url"],
        },
    },
},
{
    "type": "function",                          
    "function": {
        "name": "fetch_website_contents",                          
        "description": "Get the contents of a website after scraping.",
        "parameters": {                                    
            "type": "object",
            "properties": {"url": {"type": "string", "description": "Website url"}},
            "required": ["url"],
        },
    },
}]

tool_registry = {
    "get_transcripts": get_transcripts,
    "fetch_website_contents": fetch_website_contents
}

def ask(question):
    system_prompt = f"""You are a helpful assistant. You are given website url or YouTube video url.
You help in summarizing the contents of the video or website by calling appropriate tool calls.
Also I am providing you with the previous conversation history whatever is available:

Conversation History:

{GLOBAL_MESSAGES if GLOBAL_MESSAGES else "Not Available"}


"""
    messages = [
        {"role":"system", "content": system_prompt},
        {"role":"user",   "content": question},
    ]
    response = client.chat.completions.create(
        model="gemini-3.5-flash",
        messages=messages,
        tools = tools
    )
    msg = response.choices[0].message
    GLOBAL_MESSAGES.append({"role": "user", "content": question})
    GLOBAL_MESSAGES.append({"role": "assistant", "content": msg.content})
    messages.append(msg)
    while msg.tool_calls:
        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            func_to_call = tool_registry.get(name)
            if func_to_call is None:
                continue
            result = func_to_call(**args)
            messages.append({"role": "tool", "name": name, "tool_call_id": call.id, "content": result})
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=messages
        )
        msg = response.choices[0].message
        GLOBAL_MESSAGES.append({"role": "assistant", "content": msg.content})
        messages.append(msg)
    return msg.content


demo = gr.Interface(
    fn=ask,
    inputs=gr.Textbox(placeholder="Ask"),
    outputs=gr.Textbox(label="Response"),
    title="Smart Assistant",
)

demo.launch()