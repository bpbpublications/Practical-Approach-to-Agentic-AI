import gradio as gr
import ollama
from ollama import Client

def ner_extraction(text):
    
    client = Client(
    host='http://host.docker.internal:11434',
    headers={'x-some-header': 'some-value'}
    )
    response = client.chat(model='llama3.1', messages=[{"role": "user", "content": f"Extract named entities from: {text}"}])
    return response['message']['content'] 

# Define Gradio UI
interface = gr.Interface(
    fn=ner_extraction,
    inputs=gr.Textbox(lines=5, placeholder="Enter text here..."),
    outputs="text",
    title="Named Entity Recognition App",
    description="Enter text and see extracted named entities using Ollama."
)

# Launch the app
if __name__ == "__main__":
    interface.launch()
