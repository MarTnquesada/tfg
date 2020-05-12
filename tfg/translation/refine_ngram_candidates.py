import numpy as np
import pickle
from nltk.lm import MLE
from itertools import permutations, product
from tfg.utilities import phrase_table_to_dict
import pickle


def obtain_ngram_translation(original_term, translation_dictionary, target_lang_model, max_translation_entries=3):
    global_translation_candidates = []
    original_term_perms = permutations(original_term)
    for perm in original_term_perms:
        # if a term is not contained in the translation dictionary, it is used in its original form
        unigram_candidates = [
            [translation for translation, score in translation_dictionary.get(word, [(word, 0)])[:max_translation_entries]]
            for word in perm]
        local_translation_candidates = product(*unigram_candidates)
        # choose the highest likelihood term according to the target language model
        # if all candidates have the same likelihood, the translation based on the first proposed translation is selected
        perm_translation = max(local_translation_candidates, key=lambda x: target_lang_model.score(x[-1], x[:-1]))
        global_translation_candidates.append(perm_translation)
    # choose the highest likelihood term according to the target language model
    # if all candidates have the same likelihood, the literal word-by-word translation is selected
    translated_term = max(global_translation_candidates, key=lambda x: target_lang_model.score(x[-1], x[:-1]))
    return translated_term


def main():
    original_term = 'the doctor'.lower()
    translation_dictionary = phrase_table_to_dict('../../data/pubmedplusibecs_en_3_6_300_cross_es_phrase_table.pt')
    target_lang_model = pickle.load(open('../../models/pubmedplusibecs_es_asym_MLE', 'rb'))
    translated_term = obtain_ngram_translation(original_term, translation_dictionary, target_lang_model)
    print(target_lang_model.score(translated_term[-1], translated_term[:-1]))
    print(' '.join(translated_term))


if __name__ == '__main__':
    main()