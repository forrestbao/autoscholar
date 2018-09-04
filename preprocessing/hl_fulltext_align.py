#!/usr/bin/env python

# take two inputs:
# - publisher HTML
# - highlight html

# output:
# label, sentence
# 0, "xxx" (highlight)
# 1, "xxx" (other)

from bs4 import BeautifulSoup
import csv
import tempfile
import subprocess
import re
import doctest
import math
import os
# Need to install nltk and then download nltk.download('punkt')
import nltk
import signal
import time
import argparse

from . full_text_html_extract import html2text

def devide_string(string, num_interval):
    """Devide string into intervals

    >>> devide_string('hello world lalala', 2)
    ['hello wor', 'ld lalala']
    """
    assert num_interval > 0
    if num_interval == 1:
        return [string]
    else:
        res = []
        interval = math.ceil(len(string) / num_interval)
        for i in range(num_interval):
            start = interval * i
            # using ceil means this end value is at least the lenght
            # of the string. It is find if it is out of bound
            end = start + interval
            res.append(string[start:end])
        return res


def fuzzy_search_wrapper(string, pattern, max_dist=100):
    # I'm going to determine the distance. It seems that 1000
    # character tempt to have 150 errors. For those with a lot of
    # <a>s, there will be more. So it is probabaly desired to use 1/5
    # as the ratio. Also, I should set the number of errors up to 150,
    # because larger than 200, the performance is not good.

    # Update: actually when the pattern is too long, agrep will throw
    # "agrep: Error in search pattern: Out of memory" error. So, I'm
    # going to restrict the pattern to be less than 1000. For those
    # larger than 1000, devide into equal parts, and concate them in
    # the end.

    num_interval = 1
    # 500 seems to be a good magic number for max interval size
    if len(pattern) > 500:
        num_interval = math.ceil(len(pattern) / 500)
    patterns = devide_string(pattern, num_interval)
    res = []
    res_d = 0
    for p in patterns:
        # FIXME actually here I should have used max_dist/num_interval
        # (not so good), or check whether the dist is less than
        # max_dist (better), because that should meant to be the total
        # distance for all intervals, to keep the interface
        # consistent. But this is not so important.
        fuzz_res = fuzzy_search(string, p, max_dist=max_dist)
        # we need to find all of them to be valid
        if not fuzz_res: return None
        begin, end, d = fuzz_res
        res_d += d
        res.append((begin, end))
    # merge
    # print(res)
    res = merge_sort_indexes(res, gap=100)
    # print(res)
    # print(pattern)
    # FIXME but I need to make sure they are actually continuous
    # assert len(res) <= 1
    if len(res) > 1:
        print('warning: gap too large:', res)
        return None
    if not res: return None
    else:
        return res[0][0], res[0][1], res_d
    
class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

        
def fuzzy_search_timeout(string, pattern, max_dist=100):
    sec = math.ceil(len(pattern) / 500)
    with timeout(seconds=sec):
        try:
            res = fuzzy_search_wrapper(string, pattern, max_dist=max_dist)
            return res
        except TimeoutError:
            print('timeout')
            return None
        
        
def fuzzy_search_multi(string, pattern):
    """Run agrep with multiple distance configuration. Return as long as
    one of them succeeds.
    """
    # try 100, 120, 150, 200
    res = fuzzy_search_timeout(string, pattern, max_dist=100)
    if res:
        return res
    res = fuzzy_search_timeout(string, pattern, max_dist=120)
    if res:
        return res
    res = fuzzy_search_timeout(string, pattern, max_dist=150)
    if res:
        return res
    res = fuzzy_search_timeout(string, pattern, max_dist=200)
    if res:
        return res
    print('warning: cannot find "' +
          '(' + str(len(pattern)) + ') ' +
          pattern.replace('\n', ' ') +
          '"')
    return None

    
    
