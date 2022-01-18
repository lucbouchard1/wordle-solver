import pandas as pd
import argparse, re

def makeWordDict(n, dictionaryFile):
    """Create a dictionary of words of length 'n'.
    
    Parameters:
    n              -- length of the dictionary words.
    dictionaryFile -- dictionary file to use.
    """
    words = pd.read_csv(dictionaryFile, names=['word'])
    words['word'] = words.word.str.lower()
    return words[words.word.str.len() == n]

def getBoringScores(words):
    """Compute boring scores for a dictionary of words. All words must be
    the same length.
    
    Parameters:
    words -- pandas dictionary of words.
    """
    # Split into table of characters
    chars = words.word.str.split('', expand=True).drop(labels=[0, 6], axis=1)
    # Flatten table and count discrete values
    charProbs = chars.stack().value_counts(normalize=True)
    
    boringScore = pd.DataFrame(chars.apply(lambda row: sum([charProbs[c] for c in list(set(row))]), axis=1), columns=['score'])
    return boringScore.join(words), charProbs

def stepWordTable(tbl, include=[], exclude=[], inplace=[], guess=None):
    """Filter a word dictionary by the given criteria.
    
    Parameters:
    tbl     -- word dictionary.
    include -- list of characters that must be included in the table words.
    exclude -- list of characters that cannot appear in the table words.
    inplace -- one-for-one list of characters that must appear in a certain place. None
                if it doesn't matter. e.g. [None, 'h', None, None, None] will require an
                'h' char in index 1.
    guess   -- the previous guess, which should be removed from the table.
    """
    eRgx = re.compile(f"[{''.join(exclude)}]") if len(exclude) > 0 else None
    inPRgx = re.compile(''.join(['.' if c is None else c for c in inplace]))

    conds = tbl.word.apply(lambda word: \
            all([c in word for c in include]) and \
            (len(exclude) == 0 or not bool(eRgx.search(word))) and \
            bool(inPRgx.search(word)) and \
            word != guess
        )

    return tbl[conds], (~conds).sum()

def checkWordleGuess(guess, word):
    """Check if a Wordle guess is correct and return character info"""
    correct = guess == word
    inWord = list(filter(None, [c if c in word else None for c in guess]))
    notInWord = list(set(guess) - set(inWord))
    inPlace = [c if c == w else None for c,w in zip(guess, word)]
    return (correct, inWord, notInWord, inPlace)

def solveWordle(boringScores, word):
    """Run the Wordle solver to find a given word.
    
    Parameters:
    boringScores -- table of words and their boring scores.
    word         -- the winning word of the Wordle.
    """
    tbl = boringScores
    log = []
    included = []
    excluded = []
    inPlace = []
    lastIdx = 0
    
    while len(tbl) > 0:
        guess = tbl.nlargest(lastIdx + 1, 'score').iloc[-1].word
        log.append((len(tbl), guess))
        
        success, i, e, inPlace = checkWordleGuess(guess, word)
        if (success):
            return guess, log
        
        included = list(set(i + included))
        excluded = list(set(e + excluded))
        tbl, numDropped = stepWordTable(tbl, included, excluded, inPlace, guess)
        if numDropped == 0:
            lastIdx += 1
        else:
            lastIdx = 0
    
    return None, log

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Wordle solver for a given word.")
    parser.add_argument("dictionary", type=str, help="Dictionary file")
    parser.add_argument("word", type=str, help="Answer for the Wordle.")
    args = parser.parse_args()

    words = makeWordDict(len(args.word), args.dictionary)
    boringScores, _ = getBoringScores(words)
    res = solveWordle(boringScores, args.word)

    if res[0] is not None:
        print(f"Solved the Wordle in {len(res[1])} steps!")
    else:
        print("Failed to solve the Wordle.")
    
    for i, g in enumerate(res[1]):
        print(f"   Guess {i+1}: {g[1]} -- {g[0]} words in dictionary.")