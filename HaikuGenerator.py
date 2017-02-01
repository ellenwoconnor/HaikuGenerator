from random import choice
from random import shuffle
import re 

# Goal: Generate Haiku text with Markov Chains

class HaikuGenerator:
    def __init__(self, filenames):
        self.chains = self.make_chains(filenames)
        self.syllable_lookup = self.generate_syllable_counts()

    def read_files(self, filenames):
        """Given a list of files, make chains from them."""

        body = ""

        for filename in filenames:
            text_file = open(filename)
            body = body + text_file.read()
            text_file.close()

        subs = [
            {'old': '\\xe2\\x80\\x99', 'new': '\''},
            {'old': '\\xe2\\x80\\x9d', 'new': '\"'},
            {'old': '\s|\\xc2\\xa0', 'new': ' '}
        ]

        for sub in subs: 
            body = re.sub(sub['old'], sub['new'], body)

        return body

    def generate_syllable_counts(self):
        cmu_dictionary = open('cmu_pronunciation_dictionary.txt')
        syllable_counts = {}
        for line in cmu_dictionary:
            try:
                word, pronunciation = line.split('  ')
            except ValueError:
                continue

            if '(' not in word:  # Filter out duplicate words
                syllables = [n for n in pronunciation if n in ['0', '1', '2']]
                syllable_counts[word.lower()] = len(syllables)

        return syllable_counts

    def make_chains(self, filenames):
        """Takes filenames as input; returns dictionary of markov chains."""
        corpus = self.read_files(filenames)
        chains = {}
        words = corpus.split()

        for i in range(len(words) - 2):
            key = (words[i], words[i + 1])
            value = words[i + 2]

            if key not in chains:
                chains[key] = []

            chains[key].append(value)

        return chains

    def count_syllables(self, *words):
        syllable_count = 0
        for word in words:
            word_trimmed = re.sub(r'\W+', '', word)
            syllable_count += self.syllable_lookup[word_trimmed.lower()]

        return syllable_count

    def get_seed(self, max_syllables):
        """Select seed at random (constrained to those words appearing at the beginning
         of a sentence, i.e. starting with a capital letter. Example: ["I", "bought"])
         and constrained to word combinations with <= n syllables ."""

        selected_bigram = None
        sentence_initial_bigrams = [bigram for bigram in self.chains.keys() if bigram[0][0].isupper()]

        while not selected_bigram:
            first_word, second_word = choice(sentence_initial_bigrams)
            print "Considering seed: {} {}".format(first_word, second_word)
            try:
                bigram_syllable_count = self.count_syllables(first_word, second_word)
            except KeyError:
                print "Seed words not found"
                continue

            if (bigram_syllable_count < max_syllables and 
                first_word[0].isupper() and
                self.chains[(first_word, second_word)]):
                selected_bigram = (first_word, second_word)
            else:
                print "Seed words did not meet criteria"

        return selected_bigram


    def get_line(self, bigram, syllables_left):
        # Get next words
        shuffle(self.chains[bigram])
        for current_word in self.chains[bigram]:
            try:
                word_syllables = self.count_syllables(current_word)
            except KeyError:
                continue

            syllables_left -= word_syllables

            if syllables_left == 0:
                print "Matched path at", current_word
                return current_word

            if syllables_left < 0:
                return None

            matching_path = self.get_line((bigram[1], current_word), syllables_left)
            if matching_path:
                return current_word + ' ' + matching_path


    def get_haiku(self, syllable_counts):
        original_counts = list(syllable_counts)
        seed = self.get_seed(syllable_counts[0])
        syllable_counts[0] -= self.count_syllables(*seed)
        all_lines = []

        for line_num, syllables in enumerate(syllable_counts):
            line = self.get_line(seed, syllables)

            if not line:
                print "Retrying..."
                return self.get_haiku(original_counts)

            if line_num == 0: 
                line = ' '.join(seed) + ' ' + line

            all_lines.append(line)
            print "Lines so far: ", all_lines

            try:
                seed = (line.split()[-2], line.split()[-1])
            except IndexError:
                print "Search terminated; could not get an appropriate seed"

        return all_lines

if __name__ == '__main__':
    mg = HaikuGenerator(['speeches.txt'])
    mg.get_haiku([5, 7, 5])
