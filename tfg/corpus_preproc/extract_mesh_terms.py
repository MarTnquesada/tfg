import argparse
import xml.etree.ElementTree as ET
from itertools import permutations


def main():
    # Extracts all terms belonging to descriptors from the MESH thesaurus and appends them to a given text file
    parser = argparse.ArgumentParser()
    parser.add_argument('--mesh_xml_file',
                        help='Path of the xml file in disk in which the used mesh record is contained')
    parser.add_argument('--target_file',
                        help='Path of the file in which to store the extracted terms')
    args = parser.parse_args()

    with open(args.target_file, 'a+') as f:
        tree = ET.parse(args.mesh_xml_file)
        root = tree.getroot()
        for descriptor_record in root:
            descriptor_class = descriptor_record.get('DescriptorClass')
            descriptor_name = descriptor_record.find('DescriptorName').find('String').text
            descriptor_concepts = descriptor_record.find('ConceptList')
            for concept in descriptor_concepts:
                concept_name = concept.find('ConceptName').find('String').text
                concept_terms = concept.find('TermList')
                for term in concept_terms:
                    term_is_preferred_concept = term.get('ConceptPreferredTermYN')
                    term_is_permuted = term.get('IsPermutedTermYN')
                    term_lexical_tag = term.get('LexicalTag')
                    term_name = term.find('String').text
                    term_is_preferred_record = term.get('RecordPreferredTermYN')
                    if term_is_permuted == 'Y' and len(term_name.split()) <= 3:
                        perms = list(permutations(term_name.split()))
                        for perm in perms:
                            f.write(' '.join(perm).lower() + '\n')
                    else:
                        f.write(term_name.lower() + '\n')


if __name__ == '__main__':
    main()