# implement tre_search using subprocess call to agrep.  When the
# string is long, it might be imprecise. For an example, for 42, use
# the last highlight. It says the distance is 7 (which means perfect
# alignment), but the returned string is not aligned.
def fuzzy_search(string, pattern, max_dist=120):
    """fuzzy search pattern in string. Return (start,end,dist).

    Keyword arguments:
    max_dist -- character level edit distance allowed

    >>> fuzzy_search("hello world xxx", "word")
    (6, 11, 1)
    """

    # write string into a temp [file]
    fp = tempfile.NamedTemporaryFile(mode='w')
    fp.write(string)
    fp.flush()
    # pattern should not contain brackets
    pattern = re.sub(r'[()\[\]]', '', pattern)
    # run agrep in shell
    cmd = ['tre-agrep', '-E', str(max_dist), '-d',
           'fjdsilfadsj', '--show-position',
           # treat pattern as literal. This should increase
           # performance
           '--literal',
           # only match whole word
           '--word-regexp',
           '--show-cost',
           '--delete-cost=1',
           '--insert-cost=1',
           # disable direct substitute
           '--substitute-cost=3',
           pattern,
           fp.name]
    # print(' '.join(cmd))
    completed = subprocess.run(cmd, stdout=subprocess.PIPE)
    output = completed.stdout.decode('utf8')
    # print(output)
    # parse results
    res = re.search('(\d+):(\d+)-(\d+)', output)
    # print('temp name: ' + fp.name)
    # fp.close()
    if res:
        d = int(res.group(1))
        start = int(res.group(2))
        end = int(res.group(3))
        return start, end, d
    else:
        # print('warning: cannot find "' +
        #       '(' + str(len(pattern)) + ') ' +
        #       pattern.replace('\n', ' ') +
        #       '"')
        return None


# sort indexes (indexes should not overlap)
# if overlap, combine them
def merge_sort_indexes(indexes, gap=5):
    """Merge and sort the indexes

    Update: Merge two indexes if they have very small gap (5)

    # >>> merge_sort_indexes([(1,2), (5,7), (3,4)])
    # [(1, 2), (3, 4), (5, 7)]
    # >>> merge_sort_indexes([(3,7), (1,2), (5,8)])
    # [(1, 2), (3, 8)]
    >>> merge_sort_indexes([(1,2), (3,4), (7,8)])
    [(1, 8)]
    >>> merge_sort_indexes([(1,2), (7,8)])
    [(1, 2), (7, 8)]
    >>> merge_sort_indexes([(1,2), (8,9), (11,12)])
    [(1, 2), (8, 12)]
    """
    indexes = sorted(indexes, key=lambda x: x[0])
    i = 0
    while i < len(indexes)-1:
        # if indexes[i][1] >= indexes[i+1][0]:
        if indexes[i+1][0] - indexes[i][1] < gap:
            indexes[i] = (indexes[i][0],
                          max(indexes[i][1],
                              indexes[i+1][1]))
            indexes.remove(indexes[i+1])
            # do not increase i
        else:
            i += 1
    return indexes


def complete_indexes(indexes, upper):
    """OBSOLETE return the complete indexes, up to upper

    Precondition: indexes are sorted after merge_sort_indexes
    
    Also, this should be called after merge_with_gap to allow some
    level of permission.
    
    >>> complete_indexes([(1, 2), (3, 4), (5, 7)], 10)
    [(0, 1), (2, 3), (4, 5), (7, 10)]
    >>> complete_indexes([(1, 2), (3, 8)], 10)
    [(0, 1), (2, 3), (8, 10)]

    """

    res = []
    if not indexes: return res
    start = 0
    for index in indexes:
        if start < index[0]:
            res.append((start, index[0]))
        start = index[1]
    if indexes[-1][1] < upper:
        res.append((indexes[-1][1], upper))
    return res


def extend_lists(ls):
    """Extend lists

    >>> extend_lists([[1,2], [3,4,5], [6,7]])
    [1, 2, 3, 4, 5, 6, 7]
    """
    res = []
    for l in ls:
        res.extend(l)
    return res

# TODO now I need to consider rewrite string to remove tags, get the
# alignment, and put the html tags back. This is because the html tags
# creates a lot of noise in aligning the tags
#
# Basically
# 1. find the location of all tags <...> </...>
# 2. remove those tags
# 3. do alignment, get start and end index
# 4. augment back the indexes with the consideration of removed tags location


def treat_tag(string):
    """Remove html tags and return a tuple.

    1. the clean string, and 2. the list of index of removed
    content. [(start, length), (start, length)], where the start is
    the index in the new clean string

    """
    removals = [(m.start(), m.end()) for m in re.finditer('<[^>]*>', string)]
    removed = 0
    res = []
    for r in removals:
        length = r[1] - r[0]
        start = r[0] - removed
        removed += length
        res.append((start, length))
    return (re.sub('<[^>]*>', '', string), res)


