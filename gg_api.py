'''Version 0.35'''

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']




import pandas as pd
import re

from helper_functions import *


def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here


    FILE_NAME = "gg"+ str(year) + ".json"
    cutoff = 0.50

    df = pd.read_json(FILE_NAME)

    print(list(df))

    df["text"] = df["text"].str.lower()
    df['text'] = df['text'].str.replace('http\S+|www.\S+', '', case=False)
    df['text'] = df['text'].str.replace('#goldenglobes', '', case=False)


    df1 = df[df["text"].str.contains('host')]
    df1_col = df1.apply(func= lambda row: get_chunks(row["text"]), axis=1)

    counts = make_counts(df1_col)

    counts = counts[counts >= max(counts) * cutoff]

    print(counts)

    hosts = []
    for candidate in list(counts.index):
        if verify_person(candidate):
            if candidate not in hosts:
                hosts.append(candidate)
        if len(hosts) >= 2:
            break


    print(hosts)

    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here

    FILE_NAME = "gg"+ str(year) + ".json"

    try:
        df = pd.read_json(FILE_NAME)
    except:
        df = pd.read_json(FILE_NAME, lines=True)

    df["text"] = df["text"].str.lower()
    df_goes = df[df["text"].str.contains('goes to')]
    df_goes_groups = df_goes["text"].str.extract('([^,]+) for ([^,]+) goes to ([^,]+)')

    candidates = df_goes_groups[~df_goes_groups[1].isnull()][[1]]

    candidates.columns = ["goes"]

    candidates = candidates[candidates["goes"].str.contains('$award|^best')]
    candidates["goes_count"] = candidates["goes"].str.split().apply(len)

    candidates = candidates[candidates["goes_count"] > 3]

    candidates = candidates[candidates["goes_count"] <= 11]

    # Assume number (for now)

    counts = candidates["goes"].value_counts(ascending=False)

    print(counts)

    '''
    MISSING:
    - picking the final list of winners
    - how to deal with "repeated" awards (awards that are quite similar in name)
    - Filtering "non-useful" awards (might be making too many assumptions with this tho)
    '''

    awards = []
    for candidate in list(counts.index):
        # if len(candidate.split()) <= 11 and len(candidate.split()) > 3:
        #     if candidate not in awards:
        awards.append(candidate)

    awards = awards[0:min(len(awards), 27)]

    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    if year == "2013" or year == "2015":
        nominees = {award: [] for award in OFFICIAL_AWARDS_1315}
    else:
        nominees = {award: [] for award in OFFICIAL_AWARDS_1819}

    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    if year == "2013" or year == "2015":
        winners = {award: "" for award in OFFICIAL_AWARDS_1315}
    else:
        winners = {award: "" for award in OFFICIAL_AWARDS_1819}

    awards_dict = {award: make_award_dict(award) for award in list(winners.keys())}


    FILE_NAME = "gg"+ str(year) + ".json"
    cutoff = 0.50

    try:
        df = pd.read_json(FILE_NAME)
    except:
        df = pd.read_json(FILE_NAME, lines=True)

    print(list(df))

    df["text"] = df["text"].str.lower()
    df['text'] = df['text'].str.replace('http\S+|www.\S+', '', case=False)
    df['text'] = df['text'].str.replace('#goldenglobes', '', case=False)
    df['text'] = df['text'].str.replace('tv', 'television', case=False)

    df_base = df[df["text"].str.contains('win|won|goes to')]


    for award_name, awards_dict in awards_dict.items():

        print(awards_dict)

        df1 = get_award_tweets(df_base, awards_dict)
        # print(df1["text"])
        print(df1.shape)
        print("why")


        df1_col = df1.apply(func= lambda row: get_chunks(row["text"]), axis=1)

        counts = make_counts(df1_col)

        # Remove ones that start with best
        counts = counts[~counts.index.str.contains("best|award")]

        counts = counts[counts >= max(counts) * cutoff]

        print(counts)

        winner = ""
        for candidate in list(counts.index):

            if "performance" in award_name or "award" in award_name:

                # GOTTA EMBED HERE IF A THING OR IF A PERSON
                if verify_person(candidate):
                    print(f"{candidate} is the winner of the award")
                    winner = candidate
                    break
            else:
                 # GOTTA EMBED HERE IF A THING OR IF A PERSON
                if verify_film_tv(candidate):
                    print(f"{candidate} is the winner of the award")
                    winner = candidate
                    break               

        winners[award_name] = winner

    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    if year == "2013" or year == "2015":
        presenters = {award: [] for award in OFFICIAL_AWARDS_1315}
    else:
        presenters = {award: [] for award in OFFICIAL_AWARDS_1819}
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here

    # get_winner(2020)
    get_awards(2020)

    return

if __name__ == '__main__':
    main()
