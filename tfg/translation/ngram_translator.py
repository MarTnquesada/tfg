# Built from https://github.com/yunsukim86/wbw-lm, Copyright (C) yunsukim86 (https://github.com/yunsukim86)
from math import log


class NgramTranslator:
    def __init__(self, translation_dictionary, language_model):
        self.translation_dictionary = translation_dictionary
        self.lm = language_model
        self.PROB_DEFAULT = 0.001

    def word_translation(self, src_word, topk):
        """
        This phase contains several calculations when obtaining a translation from cross-mapped embeddings,
        but since we are using an already induced phrase-table, the process is greatly simplified
        :param src_word:
        :return:
        """
        if not self.translation_dictionary.get(src_word, None):
            return [src_word], [self.PROB_DEFAULT]
        else:
            return [candidate for candidate, score in self.translation_dictionary[src_word][:topk]], \
                   [score for candidate, score in self.translation_dictionary[src_word][:topk]]

    def ngram_translation(self, sent, topk, use_lm=True, lm_scaling=0.1, lex_scaling=1.0, beam_size=10):
        beam = [[list(), 0.0]]
        for n in range(len(sent)):
            src_word = sent[n]
            if type(src_word) == bytes:
                src_word = src_word.decode()
            topk_tgt_words, topk_scores = self.word_translation(src_word, topk)

            if use_lm:
                all_candidates = list()
                topk_zipped = list(zip(topk_tgt_words, topk_scores))
                for sequence, sequence_score in beam:
                    if not sequence:
                        lm_score_history = 0
                    else:
                        lm_score_history = self.lm.score(sequence[-1], sequence[:1])
                    for tgt_word, score in topk_zipped:
                        new_sequence = sequence + [tgt_word]
                        lex_score = lex_scaling * log(score)
                        lm_score = lm_scaling * (
                                    self.lm.score(tgt_word, sequence) - lm_score_history)
                        new_sequence_score = sequence_score + lex_score + lm_score
                        all_candidates.append([new_sequence, new_sequence_score])
                ordered = sorted(all_candidates, key=lambda x: x[1], reverse=True)
                beam = ordered[:beam_size]
            else:
                beam[0][0].append(topk_tgt_words[0])
                beam[0][1] += log(topk_scores[0])
        return beam[0][0]
