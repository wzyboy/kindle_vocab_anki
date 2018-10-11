#!/usr/bin/env python

import re
import argparse
from ast import literal_eval

from tqdm import tqdm
from bs4 import BeautifulSoup


def main(dict_html, dict_tsv, expand_iform=False, expand_kanji=False, sep='\t'):

    print('Parsing markup data, this may take a while ...')
    with open(dict_html, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml-html')

    print('Converting HTML dictionary into TSV dictionary ...')
    with open(dict_tsv, 'w', encoding='utf-8') as f:
        for entry in tqdm(soup.find_all('idx:entry')):

            orth = entry.find('idx:orth')
            stem = orth['value']
            iforms = [i['value'] for i in orth.find_all('idx:iform')]

            _definition = []
            for n in entry.next_siblings:
                if n.name == 'hr':
                    break
                _definition.append(n)

            definition = ''.join(
                str(tag) for tag in _definition
                if tag.name != 'a'  # anchors do not work in Anki, strip them
            ).strip()

            # XXX: Search for and expand kanjis
            match_kanji = re.search('【(.*)】', definition)
            if match_kanji:
                kanjis = match_kanji.group(1).strip().split('、')
            else:
                kanjis = []

            f.write(f'{stem}{sep}{definition}\n')
            if expand_iform:
                for iform in iforms:
                    f.write(f'{iform}{sep}{definition}\n')
            if expand_kanji:
                for kanji in kanjis:
                    f.write(f'{kanji}{sep}{definition}\n')


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('dict_html')
    argp.add_argument('dict_tsv')
    argp.add_argument('--expand-iform', action='store_true')
    argp.add_argument('--expand-kanji', action='store_true')
    argp.add_argument('--seperator', type=lambda x: literal_eval(f"'''{x}'''"), default='\t')
    args = argp.parse_args()

    main(
        args.dict_html, args.dict_tsv,
        expand_iform=args.expand_iform,
        expand_kanji=args.expand_kanji,
        sep=args.seperator
    )
