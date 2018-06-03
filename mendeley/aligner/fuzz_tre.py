#!/usr/bin/env python2

# TRE only supports python2
import tre
import time
import re

from fuzz_common import test_dir, test_file, mutate


def tre_search(seq, pattern):
    # PARAM
    fz = tre.Fuzzyness(maxerr=150)
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

# if __name__ == '__main__':
#     dir = '/home/hebi/github/autoscholar/mendeley/html-output/'
#     t1 = time.time()
#     test_dir(dir, tre_search)
#     # time.sleep(1.2)
#     t2 = time.time()
#     print('elapsed time ' + str(t2-t1))
