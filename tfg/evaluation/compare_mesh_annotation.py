import argparse
import pandas as pd
from tfg.evaluation.metrics import precision, recall, loss, f_score
from tfg.utilities import parse_mesh, mesh_ancestors, mesh_lowest_common_ancestors, flatten
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
    # parse structured data contained in the spreadsheet
    aligned_df['descriptors_original'] = aligned_df['descriptors_original'].apply(
        lambda x: eval(x))
    aligned_df['descriptors_target'] = aligned_df['descriptors_target'].apply(
        lambda x: eval(x))

    # base precision, recall and f_score using micro-average (which is better when not all classes/topics are balanced)
    base_n_annots_original = sum(len(set([d['name'] for d in descriptors])) for descriptors in aligned_df['descriptors_original'])
    base_n_annots_target = sum(len(set([d['name'] for d in descriptors])) for descriptors in aligned_df['descriptors_target'])
    base_target_loss = aligned_df.apply(lambda x: len(loss([descriptor['name'] for descriptor in x['descriptors_original']],
                                                      [descriptor['name'] for descriptor in x['descriptors_target']])),
                                   axis=1).values.sum()
    base_target_gain = aligned_df.apply(lambda x: len(loss([descriptor['name'] for descriptor in x['descriptors_target']],
                                                      [descriptor['name'] for descriptor in x['descriptors_original']])),
                                   axis=1).values.sum()
    base_target_correct_hits = base_n_annots_target - base_target_gain
    base_precision = precision(base_target_correct_hits, base_target_gain)
    base_recall = recall(base_target_correct_hits, base_target_loss)
    base_f_score = f_score(base_precision, base_recall)

    # hierarchical precision and recall based on ancestors using micro-average
    aligned_df['y_original'] = aligned_df['descriptors_original'].apply(
        lambda x: flatten([mesh_ancestors(descriptor['tree_numbers']) for descriptor in x]))
    aligned_df['y_target'] = aligned_df['descriptors_target'].apply(
        lambda x: flatten([mesh_ancestors(descriptor['tree_numbers']) for descriptor in x]))
    hierarchical_n_annots_original = sum(
        len(set([number for number in tree_numbers])) for tree_numbers in aligned_df['y_original'])
    hierarchical_n_annots_target = sum(
        len(set([number for number in tree_numbers])) for tree_numbers in aligned_df['y_target'])
    hierarchical_target_loss = aligned_df.apply(
        lambda x: len(loss([number for number in x['y_original']],
                           [number for number in x['y_target']])),
        axis=1).values.sum()
    hierarchical_target_gain = aligned_df.apply(
        lambda x: len(loss([number for number in x['y_target']],
                           [number for number in x['y_original']])),
        axis=1).values.sum()
    hierarchical_target_correct_hits = hierarchical_n_annots_target - hierarchical_target_gain
    hierarchical_precision = precision(hierarchical_target_correct_hits, hierarchical_target_gain)
    hierarchical_recall = recall(hierarchical_target_correct_hits, hierarchical_target_loss)
    hierarchical_f_score = f_score(hierarchical_precision, hierarchical_recall)

    # hierarchical precision and recall based on lowest common ancestor using micro-average
    aligned_df['yag_original'] = aligned_df['descriptors_original'].apply(
        lambda x: flatten([mesh_lowest_common_ancestors(descriptor['tree_numbers']) for descriptor in x]))
    aligned_df['yag_target'] = aligned_df['descriptors_target'].apply(
        lambda x: flatten([mesh_lowest_common_ancestors(descriptor['tree_numbers']) for descriptor in x]))
    lca_hierarchical_n_annots_original = sum(
        len(set([number for number in tree_numbers])) for tree_numbers in aligned_df['yag_original'])
    lca_hierarchical_n_annots_target = sum(
        len(set([number for number in tree_numbers])) for tree_numbers in aligned_df['yag_target'])
    lca_hierarchical_target_loss = aligned_df.apply(
        lambda x: len(loss([number for number in x['yag_original']],
                           [number for number in x['yag_target']])),
        axis=1).values.sum()
    lca_hierarchical_target_gain = aligned_df.apply(
        lambda x: len(loss([number for number in x['yag_target']],
                           [number for number in x['yag_original']])),
        axis=1).values.sum()
    lca_hierarchical_target_correct_hits = lca_hierarchical_n_annots_target - lca_hierarchical_target_gain
    lca_hierarchical_precision = precision(lca_hierarchical_target_correct_hits, lca_hierarchical_target_gain)
    lca_hierarchical_recall = recall(lca_hierarchical_target_correct_hits, lca_hierarchical_target_loss)
    lca_hierarchical_f_score = f_score(lca_hierarchical_precision, lca_hierarchical_recall)


if __name__ == '__main__':
    main()