from nltk import ngrams, FreqDist
import argparse
import json
from tqdm import tqdm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tokenized_corpus', help='Path to tokenized source corpus')
    parser.add_argument('--ngram_frequency_json', help='File path in which to save a json-formatted dictionary'
                                                       'containing ngram frequency')
    parser.add_argument('--min_ngram', default=2)
    parser.add_argument('--max_ngram', default=5)
    args = parser.parse_args()

    ngram_freq_dictionary = {}

    with open(args.tokenized_corpus, 'r') as f:
        for line in tqdm(f.readlines()):
            words = line.split()
            for i in range(args.min_ngram, args.max_ngram + 1):
                ng = ngrams(words, i)
                ngram_freq = FreqDist(ng)
                for key, value in ngram_freq.items():
                    ngram_freq_dictionary.setdefault(i, {})[key] =  ngram_freq_dictionary.get(i, {}).get(key, 0) + value

    with open(args.ngram_frequency_json, 'w') as fjson:
        json.dump(ngram_freq_dictionary, fjson)


if __name__ == '__main__':
    main()