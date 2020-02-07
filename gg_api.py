'''Version 0.35'''

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']




import pandas as pd
import re
from collections import Counter

#
import spacy
#

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
    df['text'] = df['text'].str.replace('http\S+|www.\S+', '', case=False)
    df['text'] = df['text'].str.replace('#goldenglobes', '', case=False)
    df['text'] = df['text'].str.replace('tv ', 'television ', case=False)
    df_goes = df[df["text"].str.contains('goes to')]
    df_goes_groups = df_goes["text"].str.extract('([^,]+) goes to ([^,]+)')

    candidates = df_goes_groups[~df_goes_groups[0].isnull()][[0]]

    candidates.columns = ["goes"]

    candidates["goes"] = candidates.apply(func= lambda row: row['goes'].split('for')[0], axis=1)

    candidates = candidates[candidates["goes"].str.contains('$award|^best')]
    candidates["goes_count"] = candidates["goes"].str.split().apply(len)

    candidates = candidates[candidates["goes_count"] > 3]

    candidates = candidates[candidates["goes_count"] <= 11]

    # Assume number (for now)

    counts = candidates["goes"].value_counts(ascending=False)

    cutoff = 0.10
    counts = counts[counts >= max(counts) * cutoff]

    print(counts)

    awards = []
    for candidate in list(counts.index):
        # if len(candidate.split()) <= 11 and len(candidate.split()) > 3:
        #     if candidate not in awards:
        if "best" in candidate.split()[0] or "award" in candidate.split()[-1]:
            if candidate not in awards:
                awards.append(candidate)
        # if "actress" in candidate:
        #     inverse = candidate.replace("actress", "actor")
        #     if inverse not in awards:
        #         awards.append(inverse)
        # elif "actor" in candidate:
        #     inverse = candidate.replace("actor", "actress")
        #     if inverse not in awards:
        #         awards.append(inverse)

    print(awards)

    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''

