import pandas as pd
import xml.etree.ElementTree as ET
import os
import spacy
import argparse
from tqdm import tqdm
import pickle
from tfg.utilities import parse_mesh, contains_word


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus_path', help='Path of the xml corpus directory in disk in which the used corpus is contained')
    parser.add_argument('--lang', default='en',
                        help='Language of the used MESH thesaurus')
    parser.add_argument('--mesh', help='Path to the file containing the parsed MESH thesaurus')
    parser.add_argument('--parsed_mesh', action='store_true',
                        help='True if the MESH thesaurus has been already parsed and should be loaded from a pickle file')
    parser.add_argument('--classified_docs', help='xlsx file that will contain the classified documents for evaluation')
    parser.add_argument('--spacy_model', help='Name of a Spacy model that matches the language of the corpus to clean')
    parser.add_argument('--limit', default=5000, type=int, help='Number of documents to classify in natural order')
    args = parser.parse_args()

    if args.parsed_mesh:
        hierarchical_dict, descriptor_list = pickle.load(open(args.mesh, 'rb'))
    else:
        tree = ET.parse(args.mesh)
        hierarchical_dict, descriptor_list = parse_mesh(tree)
    rows = []
    nlp = spacy.load(args.spacy_model)

    for rootdir, dirs, files in os.walk(args.corpus_path):
        for i, path in enumerate(tqdm(files[:args.limit])):
            with open(os.path.join(rootdir, path), 'r') as f:
                tree = ET.parse(os.path.join(rootdir, path))
                root = tree.getroot()
                metadata = root.find('record')[1]
                source_lang_title = metadata.find('.//{http://purl.org/dc/elements/1.1/}title[@{http://www.w3.org/XML/1998/namespace}lang="' + args.lang + '"]')
                source_lang_description = metadata.find('.//{http://purl.org/dc/elements/1.1/}description[@{http://www.w3.org/XML/1998/namespace}lang="' + args.lang + '"]')
                row = {'id': path.split('/')[-1], 'descriptors':[]}
                full_text = ''
                if source_lang_title is not None:
                    full_text += f'{source_lang_title.text} \n'
                if source_lang_description is not None:
                    full_text += f'{source_lang_description.text}'
                clean_full_text = ' '.join([token.lower_ for token in nlp(full_text)])
                if clean_full_text:
                    for descriptor in descriptor_list:
                        for concept in descriptor['concepts']:
                            for term in concept['terms']:
                                if contains_word(clean_full_text, term['name'].lower()):
                                    row['descriptors'].append(
                                        {'name': descriptor['name'], 'tree_numbers': descriptor['tree_numbers'],
                                         'ui': descriptor['ui']})
                                    break
                rows.append(row)

    df = pd.DataFrame(rows)
    writer = pd.ExcelWriter(args.classified_docs, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=f'MESH over ibecs annotation')
    writer.save()


if __name__ == '__main__':
    main()