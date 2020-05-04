import argparse
import spacy
from tqdm import tqdm


def clean_lines(lines, nlp):
    c_lines = []
    for line in nlp.pipe(lines):
        c_lines.append(' '.join([token.lower_ for token in line]))
    return c_lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_corpus', help='Path of the file in disk in which the plaintext corpus is contained')
    parser.add_argument('--spacy_model', help='Name of a Spacy model that matches the language of the corpus to clean')
    parser.add_argument('--clean_corpus', help='Path of the file in disk in which the clean corpus will be stored')
    parser.add_argument('--batch_size', default=200, help='Number of lines contained in a batch')
    args = parser.parse_args()

    nlp = spacy.load(args.spacy_model)

    raw_f = open(args.raw_corpus, 'r')
    with open(args.clean_corpus, 'w') as clean_f:
        lines = []
        for i, line in enumerate(tqdm(raw_f.readlines()), start=1):
            lines.append(line)
            if i % args.batch_size == 0:
                c_lines = clean_lines(lines, nlp)
                clean_f.write(''.join(item for item in c_lines))
                lines = []
        if lines:
            c_lines = clean_lines(lines, nlp)
            clean_f.write(''.join(item for item in c_lines))


if __name__ == '__main__':
    main()