import argparse
import xml.etree.ElementTree as ET
from tfg.utilities import phrase_table_to_dict, validation_file_to_dict
import pickle
from tfg.translation.refine_ngram_candidates import obtain_ngram_translation
from tfg.utilities import parse_mesh


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mesh_xml_file', help='Path of the xml file in disk in which the used mesh record is contained')
    parser.add_argument('--translation_phrase_table', help='Translation phrase-table')
    parser.add_argument('--phrase_table', default=True, action='store_true',
                        help='True if the translation file is in phrase-table format')
    parser.add_argument('--target_language_model', help='Pickle file containing target language model')
    parser.add_argument('--translated_mesh', help='Translated Mesh thesaurus')
    args = parser.parse_args()

    args = parser.parse_args()

    tree = ET.parse(args.mesh_xml_file)
    hierarchical_dict, descriptor_list = parse_mesh(tree)
    if args.phrase_table:
        translation_dict = phrase_table_to_dict(args.translation_phrase_table)
    else:
        translation_dict = validation_file_to_dict(args.translation_phrase_table)
    target_language_model = pickle.load(open(args.target_language_model, 'rb'))


if __name__ == '__main__':
    main()
