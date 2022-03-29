from string import punctuation
from itertools import starmap, product
from random import sample
from statistics import mean

import pandas as pd
from gensim.models.doc2vec import TaggedDocument, Doc2Vec
import spacy
from scipy.spatial.distance import cosine


catalog = pd.read_pickle("catalog.pickle")

stopwords = set(open("stopwords.txt", "rt").read().split()) | set(punctuation)
nlp = spacy.load("en_core_web_sm")

tokenize = lambda text: [
    token.lemma_ for token in nlp(text.lower()) if token.text not in stopwords
]

tokens = list(map(tokenize, catalog["DESC"]))

depts = {
    dept: list(course_indices)
    for dept, course_indices in catalog.groupby("DEPT").groups.items()
}


def get_dept(i):
    for dept, courses in depts.items():
        if i in courses:
            return dept

    raise IndexError("Value out of bounds")


def test_k_w(k, w=4, n_samples=-1):

    tagged_docs = [TaggedDocument(doc, [i]) for i, doc in enumerate(tokens)]
    model = Doc2Vec(tagged_docs, vector_size=k, window=w, min_count=1, workers=4)
    vectors = [model.dv[i] for i in range(len(tagged_docs))]

    all_courses = set(range(len(vectors)))

    to_test = (
        sample(list(enumerate(vectors)), n_samples)
        if n_samples > 0
        else enumerate(vectors)
    )

    def get_score(i, v):
        distance_from_v = lambda j: cosine(v, vectors[j])

        dept = get_dept(i)
        in_dept = depts[dept]
        out_dept = all_courses - set(in_dept)

        in_score = mean(map(distance_from_v, in_dept))
        out_score = mean(map(distance_from_v, out_dept))

        return in_score / out_score

    score = mean(starmap(get_score, to_test))  # this is slow...

    return score


def find_best_params():

    ks = [5, 10, 25, 50, 75, 100]
    ws = [5, 10, 25, 50, 75, 100, 130]

    results = []
    for k, w in product(ks, ws):
        result = test_k_w(k, w)
        print(k, w, result)
        results.append((k, w, result))

    print("\n---DONE----\n")

    best = min(result, key=lambda x: x[-1])
    print(best)


# results of running code overnight:
# BEST: k = 90, w = 130 (max len of description)
