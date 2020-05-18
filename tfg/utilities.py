from os.path import commonprefix


def parse_mesh(xml_tree):
    # create a list containing all descriptors in the MESH thesaurus represented as dictionaries
    descriptor_list= []
    root = xml_tree.getroot()
    for descriptor_record in root:
        descriptor_dict = {}
        descriptor_dict['class'] = descriptor_record.get('DescriptorClass')
        descriptor_dict['name'] = descriptor_record.find('DescriptorName').find('String').text
        tree_numbers = descriptor_record.find('TreeNumberList')
        if tree_numbers:
            descriptor_dict['tree_numbers'] = [tree_number.text for tree_number in tree_numbers]
        else:
            descriptor_dict['tree_numbers'] = []
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
            branch[parts[-1]] = descriptor
    return hierarchical_dict, descriptor_list


def mesh_ancestors(tree_numbers):
    ancestors = []
    for number in tree_numbers:
        ancestors += ['.'.join(number.split('.')[:i+1]) for i, level in enumerate(number.split('.'))]
    return ancestors


def mesh_lowest_common_ancestors(tree_numbers):
    ancestors = []
    common_suffix = commonprefix([reversed(number) for number in tree_numbers])
    lca_splitted = list(reversed(common_suffix))
    if len(tree_numbers) <= 1 or not lca_splitted or (len(lca_splitted) == 1 and len(lca_splitted[0]) < 3):
        for number in tree_numbers:
            ancestors += ['.'.join(number.split('.')[:i + 1]) for i, level in enumerate(number.split('.'))]
    else:
        if len(lca_splitted[0]) < 3:
            lca_splitted = lca_splitted[1:]
        # TODO

    return ancestors


def flatten(iterator_of_iterators):
    return [item for sublist in iterator_of_iterators for item in sublist]


def readlines_by_chunks(filepath, chunk_size):
    """
    Generator
    :param filepath:
    :param chunk_size:
    :return:
    """
    with open(filepath, 'r') as f:
        chunk = ''
        for i, line in enumerate(f.readlines(), start=1):
            chunk += line
            if i % chunk_size == 0:
                yield chunk
                chunk = ''
        if chunk:
            yield chunk


def phrase_table_to_dict(src):
    """
    Takes a phrase-table text file as input and converts it into a dictionary
    :param src: path of the phrase-table text file
    :return: a dictionary equivalent to the phrase-table given as parameter
    :rtype: dict
    """
    pt_dict = {}
    with open(src, mode='r',) as f:
        for line in f:
            entry = line.split()
            pt_dict.setdefault(entry[0], []).append((entry[2], float(entry[4])))
    return pt_dict


def validation_file_to_dict(src):
    """
    Takes a validation dictionary text file as input and converts it into a dictionary
    :param src: path of the validation dictionary text file
    :return: a dictionary equivalent to the validation file given as parameter
    :rtype: dict
    """
    validation_dict = {}
    with open(src, mode='r', ) as f:
        for line in f:
            entry = line.split()
            validation_dict.setdefault(entry[0], []).append(entry[1])
    return validation_dict
