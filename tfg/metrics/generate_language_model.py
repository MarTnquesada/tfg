from nltk.corpus import reuters
from nltk import ngrams
from collections import Counter, defaultdict
import argparse
from tqdm import tqdm
from nltk.lm import MLE
from nltk.lm.preprocessing import padded_everygram_pipeline
import pickle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tokenized_corpus', help='Path to tokenized source corpus')
    parser.add_argument('--model', help='File path in which to save the language model')
    parser.add_argument('--n', default=2)
    args = parser.parse_args()

    # create model
    model = MLE(args.n)

    # train model
    with open(args.tokenized_corpus, 'r') as f:
            train_data, vocab = padded_everygram_pipeline(args.n, [line.split() for line in tqdm(f.readlines())])
            for t in train_data:
                print(list(t))
            model.fit(train_data, vocab)

    """
    # obtain frequencies
    with open(args.tokenized_corpus, 'r') as f:
        for line in tqdm(f.readlines()):
            words = line.split()
            for i in range(args.min_ngram, args.max_ngram + 1):
                ng = ngrams(words, i)
                ngram_freq = FreqDist(ng)
                for key, value in ngram_freq.items():
                    ngram_freq_dictionary[' '.join(key)] = ngram_freq_dictionary.get(' '.join(key), 0) + value

    with open(args.ngram_frequency_json, 'w') as fjson:
        json.dump(ngram_freq_dictionary, fjson)
    """


if __name__ == '__main__':
    main()