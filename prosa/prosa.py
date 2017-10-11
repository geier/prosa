# coding: utf-8

import operator
from collections import defaultdict
import pickle


FILENAME = '/home/cg/markov.pickle'

file = open(FILENAME, 'rb')
alldata = pickle.load(file)
DATA = alldata['data']
COUNTS = alldata['counts']

FACTOR_1_1 = 1
FACTOR_2_1 = 2
FACTOR_2_2 = 2


def unique(items):
    already = set()
    add = already.add
    return [elem for elem in items if not (elem in already or add(elem))]


def clean_tokens(tokens):
    return [token.strip('.,:;!?)(<>') for token in tokens]


def get_markov(tokens):
    tokens = clean_tokens(tokens)
    out = list()
    try:
        tokens_2_2 = sorted(DATA[2, 2][tokens[-2], tokens[-1]].items(), key=operator.itemgetter(1), reverse=True)[:5]
    except (IndexError, KeyError):
        pass
    else:
        factor = COUNTS[2, 2][tokens[-2], tokens[-1]]
        tokens_2_2 = [(' '.join(item), count * FACTOR_2_2 / factor) for item, count in tokens_2_2]
        out.extend(tokens_2_2)

    try:
        tokens_2_1 = sorted(DATA[2, 1][tokens[-2], tokens[-1]].items(), key=operator.itemgetter(1), reverse=True)[:5]
    except (IndexError, KeyError):
        pass
    else:
        factor = COUNTS[2, 1][tokens[-2], tokens[-1]]
        tokens_2_1 = [(item, count * FACTOR_2_1 / factor) for item, count in tokens_2_1]
        out.extend(tokens_2_1)

    try:
        tokens_1_1 = sorted(DATA[1, 1][tokens[-1]].items(), key=operator.itemgetter(1), reverse=True)[:5]
    except (IndexError, KeyError):
        pass
    else:
        factor = COUNTS[1, 1][tokens[-1]]
        tokens_1_1 = [(item, count * FACTOR_1_1 / factor) for item, count in tokens_1_1]
        out.extend(tokens_1_1)

    out = sorted(out, key=operator.itemgetter(1), reverse=True)
    out = unique([item for item, count in out])
    return out
