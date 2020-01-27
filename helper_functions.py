import imdb
import pandas as pd

from itertools import chain
from collections import Counter

IA = imdb.IMDb()

import spacy

NLP = spacy.load("en_core_web_sm")

from spacy.lang.en.stop_words import STOP_WORDS

STOP_WORDS.add("the golden globes")
STOP_WORDS.add("golden globes")

'''
Medium: 0: Film,
        1: TV

Type: 0: Drama
      1: Comedy
      2: Neither/Both
'''


def make_counts(df_col):
    return pd.Series(Counter(chain.from_iterable(x for x in df_col))).sort_values(ascending=False)


def get_chunks(str):
    return [chunk.text.title() for chunk in NLP(str).noun_chunks if chunk.text  not in STOP_WORDS]


def get_medium_tweets(df, medium):
    if medium == 0:
        return df[df["text"].str.contains('movie|film|picture')]
    elif medium == 1:
        return df[df["text"].str.contains('tv|television|series|show')]
    else:
        print(f"medium {medium} not identified, error")
        exit()

def get_type_tweets(df, typeof):
    if typeof == 0:
        return df[df["text"].str.contains('drama')]
    elif typeof == 1:
        return df[df["text"].str.contains('comedy|musical')]
    elif typeof == 2:
        # Pending (?)
        return df
    else:
        print(f"typeof {typeof} not identified, error")
        exit()


def get_award_tweets(df, award):
    df1 = df[df["text"].str.contains(award["name"])]
    # print(df1.shape)
    df1 = get_medium_tweets(df1, award["medium"])
    # print(df1.shape)
    # print(df1["text"])
    return get_type_tweets(df1, award["typeof"])


def verify_person(person_name):
    # Go through list, find person with same name(ish)
    return any([person["name"] == person_name for person in IA.search_person(person_name) ])


def verify_film_tv(title):
    movies = IA.search_movie(title)

    # Go through list, find movie with same title(ish)
    index = [i for i, movie in enumerate(movies) if movie["title"] == title]

    if len(index) == 0:
        # If none, return false and null
        return False
    else:
        # If you do find one, return what it is
        return movies[index[0]]["kind"]
 