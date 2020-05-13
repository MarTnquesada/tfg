import argparse
import pandas as pd
from tfg.evaluation.metrics import precision, recall, loss


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_lang_annotation',
                        help='xlsx file where each row corresponds to an annotation performed over a corpus using '
                             'the source language MESH thesaurus')
    parser.add_argument('--target_lang_annotation',
                        help='xlsx file where each row corresponds to an annotation performed over a corpus using '
                             'the target language MESH thesaurus')
    args = parser.parse_args()

    # read dataframes from xls files
    source_annots_df = pd.read_excel(args.source_lang_annotation)
    target_annots_df = pd.read_excel(args.target_lang_annotation)

    # merge both dataframes for easier comparison down the line
    aligned_df = source_annots_df[['descriptors', 'id']].merge(
        target_annots_df[['descriptors', 'id']], on=['id'],
        suffixes=('_original', '_target'),
        how='inner')

    # extract global metrics
    n_annots_original = sum(len(descriptors.keys()) for descriptors in aligned_df['descriptors_original'])
    n_annots_target = sum(len(descriptors.keys()) for descriptors in aligned_df['descriptors_target'])
    target_loss = aligned_df.apply(lambda x: len(loss([descriptor_name for descriptor_name, descriptor in x['descriptors_original'].items()],
                                                      [descriptor_name for descriptor_name, descriptor in x['descriptors_target'].items()])),
                                   axis=1).values.sum()
    target_gain = aligned_df.apply(lambda x: len(loss([descriptor_name for descriptor_name, descriptor in x['descriptors_target'].items()],
                                                      [descriptor_name for descriptor_name, descriptor in x['descriptors_original'].items()])),
                                   axis=1).values.sum()
    target_correct_hits = n_annots_target - target_gain

    # general precision and recall using micro-average (which is better when not all classes/topics are balanced)
    target_precision = precision(target_correct_hits, target_gain)
    target_recall = precision(target_correct_hits, target_loss)


if __name__ == '__main__':
    main()