import requests

import pandas as pd
import spacy
from bs4 import BeautifulSoup
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from tqdm import tqdm as progress_bar


# SCRAPE COURSE DESCRIPTIONS
print("Scraping course descriptions...")

url = "https://apps.carleton.edu/campus/registrar/catalog/current/departments/"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
departments = soup.select(".childrenList a")

catalog = []

for department in progress_bar(departments):
    department_name = department.text

    page = requests.get(f"{url}{department.get('href')}")
    soup = BeautifulSoup(page.content, "html.parser")

    courses = soup.select(".catalog_block .courseContainer")
    for course in courses:
        dept, number = course.select_one(".courseNumber").text.split()
        title = course.select_one(".courseTitle").text
        description = (
            course.select_one(".courseDescription")
            .text.rsplit("Prerequisite:", 1)[0]
            .strip()
        )

        if description != "":
            catalog.append((dept, number, title, description))


catalog = pd.DataFrame.from_records(
    catalog, columns=["DEPT", "NUMBER", "TITLE", "DESC"]
).dropna()
catalog = catalog[catalog.DESC != ""]

# CREATE DOCUMENT VECTORS
# (using values for k and w determined in k-hell.py)
print("Tokenizing course descriptions...")

stopwords = set(open("stopwords.txt", "rt").read().split())
nlp = spacy.load("en_core_web_sm")

tokenize = lambda text: [
    token.lemma_
    for token in nlp(text.lower())
    if token.pos_ != "PUNCT" and token.text not in stopwords
]

tokens = []
for *_, desc in catalog.itertuples():
    tokens.append(tokenize(desc))

print("Creating document vectors...")
tagged_docs = [TaggedDocument(doc, [i]) for i, doc in enumerate(tokens)]
model = Doc2Vec(tagged_docs, vector_size=90, window=130, min_count=1, workers=4)
vectors = [model.dv[i] for i in range(len(tagged_docs))]
catalog["VECTORS"] = vectors

print("Saving...")
catalog.to_pickle("catalog.pickle")

print("DONE!")

# to load catalog, use
# pd.read_pickle("catalog.pickle")
