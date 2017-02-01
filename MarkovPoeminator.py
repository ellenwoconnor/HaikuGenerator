from random import choice
from random import shuffle
import re 
from collections import defaultdict

class MarkovPoeminator:

    def __init__(self, filenames, split_sentences=True):
        self.split_sentences = split_sentences
        self.forwards_chains = self.get_chains(filenames, forwards=True)
        self.backwards_chains = self.get_chains(filenames, forwards=False)
        self.pronunciations = self.generate_pronunciation_lookup()

    def get_corpus(self, filenames):
        """Returns a cleaned corpus of text as a single string."""
        body = ""

        for filename in filenames:
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

    def get_chains(self, filenames, forwards=True):
        chains = {}
        all_text = self.get_corpus(filenames)

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
            n_sentences = len(sentences)
            print "Number of sentences to process", n_sentences
            n = 1
            for sentence in sentences:
                _make_chains(sentence)
                print "Progress: ", n, n_sentences
                n += 1

        else:
            _make_chains(all_text)

        return chains

    def split_by_sentence(self, text):
        # NOTE: this is currently stripping off the punctuation
        # Ideally we would keep it and strip it off only for word lookup
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

    def get_rhyming_seed(self, source_word):
        try:
            coda = self.pronunciations[source_word]['rhyming_coda']
        except:
            print 'Failed to find coda:',  source_word
            return
        sentence_final_bigrams = self.get_bigrams_by_position(start_index=-2)
        rhyming_words = [word for word in self.pronunciations.keys() \
                         if self.pronunciations[word]['rhyming_coda'] == coda \
                         and word != source_word]
        rhyming_seeds = [(first, second) for first, second in sentence_final_bigrams if second in rhyming_words]

        return choice(rhyming_seeds)

    def get_forwards_line(self):
        seed = choice(self.get_bigrams_by_position(0))
        end_of_line_chars = '!.?;'
        line = [word for word in seed]
        while seed in self.forwards_chains and not any(char for char in end_of_line_chars if char in line[-1]):
            next_word = choice(self.forwards_chains[seed])
            line.append(next_word)
            seed = (seed[1], next_word)

        return line

    def get_backwards_line(self, rhyming_word):
        seed = self.get_rhyming_seed(rhyming_word)
        if not seed:
            print "Could not find bigram rhyming with", rhyming_word
            return None
        line = [word for word in seed]
        while seed in self.backwards_chains and not line[0][0].isupper():
            previous_word = choice(self.backwards_chains[seed])
            line.insert(0, previous_word)
            seed = (previous_word, seed[0])

        return line

    def get_verse(self, number_verses=3):
        text = []

        while len(text) <= number_verses*2:
            first_line = self.get_forwards_line()

            # Get the last word and try to build a line that rhymes with it
            last_word = re.sub(r'\W+', '', first_line[-1])
            rhyming_line = self.get_backwards_line(rhyming_word=last_word)
            if not rhyming_line:
                continue

            text.append(' '.join(first_line))
            text.append(' '.join(rhyming_line))
            print ' '.join(first_line)
            print ' '.join(rhyming_line)

        return text


if __name__ == '__main__':
    mg = MarkovPoeminator(filenames=['speeches.txt'], split_sentences=True)
