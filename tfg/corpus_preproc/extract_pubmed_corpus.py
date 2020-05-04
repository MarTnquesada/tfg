import argparse
import xml.etree.ElementTree as ET
import os
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rootdir', help='Path of the xml corpus directory in disk in which the used corpus is contained')
    parser.add_argument('--source_lang', default='en',
                        help='Source language that corresponds with that of the key terms and is included in the used '
                             'xml corpus')
    parser.add_argument('--target_lang', default='es',
                        help='Target language that corresponds with that of the key terms and is included in the used '
                             'xml corpus')
    parser.add_argument('--source_lang_plaintext', help='Path of the plaintext file in disk in which the source language '
                                                        'filtered corpus will be stored')
    parser.add_argument('--target_lang_plaintext', help='Path of the plaintext file in disk in which the target language '
                             'filtered corpus will be stored')
    args = parser.parse_args()

    total_article_pairs = len(os.listdir(args.rootdir))
    source_lang_f = open(args.source_lang_plaintext, 'a+')
    target_lang_f = open(args.target_lang_plaintext, 'a+')
    print(f'Started extracting from {args.rootdir}')
    print(f'Total number of article pairs: {total_article_pairs}')
    print('---------------------------------------------------')

    for rootdir, dirs, files in os.walk(args.rootdir):
        for i, path in enumerate(tqdm(files)):
            with open(os.path.join(rootdir, path), 'r') as f:
                tree = ET.parse(os.path.join(rootdir, path))
                root = tree.getroot()
                metadata = root.find('record')[1]
                creator = metadata.find('{http://purl.org/dc/elements/1.1/}creator')
                title = metadata.find('{http://purl.org/dc/elements/1.1/}title')
                description = metadata.find('{http://purl.org/dc/elements/1.1/}description')
                source_lang_title = metadata.find('.//{http://purl.org/dc/elements/1.1/}title[@{http://www.w3.org/XML/1998/namespace}lang="en"]')
                target_lang_title = metadata.find('.//{http://purl.org/dc/elements/1.1/}title[@{http://www.w3.org/XML/1998/namespace}lang="es"]')
                source_lang_description = metadata.find('.//{http://purl.org/dc/elements/1.1/}description[@{http://www.w3.org/XML/1998/namespace}lang="en"]')
                target_lang_description = metadata.find('.//{http://purl.org/dc/elements/1.1/}description[@{http://www.w3.org/XML/1998/namespace}lang="es"]')
            if i % 2 == 0:
                if source_lang_title is not None and source_lang_title.text is not None:
                    source_lang_f.write(source_lang_title.text.replace('[', '').replace(']', '') + '\n')
                if source_lang_description is not None and source_lang_description.text is not None:
                    source_lang_f.write(source_lang_description.text + '\n')
            else:
                if target_lang_title is not None and target_lang_title.text is not None:
                    target_lang_f.write(target_lang_title.text.replace('[', '').replace(']', '')+ '\n')
                if target_lang_description is not None and target_lang_description.text is not None:
                    target_lang_f.write(target_lang_description.text + '\n')


if __name__ == '__main__':
    main()
