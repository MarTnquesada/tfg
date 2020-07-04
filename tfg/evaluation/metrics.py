import numpy as np
from math import log, log2, log10
from typing import List

VALID_UNIT = {'log', 'log2', 'log10'}
VALID_UNIT_ERR = ValueError("Unit must be one of: '{}'".format("', ".join(VALID_UNIT)))


def check_unit_validity(unit):
    if unit not in VALID_UNIT:
        raise VALID_UNIT_ERR


def check_length_of_lists(l1, l2):
    if len(l1) != len(l2):
        msg = 'Different number of items in both frequency distributions (len1 == {}) != (len2 == {})!'.format(
            len(l1), len(l2))
        raise ValueError(msg)


def smooth(freqs1: List[int], freqs2: List[int], constant: float = 0.001) -> List[float]:
    """Smooth the probabilities of freq1.

    :param freqs1: absolute frequencies from sample 1
    :param freqs2: absolute frequences from sample 2
    :param constant: a constant to modulate the smoothing factor
    :return: the smoothed probability distribution for freqs1
    """
    ## should have inputs the same length? If we don't it is more general, but we might want to check this in our particular case
    ## We could check if there are no 0 in any of the two probability distributions, we do no smoothing, as it is useless?
    ## if all freqs in one of the two distributions is 0, it breaks freq1 = [0, 0, 0], freq2 = [2,3,1]
    ## if freqs are length 1, the smoothing is 1, there's technically no difference freq1 = [4], freq2 = [2]
    ## if the length for values not being 0 is 1, the results are 0 and 1
    ## if there are zeros in both sides as minimmal value and length is 0, we get 0 as min smooth value

    # check if any of the distributions has no hits
    ## if freqs2 has no hits, just normalize distribution 1, without smoothing
    if all(x == 0 for x in freqs2):
        # just normalize
        output = normalize(freqs1)
    ## if all elements of freqs1 have zero hits (more likely to happen at term level analysis),
    ## log operations will break, yielding errors in the metrics
    ## we assign a very tiny probability to each element
    elif all(x == 0 for x in freqs1):
        probs2 = normalize(freqs2)
        # get all probabilities filtering out zeros
        non_zero_probs = [x for x in probs2 if x > 0]
        # get the lowest probability
        min_prob = min(non_zero_probs)
        # calculate smoothing factor making the constant even smaller
        smoothing_factor = min_prob * (constant**2)
        # return the smallest number possible
        output = [smoothing_factor] * len(freqs1)
    # for the rest smooth probabilities
    else:
        # calculate probabilities
        probs1 = normalize(freqs1)
        probs2 = normalize(freqs2)
        # get all probabilities filtering out zeros
        non_zero_probs = [x for x in probs1 + probs2 if x > 0]
        # get the lowest probability
        min_prob = min(non_zero_probs)
        # calculate smoothing factor
        smoothing_factor = min_prob * constant
        # smooth probs1 and normalize probabilities and readjust probabilities so their sum == 1
        output = normalize([x + smoothing_factor for x in probs1])
    return output


def normalize(freqs: List[int]) -> List[int]:
    """Normalize frequencies or calculate probabilities from 0 to 1.

    :param freqs: the absolute frequencies of a probability distribution
    :return: the normalized frequencies
    """
    return [x / sum(freqs) if sum(freqs) > 0 else 0 for x in freqs]


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
        return np.nan


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
        return np.nan


def f_score(precision, recall):
    try:
        return 2*precision*recall/(precision+recall)
    except ZeroDivisionError:
        return np.nan



def lr(f1: float, f2: float, unit: str) -> float:
    """Calculate the LogRatio for two probabilities.

    :param f1: probability from distribution 1
    :param f2: probability from distribution 2
    :param unit: the type of logarithm: log, log2, log10
    :return: the LogRatio
    """
    check_unit_validity(unit)
    try:
        r = f1 / f2
    except ZeroDivisionError:
        r = f1
    if unit == 'log':
        lr = log(r)
    elif unit == 'log2':
        lr = log2(r)
    elif unit == 'log10':
        lr = log10(r)
    return lr


def logratio(freqs1: List[int], freqs2: List[int], smoothing: bool = False) -> List[float]:
    """Calculate LogRatio for each item in two different frequency distributions.

    http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/
    https://pdfs.semanticscholar.org/c71f/b1284f9af79fd4b5510839f2660f75218986.pdf

    :param freqs1: absolute frequencies from sample 1
    :param freqs2: absolute frequences from sample 2
    :param smoothing: whether to apply smoothing to the probabilities of the frequency distributions
    :return: the LogRatio for each item in the frequency distributions
    """
    check_length_of_lists(freqs1, freqs2)
    if smoothing:
        probs1 = smooth(freqs1, freqs2)
        probs2 = smooth(freqs2, freqs1)
    else:
        probs1 = normalize(freqs1)
        probs2 = normalize(freqs2)
    items = zip(probs1, probs2)
    LR = [lr(f1, f2, 'log2') for f1, f2 in items]
    return LR


def kl(freqs1: List[int], freqs2: List[int], unit: str, smoothing: bool = True) -> float:
    """Calculate KLD for two lists of absolute frequencies.
    :param freqs1: the list of frequencies 1
    :param freqs2: the list of frequencies 2
    :param unit: the logarithm to be used: log, log2, or log10
    :param smoothing: whether to smooth the probabilities or not (if there are zeros, you better smooth)
    :return: the KLD value
    """
    check_unit_validity(unit)
    check_length_of_lists(freqs1, freqs2)
    if smoothing:
        probs1 = smooth(freqs1, freqs2)
        probs2 = smooth(freqs2, freqs1)
    else:
        probs1 = normalize(freqs1)
        probs2 = normalize(freqs2)
    items = zip(probs1, probs2)
    kl = sum([p1 * lr(p1, p2, unit) for p1, p2 in items])
    return kl
