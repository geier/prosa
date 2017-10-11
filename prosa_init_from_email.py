# coding: utf-8

from collections import defaultdict
import email
from email.header import decode_header
import codecs
from html.parser import HTMLParser
import pickle

import notmuch

FILENAME = '/home/cg/markov.pickle'

DATA = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
COUNTS = defaultdict(lambda: defaultdict(int))


def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d


def unique(items):
    already = set()
    add = already.add
    return [elem for elem in items if not (elem in already or add(elem))]


class MLStripper(HTMLParser):

    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def get_tokens(msg):
    """split an email into tokens

    :type msg: email.message
    """
    tokens = list()

    if msg['Subject'] is not None:
        for text, encoding in decode_header(msg['Subject']):
            if encoding is not None:
                text = text.decode(encoding)
                tokens.extend(text.split())

    for part, charset in zip(msg.walk(), msg.get_charsets()):
        try:
            codecs.lookup(charset)
        except (LookupError, TypeError):
            charset = 'ascii'

        if part.get_content_type() not in ['text/plain', 'text/html']:
            continue
        payload = part.get_payload(decode=True).decode(charset, 'ignore')  # TODO fix broken html encodings
        if part.get_content_type() == 'text/html':
            payload = strip_tags(payload)

        lines = payload.splitlines()
        for num, line in enumerate(lines):
            if line.startswith('> '):
                break
            else:
                tokens += line.split()
    return tokens


def clean_tokens(tokens):
    return [token.strip('.,:;!?)(<>') for token in tokens]


def set_markov(tokens):
    for current, next in zip(tokens[:-1], tokens[1:]):
        DATA[1, 1][current][next] += 1
        COUNTS[1, 1][current] += 1
    for previous, current, next in zip(tokens[:-2], tokens[1:-1], tokens[2:]):
        DATA[2, 1][(previous, current)][next] += 1
        COUNTS[2, 1][previous, current] += 1
    for previous, current, next, after in zip(tokens[:-3], tokens[1:-2], tokens[2:-1], tokens[3:]):
        DATA[2, 2][(previous, current)][(next, after)] += 1
        COUNTS[2, 2][previous, current] += 1


def populate_from_mail():
    db = notmuch.Database()
    query = db.create_query('from:geier@lostpackets.de OR from:geier@uni-bonn.de')
    messages = query.search_messages()
    for message in messages:
        filename = message.get_filename()
        file = open(filename, 'rb')
        msg = email.message_from_binary_file(file)

        tokens = get_tokens(msg)
        tokens = clean_tokens(tokens)
        set_markov(tokens)


if __name__ == '__main__':
    populate_from_mail()

    pickle.dump(
        {'data': default_to_regular(DATA), 'counts': default_to_regular(COUNTS)},
        open(FILENAME, 'bw'),
        protocol=2,
    )