def recover_tag(index, removed_indexes):
    """Recover the indexes by considering the removed_indexes back.
    """
    def func(pos):
        return pos + sum([r[1] for r in removed_indexes if r[0] < pos])
    return func(index[0]), func(index[1])


def treat_unicode(string):
    unicode_indexes = [idx for idx, c in enumerate(string)
                       if ord(c) > 127]
    res = ''.join([c for c in string if ord(c) <= 127])
    return res, unicode_indexes


def recover_unicode(index, unicode_indexes):
    def func(pos):
        return pos + len([i for i in unicode_indexes if i < pos])
    return func(index[0]), func(index[1])


def append_lists(lsts):
    ret = []
    for l in lsts:
        ret += l
    return ret


def shift_magic_index(magic_index, hl_indexes):
    ret = []
    for index in hl_indexes:
        start = index[0]
        end = index[1]
        magic_start = magic_index[0]
        magic_end = magic_index[1]
        if start > magic_end or end < magic_start:
            ret.append(index)
        elif start < magic_start and end > magic_end:
            # magic string inside
            ret.append((start, magic_start))
            ret.append((magic_end, end))
        elif start > magic_start and end < magic_end:
            pass
        elif start >= magic_start and start <= magic_end:
            ret.append((magic_end, end))
        elif end >= magic_start and end <= magic_end:
            ret.append((start, magic_end))
        else:
            # should not reach here
            pass
    return ret


def shift_magic_indexes(magic_indexes, hl_indexes):
    ret = hl_indexes
    for index in magic_indexes:
        ret = shift_magic_index(index, ret)
    return ret


def adjust_word_breaking(publisher_content, indexes):
    """fine tune the indexes so that it does not split a word.

    I'm including the word here. This should be removed when I use
    --word-regexp option of agrep, but seems there are still such
    cases.
    
    A more powerful one is to analyze the sentence endding and if the
    segment is around the ending, use the ending instead.
    """
    def adjust_one(content, index):
        start = index[0]
        end = index[1]
        if (start > 0
            and not content[start].isspace()
            and content[start-1].isalnum()):
            start = re.search(r'(\w+)$', content[:start]).start()
        if end < len(publisher_content) and content[end].isalnum():
            end += re.search(r'^(\w+)', content[end:]).end()
        return (start, end)
    return [adjust_one(publisher_content, index) for index in indexes]


