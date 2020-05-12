import argparse
import xml.etree.ElementTree as ET
from tfg.utilities import phrase_table_to_dict, validation_file_to_dict
from tfg.translation.refine_ngram_candidates import obtain_ngram_translation
from tfg.utilities import parse_mesh
import pickle
from tqdm import tqdm
from tfg.translation.ngram_translator import NgramTranslator


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

    # load translation dictionary, MESH thesaurus and language model
    print('Parsing and loading MESH thesaurus')
    tree = ET.parse(args.mesh_xml_file)
    hierarchical_dict, descriptor_list = parse_mesh(tree)
    print('Loading translation dictionary')
    if args.phrase_table:
        translation_dict = phrase_table_to_dict(args.translation_phrase_table)
    else:
        translation_dict = validation_file_to_dict(args.translation_phrase_table)
    print("Loading language model")
    target_language_model = pickle.load(open(args.target_language_model, 'rb'))
    translator = NgramTranslator(translation_dict, target_language_model)

    # translating parsed mesh thesaurus
    print('Translating MESH thesaurus')
    for descriptor in tqdm(descriptor_list):
        for concept in descriptor['concepts']:
            for term in concept['terms']:
                translated_term = ' '.join(translator.ngram_translation(
                    term['name'].lower().split(), topk=3, use_lm=True, lm_scaling=0.1, lex_scaling=1.0, beam_size=10))
                term['name'] = ' '.join(translated_term)

    # storing parsed translated thesaurus as a serialized python object
    pickle.dump(descriptor_list, open(args.translated_mesh, 'wb'))


if __name__ == '__main__':
    main()
