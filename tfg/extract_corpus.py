import argparse
import xml.etree.ElementTree as ET


def parse_elem_plaintext(xml_elem):
    plaintext_chunks = []
    for t in xml_elem.itertext():
        plaintext_chunks.append(t)
    return ''.join(plaintext_chunks)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--xml_corpus', help='Path of the xml file in disk in which the used corpus is contained')
    parser.add_argument('--key_terms', help='Path of the text file containing a list of key terms')
    parser.add_argument('--source_lang', default='en',
                        help='Source language that corresponds with that of the key terms and is included in the used '
                             'xml corpus')
    parser.add_argument('--source_lang_plaintext', help='Path of the plaintext file in disk in which the source language '
                                                        'filtered corpus will be stored')
    parser.add_argument('--target_lang_plaintext', help='Path of the plaintext file in disk in which the target language '
                             'filtered corpus will be stored')
    args = parser.parse_args()

    key_terms_lower = [line.lower() for line in open(args.key_terms, 'r')]
    tree = ET.parse(args.xml_corpus)
    root = tree.getroot()
    total_article_pairs = len(root[1:])
    checked_article_pairs = 0
    source_lang_f = open(args.source_lang_plaintext, 'w')
    target_lang_f = open(args.target_lang_plaintext, 'w')
    print(f'Started extracting from {args.xml_corpus}')
    print(f'Total number of article pairs: {total_article_pairs}')
    print('---------------------------------------------------\n')

    for article_pair in root[1:]:
        source_lang_article = article_pair[0]
        categories = source_lang_article.find('categories').get('name')
        content_plaintext = parse_elem_plaintext(source_lang_article.find('content'))
        # if one of the key terms is included in the categories or the content of the source language article
        if any(word in categories.lower() for word in key_terms_lower) or \
                any(word in content_plaintext.lower() for word in key_terms_lower):
            # store the selected article pair, each article in a different text file corresponding to their language
            source_lang_f.write(content_plaintext)
            target_lang_article = article_pair[1]
            target_content_plaintext = parse_elem_plaintext(target_lang_article.find('content'))
            target_lang_f.write(target_content_plaintext)
        # increase number of checked article pairs and print an update every batch
        checked_article_pairs += 1
        if checked_article_pairs % 1000 == 0:
            print(f'{checked_article_pairs}/{total_article_pairs} checked article pairs')


if __name__ == '__main__':
    main()
