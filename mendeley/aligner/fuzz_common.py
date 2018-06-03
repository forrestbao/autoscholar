#!/usr/bin/env python

import os
import math
import random
import uuid

def random_word():
    return uuid.uuid4().hex[:10]

def mutate(s, ratio=0.1):
    words = s.split()
    # PARAM do not mutate for too small string
    if len(words) < 10:
        return s
    # PARAM: ratio of mutation
    # mutate 10% of the sentence
    num = int(math.ceil(len(words) * ratio / 3.0))
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

# read html output file. This are the files generated from PDF, not
# the downloaded webpage, because the webpage contains so many html
# tags.
#
# The experiment read each of the file. For each of them, get the text
# within each <hl></hl> tag. For each of them, randomly mutate the
# string by some distance in word level. Then, invoke the procedure to
# fuzzy search, and report found or not.
def test_file(f, func, verbose=False, ratio=0.1):
    content = open(f).read()
    start_indexes = indexes_of(content, '<hl>')
    end_indexes = indexes_of(content, '</hl>')
    assert(len(start_indexes) == len(end_indexes))
    suc=0
    fail=0
    for start, end in zip(start_indexes, end_indexes):
        pattern = content[start:end]
        # PARAM: do not match too small string
        if (len(pattern.split()) < 3):
            continue
        mutated_pattern = mutate(pattern)
        # mutated_pattern = pattern
        if verbose:
            print('------ ' + str(start) + ',' + str(end) + ' -------')
        res_start, res_end = func(content, mutated_pattern)
        if res_start == res_end == 0:
            fail+=1
            if verbose:
                print('no match')
                print('pattern: ' + pattern)
                print('mutated: ' + mutated_pattern)
        elif abs(start - res_start) < 30 and abs(end - res_end) < 30:
            # parameter: index shift (due to words split precision <br>AWord)
            suc+=1
            if verbose:
                print('success')
                print(start, res_start, end, res_end)
        else:
            fail+=1
            if verbose:
                print('fail')
                print(start, res_start, end, res_end)
                print('pattern: ' + pattern)
                print('mutated: ' + mutated_pattern)
                print('result: ' + content[res_start:res_end])
    # print('suc/fail: ' + str(suc) + "/" + str(fail))
    return suc,fail


def test_dir(p, func, ratio=0.1):
    suc = 0
    fail = 0
    for root, dirs, files in os.walk(p):
        for f in files:
            if f.endswith('.html'):
                p = os.path.join(root, f)
                # print('==============================')
                print(p)
                a, b = test_file(p, func, ratio=ratio)
                suc += a
                fail += b
    return suc, fail
