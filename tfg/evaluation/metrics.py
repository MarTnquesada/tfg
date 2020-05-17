

def loss(reference_list, observed_list):
    """
    Given two lists of string, returns a list of the strings present in true_list that
    do not appear in observed_list. If any of the lists is NaN or an instance of a float, it is considered empty.
    :param reference_list:
    :param observed_list:
    :return:
    """
    if isinstance(reference_list, float):
        return []
    elif isinstance(observed_list, float):
        return reference_list
    else:
        return list(set(reference_list) - set(observed_list))


def precision(true_positives, false_positives):
    """
    Calculates precision given a number of true positives and false positives
    :param true_positives:
    :param false_positives:
    :return:
    """
    try:
        return true_positives / (true_positives + false_positives)
    except ZeroDivisionError:
        return true_positives


def recall(true_positives, false_negatives):
    """
    Calculates precision given a number of true positives and false positives
    :param true_positives:
    :param false_negatives:
    :return:
    """
    try:
        return true_positives / (true_positives + false_negatives)
    except ZeroDivisionError:
        return true_positives


def hprecision(original_y, estimated_y):
    try:
        len(set(original_y).intersection(set(estimated_y))) / len(set(estimated_y))
    except ZeroDivisionError:
        return len(set(original_y).intersection(set(original_y)))


def hrecall(original_y, estimated_y):
    try:
        len(set(original_y).intersection(set(estimated_y))) / len(set(estimated_y))
    except ZeroDivisionError:
        return len(set(original_y).intersection(set(estimated_y)))


def f_score(precision, recall):
    try:
        return 2*precision*recall/(precision+recall)
    except ZeroDivisionError:
        return 2*precision*recall