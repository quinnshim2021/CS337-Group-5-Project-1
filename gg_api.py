'''Version 0.35'''

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

import pandas as pd
import re
from collections import Counter

import spacy

nlp = spacy.load("en_core_web_sm")

from helper_functions import *

from collections import Counter 
#
import time


WINNERS = {}
PRESENTERS = {}
HOSTS_GLOBAL = {}
HOST_SENTIMENTS = {}
BEST_DRESSED = {}
BEST_SPEECH = {}
EXTRA_AWARDS = {}
AWARD_NAMES = {}
NOMINEES = {}


def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    '''
    {'2013': {'hosts': {'completeness': 1.0, 'spelling': 1.0}},
    '2015': {'hosts': {'completeness': 1.0, 'spelling': 1.0}}}
    '''
    # start = time.time()

    if year in HOSTS_GLOBAL:
        return HOSTS_GLOBAL[year]


    FILE_NAME = "gg"+ str(year) + ".json"
    cutoff = 0.50

    try:
        df = pd.read_json(FILE_NAME)
    except:
        df = pd.read_json(FILE_NAME, lines=True)

    df["text"] = df["text"].str.lower()
    df = df[df["text"].str.contains('host')]
    #df['text'] = df['text'].str.replace('http\S+|www.\S+', '', case=False)
    df['text'] = df['text'].str.replace('#goldenglobes', '', case=False)

    df1 = df.sample(n=min(1500, df.shape[0]))
    df1_col = df1.apply(func= lambda row: get_chunks(row["text"]), axis=1)

    counts = make_counts(df1_col)

    counts = counts[counts >= max(counts) * cutoff]

    hosts = []
    for candidate in list(counts.index):

        if len(candidate.split()) > 1 and strict_verify_person(candidate):
            if candidate not in hosts:
                hosts.append(candidate)
        if len(hosts) >= 2:
            break

    # print('Host took', time.time()-start, 'seconds.')
    HOSTS_GLOBAL[year] = hosts
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    '''
    {'2013': {'awards': {'completeness': 0.16666666666666666,
                     'spelling': 0.8005731028404686},
     '2015': {'awards': {'completeness': 0.2756756756756757,
                         'spelling': 0.8083238461538619}}}
    '''

    if year in AWARD_NAMES:
        return AWARD_NAMES[year]

    # start = time.time()
    FILE_NAME = "gg"+ str(year) + ".json"

    try:
        df = pd.read_json(FILE_NAME)
    except:
        df = pd.read_json(FILE_NAME, lines=True)



    df["text"] = df["text"].str.lower() 
    df = df[df["text"].str.contains('goes to')]
    df['text'] = df['text'].str.replace('http\S+|www.\S+', '', case=False)
    df['text'] = df['text'].str.replace('#goldenglobes', '', case=False)
    df['text'] = df['text'].str.replace('tv ', 'television ', case=False)

    df_goes = df
    
    df_goes_groups = df_goes["text"].str.extract('([^,]+) goes to ([^,]+)')

    candidates = df_goes_groups[~df_goes_groups[0].isnull()][[0]]

    candidates.columns = ["goes"]
    candidates["goes"] = candidates.apply(func= lambda row: row['goes'].split('for')[0], axis=1)

    candidates = candidates[candidates["goes"].str.contains('$award|^best')]
    candidates["goes_count"] = candidates["goes"].str.split().apply(len)

    candidates = candidates[candidates["goes_count"] > 3]
    candidates = candidates[candidates["goes_count"] <= 11]


    counts = candidates["goes"].value_counts(ascending=False)

    cutoff = 0.10
    counts = counts[counts >= max(counts) * cutoff]

    awards = []
    for candidate in list(counts.index):
        if "best" in candidate.split()[0] or "award" in candidate.split()[-1]:
            if should_add_award(candidate, awards):
                awards.append(candidate)


    # print('Awards took', time.time()-start, 'seconds.')
    AWARD_NAMES[year] = awards
    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.

    {'2013': 'nominees': {'completeness': 0.06088095238095239,
                       'spelling': 0.25666666666666665},
    '2015': {'nominees': {'completeness': 0.052571428571428575,
                         'spelling': 0.22833333333333333}}}
    '''

    # Your code here
    if year in NOMINEES:
        return NOMINEES[year]
    
    ### create a subset of nominees with word "nominee" and then from that subset extract the award names an
    if year == "2013" or year == "2015":
        nominees = {award: [] for award in OFFICIAL_AWARDS_1315}
    else:
        nominees = {award: [] for award in OFFICIAL_AWARDS_1819}

    awards_dict = {award: make_award_dict(award) for award in list(nominees.keys())}
    FILE_NAME = "gg"+ str(year) + ".json"

    try:
        df = pd.read_json(FILE_NAME)
    except:
        df = pd.read_json(FILE_NAME, lines=True)

    if year in WINNERS:
        winners = WINNERS[year]
    else:
        winners = get_winner(year)


    if year in PRESENTERS:
        presenters = PRESENTERS[year]
    else:
        presenters = get_presenters(year)

    # start = time.time()

    df['text'] = df["text"].str.lower()
 
    # df = df[df["text"].str.contains("should('ve| have)? (win|won|go|get)|predict|lost|hoping|hope|expect|robbed|snub|beat")]

    # start2 = time.time()
    df = df[df["text"].str.contains("should('ve| have)? (win|won|go|get)|predict|lost|hop(e|ing)|expect|robbed|snub|beat")]
    # print('Noms filter took', time.time()-start2, 'seconds.')

    # start2 = time.time()
    df['text'] = df['text'].str.replace('http\S+|www.\S+', '', case=False)
    df['text'] = df['text'].str.replace('#goldenglobes', '', case=False)
    df['text'] = df['text'].str.replace('tv ', 'television ', case=False)
    df['text'] = df['text'].str.replace('#', '', case=False)
    # df['text'] = df['text'].str.replace('movie', 'motion picture', case=False)
    # print('Noms replace took', time.time()-start2, 'seconds.')
        

    df_base = df[["text"]]
    for award_name, award_dict in awards_dict.items():
        start2 = time.time()
        df1 = get_award_tweets(df_base, award_dict)
        # print('Noms get award tweets took', time.time()-start2, 'seconds.')
        # df1 = df1.head(50)
        
        df1 = df1.sample(n=min(50, df1.shape[0]))
        # print(df1.shape)
        # start2 = time.time()
        df_col = df1.apply(func= lambda row: get_chunks(row["text"]), axis=1)
        # print('Noms noun chunking took', time.time()-start2, 'seconds.')
        # print(df_col.shape)
        if df_col.shape[0] > 0:

            counts = make_counts(df_col)

            # Remove counts that have "best" in index
            counts = counts[~counts.index.str.contains("best|motion picture|film|actor|actress|golden( )?globe|award")]

            counts = counts[0: min(counts.shape[0], 15)]

            # print(counts)
        
            noms = []
            # start2 = time.time()
            for candidate in list(counts.index):

                if award_dict["weird_noun"]:
                     # GOTTA EMBED HERE IF A THING OR IF A PERSON
                    answer = verify_film_tv(candidate, award_dict["medium"], year)
                    if answer and answer not in noms:
                        # noms.append(answer)
                        if answer not in winners[award_name] and answer not in presenters[award_name]:
                            noms.append(answer)
                else:
                      # GOTTA EMBED HERE IF A THING OR IF A PERSON
                    answer = verify_person(candidate)
                    if answer and answer not in noms:
                        # noms.append(answer)
                        if answer not in winners[award_name] and answer not in presenters[award_name]:
                            noms.append(answer)
                if len(noms) >= 4:
                    break     
            # print('Noms verification took', time.time()-start2, 'seconds.')

            nominees[award_name] = noms
    # print(nominees)
    # print('Noms took', time.time()-start, 'seconds.')
    NOMINEES[year] = nominees
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    '''
    {'2013': {'winner': {'spelling': 0.6923076923076923}},
    '2015': {'winner': {'spelling': 0.7692307692307693}}}
    '''
    # Your code here
    # start = time.time()

    if year in WINNERS:
        # print('Winner took', time.time()-start, 'seconds.')
        return WINNERS[year]

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

    # print(list(df))
    df = df[["text"]]
    df['text'] = df['text'].str.lower()
    df = df[df["text"].str.contains('goes to')]

    df['text'] = df['text'].str.replace('http\S+|www.\S+', '', case=False)
    df['text'] = df['text'].str.replace('#goldenglobes', '', case=False)
    df['text'] = df['text'].str.replace('tv ', 'television ', case=False)

    df_base = df
 
    for award_name, award_dict in awards_dict.items():

        df1 = get_award_tweets(df_base, award_dict)
        # print(df1.shape)
        df1 = df1.sample(n=min(30, df1.shape[0]))
        # df_goes = df1[df1["text"].str.contains('goes to')]
        df_goes_groups = df1["text"].str.extract('([^,]+) goes to ([^,]+)')
        candidates = df_goes_groups[~df_goes_groups[1].isnull()][[1]]
        # print(candidates)

        candidates.columns = ["won"]
        candidates["won"] = candidates.apply(func= lambda row: row['won'].split('for')[0], axis=1)
        # candidates["won"] = candidates['won'].str.replace('[^\w\s]','')

        # candidates = candidates[candidates["goes"].str.contains('$award|^best')]
        candidates["won_len"] = candidates["won"].str.split().apply(len)
        candidates = candidates[candidates["won_len"] <= 8]
        counts = candidates["won"].value_counts(ascending=False)

        # print(counts)

        winner = ""
        for candidate in list(counts.index):

            if award_dict["weird_noun"]:
                 # GOTTA EMBED HERE IF A THING OR IF A PERSON
                answer = verify_film_tv(candidate, award_dict["medium"], year)
                if answer:
                    # print(f"{answer} is the winner of the award")
                    winner = answer
                    break
            else:
                  # GOTTA EMBED HERE IF A THING OR IF A PERSON
                answer = verify_person(candidate)
                if answer:
                    # print(f"{answer} is the winner of the award")
                    winner = answer
                    break          

        winners[award_name] = winner

    # print(winners)
    # print('Winner took', time.time()-start, 'seconds.')
    WINNERS[year] = winners
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.

    {'2013': {'presenters': {'completeness': 0.2108974358974359,
                             'spelling': 0.38461538461538464}}}
    {'2015': {'presenters': {'completeness': 0.26282051282051283,
                             'spelling': 0.5}}}
    '''
    

    if year in PRESENTERS:
        return PRESENTERS[year]


    if year == "2013" or year == "2015":
        presenters = {award: [] for award in OFFICIAL_AWARDS_1315}
    else:
        presenters = {award: [] for award in OFFICIAL_AWARDS_1819}

    FILE_NAME = "gg"+ str(year) + ".json"

    try:
        df = pd.read_json(FILE_NAME)
    except:
        df = pd.read_json(FILE_NAME, lines=True)



    if year in WINNERS:
        winners = WINNERS[year]
    else:
        winners = get_winner(year)
        
    # start = time.time()

    df["text"] = df["text"].str.lower()

    df = df[df["text"].str.contains('present')]
    df = df[~df["text"].str.contains("represent")]

    df['text'] = df['text'].str.replace('http\S+|www.\S+', '', case=False)
    df['text'] = df['text'].str.replace('#goldenglobes', '', case=False)
    df['text'] = df['text'].str.replace('tv ', 'television ', case=False)
    df['text'] = df['text'].str.replace('@', '', case=False)
    df['text'] = df['text'].str.replace('\'s', '', case=False)
    df['text'] = df['text'].str.replace('movie', 'motion picture', case=False)


    df_base = df

    # print(df_base.shape)
    cutoff = 0.0
    awards_dict = {award: make_award_dict(award) for award in list(presenters.keys())}
    for award, award_dict in awards_dict.items():
        
        df = get_award_tweets(df_base, award_dict)
        # print(df.shape)
        df = df.sample(n=min(30, df.shape[0]))
        df_col = df.apply(func= lambda row: get_chunks(row["text"]), axis=1)

        if df_col.shape[0] > 0:
            counts = make_counts(df_col)

            counts = counts[counts >= max(counts) * cutoff]


            # Remove counts that have "best" in index
            counts = counts[~counts.index.str.contains("best")]

            # print(counts)

            potential_presenters = []
            for candidate in list(counts.index):

                answer = verify_person(candidate)
                if answer and answer not in potential_presenters:
                    if answer not in winners[award]:
                        potential_presenters.append(answer)
                if len(potential_presenters) >= 2:
                    break
            presenters[award] = potential_presenters

    # print(presenters)
    PRESENTERS[year] = presenters
    # print('Presenter took', time.time()-start, 'seconds.')
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print("Pre-ceremony processing complete.")
    return

