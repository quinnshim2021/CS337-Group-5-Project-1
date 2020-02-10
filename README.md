# CS337-Group-5-Project-1


Code can also be found in github repo: https://github.com/quinnshim2021/CS337-Group-5-Project-1

## Requirements

Requirements are specified in the requirements.txt file. Note that we use spacy's en_core_web_sm model, so it might be necessary to install it via 
`python -m spacy download en_core_web_sm`

## How to Run

The main code files for this program are `autograder.py`, `gg_api.py`, and `helper_functions.py`.

To run this program, you just need to run `python autograder.py XXXX` where XXXX is the year of choice. We assume the files "ggXXXX.json" and "ggXXXXanswers.json" are in the same directory as this project. We did not include the 2013 and 2015 files given that they were quite large.

### Output of Program

Running `python autograder.py XXXX` will output to the terminal:
- All of the "regular" goals in human-readable format
- All of the additional goals in human-readable format
- The score on the autograder
- The runtime of the program

Additionally, a file called "results_XXXX.json" will be created with a json structure that will have all of the information described above (Except for the autograder score and runtime of program).


## Additional Goals

The additional goals that we covered are:
- Best dressed
- Best speech
- Additional user-given awards (e.g. "best reaction face of the night" to "jessica chastain" in 2015)
- Host sentiment analysis statistics

The host sentiment analysis will tell you (for each host):
- Mean sentiment (ranges from -1 to 1, with -1 being the most negative and 1 being the most positive)
- Standard deviation sentiment
- Number of tweets about the host
- Fraction of tweets that are very positive, somewhat positive, neutral, somewhat negative, and very negative. The breakdown of these categories are based on the sentiment of each tweet, with the following discretization:

```
    ranges = {"Very Positive": (0.50, 1.00),
              "Somewhat Positive": (0.10, 0.50),
              "Neutral": (-0.10,0.10),
              "Somewhat Negative": (-0.50, -0.10),
              "Very Negative": (-1.00, -0.50)
              }
```

## Randomness Caveat

Results for this program are a bit non-deterministic due to some randomness. If there were a large enough number of tweets, we did random sampling to ensure that runtime was stable. Though this generally gave us good results, there are instances were the random sampling might yield lower performance in terms of completeness and spelling.