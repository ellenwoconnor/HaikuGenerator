# Goal: Generate Haiku text using backtracking + Markov Chains

# 1. Read in source text + make a dictionary of Markov chains

# 2. Get total syllable count for some list of words from CMUdict 
#     e.g. ["I", "bought"] returns 2 
#     In CMUdict, syllable stress is indicated with an integer on the vowel (e.g. AH1/EH2)
#     so you can infer the number of syllables by looking at the number phones that
#     end in an integer

# 3. Generate text: 

# a. Select seed at random (constrained to those words appearing at the beginning
#     of a sentence, i.e. starting with a capital letter. Example: ["I", "bought"])
#     and constrained to word combinations with <= 5 syllables (for reasons related
#     to the algorithm for get_lines)

# b. get_lines
#     (run 3 times- first line: 5 syllables, second line: 7 syllables,
#     third line: 5 syllables. Each time the function gets called
#     more words are added to the input.)

#     Args:   list of words (default is random seed generated in 3a), 
#             the number of syllables desired 
#     Returns: a list of words (corresponding to the seed words, or else
#             the haiku lines generated so far, if applicable)

#     get syllable count of words

#     if syllable count is exactly 5
#         return words                base case: gives us a full line

#     w_candidates =  chains[w1, w2]

#     if syllable count < 5, add another word and recheck

#         pop a word from w_candidates and append it to words
#         return get_lines(words)     check if syll count is 5 with new word

#     else:
#         return  

#             (= if we have > 5 syllables, go back to the last string and reselect 
#             a new word) 

#             ??? How to make sure we don't keep selecting the same word over and
#             over? (and if we exhaust all possible candidates we go up another node?)
