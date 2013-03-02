#!/usr/bin/env python

# This is the Reddit Analysis project.
#
# Copyright 2013 Randal S. Olson.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/.

import csv
import praw
import string
import sys
from collections import defaultdict

popularWords = defaultdict(int)
commonWords = set()

# punctuation to strip from words
punctuation = " " + string.punctuation + "\n"

# load a list of common words to ignore
with open("common-words.csv", "r") as commonWordsFile:
    for commonWordFileLine in csv.reader(commonWordsFile):
        for commonWord in commonWordFileLine:
            commonWords.add(commonWord.strip(punctuation).lower())

with open("/usr/share/dict/words", "r") as dictionaryFile:
    for dictionaryWord in dictionaryFile:
        commonWords.add(dictionaryWord.strip(punctuation).lower())

# put words here that you don't want to include in the word cloud
excludedWords = ["http://", "r/", "https://", "gt", "...", "deleted",
                 "k/year", "--", "/", "u/", ")x", "amp;c"]


def parseText(text):
    """Parse the passed in text and add words that are not common."""
    for word in text.split():  # Split on all whitespace
        word = word.strip(punctuation).lower()
        if word not in commonWords:  # Guaranteed not to be ''
            popularWords[word] += 1


def processRedditor(r, user):
    """Parse all comments, title text, and selftext for a given user."""
    sys.stderr.write('Analyzing /u/{0}\n'.format(user))
    
    entryCount = 0
    dotCount = 0
    
    for entry in user.get_overview(limit=None):

    	entryCount += 1
		
		if entryCount % 100 == 0:
			# provide a visible status indicator
			sys.stderr.write('.')
			sys.stderr.flush()
			dotCount += 1
        
		if dotCount >= 50:
			sys.stderr.write('\n')
			dotCount = 0

		# comments
		if type(entry) is praw.objects.Comment:
			parseText(entry.body)
        
        # submissions
		if type(entry) is praw.objects.Submission:
			# parse the title of the submission
			parseText(entry.title)

			# parse the selftext of the submission (if applicable)
			if entry.is_self:
				parseText(entry.selftext)


def main():
    try:
        username, userToAnalyze = sys.argv[1:]
    except:
        print 'Usage: subreddit_word_freqs.py username user-to-analyze'
        return 1

    # open connection to Reddit
    r = praw.Reddit(user_agent="bot by /u/{0}".format(username))
    processRedditor(r, r.get_redditor(userToAnalyze))

    # build a string containing all the words for the word cloud software
    output = ""
    
    # open output file to store the output string
    outFile = open("user " + str(userToAnalyze) + ".csv", "w")

    for word in sorted(popularWords.keys()):

        # tweak this number depending on the subreddit
        # some subreddits end up having TONS of words and it seems to overflow
        # the Python string buffer
        if popularWords[word] > 2:
            pri = True

            # do not print a word if it is in the excluded word list
            for ew in excludedWords:
                if ew in word:
                    pri = False
                    break
               
            # don't print the word if it's just a number
            try:
                int(word)
                pri = False
            except:
                pass

            # add as many copies of the word as it was mentioned in the
            # subreddit
            if pri:
            	txt = ((word + " ") * popularWords[word])
            	txt = txt.encode("UTF-8").strip(" ")
            	txt += " "
                output += txt
                outFile.write(txt)

    outFile.close()

    # print the series of words for the word cloud software
    # place this text into wordle.net
    print output


if __name__ == '__main__':
    sys.exit(main())
