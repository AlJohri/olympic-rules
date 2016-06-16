#!/usr/bin/env python3

import os, json, requests, lxml.html, lxml.etree
from bs4 import BeautifulSoup
import pypandoc

os.makedirs("rules", exist_ok=True)

def load_disciplines():
    with open("disciplines.json") as f: return json.load(f)

def get_nbc_disciplines():
    disciplines = load_disciplines()
    discipline_names = [x['name'] for x in disciplines]

    nbc_discplines_map = {
        "Trampoline Gymnastics": "Trampoline",
        "Artistic Gymnastics": "Gymnastics",
        "Synchronised Swimming": "Synchronized Swimming",
        "Football": "Soccer",
        "Athletics": "Track and Field",
        "Hockey": "Field Hockey",

        # group cycling
        "Cycling Track": "Cycling",
        "Cycling Mountain Bike": "Cycling",
        "Cycling Road": "Cycling",
        "Cycling BMX": "Cycling",

        # group swimming
        "Swimming": "Swimming",
        "Marathon Swimming": "Swimming",

        # group canoe
        "Canoe Slalom": "Canoe Kayak",
        "Canoe Sprint": "Canoe Kayak",
    }

    nbc_discpline_names = list(set([nbc_discplines_map.get(x) or x for x in discipline_names]))

    # print("Number of Original Disciplines:", len(disciplines)) # 39
    # print("Number of NBC Grouped Disciplines/Sports", len(nbc_discpline_names)) # 34

    return nbc_discpline_names

for discipline_name in get_nbc_disciplines():

    discipline_slug = discipline_name.lower().replace(" ", "-")
    print(discipline_slug)

    os.makedirs("rules/%s" % discipline_slug, exist_ok=True)

    # hack entrypoint for weightlifting
    endpoint = "basics"
    if discipline_slug == "weightlifting": endpoint = "history"

    entrypoint_url = "http://www.nbcolympics.com/news/" + discipline_slug + "-101-" + endpoint
    r = requests.get(entrypoint_url)
    doc = lxml.html.fromstring(r.content)
    urls = []

    for atag in doc.cssselect("div.inline-card--content.fun-fact-type-general p a"):
        url = "http://www.nbcolympics.com" + atag.get('href')
        if discipline_slug in url:

            # hack for wrong urls
            if url == "http://www.nbcolympics.com/news/handball-101-venue":
                url = "http://www.nbcolympics.com/news/handball-101-venues"
            elif url == "http://www.nbcolympics.com/news/badminton-101--history":
                url = "http://www.nbcolympics.com/news/badminton-101-history"

            urls.append(url)

    for url in urls:
        print(url)
        filename = url.replace(("http://www.nbcolympics.com/news/" + discipline_slug + "-101-"), "")
        filepath = "rules/%s/%s.md" % (discipline_slug, filename)
        r = requests.get(url)

        soup = BeautifulSoup(r.content, "lxml")

        try:
            for x in soup.select("div.inline-card.inline-card--type-image"): x.extract()
            for x in soup.select("div.inline-card.inline-card--type-fun-fact"): x.extract()
            for x in soup.select("div.social-links.article--social-links"): x.extract()
            for x in soup.select("div.media-box.media-box--type-image"): x.extract()
            for x in soup.select("div.tags.article--tags"): x.extract()
            for x in soup.select("div.article--meta-data"): x.extract()
        except IndexError:
            pass

        article_element = soup.select("article.article-page--main-content")[0]
        article_html = str(article_element.prettify())
        output = pypandoc.convert(article_html, to='markdown_github', format='html', outputfile=filepath)

    print()
