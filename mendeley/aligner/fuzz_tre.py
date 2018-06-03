#!/usr/bin/env python2

# TRE only supports python2
import tre
import time
import re

from fuzz_common import test_dir, test_file, mutate


def tre_search(seq, pattern, max_dist=150):
    # PARAM
    fz = tre.Fuzzyness(maxerr=max_dist)
    # FIXME this escape might cause tre.compile to fail
    pattern = re.sub(r'[()\[\]]', '', pattern)
    # pt = tre.compile(re.escape(pattern))
    # print(pattern)
    pt = tre.compile(pattern)
    m = pt.search(seq, fz)
    if m:
        # m[0]
        return m.groups()[0]
    else:
        return 0, 0
    pass

# def agrep_search(path, pattern):
#     cmd = ('agrep -E 100 -d "hflsdajfdiosfdsn" --show-position '
#            + pattern + ' ' + path)
#     return

if __name__ == '__hebi__':
    dir = '/home/hebi/github/autoscholar/mendeley/html-output/'
    
    t1 = time.time()
    test_dir(dir, tre_search)
    # time.sleep(1.2)
    t2 = time.time()
    print('elapsed time ' + str(t2-t1))

    # 302s
    test_file('/home/hebi/github/autoscholar/mendeley/html-output/50.html',
              tre_search)
    # 67, 64

    sub = '<hl>Metabolic engineering for enhanced fatty acids synthesis in Saccharomyces'
    sub = '<hl>cerevisiae'
    sub = 'M9 minimal medium in the presence'
    content = open('../html-output/50.html').read()
    
    start, end = tre_search(content, mutate(sub))
    print(content[start:end])
    pass

def test_distance(dir):
    for max_dist in (10, 30, 50, 80, 100, 150, 200):
        t1 = time.time()
        suc, fail = test_dir(dir,
                             lambda x, y: tre_search(x, y, max_dist))
        # time.sleep(1.2)
        t2 = time.time()
        print('-----------------')
        print('max distance: ' + str(max_dist))
        print('elapsed time: ' + str(t2-t1))
        print('suc/fail: ' + str(suc) + '/' + str(fail))

def test_mutation(dir):
    for ratio in (0.05, 0.1, 0.2, 0.3):
        t1 = time.time()
        suc, fail = test_dir(dir,
                             lambda x, y: tre_search(x, y, 100),
                             ratio)
        # time.sleep(1.2)
        t2 = time.time()
        print('-----------------')
        print('ratio: ' + str(ratio))
        print('elapsed time: ' + str(t2-t1))
        print('suc/fail: ' + str(suc) + '/' + str(fail))
    
# if __name__ == '__main__':
#     dir = '/home/hebi/github/autoscholar/mendeley/aligner/test/'
#     # test_distance(dir)
#     test_mutation(dir)
