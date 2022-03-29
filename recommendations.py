import re
from statistics import mean
from typing import Iterable

from scipy.spatial.distance import cosine
import pandas as pd


def find_similar(titles_to_compare: Iterable[str], catalog=pd.read_pickle("catalog.pickle")):
    """
    TODO: add docstring
    """
    def get_index(name):
        try:
            dept, number, title = re.split(r":?\s+", name, maxsplit=2)
            in_dept = catalog["DEPT"] == dept.upper()
            matches_number = catalog["NUMBER"] == str(number)
            matches = catalog[in_dept & matches_number]
            if title:
                candidate_titles = matches["TITLE"].str.lower()
                matches = matches[candidate_titles.str.contains(title.lower())]
            v = list(matches.index.tolist())[0]
            return v

        except IndexError:
            raise LookupError(f"Could not retrieve '{name}' from catalog.")

    get_vector = lambda i: catalog["VECTORS"].iloc[i]

    to_return = catalog.copy()
    all_vectors = list(catalog["VECTORS"])
    indices_to_compare = list(map(get_index, titles_to_compare))
    vectors_to_compare = map(get_vector, indices_to_compare)

    # function to compare two vectors:
    get_similarity = lambda u, v: 1 - cosine(u, v)
    # function to compare one vector to all other vectors:
    get_similarities = lambda u: map(lambda v: get_similarity(u, v), all_vectors)

    # list of avg similarity to all courses
    similarities = map(get_similarities, vectors_to_compare)
    avg_similarities = map(mean, zip(*similarities))
    to_return["SIMILARITY"] = list(avg_similarities)

    # don't return courses that the user searched for
    to_return.drop(index=indices_to_compare, inplace=True)

    return to_return.sort_values("SIMILARITY", ascending=False)


if __name__ == "__main__":
    s1 = find_similar(["ENGL 265", "CAMS 111"])
    s2 = find_similar(["CS 322", "PHYS 144", "MATH 236", "CS 201"])
    print(s1[["DEPT", "NUMBER", "SIMILARITY"]][:10])
    print(s2[["DEPT", "NUMBER", "SIMILARITY"]][:10])
