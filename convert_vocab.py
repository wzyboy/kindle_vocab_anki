#!/usr/bin/env python

import sys
import sqlite3
import argparse
import itertools
from datetime import datetime
from operator import itemgetter
from operator import attrgetter
from collections import namedtuple


AnkiNote = namedtuple('AnkiNote', 'word usage definition timestamp')


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
        order by WORDS.stem, LOOKUPS.timestamp
    '''
    rows = cur.execute(sql, (since,)).fetchall()
    return rows


def make_notes(vocab, dict_tsv):

    # OALD is ~38 MiB for each stem and ~110 MiB for each iform,
    # read it all into a Python dict does not hurt on mordern PCs.
    with open(dict_tsv, 'r') as f:
        dict_db = dict(line.split('\t') for line in f.readlines())

    stems_no_def = set()
    notes = []
    # vocab is a list of db rows order by (stem, timestamp)
    for stem, entries in itertools.groupby(vocab, itemgetter('stem')):
        # Merge multiple usages into one.
        usage_all = ''
        usage_timestamp = None
        for entry in entries:
            word = entry['word']
            _usage = entry['usage'].replace(word, f'<strong>{word}</strong>').strip()
            usage = f'<blockquote>{_usage}<small>{entry["title"]}</small></blockquote><br/>'
            usage_all += usage
            usage_timestamp = entry['timestamp']

        # Look up definition in dictionary
        try:
            definition = dict_db[stem].strip()
        except KeyError:
            stems_no_def.add(stem)
            definition = None

        note = AnkiNote(stem, usage_all, definition, usage_timestamp)
        notes.append(note)

    if stems_no_def:
        print(f'WARNING: Some words cannot be found in dictionary:\n{stems_no_def}', file=sys.stderr)

    return notes


def output_anki_tsv(notes, output, sort=True):

    if sort:
        notes.sort(key=attrgetter('timestamp'), reverse=True)

    with output as f:
        for note in pbar(notes):
            line = f'{note.word}\t{note.usage}\t{note.definition}\n'
            f.write(line)


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--since', type=lambda s: datetime.strptime(s, '%Y-%m-%d'), default=datetime.utcfromtimestamp(0))
    argp.add_argument('vocab_db')
    argp.add_argument('dict_tsv')
    argp.add_argument('anki_tsv', type=argparse.FileType('w'))
    args = argp.parse_args()
    vocab = get_vocab(args.vocab_db, _since=args.since)
    notes = make_notes(vocab, args.dict_tsv)
    output_anki_tsv(notes, args.anki_tsv)
