import pandas as pd
import argparse

def makeWordDict(n, dictionaryFile):
    words = pd.read_csv(dictionaryFile, names=['word'])
    words['word'] = words.word.str.lower()
    return words.where(words.word.str.len() == n).dropna()

def getBoringScores(words):
    # Split into table of characters
    chars = words.word.str.split('', expand=True).drop(labels=[0, 6], axis=1)
    # Flatten table and count discrete values
    charProbs = chars.stack().value_counts(normalize=True)
    
    boringScore = pd.DataFrame(chars.apply(lambda row: sum([charProbs[c] for c in list(set(row))]), axis=1), columns=['score'])
    return boringScore.join(words), charProbs

def stepWordTable(tbl, include=[], exclude=[], inplace=[], guess=None):
    conds = ~tbl.word.isna()
    
    # Includes
    for c in include:
        conds &= tbl.word.str.contains(c)
    
    # Excludes
    if len(exclude) > 0:
        conds &= ~tbl.word.str.contains(f"[{''.join(exclude)}]")
    
    # In place
    for i,c in enumerate(inplace):
        if c is None:
            continue
        conds &= tbl.word.str[i] == c

    # Drop guess
    if guess is not None:
        conds &= ~tbl.word.str.match(guess)

    return tbl.where(conds).dropna(), (~conds).sum()

def checkWordleGuess(guess, word):
    correct = guess == word
    inWord = list(filter(None, [c if c in word else None for c in guess]))
    notInWord = list(set(guess) - set(inWord))
    inPlace = [c if c == w else None for c,w in zip(guess, word)]
    return (correct, inWord, notInWord, inPlace)

def solveWordle(boringScores, word):
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