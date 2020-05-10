import pandas as pd
import xml.etree.ElementTree as ET
import os
import argparse
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rootdir', help='Path of the xml corpus directory in disk in which the used corpus is contained')
    parser.add_argument('--lang', default='en',
                        help='Language of the used MESH thesaurus')
    parser.add_argument('--classified_docs', help='csv file that will contain the classified documents for evaluation')
    args = parser.parse_args()


    for rootdir, dirs, files in os.walk(args.rootdir):
        for i, path in enumerate(tqdm(files)):
            with open(os.path.join(rootdir, path), 'r') as f:
                tree = ET.parse(os.path.join(rootdir, path))
                root = tree.getroot()
                metadata = root.find('record')[1]
                source_lang_title = metadata.find('.//{http://purl.org/dc/elements/1.1/}title[@{http://www.w3.org/XML/1998/namespace}lang="en"]')
                target_lang_title = metadata.find('.//{http://purl.org/dc/elements/1.1/}title[@{http://www.w3.org/XML/1998/namespace}lang="es"]')
                source_lang_description = metadata.find('.//{http://purl.org/dc/elements/1.1/}description[@{http://www.w3.org/XML/1998/namespace}lang="en"]')
                target_lang_description = metadata.find('.//{http://purl.org/dc/elements/1.1/}description[@{http://www.w3.org/XML/1998/namespace}lang="es"]')
            # odd documents are considered for the source language (en), and even docs for the target language (es)
            if args.lang == 'es' and i % 2 == 0:
                if source_lang_title is not None:
                    source_lang_f.write(source_lang_title.text + '\n')
                if source_lang_description is not None:
                    source_lang_f.write(source_lang_description.text + '\n')
            elif args.lang == 'en' and i % 2 != 0:



if __name__ == '__main__':
    main()