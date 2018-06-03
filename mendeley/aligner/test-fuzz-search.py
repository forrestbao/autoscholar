#!/usr/bin/env python3

import os
import math
import random
import uuid

from fuzzysearch import find_near_matches

# read html output file. This are the files generated from PDF, not
# the downloaded webpage, because the webpage contains so many html
# tags.

# The experiment read each of the file. For each of them, get the text
# within each <hl></hl> tag. For each of them, randomly mutate the
# string by some distance in word level. Then, invoke the procedure to
# fuzzy search, and report found or not.

def random_word():
    return uuid.uuid4().hex[:10]

def mutate(s):
    words = s.split()
    # mutate 10% of the sentence
    num = math.ceil(len(words) / 30)
    # deletion
    for _ in range(num):
        if len(words) > 0:
            idx = random.randint(0, len(words)-1)
            words.pop(idx)
    # substituting
    for _ in range(num):
        if len(words) > 0:
            idx = random.randint(0, len(words)-1)
            words[idx] = random_word()
    # insertion
    for _ in range(num):
        idx = random.randint(0, len(words))
        words.insert(idx, random_word())
    return ' '.join(words)
    
def indexes_of(s, sub):
    def helper(s, sub):
        start = 0
        while True:
            start = s.find(sub, start)
            if start == -1:
                return
            yield start
            start += len(sub)
    return list(helper(s, sub))
        
def test_file(f):
    content = open(f).read()
    start_indexes = indexes_of(content, '<hl>')
    end_indexes = indexes_of(content, '</hl>')
    assert(len(start_indexes) == len(end_indexes))
    for start, end in zip(start_indexes, end_indexes):
        print(start, end)
        pattern = content[start:end]
        # pattern = mutate(pattern)
        res_start, res_end = fuzzy_search_word(content, pattern)
        if res_start == res_end == 0:
            print('no match')
            print(pattern)
        elif abs(start - res_start) < 30 and abs(end - res_end) < 30:
            print('success')
        else:
            print('fail')
            print(start, end, res_start, res_end)
            print(pattern)
            print(content[res_start:res_end])

def test(p):
    for root, dirs, files in os.walk(p):
        for f in files:
            if f.endswith('.html'):
                test_file(f)

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

def fuzzy_search_word(seq, pattern):
    # return string
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

def fuzzy_search(seq, pattern):
    matches = find_near_matches(pattern, seq, max_l_dist=10)
    if not matches:
        return 0, 0
    else:
        match = min(matches, key=lambda x: x.dist)
        return match.start, match.end

if __name__ == '__hebi__':
    test('../html-output/')
    test_file('../html-output/70.html')
    sub = '<hl>Metabolic engineering for enhanced fatty acids synthesis in Saccharomyces'
    sub = '<hl>cerevisiae'
    content = open('../html-output/70.html').read()
    start, end = fuzzy_search_word(content, sub)
    start, end = fuzzy_search(content, sub)

    find_near_matches(['<hl>cerevisiae'],
                      ['<hl>cerevisiae</hl>', 'hello', 'world'], max_l_dist = 5)
    print(content[start:end])
        

def test_fuzzysearch():
    subseq = '''
    Phleomycin  for double gene disruption. The selective
    medium for gene insertion strains was YNBD-URA 
    minimalist add some words medium (0.67% yeast nitrogen base, subcontaining 2%
    <hl>glucose and supplemented with URA dropout amino acidence mix
    '''

    seq = open('../html-output/70.html').read()

    subseq = subseq.split()
    seq = seq.split()
    find_near_matches(subseq, seq, max_l_dist=100)
