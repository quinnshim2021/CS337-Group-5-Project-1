import pandas as pd
import re

from helper_functions import *


FILE_NAME = "gg2020.json"

'''
Name: Used for querying (does not need to be literal name)

Medium: 0: Film,
        1: TV

Type: 0: Drama
      1: Comedy
      2: Neither/Both

String: Name that will be printed for autograder


Winner: Winner(s) of award (to be filled out)


Nominees: Nominees of award (to be filled out)
'''

AWARDS = [
            {"name": "best actor",
             "medium": 0,
             "typeof": 0},
            # {"name": "best actor",
            #  "medium": 0,
            #  "typeof": 1},
            # {"name": "best actor",
            #  "medium": 1,
            #  "typeof": 0},
            # {"name": "best actor",
            #  "medium": 1,
            #  "typeof": 1},
            # {"name": "best actress",
            #  "medium": 0,
            #  "typeof": 0},
            # {"name": "best actress",
            #  "medium": 0,
            #  "typeof": 1},
            # {"name": "best actress",
            #  "medium": 1,
            #  "typeof": 0},
            # {"name": "best actress",
            #  "medium": 1,
            #  "typeof": 1},
            # {"name": "best supporting actor|best actor in supporting role",
            #  "medium": 1,
            #  "typeof": 2},
            # {"name": "best supporting actor|best actor in supporting role",
            #  "medium": 0,
            #  "typeof": 2},
            # {"name": "best supporting actress|best actress in supporting role",
            #  "medium": 1,
            #  "typeof": 2},
            # {"name": "best supporting actress|best actress in supporting role",
            #  "medium": 0,
            #  "typeof": 2},

            # ERROR: THESE DONT WORK GREAT, MOVIE TITLES ARE WEIRD
            # {"name": "best film|best drama",
            #  "medium": 0,
            #  "typeof": 0},
            # {"name": "best film|best comedy",
            #  "medium": 0,
            #  "typeof": 1},
            # {"name": "best show|best series|best drama",
            #  "medium": 1,
            #  "typeof": 0},
            # {"name": "best show|best series|best comedy",
            #  "medium": 1,
            #  "typeof": 1},

            # {"name": "best director",
            #  "medium": 0,
            #  "typeof": 2},


        ]



def get_host(df, cutoff=0.70):
    # Works pretty well

    df1 = df[df["text"].str.contains('host')]
    df1_col = df1.apply(func= lambda row: get_chunks(row["text"]), axis=1)

    counts = make_counts(df1_col)

    counts = counts[counts >= max(counts) * cutoff]

    hosts = []
    for candidate in list(counts.index):
        if verify_person(candidate):
            hosts.append(candidate.title())
        if len(hosts) >= 2:
            break


    print(counts)
    print(hosts)

    return hosts


def get_awards(df):

    # df1 = df[df["text"].str.contains('the winner is | goes to | won|the award|went to')]

    # "Goes to" structure:

    df_goes = df[df["text"].str.contains('goes to')]
    df_goes_groups = df_goes["text"].str.extract('([^,]+) for ([^,]+) goes to ([^,]+)')

    candidates = df_goes_groups[~df_goes_groups[1].isnull()][[1]]

    candidates.columns = ["goes"]

    candidates = candidates[candidates["goes"].str.contains('$award|^best')]
    candidates["goes_count"] = candidates["goes"].str.split().apply(len)

    candidates = candidates[candidates["goes_count"] > 3]

    candidates = candidates[candidates["goes_count"] <= 12]

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


def get_winners(df, awards, cutoff=0.20):
    # Works pretty well

    df_base = df[df["text"].str.contains('win|won|goes to')]

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


def get_nominees(df, awards, cutoff=0.05):
    # changed cutoff
    # banderas & others weren't recognized
        # in json, their names were included with their movies and a negative reaction for NOT winning
        # perhaps need to clump actors with movies
        # will need a different approach from how we did winners

    df_base = df[df["text"].str.contains('nominated|nominee|nominees')]

    print(df_base.shape)

    for award in awards:

        df1 = get_award_tweets(df_base, award)
        # print(df1["text"])
        print(df1.shape)
        print("why")

        df1_col = df1.apply(func= lambda row: get_chunks(row["text"]), axis=1)

        counts = make_counts(df1_col)

        # Remove ones that start with best
        counts = counts[~counts.index.str.contains("Best")]

        counts = counts[counts >= max(counts) * cutoff]

        print(counts)
        print("AWARD:", award['name'])
        for candidate in list(counts.index):
            if verify_person(candidate):
                print(f"{candidate} is a nominee")
        break # runs for only one award


def get_presenters(df, award, cutoff=0.50):


    df1 = df[df["text"].str.contains('present')]

    df1 = df1[~df1["text"].str.contains("represent")]

    df1.to_csv("presenters.csv", index=False)

    print(df1.shape)

    df1 = get_award_tweets(df1, award)
    print(df1["text"])
    print(df1.shape)
    print("why")

    df1_col = df1.apply(func= lambda row: get_chunks(row["text"]), axis=1)

    counts = make_counts(df1_col)

    counts = counts[counts >= max(counts) * cutoff]

    print(counts)

def main():


    df = pd.read_json(FILE_NAME, lines=True)

    print(list(df))

    df["text"] = df["text"].str.lower()

    df = df[~df["text"].str.contains("predict")]

    get_awards(df)

    # get_presenters(df, AWARDS[0])

    # get_awards(df)

    # get_host(df)

'''

    "@nbc Heartiest Congratulations to all the Team #OnceUponATimeInHollywood \nfor winning most deservingly 
    the Golden Globe in the Musical/Comedy category  for : \nBest Motion Picture,
    Best Screenplay,Best Actor in a Supporting Role \nThank your #QuentinTarantino\nfor a great presentation"
    
'''

if __name__ == "__main__":
    main()