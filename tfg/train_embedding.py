from gensim.models import FastText
import fasttext as fasttext
from gensim.test.utils import datapath
import argparse


def train_facebook_fasttext_embedding(data, emb_nm, minn=3, maxn=6, dim=100, epoch=5, lr=0.05, thread=4, max_vocab_size=200000):
    # unsupervised training with custom parameters
    emb = fasttext.train_unsupervised(data, minn=minn, maxn=maxn, dim=dim, epoch=epoch, lr=lr, thread=thread)

    # we only select the vocab_size most frequent terms
    # TODO this should probably be emb.words = [:max_vocab_size]. Use Gensim to change format and reduce size
    # TODO ref: https://medium.com/@vasnetsov93/shrinking-fasttext-embeddings-so-that-it-fits-google-colab-cd59ab75959e
    # del emb.words[max_vocab_size:]

    # saving trained model
    emb.save_model(emb_nm)


def train_gensim_fasttex_embedding(corpus_relative_path, emb_nm, minn=3, maxn=6, dim=100, epoch=5, lr=0.05, thread=4,
                            max_vocab_size=200000):
    corpus_absolute_path = datapath(corpus_relative_path)
    # unsupervised training with custom parameters
    model = FastText(size=4, window=3, min_count=1)
    model.build_vocab(corpus_file=corpus_absolute_path)

    # we only select the vocab_size most frequent terms
    # TODO this should probably be emb.words = [:max_vocab_size]. Use Gensim to change format and reduce size
    # TODO ref: https://medium.com/@vasnetsov93/shrinking-fasttext-embeddings-so-that-it-fits-google-colab-cd59ab75959e
    # del emb.words[max_vocab_size:]

    # saving trained model
    model.save_model(emb_nm)


def main():
    parser = argparse.ArgumentParser(description='Creates 2 word embeddings from 2 distinct datasets')
    parser.add_argument('--thread', default=4, type=int, help='number of threads that will be launched')
    parser.add_argument('--src_data', help='name of the dataset used for the source language')
    parser.add_argument('--src_emb', default="src_emb",
                        help='name of the word embedding created in the source language')
    parser.add_argument('--max_vocab_size', default=200000,
                        help='maximum size of the vocabulary represented in the word embedding')
    args = parser.parse_args()

    train_facebook_fasttext_embedding(args.src_data, args.src_emb,
                         thread=args.thread, minn=3, maxn=6, dim=300, epoch=5, lr=0.05,
                         max_vocab_size=args.max_vocab_size)
    print("Showing a sample of embedding words ordered by frequency")
    emb = fasttext.load_model(args.src_emb)
    print(emb.get_words())
    print("Showing nearest neighbours of top 3 words")
    for n in range(0, 3):
        print(str(n) + ".Nearest neighbours of " + str(emb.get_words()[0]) + ":\n" +
                    str(emb.get_nearest_neighbors(emb.get_words()[n])))


if __name__ == '__main__':
    main()
