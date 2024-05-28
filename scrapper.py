'''
Scrape improvencyclopedia.org/games for improv games

This file scrapes the list of improv games and their descriptions from 
https://improvencyclopedia.org/games/index.html and writes them to disk as a
CSV file. The CSV file is single column and only contains the name and
description in a single line per row.
'''


from bs4 import BeautifulSoup
from urllib.request import urlopen
import os
import html2text as h2t


csv_filename = "improvencyclopedia.csv"
err_filename = "scrap_errors.txt"
curr_dir = os.path.dirname(os.path.abspath(__file__))
output_file = open(os.path.dirname(os.path.abspath(__file__)) + "/" + csv_filename, "w+")
print(f"Saving output to {output_file.name}")

# Write column heading to CSV file
output_file.write("text\n")

error_file = open(os.path.dirname(os.path.abspath(__file__)) + "/" + err_filename, "w+")




# Scrap Improv Encyclopedia

url = "https://improvencyclopedia.org/games/index.html"
print(f"Scrapping {url}")

page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")

def get_details(tag):
    return tag.name=="div" and tag.has_attr('class') and tag["class"] == ["details"]

details = soup.find(get_details)

bad_urls = []
count = 0

# Write rest of data
for list in details.find_all("ul"):
    for game in list.find_all('a'):
        name = game.string
        # url is the URL of the improv game page
        url = game["href"]
        print(f"Opening: {url}")
        count += 1
        try:
            desc_html = urlopen(url).read().decode("utf-8")
            desc_page = BeautifulSoup(desc_html, "html.parser")
            desc_det = desc_page.find(get_details)
            desc = str(desc_det.text).strip().replace("\"", "")
            # Consolidate into single line, adding context, and write to CSV file
            # Quote marks are needed so CSV can handle multiline strings
            context = f"This improv game is called {name} and its description is as follows: {desc}"
            output_file.write("\""+context+"\"\n")
        except:
            print(" Error has occurred!")
            bad_urls.append(url)
print()
print(f"Scrapped {count} improv games, {count-len(bad_urls)} successful, {len(bad_urls)} failed.")
print()



# Scrap https://improwiki.com/

bad_urls = []
count = 0

def scrap_ImprovWiki(url):
    global count
    global bad_urls
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    cards = soup.find_all("div", {"class": "card mb-2"})
    for card in cards:
        if card.find("div", {"class": "card-title h3"}) != None:
            continue
        name = card.a.string
        url = "https://improwiki.com" + card.a["href"]
        print(f"Opening: {url}")
        count += 1
        try:
            desc_html = urlopen(url).read().decode("utf-8")
            desc_page = BeautifulSoup(desc_html, "html.parser")
            desc_div = desc_page.find("div", {"class": "col-lg-9 order-last order-lg-first"})
            desc = h2t.html2text(desc_div.prettify())
            desc = desc.strip().replace("\"", "")
            # Consolidate into single line, adding context, and write to CSV file
            # Quote marks are needed so CSV can handle multiline strings
            context = f"This improv game is called {name} and its description is as follows: {desc}"
            output_file.write("\""+context+"\"\n")
        except:
            print(" Error has occurred!")
            bad_urls.append(url)

    print()
    print(f"Scrapped {count} improv games, {count-len(bad_urls)} successful, {len(bad_urls)} failed.")
    print()

url = "https://improwiki.com/en/warm-ups"
print(f"Scrapping {url}")
scrap_ImprovWiki(url)

url = "https://improwiki.com/en/improv-games"
print(f"Scrapping {url}")
scrap_ImprovWiki(url)

if len(bad_urls) > 0:
    print(f"Failed to open {len(bad_urls)} pages, saving bad pages to {error_file.name}")
    for b in bad_urls:
        error_file.write(b+"\n")

# Where is my defer in Python?? :(
output_file.close()
error_file.close()
