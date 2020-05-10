import pandas as pd
import xml.etree.ElementTree as ET
import os
import argparse
from tqdm import tqdm
import pickle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus_path', help='Path of the xml corpus directory in disk in which the used corpus is contained')
    parser.add_argument('--lang', default='en',
                        help='Language of the used MESH thesaurus')
    parser.add_argument('--parsed_mesh', help='Path to the pickle file containing the parsed MESH thesaurus')
    parser.add_argument('--classified_docs', help='csv file that will contain the classified documents for evaluation')
    args = parser.parse_args()

    hierarchical_dict, descriptor_list = pickle.load(open(args.parsed_mesh, 'rb'))
    df = pd.DataFrame()

    for rootdir, dirs, files in os.walk(args.corpus_path):
        for path in tqdm(files):
            with open(os.path.join(rootdir, path), 'r') as f:
                tree = ET.parse(os.path.join(rootdir, path))
                root = tree.getroot()
                metadata = root.find('record')[1]
                source_lang_title = metadata.find('.//{http://purl.org/dc/elements/1.1/}title[@{http://www.w3.org/XML/1998/namespace}lang="en"]')
                target_lang_title = metadata.find('.//{http://purl.org/dc/elements/1.1/}title[@{http://www.w3.org/XML/1998/namespace}lang="es"]')
                source_lang_description = metadata.find('.//{http://purl.org/dc/elements/1.1/}description[@{http://www.w3.org/XML/1998/namespace}lang="en"]')
                target_lang_description = metadata.find('.//{http://purl.org/dc/elements/1.1/}description[@{http://www.w3.org/XML/1998/namespace}lang="es"]')
                row = {'id': path.split('/')[-1], 'descriptors':{}}
                if source_lang_title is not None:
                    for descriptor in descriptor_list:
                        for concept in descriptor['concepts']:
                            for term in concept['terms']:
                                if term['name'].lower() in source_lang_title.text.lower():
                                    row['descriptors'][descriptor['name']] = descriptor
                if source_lang_description is not None:
                    for descriptor in descriptor_list:
                        for concept in descriptor['concepts']:
                            for term in concept['terms']:
                                if term['name'].lower() in source_lang_description.text.lower():
                                    row['descriptors'][descriptor['name']] = descriptor
                df.append(row)

    writer = pd.ExcelWriter(args.classified_docs, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=f'MESH over {args.corpus_path.split("/")[-1]} annotation')
    writer.save()


if __name__ == '__main__':
    main()