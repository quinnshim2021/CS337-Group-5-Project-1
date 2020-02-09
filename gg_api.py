'''Version 0.35'''

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

import pandas as pd
import re
from collections import Counter

import spacy
<<<<<<< HEAD
=======
nlp = spacy.load("en_core_web_sm")
#
>>>>>>> 1b0f06f30fa78dc786f2a4277fec3701a6e15aa2

from helper_functions import *



#
from collections import Counter 
#



def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    '''
    {'2013': {'hosts': {'completeness': 1.0, 'spelling': 1.0}},
    '2015': {'hosts': {'completeness': 1.0, 'spelling': 1.0}}}
    '''


    FILE_NAME = "gg"+ str(year) + ".json"
    cutoff = 0.60

    try:
        df = pd.read_json(FILE_NAME)
    except:
        df = pd.read_json(FILE_NAME, lines=True)

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

        if len(candidate.split()) > 1 and strict_verify_person(candidate):
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
    '''
    {'2013': {'awards': {'completeness': 0.187, 'spelling': 0.8313574982100284}},
     '2015': {'awards': {'completeness': 0.2756756756756757,
                         'spelling': 0.8083238461538619}}}
    '''


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
            if should_add_award(candidate, award):
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

# {'2013': {'nominees': {'completeness': 0.034364285714285715,
#                        'spelling': 0.22833333333333333}},
#  '2015': {'nominees': {'completeness': 0.052571428571428575,
#                        'spelling': 0.22833333333333333}}}

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
    # df['text'] = df['text'].str.replace('The', '', case=False)
    # df['text'] = df['text'].str.replace('And', '', case=False)
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
    df['text'] = df['text'].str.replace('@', '', case=False)
    df['text'] = df['text'].str.replace('wtf', '', case=False)
    

    df['text'] = df["text"].str.lower()
    for award_name, award_dict in awards_dict.items():
        df1 = get_award_tweets_nominees(df, award_dict)
        df_beat = df1[df1["text"].str.contains('beat|beating|bested|defeated|won against|lost to')]
        # df1 = df_base[df_base["text"].str.contains('have won|won|win|had won|lost|loses|sad|might have|mentioned')]
        # print(df1['text'])

        # print(df1['text'])
        df_beat_groups1 = df_beat["text"].str.extract('([^,]+) (beat|beating|bested|defeated|won against) ([^,]+)')
        df_beat_groups2 = df_beat["text"].str.extract('([^,]+) (lost to) ([^,]+)')
        candidates = df_beat_groups1[~df_beat_groups1[2].isnull()][[2]]
        temp = df_beat_groups2[~df_beat_groups2[0].isnull()][[0]]
        
        candidates.columns = ["nominee"]
        candidates['nominee'] = candidates['nominee'].apply(lambda x: [ent.text for ent in list(nlp(x).ents)])
        candidates['nominee'] = candidates['nominee'].apply(lambda x: None if len(x) is 0 else x[0])
        candidates = candidates[~candidates['nominee'].isnull()][['nominee']]

        temp.columns = ['nominee']
        temp['nominee'] = temp['nominee'].apply(lambda x: [ent.text for ent in list(nlp(x).ents)])
        temp['nominee'] = temp['nominee'].apply(lambda x: None if len(x) is 0 else x[0])
        temp = temp[~temp['nominee'].isnull()][['nominee']]
        
        candidates = candidates.append(temp)
        

        # candidates = candidates.split()
        # print(candidates['nominee'])


        # temp = pd.Series()
        # candidates['nominee'] = candidates['nominee'].apply(lambda x: temp.append(pd.Series(x))) 
        # print(temp)
        
  


        # df_pronouns = df_beat_groups["text"].str.extractall('([A-Z][a-z]+(?=\s[A-Z])(?:\s[A-Z][a-z]+)+)') 
        # # df_temp = df1["text"].str.extractall('([A-Z][a-z]+)')
        # # df_pronouns = df_pronouns.append(df_temp)

        
        candidates["nominee"] = candidates["nominee"].str.lower()
        candidates["nominee_len"] = candidates["nominee"].str.split().apply(len)
        candidates = candidates[candidates["nominee_len"] <= 8]
        counts = candidates["nominee"].value_counts(ascending=False)
        print(award_name)
        print(counts)
        nominee = []
        count = 0
        candidates = list(counts.index)
        len_candidates = len(candidates)
        for i in range(len_candidates):
            # if counts.values[count] < 2:
            #     break
            if count == 4:
                break
            elif award_dict["weird_noun"]:
                 # GOTTA EMBED HERE IF A THING OR IF A PERSON
                answer = verify_film_tv(candidates[i], award_dict["medium"], year, threshold=60)
                if answer:
                    if answer != winners[award_name]:
                        # if should_add_candidate(answer, candidates[i+1:]) and answer not in nominee:
                        print(f"{answer} is a nominee of the award")
                        nominee.append(answer)
                        count += 1
                        # else:
                        #     candidates[i] = ''
                            
            else:
                  # GOTTA EMBED HERE IF A THING OR IF A PERSON
                answer = verify_person(candidates[i], threshold=60)
                if answer:
                    if answer != winners[award_name]:
                        # if should_add_candidate(answer, candidates[i+1:]) and answer not in nominee:
                        print(f"{answer} is a nominee of the award")
                        nominee.append(answer)
                        count += 1
                        # else:
                        #     candidates[i] = ''
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
    '''
    {'2013': {'winner': {'spelling': 0.6923076923076923}},
    '2015': {'winner': {'spelling': 0.7692307692307693}}}
    '''
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
 
    df_base = df[df["text"].str.contains('goes to')]

    for award_name, award_dict in awards_dict.items():

        df1 = get_award_tweets(df_base, award_dict)

        # df_goes = df1[df1["text"].str.contains('goes to')]
        df_goes_groups = df_goes["text"].str.extract('([^,]+) (goes to) ([^,]+)')
        candidates = df_goes_groups[~df_goes_groups[2].isnull()][[2]]
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

    FILE_NAME = "gg"+ str(year) + ".json"

    try:
        df = pd.read_json(FILE_NAME)
    except:
        df = pd.read_json(FILE_NAME, lines=True)

    df["text"] = df["text"].str.lower()
    df['text'] = df['text'].str.replace('http\S+|www.\S+', '', case=False)
    df['text'] = df['text'].str.replace('#goldenglobes', '', case=False)
    df['text'] = df['text'].str.replace('tv ', 'television ', case=False)
    df['text'] = df['text'].str.replace('@', '', case=False)
    df['text'] = df['text'].str.replace('\'s', '', case=False)
    df['text'] = df['text'].str.replace('movie', 'motion picture', case=False)

    nlp = spacy.load("en_core_web_sm")

    presenters_tweets = []
    presenter_words = ['present', 'presents', 'presenting','presenter','presented' 'Present', 'Presenter', 'Presenting', 'Presented', 'Presents']
    stopwords = ['goldenglobes', 'golden globes', 'gg', 'gg2020', 'actor', 'actress', 'award', 'cecil', 'movie', 'drama']
    for tweet in df['text']:
        if any(word in tweet for word in presenter_words):
            presenters_tweets.append(tweet)

    for award in presenters:
        potential_presenters = {}
        for pt in presenters_tweets:
            # filter by award key words to make sure it's award specific
            if 'actor' in award:
                if 'actor' not in pt:
                    continue
            if 'actress' in award:
                if 'actress' not in pt:
                    continue
            if 'television' in award:
                if 'television' not in pt and 'tv' not in pt:
                    continue
            if 'drama' in award:
                if 'drama' not in pt:
                    continue
            if 'score' in award:
                if 'score' not in pt and 'song' not in pt:
                    continue
            if 'animated' in award:
                if 'animated' not in pt:
                    continue
            if 'musical' in award or 'comedy' in award:
                if 'musical' not in pt and 'comedy' not in pt:
                    continue
            
            t = nlp(pt)
            for p in t.ents:
                if p.label_ == "PERSON":
                    if 'http' not in p.text:
                        presenter_names = p.text.split()
                        g = True
                        for n in presenter_names or n in stopwords:
                            if n in presenter_words:
                                g = False
                        if g:
                            if p.text in potential_presenters:
                                potential_presenters[p.text] += 1
                            else:
                                potential_presenters[p.text] = 1
        # find the most common presenters  
        k = Counter(potential_presenters)
        top_two = k.most_common(2)
        for i in top_two:
            presenters[award].append(i[0])

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

    print(df_awards.shape)
    print(df_awards.columns)

    # Best dressed

    df_dressed = df_awards[df_awards["award_part"].str.contains('dress|outfit')]
    if df_dressed.shape[0] > 0:
        df_dressed["winner"] = df_dressed.apply(func= lambda row: verify_person(row['winner_part'], threshold=50), axis=1)
        df_dressed = df_dressed[~df_dressed["winner"].isnull()] 

        counts = df_dressed["winner"].value_counts(ascending=False)

    else:
        cutoff = 0.50
        df_dressed = df[df["text"].str.contains('dress|outfit')]
        print(df_dressed.shape)
        print(df_dressed.columns)

        dressed_col = df_dressed.apply(func= lambda row: get_chunks(row["text"]), axis=1)
        counts = make_counts(dressed_col)
        counts = counts[counts >= max(counts) * cutoff]

    print(counts)

    best_dressed = []
    for candidate in list(counts.index):
        if verify_person(candidate, threshold=0.80):
            if candidate not in best_dressed:
                best_dressed.append(candidate)
        if len(best_dressed) >= 2:
            break

    print(best_dressed)


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

    extra_awards = {}
    for row in df_awards.iterrows():
        # if len(candidate.split()) <= 11 and len(candidate.split()) > 3:
        #     if candidate not in awards:
        if should_add_award(row["award_part"], list(extra_awards.keys())):
            extra_awards[row["award_part"]] = row["winner"]

    print(df_awards)
    print(df_awards.shape)

    # Sentiment Analysis of Host
    hosts = get_hosts(year)

    host_sentiments = {host: {"mean": None, "std": None} for host in hosts}

    print(hosts)

    for host in hosts:
        df_col = df[df["text"].str.contains(host)]["text"]
        # print(df_col)
        stats = sentiment_stats(df_col)
        print(stats)
        print("hola")
        

    print(hosts)



def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here

    # get_winner(2020)
    extra_credit(2015)
    print("bye")

    # get_winner(2013)

    # extra_credit(2015)

    #get_awards(2020)
    # get_presenters(2020)
    #get_nominees(2013)

    # get_winner(2020)
    #extra_credit(2015)
    #get_awards(2020)
    # get_presenters(2020)
    return

if __name__ == '__main__':
    main()
