# Improving improv related responses with RAG
#### Author: Alex Loh (alexloh360@gmail.com) Last updated: May 2024
---

ChatGPT3.5 is very bad at improv-related prompts, often producing confident-sounding but nonsensical responses. Here is an example of asking ChatGPT3.5 about the game "Big Booty":

![image](bigbooty.jpg)

Our goal is to improve these repsonses using RAG by ingesting information scrapped from the web. We follow closely the example from Don Woodlocks' [How to set up RAG - Retrieval Augmented Generation](https://www.youtube.com/watch?v=P8tOjiYEFqU).

The basic flow is to scrap descriptions for all improv game pages from authoritative web source and calculate their embedding. For each query, we find the most relevant page using a dot product of the query's embedding against the embeddings all pages. This one page is then passed as context to the OpenAI call.


## Scrapping sources for RAG
We scrap descriptions for improv games from [Improv Encyclopedia](https://improvencyclopedia.org/games/index.html) using [BeautifulSoup](https://pypi.org/project/beautifulsoup4/).  A total of 575 games were scrapped into the file improvencyclopedia.csv. Files that produced errors during scrapping are written to scrap_errors.txt. Source for the scrapper script is found in this repo under scrapper.py.

The format of the CSV file is one row per entry, and one column for each row containing the context, including surrounding words such as the name of the game and instructions for the LLM. Each row looks like this:

    "This improv game is called <NAME OF GAME> and its description is as follows: <DESC FROM WEB PAGE>"

The reason this is a CSV file is to make it easier to load into pandas which handles the embedding logic later.

## ChatGPT call

## Frontend
We will build a web interface using [Python Anywhere](https://www.pythonanywhere.com/) following the guide at https://blog.pythonanywhere.com/210/.
