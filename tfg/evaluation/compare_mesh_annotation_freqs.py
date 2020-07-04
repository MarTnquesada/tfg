import argparse
import pandas as pd
from tfg.utilities import parse_mesh
import pickle
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt


def plot_distributions(descriptor_codes, descriptor_freqs, descriptor_freqs_nm, descriptor_freqs_colour):
    for distr, colour in zip(descriptor_freqs, descriptor_freqs_colour):
        y = [distr.get(descriptor_code, 0) for descriptor_code in descriptor_codes]
        plt.plot(descriptor_codes, y, color=colour)
        # plt.fill_between(descriptor_codes, 0, y)
    # plt.title()
    plt.xlabel('MeSH Descriptors ')
    plt.ylabel('Frequency')
    plt.legend(descriptor_freqs_nm)
    ax = plt.gca()
    ax.axes.get_xaxis().set_ticks([])
    plt.ylim(bottom=0.0, top=0.6)
    plt.show()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_lang_annotation',
                        help='xlsx file where each row corresponds to an annotation performed over a corpus using '
                             'the source language MESH thesaurus')
    parser.add_argument('--source_lang_name')
    parser.add_argument('--source_lang_colour')
    parser.add_argument('--target_lang_annotation',
                        help='xlsx file where each row corresponds to an annotation performed over a corpus using '
                             'the target language MESH thesaurus')
    parser.add_argument('--target_lang_name')
    parser.add_argument('--target_lang_colour')
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
    descriptor_df = pd.DataFrame(descriptor_list)
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
    # obtain all original and target(s) frequencies to fill descriptor_df
    descriptor_df['freq_original'] = descriptor_df['ui'].apply(
        lambda x: sum(1 for descriptors in aligned_df['descriptors_original'] if x in set([d['ui'] for d in descriptors]))/ len(aligned_df))
    # sort frequencies in descending order according to the original data
    descriptor_df = descriptor_df.sort_values(by=['freq_original'], ascending=False)
    descriptor_df['freq_target'] = descriptor_df['ui'].apply(
        lambda x: sum(1 for descriptors in aligned_df['descriptors_target'] if x in set([d['ui'] for d in descriptors])) / len(aligned_df))
    maximum = descriptor_df['freq_target'].idxmax()
    print(descriptor_df.iloc[maximum])
    plot_distributions(descriptor_codes=descriptor_df['ui'],
                       descriptor_freqs=[{code: freq for code, freq in zip(descriptor_df['ui'], descriptor_df['freq_original'])},
                                         {code: freq for code, freq in zip(descriptor_df['ui'], descriptor_df['freq_target'])}],
                       descriptor_freqs_nm=[args.source_lang_name, args.target_lang_name],
                       descriptor_freqs_colour=[args.source_lang_colour, args.target_lang_colour])


if __name__ == '__main__':
    main()
    plot_distributions(descriptor_codes=['a', 'b', 'c', 'd', 'e', 'f'],
                       descriptor_freqs=[{'a': 0.2, 'b':0.3, 'c':0.7, 'd':0.1, 'e': 0.01, 'f':0.8},
                                         {'a': 0.1, 'b':0.2, 'c':0.5, 'd':0.4, 'e': 0.3, 'f':0.1}],
                       descriptor_freqs_nm=['Yoshi', 'Waluigi'],
                       descriptor_freqs_colour=['red', 'black'])
