import argparse
import spacy


def clean_text(text, lang):
    nlp = spacy.load(f'{lang}_core_web_sm')
    doc = nlp(text)
    lower_tokenized_text = ' '.join([token.lower_ for token in doc])
    return lower_tokenized_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_corpus', help='Path of the file in disk in which the plaintext corpus is contained')
    parser.add_argument('--lang', help='Corpus language')
    parser.add_argument('--clean_corpus', help='Path of the file in disk in which the clean corpus will be stored')
    args = parser.parse_args()

    with open(args.raw_corpus, 'r') as raw_f:
        clean_corpus = clean_text(raw_f.read())
        with open(args.clean_corpus, 'w') as clean_f:
            clean_f.write(clean_corpus)


if __name__ == '__main__':
    main()