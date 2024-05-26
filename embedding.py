from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
import os
import pandas as pd

csv_filename = "improvencyclopedia.csv"

load_dotenv()
client = OpenAI()

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding

curr_dir = os.path.dirname(os.path.abspath(__file__))

# This part is costly and happens only once in dev

# df = pd.read_csv(curr_dir + "/" + csv_filename)

# df['embeddings'] = df['text'].apply(get_embedding)
# df.to_csv(curr_dir + "/" + "embeddings.csv")
# df.to_pickle(curr_dir + "/" + "embeddings.pkl")

# This part happen in the frontend
question1 = "Can you tell me about the improv game Big Booty?"
question2 = "Which long forms were invented in Chicago?"
question3 = "Which improv games can I play with three players?"
question4 = "Tell me more about the improv game with three line scenes!"
question = question3
qn_embedding = get_embedding(question)

df2 = pd.read_pickle(curr_dir + "/" + "embeddings.pkl")

def dot(embedding):
    return np.dot(embedding, qn_embedding)

df2['distance'] = df2['embeddings'].apply(dot)
df2.sort_values('distance', ascending=False, inplace=True)

print(df2.head(20))
