# Markov Poeminator

The Markov Poeminator uses Markov chains to generate rhyming and haiku poems in the style of some source text using the CMU pronouncing dictionary as a reference. 

Example usage:

Instantiate a Poeminator object and train it with some text:
```poeminator = MarkovPoeminator(['sometext.txt', 'anothertext.txt'])```

Get a haiku with a 5-7-5 syllable sequence:
```poeminator.get_haiku(syllable_counts=[5, 7, 5])```

Get a rhyming poem with 3 pairs of rhyming lines:
```poeminator.get_rhyming_verse(number_verses=3)```

