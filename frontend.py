from ast import literal_eval
from flask import Flask, request, render_template_string
import pandas as pd
from openai import OpenAI
import os
import numpy as np
from dotenv import load_dotenv

app = Flask(__name__)
curr_dir = os.path.dirname(os.path.abspath(__file__))

client = None
def get_client():
    global client
    if client is None:
      load_dotenv()
      client = OpenAI()
    return client

embedding = None
def init_embedding():
    global embedding
    if embedding is None:
        embedding = pd.read_csv(curr_dir + "/" + "embeddings.csv", sep=',', converters=dict(embeddings=literal_eval))
    return embedding

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding

def ask_no_rag(question: str) -> str:
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "user", "content": question},
        ]
    )
    return response.choices[0].message.content

def ask_rag(question: str) -> (str, str):
    df = init_embedding()
    qn_embedding = get_embedding(question)

    def dot(embedding):
        return np.dot(embedding, qn_embedding)

    df['distance'] = df['embeddings'].apply(dot)
    df.sort_values('distance', ascending=False, inplace=True)

    context = ""
    for i in range(3):
        context += f"[{i+1}] ({df['distance'].iloc[i]:.4f})  " + df['text'].iloc[i] + "\n\n"

    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "user", "content": question},
            {"role": "assistant", "content": "Use the following context to help you: "+context}
        ]
    )
    return response.choices[0].message.content, context

@app.route('/rag', methods=['GET', 'POST'])
def classify_emotion():
    if request.method == 'POST':
        get_client()
        text = request.form['text']
        result = ask_no_rag(text)
        result_rag, rag_context = ask_rag(text)
        return render_template_string('''
            <h2>You asked:</h1>
            <pre style="white-space: pre-wrap;">{{ text }}</pre>
            <h2>Original ChatGPT response (no RAG):</h1>
            <pre style="white-space: pre-wrap;">{{ result }}</pre>
            <h2>RAG-augmented ChatGPT response:</h1>
            <pre style="white-space: pre-wrap;">{{ result_rag }}</pre>
            <h4>Context used for RAG:<h4>
            <p style="white-space: pre-line"><small>{{ rag_context }}</small></p>
            <a href="/rag">Go Back</a>
        ''', text=text, result=result, result_rag=result_rag, rag_context=rag_context)

    return render_template_string('''
        <style>
        button2 {
            background: none!important;
            border: none;
            padding: 0!important;
            /*optional*/
            font-family: arial, sans-serif;
            /*input has OS specific font-family*/
            color: #069;
            text-decoration: underline;
            cursor: pointer;
        }
        </style>

        <h1>Ask an Improv-related question!</h1>
        <p>ChatGPT3.5 is very bad at improv-related prompts, often producing confident-sounding but nonsensical responses.
           This website uses Retrieval Augmented Generation (RAG) and information sourced from <a href="https://improvencyclopedia.org/games/index.html">Improv Encyclopedia</a>
            to (significantly?) improve its result. And when it doesn't, that can make for a hilarious scene!
        </p>
        <p>Ask it any question and compare the response with and without RAG:</p>
        <ul>
            <form action="" method="post">
                <li><button type="submit" name="text" value="Can you tell me about the improv game Big Booty?" class="button2">
                    Can you tell me about the improv game Big Booty?
                </button></li>
                <li><button type="submit" name="text" value="Can you tell me about the improv game Hitch Hiker?" class="button2">
                    Can you tell me about the improv game Hitch Hiker?
                </button></li>
                <li><button type="submit" name="text" value="Can you tell me about improv long form La Ronde?" class="button2">
                    Can you tell me about the improv long form La Ronde?
                </button></li>
                <li><button type="submit" name="text" value="Which improv long forms were invented in Chicago?" class="button2">
                    Which improv long forms were invented in Chicago?
                </button></li>
                <li><button type="submit" name="text" value="Which improv games can I play with 3 players?" class="button2">
                    Which improv games can I play with 3 players?
                </button></li>
            </form>
        </ul>
        <form method="post">
            <textarea name="text" rows="4" cols="50">Can you tell me about the improv game Big Booty?</textarea><br><br>
            <input type="submit" value="Ask">
        </form>
        <p><small>By Alex Loh. Full source available on my <a href='https://github.com/alexloh/improv-rag/tree/main'>Github</a></small></p>
    ''')

if __name__ == "__main__": 
  app.run()