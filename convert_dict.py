#!/usr/bin/env python

from tqdm import tqdm
from bs4 import BeautifulSoup


def main(book, dic):

    with open(book, 'r') as f:
        html = f.read()
    print('Parsing markup data, this may take a while ...')
    soup = BeautifulSoup(html, 'xml')

    with open(dic, 'w') as f:
        for entry in tqdm(soup.html.body.contents):
            if entry.name != 'entry':
                continue
            orth, *_definition = entry.contents
            stem = orth['value']
            iforms = [i['value'] for i in orth.find_all('iform')]
            definition = ''.join(
                str(tag) for tag in _definition
                if tag.name != 'a'  # anchors do not work in Anki, strip them
            )
            f.write(f'{stem}\t{definition}\n')
            for iform in iforms:
                f.write(f'{iform}\t{definition}\n')


if __name__ == '__main__':
    import sys
    try:
        book, dic = sys.argv[1:]
    except ValueError:
        raise SystemExit(f'Usage: {__file__} book.html dict.txt')
    main(book, dic)
