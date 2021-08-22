import nltk
import re
import sys

NP_COMP = ['N', 'NP']
TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to" | "until"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP S | VP S | NP VP | Conj S | VP NP | NP
NP -> N | Det NP | Adj NP | P NP | NP Adv 
VP -> V | V NP | Adv VP | VP Adv 
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    list_of_words = nltk.word_tokenize(sentence)
    list_of_words_lower = [word.lower() for word in list_of_words if re.match(r'[^\W\d]*$', word)]
    print(list_of_words_lower)
    return list_of_words_lower


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    return traverse_tree(tree, [])


def traverse_tree(tree, NP_chunks):
    for subtree in tree:
        if isinstance(subtree, nltk.tree.Tree):
            if check_child_leaves(subtree):
                traverse_tree(subtree, NP_chunks)                
            elif subtree.label() in NP_COMP:
                NP_chunks.append(subtree)
    return NP_chunks
    
           
def check_child_leaves(tree):
    for subtree in tree:
        if not isinstance(subtree, str) and subtree.label() in ['NP', 'S']:
            return True
        
    return False

if __name__ == "__main__":
    main()
