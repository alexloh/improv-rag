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


csv_filename = "improvencyclopedia.csv"
err_filename = "scrap_errors.txt"

url = "https://improvencyclopedia.org/games/index.html"
page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")

def get_details(tag):
    return tag.name=="div" and tag.has_attr('class') and tag["class"] == ["details"]

details = soup.find(get_details)

curr_dir = os.path.dirname(os.path.abspath(__file__))
output_file = open(os.path.dirname(os.path.abspath(__file__)) + "/" + csv_filename, "w+")
print(f"Saving output to {output_file.name}")

bad_urls = []
count = 0
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
output_file.close()

print()
print(f"Scrapped {count} improv games, {count-len(bad_urls)} successful, {len(bad_urls)} failed.")

if len(bad_urls) > 0:
    error_file = open(os.path.dirname(os.path.abspath(__file__)) + "/" + err_filename, "w+")
    print(f"Failed to open {len(bad_urls)} pages, saving bad pages to {error_file.name}")
    for b in bad_urls:
        error_file.write(b+"\n")
    error_file.close()