# {'2013': {'nominees': {'completeness': 0.015380952380952379,
#                        'spelling': 0.09166666666666667}}}

    # Your code here
    ### create a subset of nominees with word "nominee" and then from that subset extract the award names an
    if year == "2013" or year == "2015":
        nominees = {award: [] for award in OFFICIAL_AWARDS_1315}
    else:
        nominees = {award: [] for award in OFFICIAL_AWARDS_1819}

    awards_dict = {award: make_award_dict(award) for award in list(nominees.keys())}
    ### need to call get winners. Make sure that the nominees that I am finding are not in the winners
    FILE_NAME = "gg"+ str(year) + ".json"

    try:
        df = pd.read_json(FILE_NAME)
    except:
        df = pd.read_json(FILE_NAME, lines=True)

    winners = get_winner(year)  ### Make sure nominee is not in this list
   
    df['text'] = df['text'].str.replace('http\S+|www.\S+', '', case=False)
    df['text'] = df['text'].str.replace('#GoldenGlobes', '', case=False)
    df['text'] = df['text'].str.replace('#goldenglobes', '', case=False)
    df['text'] = df['text'].str.replace('tv ', 'television ', case=False)
    df['text'] = df['text'].str.replace('#', '', case=False)
    df['text'] = df['text'].str.replace('Golden Globes', '', case=False)
    df['text'] = df['text'].str.replace('Congratulations', '', case=False)
    df['text'] = df['text'].str.replace('Golden Globe', '', case=False)
    df['text'] = df['text'].str.replace('Congrats', '', case=False)
    df['text'] = df['text'].str.replace('Nshowbiz', '', case=False)
    df['text'] = df['text'].str.replace('The', '', case=False)
    df['text'] = df['text'].str.replace('And', '', case=False)
    df['text'] = df['text'].str.replace('Congrats', '', case=False)
    df['text'] = df['text'].str.replace('Another', '', case=False)
    # df['text'] = df['text'].str.replace('Go On', '', case=False)
    df['text'] = df['text'].str.replace('OMG', '', case=False)
    df['text'] = df['text'].str.replace('Globe', '', case=False)
    df['text'] = df['text'].str.replace('Golden', '', case=False)
    df['text'] = df['text'].str.replace('Wow', '', case=False)
    df['text'] = df['text'].str.replace('Variety', '', case=False)
    df['text'] = df['text'].str.replace('Latest', '', case=False)
    df['text'] = df['text'].str.replace('Golden', '', case=False)




    # df_base = df[df["text"].str.contains('nominated|nominated for|nominee|nominees')]
    
    
    for award_name, award_dict in awards_dict.items():
        df1 = get_award_tweets(df, award_dict)
        df_pronouns = df1["text"].str.extractall('([A-Z][a-z]+(?=\s[A-Z])(?:\s[A-Z][a-z]+)+)') 
        df_temp = df1["text"].str.extractall('([A-Z][a-z]+)')
        df_pronouns = df_pronouns.append(df_temp)

        candidates = df_pronouns[~df_pronouns[0].isnull()][[0]]
        candidates.columns = ["nominee"]
        candidates["nominee"] = candidates["nominee"].str.lower()
        candidates["nominee_len"] = candidates["nominee"].str.split().apply(len)
        candidates = candidates[candidates["nominee_len"] <= 8]
        counts = candidates["nominee"].value_counts(ascending=False)
        # print(award_name)
        # print(counts)
        nominee = []
        count = 0
        candidates = list(counts.index)
        for i in range(len(candidates)):
            # if counts.values[count] < 2:
            #     break
            if count == 4:
                break
            elif award_dict["weird_noun"]:
                 # GOTTA EMBED HERE IF A THING OR IF A PERSON
                answer = verify_film_tv(candidates[i], award_dict["medium"], year)
                if answer:
                    if answer != winners[award_name]:
                        if should_add_candidate(answer, candidates[i+1:]):
                            print(f"{answer} is a nominee of the award")
                            nominee.append(answer)
                            count += 1
                            
            else:
                  # GOTTA EMBED HERE IF A THING OR IF A PERSON
                answer = verify_person(candidates[i])
                if answer:
                    if answer != winners[award_name]:
                        if should_add_candidate(answer, candidates[i+1:]):
                            print(f"{answer} is a nominee of the award")
                            nominee.append(answer)
                            count += 1
            # count += 1          
        # temp = Counter(nominee)
        # nominee = list(list(zip(*(temp.most_common(4))))[0])
        nominees[award_name] = nominee
    print(nominees)
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

    # print(list(df))

    df['text'] = df['text'].str.lower()
    df['text'] = df['text'].str.replace('http\S+|www.\S+', '', case=False)
    df['text'] = df['text'].str.replace('#goldenglobes', '', case=False)
    df['text'] = df['text'].str.replace('tv ', 'television ', case=False)
    

    df_base = df[df['text'].str.contains('win|won|goes to')]

    for award_name, award_dict in awards_dict.items():

        df1 = get_award_tweets(df_base, award_dict)

        df_goes = df1[df1["text"].str.contains('goes to')]
        df_goes_groups = df_goes["text"].str.extract('([^,]+) (goes to) ([^,]+)')
        candidates = df_goes_groups[~df_goes_groups[2].isnull()][[2]]
        # print(candidates)

        candidates.columns = ["won"]
        # candidates["won"] = candidates['won'].str.replace('[^\w\s]','')
        candidates["won"] = candidates.apply(func= lambda row: row['won'].split('for')[0], axis=1)

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

    awards_dict = {award: make_award_dict(award) for award in list(presenters.keys())}

    FILE_NAME = "gg"+ str(year) + ".json"

    try:
        df = pd.read_json(FILE_NAME)
    except:
        df = pd.read_json(FILE_NAME, lines=True)

    print(list(df))

    # holds some of the awards so I can just test a few at a time

    television_synonyms = ["television", "tv", "television series", "tv series", "television show", "tv show"]
    motion_picture_synonyms = ["motion picture", "movie", "film"]
    nlp = spacy.load("en_core_web_sm")

    test_awards_dict = {award: {} for award in presenters} # need to change to presenters later
    #presenter_words = ['present', 'gave', 'giving', 'give', 'announce', 'read', 'introduce', 'host', 'will host']

    # filter tweets by presenter_words
        # do if re.search(next year...)
            # if word=='television' and everything after taht 
                #-> allow me to affiliate presenters with awards

    # do same thing as github but extract prsetner is just nlp with ents

    # kind of working...
    # imdb check is making it a lot slower
    for tweet in df['text']:
        tweet = tweet.lower()
        for award in presenters:
            award_words = award.split()
            # may want to add re_presenters here
            # if "represent" in award_words or "representation" in award_words or "next year" in award_words or "last year" in award_words:
            #     continue
            try:
                award_words.remove('-')
                award_words.remove('or')
            except:
                pass
            if re.search('(next year|last year|representation)', tweet) is None: # need to find phrases like these
                for word in award_words:
                    if word == "television":
                        award_words.remove("television")
                        if any([kw in tweet for kw in television_synonyms]):
                            if all([kw in tweet for kw in award_words]): # maybe an any or a cutoff %
                                t = nlp(tweet)
                                for person in t.ents:
                                    if person.label_ == "PERSON":
                                        if person.text not in ["Golden Globes", "GG", "GoldenGlobes", "golden globes", "goldenglobes", "goldenglobes2020"]:
                                            poss_host = person.text.lower()
                                            # if verify_person(poss_host):
                                            if poss_host not in test_awards_dict[award]:
                                                test_awards_dict[award][poss_host] = 1
                                            else:
                                                test_awards_dict[award][poss_host] += 1
                    elif word == "motion":
                        award_words.remove('motion')
                        if any([kw in tweet for kw in motion_picture_synonyms]):
                            if all([kw in tweet for kw in award_words]):
                                t = nlp(tweet)
                                for person in t.ents:
                                    if person.label_ == "PERSON":
                                        if person.text not in ["Golden Globes", "GG", "GoldenGlobes", "golden globes", "goldenglobes", "goldenglobes2020"]:
                                            poss_host = person.text.lower()
                                            # if verify_person(poss_host):
                                            if poss_host not in test_awards_dict[award]:
                                                test_awards_dict[award][poss_host] = 1
                                            else:
                                                test_awards_dict[award][poss_host] += 1
                    elif word=="cecil":
                        t = nlp(tweet)
                        for person in t.ents:
                            if person.label_ == "PERSON":
                                if person.text not in ["Golden Globes", "GG", "GoldenGlobes", "golden globes", "goldenglobes", "goldenglobes2020"]:
                                    poss_host = person.text.lower()
                                    # if verify_person(poss_host):
                                    if poss_host not in test_awards_dict[award]:
                                        test_awards_dict[award][poss_host] = 1
                                    else:
                                        test_awards_dict[award][poss_host] += 1    
                
                
    for award in test_awards_dict:
        {k: v for k, v in sorted(test_awards_dict[award].items(), key=lambda item: item[1])}
        i = 0
        for key in test_awards_dict[award]:
            presenters[award].append(key)
            i += 1
            if i == 2:
                break
    print(presenters)
    
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print("Pre-ceremony processing complete.")
    return

