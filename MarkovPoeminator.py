from random import choice
from random import shuffle
import re


class MarkovPoeminator:

    def __init__(self, filenames, observe_sentence_boundaries=True):
        self.corpus = self.get_corpus(filenames)
        self.observe_sentence_boundaries = observe_sentence_boundaries
        self.forwards_chains = self.get_chains(filenames, forwards=True)
        self.backwards_chains = self.get_chains(filenames, forwards=False)
        self.pronunciations = self.generate_pronunciation_lookup()

    def get_corpus(self, filenames):
        """Returns a cleaned corpus of text as a single string."""
        body = ''

        for filename in filenames:
            text_file = open(filename)
            body = body + text_file.read()
            text_file.close()

        return self.clean_text(body)

    def clean_text(self, body):
        # Inconsistent punctuation encoding causes problems with chains
        subs = [
            {'old': '\\xe2\\x80\\x99', 'new': '\''},
            {'old': '\\xe2\\x80\\x9d', 'new': ''},
            {'old': '\s|\\xc2\\xa0', 'new': ' '},
            {'old': '\"', 'new': ''},
            {'old': '\\xe2\\x80\\x93', 'new': '--'},
            {'old': '\r\n', 'new': ' '},
            {'old': '\\xe2\\x80\\x9c', 'new': ''},
            {'old': '_', 'new': ''}
        ]

        for sub in subs: 
            body = re.sub(sub['old'], sub['new'], body)

        return body

    def get_chains(self, filenames, forwards=True):
        """Gets a body of text and generates Markov chains from it. 
            filenames:  a list of filenames containing text to train the model
            forwards:   tracks whether the chains are generated by tracking the word 
                        before the bigram seed or the word after it.
        Backwards chains are useful if the last word of the sequence needs to have
        a rare property (in this case, a specific rhyming coda)"""

        chains = {}

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

        # Causes Markov text to terminate at sentence boundaries
        # I'm unclear on whether it's better or worse than looking for 
        # e.g. uppercase letters/punctuation. 
        if self.observe_sentence_boundaries:
            sentences = self.split_by_sentence(self.corpus)
            n_sentences = len(sentences)
            print "Number of sentences to process", n_sentences
            n = 1
            for sentence in sentences:
                _make_chains(sentence)
                print "Progress: ", n, n_sentences
                n += 1

        else:
            _make_chains(self.corpus)

        return chains

    def split_by_sentence(self, text):
        # NOTE: re.split is currently stripping off the punctuation 
        # Ideally we would keep it and strip it off only for word lookup 
        return [sentence + '.' for sentence in re.split('! |; |\? |\. |\\r\\n|\\n|\\r', text)]
 
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
                                        'rhyming_coda': self.get_rhyming_coda(pronunciation.split())}

        return pronunciations

    def count_syllables(self, *words):
        syllable_count = 0
        for word in words:
            word_trimmed = re.sub(r'\W+', '', word)
            print word_trimmed
            syllable_count += self.pronunciations[word_trimmed.lower()]['number_syllables']

        return syllable_count

    def get_rhyming_coda(self, segments, rhyme_syllable_length=2):
        """Given a list of segments and a target rhyme length (default 2 syllables),
        returns a rhyming coda
                 [HH, AE1, P, IY0] -> 'AE1 P IY0' 
                 [HH, AE1, P, IY0, N, AH0, S] -> 'IY0 N AH0 S'
                 [HH, AA1, R, D] -> 'AA1 R D'
        """
        vowel_indices = [i for i, segment in enumerate(segments) \
                         if ('0' in segment or '1' in segment or '2' in segment)]
        number_vowels = len(vowel_indices)

        if vowel_indices:
            starting_rhyme_index = vowel_indices[-(rhyme_syllable_length)] \
                                   if number_vowels >= rhyme_syllable_length \
                                   else vowel_indices[-(number_vowels)]
            rhyme = segments[starting_rhyme_index:]
            return ' '.join(rhyme)

    def get_bigrams_by_position(self, start_index):
        """Gets sentence-initial or sentence-final bigrams from the corpus.""" 
        sentences = self.split_by_sentence(self.corpus)
        bigrams = []

        for sentence in sentences:
            words = sentence.split()
            if len(words) > 1:
                bigrams.append((words[start_index], words[start_index+1]))

        return bigrams

    def get_rhyming_seed(self, source_word):
        """Randomly select sentence-final seed where word 2 rhymes with some source word."""
        try:
            coda = self.pronunciations[source_word]['rhyming_coda']
        except:
            return None
        sentence_final_bigrams = self.get_bigrams_by_position(start_index=-2)
        # This is clunky; figure out a way to stop appending '.' to stuff in so many places
        # but still retain the sentence boundaries... 
        rhyming_words = set([word + '.' for word in self.pronunciations.keys() \
                             if self.pronunciations[word]['rhyming_coda'] == coda \
                             and word != source_word])
        rhyming_seeds = [(first, second) for first, second in sentence_final_bigrams if second in rhyming_words]
        return choice(rhyming_seeds) if rhyming_seeds else None

    def get_seed_by_syllables(self, syllables, exact=False):
        """Randomly select sentence-initial seed with <= n syllables if nonexact;
        exactly n syllables if exact."""
        # TODO There are some redundancies here... look into (first word, second word)
        # and return position; rename max_syllables
        print "Looking for seed with {} {} syllables".format('exactly' if exact else 'less than', syllables)
        selected_bigram = None
        sentence_initial_bigrams = self.get_bigrams_by_position(0)

        while not selected_bigram:
            candidate_bigram = choice(sentence_initial_bigrams)
            print "Considering seed: {}".format(' '.join(candidate_bigram))
            try:
                bigram_syllable_count = self.count_syllables(*candidate_bigram)
            except KeyError:
                print "Seed words not found"
                continue

            correct_syllable_count = (bigram_syllable_count == syllables) if exact \
                                     else (bigram_syllable_count < syllables)
            if correct_syllable_count and self.forwards_chains.get(candidate_bigram) is not None:
                selected_bigram = candidate_bigram
            else:
                print "Seed words did not meet criteria"

        return selected_bigram

    def get_forwards_line(self):
        seed = choice(self.get_bigrams_by_position(0))
        line = [word for word in seed]
        while seed in self.forwards_chains and not (line[-1][-1] == '.'):
            next_word = choice(self.forwards_chains[seed])
            line.append(next_word)
            seed = (seed[1], next_word)

        return line

    def get_backwards_line(self, rhyming_word):
        seed = self.get_rhyming_seed(rhyming_word)
        if not seed:
            return None
        line = [word for word in seed]
        while seed in self.backwards_chains and not line[0][0].isupper():
            previous_word = choice(self.backwards_chains[seed])
            line.insert(0, previous_word)
            seed = (previous_word, seed[0])

        return line

    def get_rhyming_verse(self, number_verses=2):
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

    def get_haiku_line(self, bigram, syllables_left):
        # If the seed is sentence-final and we are observing sentence boundaries
        # the path will terminate here... need to explore consequences of this
        if bigram not in self.forwards_chains:
            return None

        shuffle(self.forwards_chains[bigram])

        for current_word in self.forwards_chains[bigram]:
            try:
                word_syllables = self.count_syllables(current_word)
            except KeyError:
                continue

            if (syllables_left - word_syllables) == 0:
                return current_word

            if (syllables_left - word_syllables) < 0:
                return None

            matching_path = self.get_haiku_line((bigram[1], current_word),
                                                (syllables_left - word_syllables))
            if matching_path:
                return current_word + ' ' + matching_path

    def get_haiku(self, syllable_counts):
        original_counts = list(syllable_counts)
        seed = self.get_seed_by_syllables(syllable_counts[0])
        syllable_counts[0] -= self.count_syllables(*seed)
        all_lines = []

        for line_num, syllables in enumerate(syllable_counts):
            line = self.get_haiku_line(seed, syllables)

            if not line:
                print "Retrying..."
                return self.get_haiku(original_counts)

            if line_num == 0: 
                line = ' '.join(seed) + ' ' + line

            all_lines.append(line)

            try:
                seed = (line.split()[-2], line.split()[-1])
            except IndexError:
                print "Search terminated; could not get an appropriate seed"

        return all_lines


if __name__ == '__main__':
    poeminator = MarkovPoeminator(filenames=['speeches.txt', '1984.txt'], observe_sentence_boundaries=True)
    print poeminator.get_rhyming_verse(2)
    print poeminator.get_haiku([5, 7, 5])
