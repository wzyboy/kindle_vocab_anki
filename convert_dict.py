#!/usr/bin/env python

import argparse

from tqdm import tqdm
from bs4 import BeautifulSoup
from bs4 import SoupStrainer


def main(dict_html, dict_tsv, expand_iform=False):

    print('Parsing markup data, this may take a while ...')
    parse_only_entry = SoupStrainer('entry')
    with open(dict_html, 'r') as f:
        soup = BeautifulSoup(f, 'xml', parse_only=parse_only_entry)

    print('Converting HTML dictionary into TSV dictionary ...')
    with open(dict_tsv, 'w') as f:
        for entry in tqdm(soup.find_all('entry')):
            orth, *_definition = entry.contents
            stem = orth['value']
            iforms = [i['value'] for i in orth.find_all('iform')]
            definition = ''.join(
                str(tag) for tag in _definition
                if tag.name != 'a'  # anchors do not work in Anki, strip them
            ).strip()
            f.write(f'{stem}\t{definition}\n')
            if expand_iform:
                for iform in iforms:
                    f.write(f'{iform}\t{definition}\n')


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('dict_html')
    argp.add_argument('dict_tsv')
    argp.add_argument('--expand-iform', action='store_true')
    args = argp.parse_args()
    main(args.dict_html, args.dict_tsv, args.expand_iform)
