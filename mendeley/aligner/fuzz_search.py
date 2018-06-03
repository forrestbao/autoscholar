#!/usr/bin/env python3

import time
from fuzzysearch import find_near_matches
from fuzz_common import test_dir, test_file, mutate


def str_split_length(s):
    res = []
    while s:
        splits = s.split(maxsplit=1)
        if len(splits) == 0:
            break
        elif len(splits) == 1:
            res.append(len(s))
            break
        else:
            res.append(len(s) - len(splits[1]))
            s = splits[1]
    return res


def fuzz_search(seq, pattern, max_dist=10):
    # use word level distance
    pattern_split = pattern.split()
    seq_split = seq.split()
    # keep a list of indexes
    lengths = str_split_length(seq)
    matches = find_near_matches(pattern_split, seq_split, max_l_dist=max_dist)
    if not matches:
        return 0, 0
    else:
        match = min(matches, key=lambda x: x.dist)
        start = sum(l for l in lengths[:match.start])
        end = sum(l for l in lengths[:match.end])
        # print(seq_split[match.start:match.end])
        return start, end
    pass


def fuzz_search_char(seq, pattern, max_dist=10):
    # use character distance
    matches = find_near_matches(pattern, seq, max_l_dist=max_dist)
    if not matches:
        return 0, 0
    else:
        match = min(matches, key=lambda x: x.dist)
        return match.start, match.end
    pass


if __name__ == '__hebi__':
    # 776s
    dir = '/home/hebi/github/autoscholar/mendeley/html-output/'
    t1 = time.time()
    test_dir(dir, fuzz_search)
    t2 = time.time()
    print('elapsed time ' + str(t2-t1))

    test_file('/home/hebi/github/autoscholar/mendeley/html-output/64.html',
              fuzz_search)
    sub = '<hl>cerevisiae'
    
    content = open('../html-output/64.html').read()
    start, end = fuzz_search(content, mutate(sub))
    start, end = fuzz_search_char(content, sub)

    find_near_matches(['<hl>cerevisiae'],
                      ['<hl>cerevisiae</hl>', 'hello', 'world'],
                      max_l_dist=5)
    print(content[start:end])
    pass

def test_distance(dir):
    for max_dist in (5, 8, 10, 13):
        t1 = time.time()
        suc, fail = test_dir(dir,
                             lambda x, y: fuzz_search(x, y, max_dist),
                             ratio=0.1)
        t2 = time.time()
        print('-----------------')
        print('max distance: ' + str(max_dist))
        print('elapsed time: ' + str(t2-t1))
        print('suc/fail: ' + str(suc) + '/' + str(fail))

def test_mutation(dir):
    for ratio in (0.05, 0.1, 0.2, 0.3):
        t1 = time.time()
        suc, fail = test_dir(dir,
                             lambda x, y: fuzz_search(x, y, 8),
                             ratio)
        t2 = time.time()
        print('-----------------')
        print('ratio: ' + str(ratio))
        print('elapsed time: ' + str(t2-t1))
        print('suc/fail: ' + str(suc) + '/' + str(fail))


# if __name__ == '__main__':
#     dir = '/home/hebi/github/autoscholar/mendeley/aligner/test/'
#     # test_distance(dir)
#     test_mutation(dir)
