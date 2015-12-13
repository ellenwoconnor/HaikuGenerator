# Goal: Generate Haiku text with Markov Chains

# 1. Read in source text + make a dictionary of Markov chains
def read_files(filenames):
    """Given a list of files, make chains from them."""

    body = ""

    for filename in filenames:
        text_file = open(filename)
        body = body + text_file.read()
        text_file.close()

    return body

def make_chains(text):
    """Takes input text as string; returns dictionary of markov chains."""

    chains = {}

    words = corpus.split()

    for i in range(len(words) - 2):
        key = (words[i], words[i + 1])
        value = words[i + 2]

        if key not in chains:
            chains[key] = []

        chains[key].append(value)

    return chains

# Helper: get syll count 
def count_syll(words):
    """Get total syllable count for some list of words from CMUdict 
    e.g. ["I", "bought"] returns 2 
    In CMUdict, syllable stress is indicated with an integer on the vowel (e.g. AH1/EH2)
    so you can infer the number of syllables by looking at the number phones that
    end in an integer.

    TODO"""

# 3. Generate text: 

def get_seed(chains):
    """Select seed at random (constrained to those words appearing at the beginning
     of a sentence, i.e. starting with a capital letter. Example: ["I", "bought"])
     and constrained to word combinations with <= 5 syllables ."""


def get_lines(words, chains, target_syll):
    """(run 3 times- first line: 5 syllables, second line: 7 syllables,
    third line: 5 syllables. Each time the function gets called
    more words are added to the input.)

    Args:   list of words (default is random seed generated in 3a), 
            the number of syllables desired 
    Returns: a list of words (corresponding to the seed words, or else
            the haiku lines generated so far, if applicable)"""

    curr_syll = count_syll(words)
    key = 
    
    while curr_syll < target_syll:

        # So long as we haven't already popped off all of the candidate words (?) 
        if len(chains[(words[-2], words[-1])]) > 0:     
            # pop a random word from chains[(words[-2], words[-1])] & append it to words
            curr_syll = count_syll(words)
        else:
            # remove the last word from words, chains
            # update syllable count

    if curr_syll == target_syll:  # base case: we have a complete line 
        return words  

    elif curr_syll > target_syll:
        # remove the last word from words
        return get_lines(words, chains) 
