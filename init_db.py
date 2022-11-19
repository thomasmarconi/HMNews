"""this script is run every hour to fetch updated articles"""
from collections import Counter
from string import punctuation
from urllib.request import urlopen
import json
import http.client
import sqlite3
import spacy
import en_core_web_sm
from bs4 import BeautifulSoup

nlp = spacy.load('en_core_web_sm')

def find_keywords(text):
    """scrapes articles to find keywords"""
    print("in find_keywords")
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN'] # 1
    doc = nlp(text.lower()) # 2
    print("here")
    for token in doc:
        if(token.text in nlp.Defaults.stop_words or token.text in punctuation):
            continue
        if token.pos_ in pos_tag:
            print("appending")
            result.append(token.text)
    print("here3")
    result = [(x[0]) for x in Counter(result).most_common(5)]
    result = " ".join(result)
    return result

def get_text_from_html(url):
    """used to get text from html page, helps to scrape fot keywords"""
    #https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python -- MattDMo
    print("in get_text")
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

CONNECTION = sqlite3.connect('database.db')


with open('schema.sql') as f:
    CONNECTION.executescript(f.read())

CONN = http.client.HTTPSConnection("hacker-news.firebaseio.com")
PAYLOAD = "[]"
CONN.request("GET", "/v0/topstories.json?print=pretty", PAYLOAD)
RES = CONN.getresponse()
DATA = RES.read().decode("utf-8")
DATA = DATA[2 : len(DATA) - 2]
DATA = DATA.split(", ")
DATA = [int(x) for x in DATA]
CONN.close()
DATA2 = []
for x in range(10):
    CONN.request("GET", "/v0/item/{}.json?print=pretty".format(DATA[x]), PAYLOAD)
    RES2 = CONN.getresponse()
    RES2 = RES2.read().decode("utf-8")
    DATA2.append(json.loads(RES2))
    CONN.close()
for x in DATA2:
    if("url" in x and "title" in x and "id" in x and "by" in x):
        keywords = find_keywords(get_text_from_html(x["url"]))
        print(keywords)
        CONNECTION.execute('INSERT INTO articles (id, url, title, author, keywords) VALUES (?, ?, ?, ?, ?)', (x["id"], x["url"], x["title"], x["by"], keywords))

CONNECTION.commit()
CONNECTION.close()
