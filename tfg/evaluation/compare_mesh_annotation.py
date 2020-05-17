import argparse
import pandas as pd
from tfg.evaluation.metrics import precision, recall, loss, hprecision, hrecall, f_score
from tfg.utilities import parse_mesh, mesh_ancestors, flatten
import pickle
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_lang_annotation',
                        help='xlsx file where each row corresponds to an annotation performed over a corpus using '
                             'the source language MESH thesaurus')
    parser.add_argument('--target_lang_annotation',
                        help='xlsx file where each row corresponds to an annotation performed over a corpus using '
                             'the target language MESH thesaurus')
    parser.add_argument('--mesh', help='Path to the file containing the parsed MESH thesaurus')
    parser.add_argument('--parsed_mesh', action='store_true',
                        help='True if the MESH thesaurus has been already parsed and should be loaded from a pickle file')
    args = parser.parse_args()

    # read dataframes from xls files
    source_annots_df = pd.read_excel(args.source_lang_annotation)
    target_annots_df = pd.read_excel(args.target_lang_annotation)

    # load original thesaurus information
    if args.parsed_mesh:
        hierarchical_dict, descriptor_list = pickle.load(open(args.mesh, 'rb'))
    else:
        tree = ET.parse(args.mesh)
        hierarchical_dict, descriptor_list = parse_mesh(tree)

    # merge both dataframes for easier comparison down the line
    aligned_df = source_annots_df[['descriptors', 'id']].merge(
        target_annots_df[['descriptors', 'id']], on=['id'],
        suffixes=('_original', '_target'),
        how='inner')

    # extract base precision and recall
    n_annots_original = sum(len(set(descriptors)) for descriptors in aligned_df['descriptors_original'])
    n_annots_target = sum(len(set(descriptors)) for descriptors in aligned_df['descriptors_target'])
    target_loss = aligned_df.apply(lambda x: len(loss([descriptor['name'] for descriptor in x['descriptors_original']],
                                                      [descriptor['name'] for descriptor in x['descriptors_target']])),
                                   axis=1).values.sum()
    target_gain = aligned_df.apply(lambda x: len(loss([descriptor['name'] for descriptor in x['descriptors_target']],
                                                      [descriptor['name'] for descriptor in x['descriptors_original']])),
                                   axis=1).values.sum()
    target_correct_hits = n_annots_target - target_gain
    # base precision, recall and f_score using micro-average (which is better when not all classes/topics are balanced)
    base_precision = precision(target_correct_hits, target_gain)
    base_recall = recall(target_correct_hits, target_loss)
    base_f_score = f_score(base_precision, base_recall)

    # extract hierarchical precision and recall based on lowest common ancestor
    aligned_df['y_original'] = aligned_df['descriptors_original'].apply(
        lambda x: flatten([mesh_ancestors(hierarchical_dict, descriptor) for name, descriptor in x]))
    aligned_df['y_target'] = aligned_df['descriptors_target'].apply(
        lambda x: flatten([mesh_ancestors(hierarchical_dict, descriptor) for name, descriptor in x]))
    aligned_df['hprecision'] = aligned_df.apply(
        lambda x: hprecision(x['y_original'], x['y_target']), axis=1)
    aligned_df['hrecall'] = aligned_df.apply(
        lambda x: hrecall(x['y_original'], x['y_target']), axis=1)
    aligned_df['hf_score'] = aligned_df.apply(
        lambda x: f_score(x['hprecision'], x['hrecall']), axis=1)
    hierachical_precision = aligned_df['hprecision'].values.mean()
    hierachical_recall = aligned_df['hrecall'].values.mean()
    hierachical_f_score = aligned_df['hf_score'].values.mean()


if __name__ == '__main__':
    main()