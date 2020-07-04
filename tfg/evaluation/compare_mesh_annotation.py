import argparse
import pandas as pd
from tfg.evaluation.metrics import precision, recall, loss, f_score
from tfg.utilities import parse_mesh, mesh_ancestors, mesh_lowest_common_ancestors, flatten
from tfg.evaluation.metrics import kl
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
    descriptor_df = pd.DataFrame(descriptor_list[:15])
    # filter data
    descriptor_df = descriptor_df[['ui', 'tree_numbers', 'name']]

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
    base_n_annots_original = sum(len(set([d['ui'] for d in descriptors])) for descriptors in aligned_df['descriptors_original'])
    base_n_annots_target = sum(len(set([d['ui'] for d in descriptors])) for descriptors in aligned_df['descriptors_target'])
    base_target_loss = aligned_df.apply(lambda x: len(loss([descriptor['ui'] for descriptor in x['descriptors_original']],
                                                      [descriptor['ui'] for descriptor in x['descriptors_target']])),
                                   axis=1).values.sum()
    base_target_gain = aligned_df.apply(lambda x: len(loss([descriptor['ui'] for descriptor in x['descriptors_target']],
                                                      [descriptor['ui'] for descriptor in x['descriptors_original']])),
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
    print(f'{"*"*15}MICRO{"*"*15}')
    print('BASE')
    print(f'Precision: {base_precision}')
    print(f'Recall: {base_recall}')
    print(f'F-score: {base_f_score}')
    print('-'*30)
    print('HIERARCHICAL')
    print(f'Precision: {hierarchical_precision}')
    print(f'Recall: {hierarchical_recall}')
    print(f'F-score: {hierarchical_f_score}')
    print('-' * 30)
    print('HIERARCHICAL LCA')
    print(f'Precision: {lca_hierarchical_precision}')
    print(f'Recall: {lca_hierarchical_recall}')
    print(f'F-score: {lca_hierarchical_f_score}')

    # base
    descriptor_df['n_annots_target_base'] = descriptor_df['ui'].apply(
        lambda x: sum(any([1 for d in descriptors if d['ui'] == x])
                      for descriptors in aligned_df['descriptors_target']))
    descriptor_df['target_loss_base'] = descriptor_df['ui'].apply(
        lambda x: sum(len(loss([d['ui'] for d in descriptors_original if d['ui'] == x],
                           [d['ui'] for d in descriptors_target if d['ui'] == x]))
                      for descriptors_original, descriptors_target
                      in zip(aligned_df['descriptors_original'], aligned_df['descriptors_target'])))
    descriptor_df['target_gain_base'] = descriptor_df['ui'].apply(
        lambda x: sum(len(loss([d['ui'] for d in descriptors_target if d['ui'] == x],
                               [d['ui'] for d in descriptors_original if d['ui'] == x]))
                      for descriptors_original, descriptors_target
                      in zip(aligned_df['descriptors_original'], aligned_df['descriptors_target'])))
    descriptor_df['target_correct_hits_base'] = descriptor_df.apply(
        lambda x: x['n_annots_target_base'] - x['target_gain_base'] ,
        axis=1)
    descriptor_df['precision_base'] = descriptor_df.apply(
        lambda x: precision(x['target_correct_hits_base'], x['target_gain_base']),
        axis=1)
    descriptor_df['recall_base'] = descriptor_df.apply(
        lambda x: recall(x['target_correct_hits_base'], x['target_loss_base']),
        axis=1)
    descriptor_df['f_score_base'] = descriptor_df.apply(
        lambda x: f_score(x['precision_base'], x['recall_base']),
        axis=1)

    # hierarchical
    descriptor_df['n_annots_target_hierarchical'] = descriptor_df['tree_numbers'].apply(
        lambda x: sum(any([1 for n in numbers if n in x])
                      for numbers in aligned_df['y_target']))
    descriptor_df['target_loss_hierarchical'] = descriptor_df['tree_numbers'].apply(
        lambda x: sum(any(loss([n for n in y_original if n in x],
                               [n for n in y_target if n in x]))
                      for y_original, y_target
                      in zip(aligned_df['y_original'], aligned_df['y_target'])))
    descriptor_df['target_gain_hierarchical'] = descriptor_df['tree_numbers'].apply(
        lambda x: sum(any(loss([n for n in y_target if n in x],
                               [n for n in y_original if n in x]))
                      for y_original, y_target
                      in zip(aligned_df['y_original'], aligned_df['y_target'])))
    descriptor_df['target_correct_hits_hierarchical'] = descriptor_df.apply(
        lambda x: x['n_annots_target_hierarchical'] - x['target_gain_hierarchical'],
        axis=1)
    descriptor_df['precision_hierarchical'] = descriptor_df.apply(
        lambda x: precision(x['target_correct_hits_hierarchical'], x['target_gain_hierarchical']),
        axis=1)
    descriptor_df['recall_hierarchical'] = descriptor_df.apply(
        lambda x: recall(x['target_correct_hits_hierarchical'], x['target_loss_hierarchical']),
        axis=1)
    descriptor_df['f_score_hierarchical'] = descriptor_df.apply(
        lambda x: f_score(x['precision_hierarchical'], x['recall_hierarchical']),
        axis=1)

    # hierarchical_lca
    descriptor_df['n_annots_target_hierarchical_lca'] = descriptor_df['tree_numbers'].apply(
        lambda x: sum(any([1 for n in numbers if n in x])
                      for numbers in aligned_df['yag_target']))
    descriptor_df['target_loss_hierarchical_lca'] = descriptor_df['tree_numbers'].apply(
        lambda x: sum(any(loss([n for n in yag_original if n in x],
                               [n for n in yag_target if n in x]))
                      for yag_original, yag_target
                      in zip(aligned_df['yag_original'], aligned_df['yag_target'])))
    descriptor_df['target_gain_hierarchical_lca'] = descriptor_df['tree_numbers'].apply(
        lambda x: sum(any(loss([n for n in yag_target if n in x],
                               [n for n in yag_original if n in x]))
                      for yag_original, yag_target
                      in zip(aligned_df['yag_original'], aligned_df['yag_target'])))
    descriptor_df['target_correct_hits_hierarchical_lca'] = descriptor_df.apply(
        lambda x: x['n_annots_target_hierarchical_lca'] - x['target_gain_hierarchical_lca'],
        axis=1)
    descriptor_df['precision_hierarchical_lca'] = descriptor_df.apply(
        lambda x: precision(x['target_correct_hits_hierarchical_lca'], x['target_gain_hierarchical_lca']),
        axis=1)
    descriptor_df['recall_hierarchical_lca'] = descriptor_df.apply(
        lambda x: recall(x['target_correct_hits_hierarchical_lca'], x['target_loss_hierarchical_lca']),
        axis=1)
    descriptor_df['f_score_hierarchical_lca'] = descriptor_df.apply(
        lambda x: f_score(x['precision_hierarchical_lca'], x['recall_hierarchical_lca']),
        axis=1)
    """
    # drop cases where true positives + false negatives= 0, that is, where recall is undefined (nan)
    descriptor_df = descriptor_df.dropna(axis=0, subset=['recall_base'])
    # score with 0 cases where true positives + false positives = 0, that is, where precision is undefined (nan)
    descriptor_df['precision_base'] = descriptor_df['precision_base'].apply(lambda x: 0 if pd.isna(x) else x)
    descriptor_df['f_score_base'] = descriptor_df['f_score_base'].apply(lambda x: 0 if pd.isna(x) else x)
    
    In some rare cases, the calculation of Precision or Recall can cause a division by 0. Regarding the precision, this can happen if there are no results inside the answer of an annotator and, thus, the true as well as the false positives are 0. For these special cases, we have defined that if the true positives, false positives and false negatives are all 0, the precision, recall and F1-measure are 1. This might occur in cases in which the gold standard contains a document without any annotations and the annotator (correctly) returns no annotations. If true positives are 0 and one of the two other counters is larger than 0, the precision, recall and F1-measure are 0.
    """
    descriptor_df = descriptor_df[['precision_base', 'recall_base', 'f_score_base']].apply(
        lambda x: (1, 1, 1)
        if pd.isna(x['precision_base']) and pd.isna(x['recall_base']) and pd.isna(x['f_score_base'])
        else (0, 0, 0) if pd.isna(x['precision_base']) or pd.isna(x['recall_base'])
        else x, axis=1)

    print(f'{"*" * 15}MACRO{"*" * 15}')
    print('BASE')
    print(f'Precision: {descriptor_df["precision_base"].mean()}')
    print(f'Recall: {descriptor_df["recall_base"].mean()}')
    print(f'F-score: {descriptor_df["f_score_base"].mean()}')
    print('-' * 30)
    print('HIERARCHICAL')
    print(f'Precision: {descriptor_df["precision_hierarchical"].mean()}')
    print(f'Recall: {descriptor_df["recall_hierarchical"].mean()}')
    print(f'F-score: {descriptor_df["f_score_hierarchical"].mean()}')
    print('-' * 30)
    print('HIERARCHICAL LCA')
    print(f'Precision: {descriptor_df["precision_hierarchical_lca"].mean()}')
    print(f'Recall: {descriptor_df["recall_hierarchical_lca"].mean()}')
    print(f'F-score: {descriptor_df["f_score_hierarchical_lca"].mean()}')

    # obtain all original and target frequencies
    descriptor_df['freq_original'] = descriptor_df['ui'].apply(
        lambda x: sum(
            1 for descriptors in aligned_df['descriptors_original'] if x in set([d['ui'] for d in descriptors])) / len(
            aligned_df))
    descriptor_df['freq_target'] = descriptor_df['ui'].apply(
        lambda x: sum(
            1 for descriptors in aligned_df['descriptors_target'] if x in set([d['ui'] for d in descriptors])) / len(
            aligned_df))
    # kld calculation
    kld = kl(descriptor_df['freq_original'], descriptor_df['freq_target'], unit='log', smoothing=True)

    print('*' * 30)
    print(f'KLD: {kld}')

    """
    # calculate metrics at descriptor level
    descriptor_df['hits_original'] = descriptor_df['ui'].apply(
        lambda x: [h for hits in aligned_df['descriptors_original'] for h in hits if h['ui'] == x])
    descriptor_df['hits_target'] = descriptor_df['ui'].apply(
        lambda x: [h for hits in aligned_df['descriptors_target'] for h in hits if h['ui'] == x])
    descriptor_df['target_loss'] = descriptor_df.apply(
        lambda x: len(loss([descriptor['ui'] for descriptor in x['hits_original']],
                           [descriptor['ui'] for descriptor in x['hits_target']])),
        axis=1)
    descriptor_df['target_gain'] = descriptor_df.apply(
        lambda x: len(loss([descriptor['ui'] for descriptor in x['hits_target']],
                           [descriptor['ui'] for descriptor in x['hits_original']])),
        axis=1)
    descriptor_df['target_correct'] = descriptor_df.apply(
        descriptor_df['hits_target'] - descriptor_df['target_gain'],
        axis=1)
    descriptor_df['precision'] = descriptor_df.apply(
        precision(descriptor_df['target_correct'], descriptor_df['target_gain']),
        axis=1)
    descriptor_df['recall'] = descriptor_df.apply(
        recall(descriptor_df['target_correct'], descriptor_df['target_loss']),
        axis=1)
    descriptor_df['f_score'] = descriptor_df.apply(
        f_score(descriptor_df['precision'], descriptor_df['recall']),
        axis=1)

    # save data into a table
    writer = pd.ExcelWriter("MESH_comparison.xlsx", engine='xlsxwriter')
    summary_data = {'Precision': [base_precision, hierarchical_precision, lca_hierarchical_precision],
                    'Recall': [base_recall, hierarchical_recall, lca_hierarchical_recall],
                    'F-score': [base_f_score, hierarchical_f_score, lca_hierarchical_f_score]}
    summary_df = pd.DataFrame(summary_data, index=['Base', 'Hierarchical', 'Hierarchical (LCA)'])
    summary_df.to_excel(writer, sheet_name='Summary', index=True)
    descriptor_df.to_excel(writer, sheet_name='Descriptors')
    writer.save()
    """


if __name__ == '__main__':
    main()