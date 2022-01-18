# Wordle Solver

A program that solves a [Wordle](https://www.powerlanguage.co.uk/wordle/) using a simple algorithm. To see its performance solving for a given word, simply run:

```
python wordle.py dictionary <word>
```

For example:

```
(base) luc@lb-lap:~/Documents/wordle$ python wordle.py dictionary hello
Solved the Wordle in 5 steps!
   Guess 1: arose -- 10230 words in dictionary.
   Guess 2: enoil -- 359 words in dictionary.
   Guess 3: luteo -- 87 words in dictionary.
   Guess 4: cello -- 3 words in dictionary.
   Guess 5: hello -- 1 words in dictionary.
```

## Solver Algorithm

To solve the Wordle, the program computes a character frequency distribution from the word dictionary. It then computes the "boring score" for each word in the dictionary--the sum of frequencies for each character in the word, ignoring repeated characters (i.e. how boring the characters in the word are).

With the boring scores computed, the program selects the most boring word, makes the guess, filters the dictionary based on the character information Wordle returns, then repeats.

This idea behind this approach is maximizing the information gained in each iteration. By using words with characters that appear often, we're more likely to end up finding characters that are in the target word.