def get_extra_stuff(year):

    # start = time.time()

    FILE_NAME = "gg"+ str(year) + ".json"
    cutoff = 0.50

    if year in EXTRA_AWARDS:
        return EXTRA_AWARDS[year]
    else:
        EXTRA_AWARDS[year] = {}

    try:
        df = pd.read_json(FILE_NAME)
    except:
        df = pd.read_json(FILE_NAME, lines=True)

    df["text"] = df["text"].str.lower()
    df['text'] = df['text'].str.replace('http\S+|www.\S+', '', case=False)
    df['text'] = df['text'].str.replace('#goldenglobes', '', case=False)
    df['text'] = df['text'].str.replace('tv ', 'television ', case=False)

    # Additional awards
    df_awards = df[df["text"].str.contains('goes to')]
    df_awards = df_awards["text"].str.extract('([^,]+) goes to ([^,]+)')

    df_awards = df_awards[~df_awards[0].isnull()]
    df_awards = df_awards[~df_awards[1].isnull()]

    df_awards.columns = ["award_part", "winner_part"]
    df_awards["award_part"] = df_awards.apply(func= lambda row: row['award_part'].split(' for ')[0], axis=1)
    df_awards = df_awards[df_awards["award_part"].str.contains('$award|^best')]

    # Best dressed

    df_dressed = df_awards[df_awards["award_part"].str.contains('dress|outfit')]
    if df_dressed.shape[0] > 0:
        df_dressed["winner"] = df_dressed.apply(func= lambda row: verify_person(row['winner_part'], threshold=50), axis=1)
        df_dressed = df_dressed[~df_dressed["winner"].isnull()] 

        counts = df_dressed["winner"].value_counts(ascending=False)

    else:
        cutoff = 0.50
        df_dressed = df[df["text"].str.contains('dress|outfit')]

        dressed_col = df_dressed.apply(func= lambda row: get_chunks(row["text"]), axis=1)
        counts = make_counts(dressed_col)
        counts = counts[counts >= max(counts) * cutoff]


    best_dressed = ""
    for candidate in list(counts.index):
        answer = verify_person(candidate, threshold=0.80)
        if answer:
            best_dressed = candidate
            break

    EXTRA_AWARDS[year]["best_dressed"] = best_dressed
    # print(f"best dressed: {best_dressed}")


    # Best Speech
    df_speech = df_awards[df_awards["award_part"].str.contains('speech')]
    df_speech["winner"] = df_speech.apply(func= lambda row: verify_person(row['winner_part'], threshold=50), axis=1)
    df_speech = df_speech[~df_speech["winner"].isnull()] 

    counts = df_speech["winner"].value_counts(ascending=False)


    best_speech = ""
    for candidate in list(counts.index):
        answer = verify_person(candidate)
        if answer:
            # print(f"{answer} is the winner of the award")
            best_speech = answer
            break    

    EXTRA_AWARDS[year]["best_speech"] = best_speech
    # print(f"best speech: {best_speech}")

    # Extra awards
    award_words = ["actress", "actor", "television", "film", "director", "screenplay",
            "score", "song", "pic", "movie", "series", "comedy", "musical", "drama",
            "direct", "anima", "foreign", "dress", "speech", "outfit"]


    # Get award name
    df_awards = df_awards[~df_awards["award_part"].str.contains('|'.join(award_words))] 
    df_awards["winner"] = df_awards.apply(func= lambda row: verify_person(row['winner_part'], threshold=60), axis=1)
    df_awards = df_awards[~df_awards["winner"].isnull()]  

    extra_awards = {}
    for index, row in df_awards.iterrows():
        # if len(candidate.split()) <= 11 and len(candidate.split()) > 3:
        #     if candidate not in awards:
        if should_add_award(row["award_part"], list(extra_awards.keys())):
            extra_awards[row["award_part"]] = row["winner"]


    EXTRA_AWARDS[year]["extra_awards"] = extra_awards
    # print(f"extra awards: {extra_awards}")

    # Sentiment Analysis of Host
    hosts = get_hosts(year)

    host_sentiments = {host: {} for host in hosts}


    for host in hosts:
        df_col = df[df["text"].str.contains(host)]["text"]
        # print(df_col)
        stats = sentiment_stats(df_col)
        host_sentiments[host] = stats

    EXTRA_AWARDS[year]["host_sentiments"] = host_sentiments
    # print(f"host sentiment_stats: {host_sentiments}")



    # print('Extra took', time.time()-start, 'seconds.')

    return EXTRA_AWARDS[year]



