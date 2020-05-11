# Copyright (C) yunsukim86 (https://github.com/yunsukim86)
from math import exp, log


class NgramTranslator:
    def __init__(self, translation_dictionary, language_model):
        self.translation_dictionary = translation_dictionary
        self.language_model = language_model
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

        if src_word not in self.translation_dictionary:  # source unknown word
            return [src_word], [PROB_DEFAULT]
        elif src_word in CATEGORY_LABELS:
            return [src_word], [PROB_DEFAULT]
        else:
            src_word_id = self.src_dico.word2id[src_word]
            src_word_vec = self.emb1[src_word_id].view(1, self.params.emb_dim)

            # nearest neighbor
            scores = src_word_vec.mm(self.emb2.transpose(0, 1))
            if self.params.similarity_measure == 'csls':
                scores.mul_(2)
                scores.sub_(self.average_dist1[[src_word_id]][:, None])
                scores.sub_(self.average_dist2[None, :])

            topk = scores.topk(self.params.topk, 1, True)
            topk_scores = topk[0].cpu().numpy()[0]
            topk_tgt_ids = topk[1][0]

            # scaling of similarity scores
            topk_scores = NgramTranslator.linear_scaling(topk_scores)

            # convert from ids to words
            topk_tgt_words = []
            topk_tgt_scores = []

            for i in range(len(topk_tgt_ids)):
                tgt_word = self.tgt_dico.id2word[topk_tgt_ids[i]]
                topk_tgt_words.append(tgt_word)
                topk_tgt_scores.append(topk_scores[i])

            if len(topk_tgt_words) == 0:
                topk_tgt_words = [src_word]
                topk_tgt_scores = [PROB_DEFAULT]

            return topk_tgt_words, topk_tgt_scores

    def sent_translation(self, sent, lm, topk, lm_scaling=0.1, lex_scaling=1.0, beam_size=10):
        beam = [[list(), 0.0]]
        for n in range(len(sent)):
            src_word = sent[n]
            if type(src_word) == bytes:
                src_word = src_word.decode()
            topk_tgt_words, topk_scores = self.word_translation(src_word, topk)

            if lm:
                all_candidates = list()

                topk_zipped = list(zip(topk_tgt_words, topk_scores))
                for sequence, sequence_score in beam:
                    lm_score_history = lm.score(' '.join(sequence), bos=True, eos=False)
                    for tgt_word, score in topk_zipped:
                        eos = False
                        if n == len(sent) - 1:
                            eos = True
                        new_sequence = sequence + [tgt_word]
                        lex_score = lex_scaling * log(score)
                        lm_score = lm_scaling * (
                                    lm.score(' '.join(new_sequence), bos=True, eos=eos) - lm_score_history)
                        new_sequence_score = sequence_score + lex_score + lm_score
                        all_candidates.append([new_sequence, new_sequence_score])
                ordered = sorted(all_candidates, key=lambda x: x[1], reverse=True)
                beam = ordered[:beam_size]
            else:
                beam[0][0].append(topk_tgt_words[0])
                beam[0][1] += log(topk_scores[0])
        return beam[0][0]
