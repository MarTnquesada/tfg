import argparse
from tqdm import tqdm
from nltk.lm import MLE
from nltk.lm.preprocessing import padded_everygram_pipeline
import pickle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tokenized_corpus', help='Path to tokenized source corpus')
    parser.add_argument('--model', help='File path in which to save the language model')
    parser.add_argument('--n', default=2, type=int)
    args = parser.parse_args()

    # create model
    model = MLE(args.n)

    # train model
    with open(args.tokenized_corpus, 'r') as f:
        print("Generating iterator from full corpus text")
        train_data, vocab = padded_everygram_pipeline(args.n, [line.split() for line in tqdm(f.readlines())])
        print("Training model")
        model.fit(tqdm(train_data), vocab)
        print(model.vocab)
        print(model.counts)

        # store model
        print("Storing model locally...")
        model_file = open(args.model, 'wb')
        pickle.dump(model, model_file)


if __name__ == '__main__':
    main()