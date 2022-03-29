import random
import time
import pandas as pd
import tracery
from recommendations import find_similar
import json


class Chatbot:
    def give_intro(self):
        print("Welcome to the Carleton Course Assistant!\n")
        text = input("What is your name? ")
        self.user_name = text
        print(
            "\nIt's nice to meet you "
            + self.user_name
            + "! I'm going to help you find out what courses you should take next term.\n"
        )

    def get_user_major(self):
        print("Let's start with some questions.")

        found_major = False
        while not found_major:
            major = input("What is your major? ")
            possibility = ""
            for m in self.majors:
                if major == m.strip():
                    found_major = True
                    self.user_major = m.strip()
                elif major in m:
                    possibility = m.strip()
            if not found_major and possibility:
                guess_correct = input("Did you mean " + possibility + "? (Yes/No) ")
                if guess_correct == "Yes":
                    found_major = True
                    self.user_major = possibility
            if not found_major:
                print("We couldn't find that major - let's try again!")

        # I was thinking of here having like varying responses based on the major!
        print("You're a " + self.user_major + " major? Cool!\n")

    def get_user_classes(self):
        print("Now let's talk about your favorite classes that you've ever taken.\n")

        mode = ""
        while mode != "Major" and mode != "General":
            if mode != "":
                print("That's not a known mode! Please try again.")
            mode = input(
                "Do you want to get general course recommendations, or just ones in your major? (General/Major) "
            )

        fav_count = 0
        number = ["", " second", " third", " fourth"]
        fav_classes = []

        while fav_count < 4:
            fav_class = input(
                "What's your"
                + number[fav_count]
                + " favorite class you've taken? (Format: DEPT #: Class Title) "
            )
            if self.check_valid(fav_class):
                fav_classes.append(fav_class)
                fav_count += 1
            else:
                print(
                    "Sorry, we couldn't find "
                    + fav_class
                    + " in our course catalog! Please try again."
                )

        class_recs = find_similar(fav_classes)

        if mode == "General":
            class_recs = class_recs[["DEPT", "NUMBER", "TITLE", "SIMILARITY"]][:3]
        elif mode == "Major":
            class_recs = class_recs[
                class_recs.DEPT == self.majors_to_codes[self.user_major]
            ]
            class_recs = class_recs[["DEPT", "NUMBER", "TITLE", "SIMILARITY"]][:3]

        print("Here are three classes we recommend for you!")
        print(class_recs)
        time.sleep(3)
        print(
            "I just got wind of a new class that will only run one term next year...check it out!"
        )
        print(self.generate_class(self.majors_to_codes[self.user_major]))

    def generate_class(self, major):
        with open("titleGrammar.json", "rt") as f:
            grammar = tracery.Grammar(json.load(f))
        grammar.add_modifiers(tracery.modifiers.base_english)
        class_name = grammar.flatten(f"#{major.strip()}#")
        class_num = str(random.randint(200, 400))
        return major.strip() + " " + class_num + ": " + class_name

    def check_valid(self, fav_class):
        classList = fav_class.split(": ")
        classList[0] = classList[0].split()
        if (
            classList[0][0] not in self.catalog["DEPT"].unique()
            or classList[0][1] not in self.catalog["NUMBER"].unique()
            or classList[1] not in self.catalog["TITLE"].unique()
        ):
            return False
        return True

    def __init__(self):
        with open("majors.txt", "rt") as f:
            self.majors = f.readlines()
        with open("minors.txt", "rt") as f:
            self.minors = f.readlines()
        with open("majors_to_codes.txt", "rt") as f:
            m_to_c = f.readlines()
        self.majors_to_codes = {}
        for row in m_to_c:
            pair = row.strip().split(":")
            self.majors_to_codes[pair[0]] = pair[1]

        self.catalog = pd.read_pickle("catalog.pickle")

        self.give_intro()
        self.get_user_major()
        self.get_user_classes()


if __name__ == "__main__":
    chatbot = Chatbot()
