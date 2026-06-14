# pip install gradio
import gradio as gr
from summarizer import summarize

gr.Interface(
    fn=summarize,                                  # your function
    inputs=gr.Textbox(label="YT Video URL"),
    outputs=gr.Markdown(label="Summary"),
    title="🔎 YT Video Summarizer",
).launch(share=True)   # share=True → a public link you can post! 🎉