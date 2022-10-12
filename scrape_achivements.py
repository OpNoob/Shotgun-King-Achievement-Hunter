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
    for row in soup.find_all("div", class_="achieveRow"):
        image_elem = row.find_next("img")
        image_url = image_elem['src']

        achieve_txt = row.find_next("div", class_="achieveTxt")
        text_elem = achieve_txt.find_next("h3")
        achievement_name = text_elem.text

        img_data = requests.get(image_url).content
        with open(os.path.join(directory, achievement_name + ".png"), 'wb') as handler:
            handler.write(img_data)


getImages("Game Data/Achievements", "https://steamcommunity.com/stats/1972440/achievements")
