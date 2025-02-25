import argparse
import xml.etree.ElementTree as ET
from tfg.utilities import phrase_table_to_dict, validation_file_to_dict
from tfg.utilities import parse_mesh
import pickle
from tqdm import tqdm
from tfg.translation.vecmap_ngram_translator import VecmapNgramTranslator
from kenlm import LanguageModel


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mesh_xml_file', help='Path of the xml file in disk in which the used mesh record is contained')
    parser.add_argument('--translation_phrase_table', help='Translation phrase-table')
    parser.add_argument('--phrase_table', default=True, action='store_true',
                        help='True if the translation file is in phrase-table format')
    parser.add_argument('--mle_lm', help='Pickle file containing target language model')
    parser.add_argument('--kenlm_lm', help='Binary file containing target language model')
    parser.add_argument('--translated_mesh', help='Translated Mesh thesaurus')
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
    if args.mle_lm:
        print("Loading NLTK MLE language model")
        target_language_model = pickle.load(open(args.mle_lm, 'rb'))
    elif args.kenlm_lm:
        print("Loading kenlm language model")
        target_language_model = LanguageModel(args.kenlm_lm)
    else:
        print('No language model given!')
        return 1
    translator = VecmapNgramTranslator(translation_dict, target_language_model)

    # translating parsed mesh thesaurus
    print('Translating MESH thesaurus')
    for descriptor in tqdm(descriptor_list):
        for concept in descriptor['concepts']:
            for term in concept['terms']:
                if args.mle_lm:
                    translated_term = ' '.join(translator.mle_ngram_translation(
                        term['name'].lower().split(), topk=3, use_lm=True, lm_scaling=0.1, lex_scaling=1.0, beam_size=10))
                else:
                    translated_term = ' '.join(translator.kenlm_ngram_translation(
                        term['name'].lower().split(), topk=3, use_lm=True, lm_scaling=0.1, lex_scaling=1.0,
                        beam_size=10))
                term['name'] = translated_term

    # storing parsed translated thesaurus as a serialized python object
    f = open(args.translated_mesh, 'wb')
    pickle.dump((hierarchical_dict, descriptor_list), open(args.translated_mesh, 'wb'))
    f.close()


if __name__ == '__main__':
    main()
