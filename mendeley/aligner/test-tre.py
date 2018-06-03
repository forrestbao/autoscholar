#!/usr/bin/env python2

import tre


import os
import math
import random
import uuid

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
    num = int(math.ceil(len(words) / 30.0))
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
        pattern = content[start:end]
        mutated_pattern = mutate(pattern)
        # mutated_pattern = pattern
        print('------ ' + str(start) + ',' + str(end) + ' -------')
        res_start, res_end = tre_search(content, mutated_pattern)
        if res_start == res_end == 0:
            print('no match')
        elif abs(start - res_start) < 30 and abs(end - res_end) < 30:
            print('success')
            print(start, res_start, end, res_end)
        else:
            print('fail')
            print(start, res_start, end, res_end)
            print('pattern: ' + pattern)
            print('mutated: ' + mutated_pattern)
            print('result: ' + content[res_start:res_end])

def test(p):
    for root, dirs, files in os.walk(p):
        for f in files:
            if f.endswith('.html'):
                p = os.path.join(root, f)
                print('==============================')
                print(p)
                test_file(p)

def tre_search(seq, pattern):
    fz = tre.Fuzzyness(maxerr=100)
    # FIXME this escape might cause tre.compile to fail
    # pt = tre.compile(re.escape(pattern))
    pt = tre.compile(pattern)
    m = pt.search(seq, fz)
    if m:
        return m.groups()[0]
    else:
        return 0,0

if __name__ == '__hebi__':
    test('../html-output/')
    test_file('../html-output/70.html')
    test_file('../html-output/71.html')
    sub = '<hl>Metabolic engineering for enhanced fatty acids synthesis in Saccharomyces'
    sub = '<hl>cerevisiae'
    sub = 'M9 minimal medium in the presence'
    content = open('../html-output/71.html').read()
    
    start, end = tre_search(content, sub)

    find_near_matches(['<hl>cerevisiae'],
                      ['<hl>cerevisiae</hl>', 'hello', 'world'], max_l_dist = 5)
    print(content[start:end])


def test_tre():
    fz = tre.Fuzzyness(maxerr = 100)

    subseq = '''
    Phleomycin  for double gene disruption. The selective
    medium for gene insertion strains was YNBD-URA 
    minimalist add some words medium (0.67% yeast nitrogen base, subcontaining 2%
    <hl>glucose and supplemented with URA dropout amino acidence mix
    '''
    
    pt = tre.compile("Don(ald( Ervin)?)? Knuth", tre.EXTENDED)

    pt = tre.compile(subseq)
    data = """
    In addition to fundamental contributions in several branches of
    theoretical computer science, Donnald Erwin Kuth is the creator of the
    TeX computer typesetting system, the related METAFONT font definition
    language and rendering system, and the Computer Modern family of
    typefaces.
    """
    data = open('../html-output/70.html').read()

    m = pt.search(data, fz)

    if m:
        print m.groups()
        print m[0]
