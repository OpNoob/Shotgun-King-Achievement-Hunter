import os
import requests
from bs4 import BeautifulSoup
import urllib.request
import re
from PIL import Image


def getImages(directory, url):
    os.makedirs(directory, exist_ok=True)

    Web = requests.get(url)
    soup = BeautifulSoup(Web.text, features="html.parser")
    for link in soup.findAll('a'):
        link_href = link['href']
        if "nocookie" in link_href and "Card_choices" not in link_href:
            print("LINK:", link_href)
            name_find = re.search('''images\/.*\/.*\/.*.png''', link_href).group(0)
            name = name_find.split("/")[-1]
            # name = name.replace("_", " ")  # .replace("%", "'")

            img_data = requests.get(link_href).content
            with open(os.path.join(directory, name), 'wb') as handler:
                handler.write(img_data)
            print()


getImages("Game Data/Negative", "https://shotgun-king.fandom.com/wiki/White_Cards")
getImages("Game Data/Positive", "https://shotgun-king.fandom.com/wiki/Black_Cards")