def align(publisher_html, extract_html, output_file):
    # open files
    # get all highlights
    # align highlights
    print('getting highlights ..')
    # need to use lxml, because html.parser is not good at
    # <hl>xxx</br>yyy</hl>, which will parse as <hl>xxx</hl>

    
    # Heuristics to remove table cells
    magic_string = 'AUTOSCHOLARREMOVE'
    extract_html_content = open(extract_html).read()
    extract_html_content = re.sub(r'\n[0-9\.±+\-%() ]*</?br ?/?>',
                                  magic_string,
                                  extract_html_content)
    extract_html_content = re.sub(r'\n\w*</?br/?>',
                                  magic_string,
                                  extract_html_content)
    def remove_short_lines(s):
        lines = s.split('\n')
        def qualify(s):
            return (len(s.split()) > 3 and len(s) > 30) or 'hl' in s
        return '\n'.join([l if qualify(l) else magic_string for l in lines])
    
    extract_html_content = remove_short_lines(extract_html_content)

    soup = BeautifulSoup(extract_html_content, 'lxml')
    hls = [hl.get_text() for hl in soup.find_all('hl')]
    # split 'AUTOSCHOLARREMOVE'.  this will introduce many splits that
    # is table cells, but not removed by heuristic. Thus we need to
    # filter based on the length
    hls = append_lists([hl.split(magic_string) for hl in hls])
    # remove empty elements (\s*)
    hls = list(filter(lambda s: len(s) > 30, hls))

    print('getting content ..')
    publisher_text = html2text(publisher_html)

    # Add a line break at the end of each paragraph
    publisher_text = [[x + "<br><br>" for x in y ] for y in publisher_text]

    # use double newlines to separate
    magic_paragraph_separator = 'AUTOSCHOLAR_PARAGRAPH_SEPARATOR'
    publisher_content = (('\n' + magic_paragraph_separator + '\n')
                         .join(publisher_text[0]
                               + publisher_text[1]
                               # FIXME table cells do not work
                               # + publisher_text[2]
                         ))

    # collapse (white)space
    publisher_content = re.sub(r' +', ' ', publisher_content)

    treated_content, removed_indexes = treat_tag(publisher_content)
    # remove unicode
    treated_content, unicode_indexes = treat_unicode(treated_content)

    print('searching ..')

    # i = 0
    # for hl in hls:
    #     print('searching: (' + str(i) + ')' + hl)
    #     i += 1
    #     fuzzy_search(treated_content, hl)
    
    indexes = [fuzzy_search_multi(treated_content, hl) for hl in hls]
    # remove None
    indexes = [index[:-1] for index in indexes if index]
    recovered_indexes = list(map(lambda x:
                                 recover_tag(
                                     recover_unicode(x, unicode_indexes),
                                     removed_indexes),
                                 indexes))
    # into two groups, highlight or not
    hl_indexes = merge_sort_indexes(recovered_indexes)

    # Now, insert the <hl> tags for the hl_indexes, into the
    # publisher_content

    magic_string_indexes = [(m.start(), m.end())
                            for m in re.finditer(magic_paragraph_separator,
                                                 publisher_content)]

    # shift magic indexes
    hl_indexes = shift_magic_indexes(magic_string_indexes, hl_indexes)

    hl_indexes = adjust_word_breaking(publisher_content, hl_indexes)

    output = '<html><meta charset="UTF-8"><head>'
    output += '<style> hl { background-color: yellow; } </style>'
    output += '</head>\n'
    output += '<body>\n'
    previous_index = 0
    for index in hl_indexes:
        output += publisher_content[previous_index:index[0]]
        # NOTE: since adding <hl> does not consider the validity of
        # html tags, the output can sometimes be
        # <span>...<hl></span>..</hl>, which will not be shown in
        # browser, and may not be shown using bs4
        output += '<hl>'
        output += publisher_content[index[0]:index[1]]
        output += '</hl>'
        previous_index = index[1]
    output += publisher_content[previous_index:]
    output += '</body></html>\n'
    # move <hl> into inner most, this seems to solve the out-of-order
    # problem for html tags
    output = reorder_hl(output)
    # remove paragraph separator
    output = re.sub(magic_paragraph_separator, '', output)

    print('writing output ..')
    with open(output_file, 'w') as f:
        f.write(output)

def reorder_hl(s):
    """Reorder <hl> and </hl> to move them as *outside* as possible among
    all tags
    ''

    Examples:
    >>> reorder_hl('<span>ss</span><p><hl><span>hello</a></hl></b><c></d>')
    '<span>ss</span><hl><p><span>hello</a></b></hl><c></d>'
    """
    # remove <hl></hl>
    s = re.sub(r'<hl>\s*</hl>', r'', s)
    # reorder
    s = re.sub(r'((?:\s*<[^/>]*>)*)(<hl>)', r'\2\1', s)
    s = re.sub(r'(</hl>)((?:</[^>]*>\s*)*)', r'\2\1', s)
    return s


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('publisher_html', help='publisher html')
    parser.add_argument('extract_html', help='extract html with <hl> from pdf')
    parser.add_argument('output_html', help='output html file')
    args = parser.parse_args()
    align(args.publisher_html, args.extract_html, args.output_html)
    
    
if __name__ == '__test__':
    doctest.testmod()

    with timeout(seconds=3):
        try:
            time.sleep(4)
        except TimeoutError:
            print('timeout')

    publisher_html = './html_output/66.html'
    extract_html = '../test/html/66.html'
    
    publisher_dir = './html_output'
    extract_dir = '../test/html'
    csv_dir = './hl_html'
    for f in [f for f in os.listdir(publisher_dir) if f.endswith('.html')]:
        id = f.split('.')[0]
        print('------ ' + id)
        publisher_html = os.path.join(publisher_dir, id + '.html')
        extract_html = os.path.join(extract_dir, id + '.html')
        output_file = os.path.join(csv_dir, id + '.html')
        if not os.path.exists(extract_html):
            print('========', extract_html, 'does not exist')
        else:
            align(publisher_html, extract_html, output_file)
