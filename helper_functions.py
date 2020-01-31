import imdb
import pandas as pd

from itertools import chain
from collections import Counter

IA = imdb.IMDb()

import spacy

NLP = spacy.load("en_core_web_sm")

from spacy.lang.en.stop_words import STOP_WORDS



NOT_USEFUL_NOUNS = set()

NOT_USEFUL_NOUNS.add("the golden globes")
NOT_USEFUL_NOUNS.add("golden globes")
NOT_USEFUL_NOUNS.add("goldenglobes")
NOT_USEFUL_NOUNS.add("golden globe")
NOT_USEFUL_NOUNS.add("the golden globe")
NOT_USEFUL_NOUNS.add("rt")
NOT_USEFUL_NOUNS.add("amp")
NOT_USEFUL_NOUNS.add("a motion picture")
NOT_USEFUL_NOUNS.add("drama")
NOT_USEFUL_NOUNS.add("comedy")
NOT_USEFUL_NOUNS.add("tv movie")
NOT_USEFUL_NOUNS.add("@goldenglobes")
NOT_USEFUL_NOUNS.add("miniseries")
NOT_USEFUL_NOUNS.add("actor")
NOT_USEFUL_NOUNS.add("motion picture")
NOT_USEFUL_NOUNS.add("congrats")
NOT_USEFUL_NOUNS.add("the goldenglobes")
NOT_USEFUL_NOUNS.add("television")
NOT_USEFUL_NOUNS.add("television movie")
NOT_USEFUL_NOUNS.add("a series")
NOT_USEFUL_NOUNS.add("limited series")

'''
Medium: 0: Film,
        1: TV,
        2: Neither

Type: 0: Drama
      1: Comedy
      2: Neither/Both
'''

NONE = 0
FILM = 1
TV = 2
LIMITED_SERIES = 3

NONE = 0
DRAMA = 1
COMEDY = 2

def get_query_dict(award_name):
    # Returns query string AND if the award has "weird" noun structure (True if it weird noun)

    if "best performance by an actress" in award_name:
        if "supporting role" in award_name:
            return "best supporting actress|best actress in supporting role", False
        else:
            return "best actress|best performance by an actress", False
    elif "best performance by an actor" in award_name:
        if "supporting role" in award_name:
            return "best supporting actor|best actor in supporting role", False
        else:
            return "best actor|best performance by an actor", False
    elif "best motion picture" in award_name:
        if "animated" in award_name:
            return "(?=.*best)(?=.*animated)", True
        elif "foreign" in award_name:
            return "(?=.*best)(?=.*foreign)", True
        else:
            return "best film|best motion picture|best picture", True
    elif "best screenplay" in award_name:
        return "best screenplay", True
    elif "director" in award_name:
        return "director", False
    elif "score" in award_name:
        return "best score|best original score", True
    elif "song" in award_name:
        return "best song|best original song", True
    elif "series" in award_name:
        if "limited" in award_name or "mini-series" in award_name:
            return "limited|mini-series|miniseries|television film|motion picture for television", True
        else:
            return "best television|best series", True
    elif 'cecil' in award_name:
        return 'cecil b. demille', False
    elif "animated" in award_name:
        return "(?=.*best)(?=.*animated)", True
    elif "foreign" in award_name:
        return "(?=.*best)(?=.*foreign)", True


def get_medium_dict(award_name):
    if "motion picture" in award_name:
        return FILM
    elif "series" in award_name:
        if "limited" in award_name or "mini-series" in award_name:
            return LIMITED_SERIES
        else:
            return TV
    else:
        return NONE


def get_typeof_dict(award_name):
    if "drama" in award_name:
        return DRAMA
    elif "comedy" in award_name:
        return COMEDY
    else:
        return NONE


def make_award_dict(award_name):
    query_name, weird_noun = get_query_dict(award_name)
    award = {"string": award_name,
             "query_name": query_name,
             "weird_noun": weird_noun,
             "typeof": get_typeof_dict(award_name),
             "medium": get_medium_dict(award_name)}

    return award


def make_counts(df_col):
    return pd.Series(Counter(chain.from_iterable(x for x in df_col))).sort_values(ascending=False)


def get_chunks(str):
    return [chunk.text for chunk in NLP(str).noun_chunks if chunk.text not in STOP_WORDS and chunk.text not in NOT_USEFUL_NOUNS]


def get_medium_tweets(df, medium):
    if medium == FILM:
        return df[df["text"].str.contains('movie|film|picture')]
    elif medium == TV:
        return df[df["text"].str.contains('television|series|show')]
    elif medium == LIMITED_SERIES:
        return df[df["text"].str.contains("limited|mini-series|miniseries|television film|motion picture for television")]
    elif medium == NONE:
        return df
    else:
        print(f"medium {medium} not identified, error")
        return df     

def get_type_tweets(df, typeof):
    if typeof == DRAMA:
        return df[df["text"].str.contains('drama')]
    elif typeof == COMEDY:
        return df[df["text"].str.contains('comedy|musical')]
    elif typeof == NONE:
        # Pending (?)
        return df
    else:
        print(f"typeof {typeof} not identified, error")
        return df


def get_award_tweets(df, award):
    df1 = df[df["text"].str.contains(award["query_name"])]
    # print(df1.shape)
    df1 = get_medium_tweets(df1, award["medium"])
    # print(df1.shape)
    # print(df1["text"])
    df1 = get_type_tweets(df1, award["typeof"])
    return df1


def verify_person(person_name):
    # Go through list, find person with same name(ish)
    return any([person["name"].lower()  == person_name for person in IA.search_person(person_name) ])


def verify_film_tv(title):
    movies = IA.search_movie(title)

    # Go through list, find movie with same title(ish)
    index = [i for i, movie in enumerate(movies) if movie["title"].lower() == title]

    if len(index) == 0:
        # If none, return false and null
        return False
    else:
        # If you do find one, return what it is
        return movies[index[0]]["kind"]
 



OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']



# import pprint

# pp = pprint.PrettyPrinter(indent=4)


# pp.pprint([make_award_dict(award) for award in OFFICIAL_AWARDS_1315])


# pp.pprint([make_award_dict(award) for award in OFFICIAL_AWARDS_1819])
