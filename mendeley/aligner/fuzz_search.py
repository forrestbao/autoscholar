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


def fuzz_search_word(seq, pattern):
    # use word level distance
    pattern_split = pattern.split()
    seq_split = seq.split()
    # keep a list of indexes
    lengths = str_split_length(seq)
    matches = find_near_matches(pattern_split, seq_split, max_l_dist=10)
    if not matches:
        return 0, 0
    else:
        match = min(matches, key=lambda x: x.dist)
        start = sum(l for l in lengths[:match.start])
        end = sum(l for l in lengths[:match.end])
        # print(seq_split[match.start:match.end])
        return start, end
    pass


def fuzz_search(seq, pattern):
    # use character distance
    matches = find_near_matches(pattern, seq, max_l_dist=10)
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
    test_dir(dir, fuzz_search_word)
    t2 = time.time()
    print('elapsed time ' + str(t2-t1))

    test_file('/home/hebi/github/autoscholar/mendeley/html-output/64.html',
              fuzz_search_word)
    sub = '<hl>cerevisiae'
    
    content = open('../html-output/64.html').read()
    start, end = fuzz_search_word(content, mutate(sub))
    start, end = fuzz_search(content, sub)

    find_near_matches(['<hl>cerevisiae'],
                      ['<hl>cerevisiae</hl>', 'hello', 'world'],
                      max_l_dist=5)
    print(content[start:end])
    pass

# if __name__ == '__main__':
#     dir = '/home/hebi/github/autoscholar/mendeley/html-output/'
#     t1 = time.time()
#     test_dir(dir, fuzz_search_word)
#     t2 = time.time()
#     print('elapsed time ' + str(t2-t1))
