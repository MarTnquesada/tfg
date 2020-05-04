import argparse
import xml.etree.ElementTree as ET
from tfg.utilities import phrase_table_to_dict, validation_file_to_dict


def parse_mesh(xml_tree):
    # create a list containing all descriptors in the MESH thesaurus represented as dictionaries
    descriptor_list= []
    root = xml_tree.getroot()
    for descriptor_record in root:
        descriptor_dict = {}
        descriptor_dict['class'] = descriptor_record.get('DescriptorClass')
        descriptor_dict['name'] = descriptor_record.find('DescriptorName').find('String').text
        tree_numbers = descriptor_record.find('TreeNumberList')
        descriptor_dict['tree_numbers'] = [tree_number.text for tree_number in tree_numbers]
        descriptor_concepts = descriptor_record.find('ConceptList')
        concept_list = []
        for concept in descriptor_concepts:
            concept_dict = {}
            concept_dict['name'] = concept.find('ConceptName').find('String').text
            concept_terms = concept.find('TermList')
            term_list = []
            for term in concept_terms:
                term_dict = {}
                term_dict['is_preferred_concept'] = term.get('ConceptPreferredTermYN')
                term_dict['is_permuted'] = term.get('IsPermutedTermYN')
                term_dict['lexical_tag'] = term.get('LexicalTag')
                term_dict['name'] = term.find('String').text
                term_dict['is_preferred_record'] = term.get('RecordPreferredTermYN')
                term_list.append(term_dict)
            concept_dict['terms'] = term_list
            concept_list.append(concept_dict)
        descriptor_dict['concepts'] = concept_list
        descriptor_list.append(descriptor_dict)

    # use the list of dictionaries obtained to build a hierarchical dictionary representing tree_number relations
    hierarchical_dict = {}
    for descriptor in descriptor_list:
        for tree_number in descriptor['tree_numbers']:
            parts = tree_number.split('.')
            branch = hierarchical_dict
            for i, level in enumerate(parts[:-1]):
                branch = branch.setdefault(level, {})
            branch[parts[:-1]] = descriptor
    return hierarchical_dict, descriptor_list


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mesh_xml_file', help='Path of the xml file in disk in which the used mesh record is contained')
    parser.add_argument('--translation_dictionary_file', help='Path of the xml file in disk in which the used mesh record is contained')
    parser.add_argument('--phrase_table', default=False, action='store_true',
                        help='True if the translation file is in phrase-table format')
    args = parser.parse_args()

    tree = ET.parse(args.mesh_xml_file)
    hierarchical_dict, descriptor_list = parse_mesh(tree)
    if args.phrase_table:
        translation_dict = phrase_table_to_dict(args.src_path)
    else:
        translation_dict = validation_file_to_dict(args.src_path)


if __name__ == '__main__':
    main()
