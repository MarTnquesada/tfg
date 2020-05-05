from nltk.collocations import BigramCollocationFinder, BigramAssocMeasur
from nltk import bigrams


bigram_measures = BigramAssocMeasures()
text = "obama says that obama says that the war is happening"
finder = BigramCollocationFinder.from_words(word_tokenize(text))
finder.nbest(bigram_measures.pmi, 5) # same as finder.items()[0:5]