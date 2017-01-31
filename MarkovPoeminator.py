## Backwards Markov chains
from random import choice
from random import shuffle
import codecs
import re 
from collections import defaultdict

class MarkovPoeminator:

    def __init__(self, filenames, split_sentences=True):
        self.sources = filenames
        self.split_sentences = split_sentences
        self.pronunciations = self.generate_pronunciation_lookup()

    def get_corpus(self):
        """Given a list of files, make chains from them."""
        body = ""

        for filename in self.sources:
            text_file = open(filename)
            body = body + text_file.read()
            text_file.close()

        return self.clean_text(body)

    def clean_text(self, body):
        subs = [
            {'old': '\\xe2\\x80\\x99', 'new': '\''},
            {'old': '\\xe2\\x80\\x9d', 'new': ''},
            {'old': '\s|\\xc2\\xa0', 'new': ' '},
            {'old': '\"', 'new': ''},
            {'old': '\\xe2\\x80\\x93', 'new': '--'},
            {'old': '\r\n', 'new': ' '},
            {'old': '\\xe2\\x80\\x9c', 'new': ''}
        ]

        for sub in subs: 
            body = re.sub(sub['old'], sub['new'], body)

        return body

    def get_chains(self, forwards=True):
        chains = {}
        all_text = self.get_corpus()

        def _make_chains(input_text):
            words = input_text.split()
            word_sequence = range(0, len(words) - 2) if forwards else range(1, len(words) - 1)

            for i in word_sequence:
                key = (words[i].strip(), words[i + 1].strip())
                # Get the word after the bigram if we are going forwards
                # Get the word before the bigram if we are going backwards
                value = words[i + 2] if forwards else words[i-1]

                if key not in chains:
                    chains[key] = []

                chains[key].append(value.strip())   

        if self.split_sentences:
            sentences = self.split_by_sentence(all_text)
            for sentence in sentences:
                _make_chains(sentence)

        else:
            _make_chains(all_text)

        return chains

    def split_by_sentence(self, text):
        return [sentence for sentence in re.split('! |; |\? |\. |\\r\\n|\\n|\\r', text)]
 
    def generate_pronunciation_lookup(self):
        cmu_dictionary = open('cmu_pronunciation_dictionary.txt')
        pronunciations = {}
        for line in cmu_dictionary:
            try:
                word, pronunciation = line.split('  ')
            except ValueError:
                continue

            if '(' not in word:  # Filter out duplicate words
                word = word.lower()
                pronunciations[word] = {'all_segments': pronunciation.split(),
                                        'number_syllables': len([n for n in pronunciation if n in ['0', '1', '2']]),
                                        'rhyming_coda': self.get_rhyming_coda(word, pronunciation.split())}

        return pronunciations

    def get_rhyming_coda(self, word, segments):
        try:
            last_vowel = max([i for i, segment in enumerate(segments) \
                              if ('0' in segment or '1' in segment or '2' in segment)])
        except ValueError:
            return

        return ' '.join(segments[last_vowel:])

    def get_bigrams_by_position(self, start_index):
        """Gets sentence-initial or sentence-final bigrams from the corpus.""" 
        corpus = self.get_corpus()
        sentences = self.split_by_sentence(corpus)
        bigrams = []

        for sentence in sentences:
            words = sentence.split()
            if len(words) > 1:
                bigrams.append((words[start_index], words[start_index+1]))

        return bigrams

    def get_rhyming_seed(self, coda):
        sentence_final_bigrams = self.get_bigrams_by_position(start_index=-2)
        rhyming_words = [word for word in self.pronunciations.keys() if self.pronunciations[word]['rhyming_coda'] == coda]
        rhyming_seeds = [(first, second) for first, second in sentence_final_bigrams if second in rhyming_words]

        return choice(rhyming_seeds)

    def get_forwards_line(self, chains):
        seed = choice(self.get_bigrams_by_position(0))
        end_of_line_chars = '!.?;'
        line = [word for word in seed]
        while seed in chains and not any(char for char in end_of_line_chars if char in line[-1]):
            next_word = choice(chains[seed])
            line.append(next_word)
            seed = (seed[1], next_word)

        return line

    def get_backwards_line(self, chains, coda):
        seed = self.get_rhyming_seed(coda)
        line = [word for word in seed]
        while seed in chains and not line[0][0].isupper():
            previous_word = choice(chains[seed])
            line.insert(0, previous_word)
            seed = (previous_word, seed[0])

        return line

    def get_verse(self, number_verses=1):
        text = []
        forwards_chains = self.get_chains(forwards=True)
        backwards_chains = self.get_chains(forwards=False)

        while len(text) <= number_verses/2:
            first_line = self.get_forwards_line(forwards_chains)
            last_word = re.sub(r'\W+', '', first_line[-1])
            try:
                coda = self.pronunciations[last_word.lower()]['rhyming_coda']
            except:
                print 'Failed to find coda:',  coda, '\nTerminating search'
                continue
            rhyming_line = self.get_backwards_line(backwards_chains, coda)
            text.append(' '.join(first_line))
            text.append(' '.join(rhyming_line))

            print ' '.join(first_line)
            print ' '.join(rhyming_line)

        return text


if __name__ == '__main__':
    mg = MarkovPoeminator(['speeches.txt'])
    mg.get_verse()


