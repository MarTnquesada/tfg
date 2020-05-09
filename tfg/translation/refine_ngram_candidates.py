import numpy as np
import pickle
from nltk.lm import MLE
from itertools import permutations


def obtain_ngram_translation(original_term, translation_dictionary, target_lang_model):
    translation_candidates = []
    original_term_perms = permutations(original_term.split())
    for perm in original_term_perms:
        tail = [translation_dictionary.get(perm[0], '')]
        for word in perm[1:]:
            predicted_word = target_lang_model.logscore(word, ' '.join(tail))
            for proposed_translation in translation_dictionary.get(word, '')[:5]:
            tail.append(chosen_word)
        translation_candidates.append(' '.join(tail))
    # choose the highest likelihood term according to the target language model
    translated_term = max(translation_candidates, key=target_lang_model.score)
    return translated_term


def main():
    pass


if __name__ == '__main__':
    main()