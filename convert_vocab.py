#!/usr/bin/env python

import sqlite3
import argparse
from datetime import datetime


def pbar(iterable):
    try:
        from tqdm import tqdm
    except ImportError:
        return iterable
    else:
        return tqdm(iterable)


def get_vocab(vocab_db, _since=0):

    if isinstance(_since, datetime):
        since = int(_since.strftime('%s')) * 1000
    else:
        since = _since * 1000

    db = sqlite3.connect(vocab_db)
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    sql = '''
        select WORDS.stem, WORDS.word, LOOKUPS.usage, BOOK_INFO.title, LOOKUPS.timestamp
        from LOOKUPS left join WORDS
        on WORDS.id = LOOKUPS.word_key
        left join BOOK_INFO
        on BOOK_INFO.id = LOOKUPS.book_key
        where LOOKUPS.timestamp > ?
        order by WORDS.stem
    '''
    rows = cur.execute(sql, (since,)).fetchall()
    return rows


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--since', type=lambda s: datetime.strptime(s, '%Y-%m-%d'))
    argp.add_argument('vocab_db')
    argp.add_argument('anki_tsv')
    args = argp.parse_args()
    vocab = get_vocab(args.vocab_db)
    for v in vocab:
        print(datetime.utcfromtimestamp(v['timestamp'] / 1000), v['stem'], v['usage'], v['title'])