def print_outputs(year):
    hosts = get_hosts(year)
    winners = get_winner(year)
    presenters = get_presenters(year)
    nominees = get_nominees(year)
    awards = get_awards(year)
    extra_stuff = get_extra_stuff(year)

    file_dict = {
        "host": get_hosts(year),
        "extra_stuff:": extra_stuff,
        "extracted_awards": awards
    }

    for award_name in winners.keys():
        new_award_dict = {
          "presenters": presenters[award_name],
          "winner": winners[award_name],
          "nominees": nominees[award_name]
        }
        file_dict[award_name] = new_award_dict


    # Print JSON file
    import json
    with open('results_' + str(year)+ '.json', 'w') as fp:
        json.dump(file_dict, fp)

    # Print to screen "normal" results
    print("Host(s): {}".format([name.title() for name in hosts]))

    print()
    print("Extracted Award Names: {}".format([name.title() for name in awards]))
    print()

    for award_name in winners.keys():
        print("Award: {}".format(award_name.title()))
        print("Winner: {}".format(winners[award_name].title()))
        print("Nominees: {}".format([name.title() for name in nominees[award_name]]))
        print("Presenter(s): {}".format([name.title() for name in presenters[award_name]]))
        print()

    print()

    print("Best Dressed: {}".format(extra_stuff["best_dressed"].title()))
    print("Best Speech: {}".format(extra_stuff["best_speech"].title()))
    print()
    print("Interesting Awards Given by Twitter Users:")
    for extra_award, extra_winner in extra_stuff["extra_awards"].items():
        print("Award: {}".format(extra_award.title()))
        print("Winner: {}".format(extra_winner.title()))
        print()

    print()

    print("Host Sentiment Stats:")
    for host in hosts:
        print("Host: {}".format(host.title()))
        print("Statistics: {}".format(extra_stuff["host_sentiments"][host]))
        print()

    print()


    return


def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here

    # get_winner(2020)

    # get_winner(2013)

    # extra_credit(2015)

    #get_awards(2020)
    # get_presenters(2020)
    get_hosts(2020)

    # get_winner(2020)
    # #extra_credit(2015)
    # #get_awards(2020)
    # get_presenters(2020)
    return

if __name__ == '__main__':
    main()
