from nltk.collocations import BigramCollocationFinder
bigram_measures = nltk.collocations.BigramAssocMeasures()
text = "obama says that obama says that the war is happening"
finder = BigramCollocationFinder.from_words(word_tokenize(text))
finder.nbest(bigram_measures.pmi, 5) # same as finder.items()[0:5]