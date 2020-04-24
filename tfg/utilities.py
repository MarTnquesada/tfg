

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
            pt_dict.setdefault(entry[0], []).append(entry[2])
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