def extra_credit(year):

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
    df_dressed["winner"] = df_dressed.apply(func= lambda row: verify_person(row['winner_part'], threshold=50), axis=1)
    df_dressed = df_dressed[~df_dressed["winner"].isnull()] 

    counts = df_dressed["winner"].value_counts(ascending=False)

    print(counts)

    best_dressed = ""
    for candidate in list(counts.index):
        answer = verify_person(candidate)
        if answer:
            print(f"{answer} is the winner of the award")
            best_dressed = answer
            break          

    # Best Speech
    df_speech = df_awards[df_awards["award_part"].str.contains('speech')]
    df_speech["winner"] = df_speech.apply(func= lambda row: verify_person(row['winner_part'], threshold=50), axis=1)
    df_speech = df_speech[~df_speech["winner"].isnull()] 

    counts = df_speech["winner"].value_counts(ascending=False)

    print(counts)

    best_speech = ""
    for candidate in list(counts.index):
        answer = verify_person(candidate)
        if answer:
            print(f"{answer} is the winner of the award")
            best_dressed = answer
            break    

    # Extra awards
    award_words = ["actress", "actor", "television", "film", "director", "screenplay",
            "score", "song", "pic", "movie", "series", "comedy", "musical", "drama",
            "direct", "anima", "foreign", "dress", "speech", "outfit"]


    # Get award name
    df_awards = df_awards[~df_awards["award_part"].str.contains('|'.join(award_words))] 
    df_awards["winner"] = df_awards.apply(func= lambda row: verify_person(row['winner_part'], threshold=50), axis=1)
    df_awards = df_awards[~df_awards["winner"].isnull()]  

    print(df_awards)
    print(df_awards.shape)



def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here

    # get_winner(2013)

    # extra_credit(2015)

    #get_awards(2020)
    # get_presenters(2020)
    get_nominees(2013)
    return

if __name__ == '__main__':
    main()
