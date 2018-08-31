#!/usr/bin/env python3

from preprocessing.full_text_html_extract import *
from collections import Counter
    
def test_export(dir, ids):
    for i in ids:
        filename = './html_output/' + str(i) + '.html'
        with open(os.path.join(dir, str(i) + '.txt')
                  , 'w') as f:
            l1, l2, l3 = html2text(filename)
            f.write('==============Paragraph('
                    + str(len(l1))
                    + ')================'
                    + '\n\n\n\n\n')
            for s in l1:
                f.write(s)
                f.write('\n\n\n\n')

            f.write('\n\n\n\n\n\n\n'
                    + '==============Captions('
                    + str(len(l2))
                    + ')================'
                    '\n\n\n\n\n\n\n')

            for s in l2:
                f.write(s)
                f.write('\n\n\n\n')

            f.write('\n\n\n\n\n\n\n'
                    + '==============Tables('
                    + str(len(l3))
                    + ')================'
                    '\n\n\n\n\n\n\n')
            for s in l3:
                f.write(s)
                f.write('\n\n\n\n')

                
def rewrite_a(s):
    # markup = '<a href="fdsfds" title="fkd" class="fdsfd">hell<em>world</em></a>'
    # s = bs4.BeautifulSoup(markup, 'html.parser')
    for a in s.find_all('a'):
        a.wrap(s.new_tag('a'))
        a.unwrap()


def count_tags(download_html_folder, align_html_folder):
    """Count the number of tags used for a specific publisher

    Args:
        download_html_folder: used to determine publisher.
        align_html_folder: used to count tags, thus only the main text
        portion, excluding e.g. bibliography

    """
    ret = {}
    for name in os.listdir(download_html_folder):
        if name.endswith('.html'):
            filename = os.path.join(download_html_folder, name)
            publisher = determine_publisher(open(filename).read())
            align_filename = os.path.join(align_html_folder, name)
            soup = bs4.BeautifulSoup(open(align_filename).read(), 'html.parser')
            i_ct = len(soup.find_all('em')) + len(soup.find_all('i'))
            b_ct = len(soup.find_all('strong')) + len(soup.find_all('b'))
            sup_ct = len(soup.find_all('sup'))
            sub_ct = len(soup.find_all('sub'))
            if publisher not in ret:
                ret[publisher] = [0,0,0,0]
            ret[publisher] = list(map(lambda x,y: x+y,
                                      ret[publisher],
                                      [i_ct, b_ct, sup_ct, sub_ct]))
    return ret

def tag_detail(download_html_folder, align_html_folder):
    """Return, for each publisher, the text of four tags
    """
    ret = {}
    for name in os.listdir(download_html_folder):
        if name.endswith('.html'):
            filename = os.path.join(download_html_folder, name)
            publisher = determine_publisher(open(filename).read())
            align_filename = os.path.join(align_html_folder, name)
            soup = bs4.BeautifulSoup(open(align_filename).read(), 'html.parser')
            # all strings are collected
            i = soup.find_all('em') + soup.find_all('i')
            b = soup.find_all('strong') + soup.find_all('b')
            sup = soup.find_all('sup')
            sub = soup.find_all('sub')
            if publisher not in ret:
                ret[publisher] = [[],[],[],[]]
            ret[publisher] = list(map(lambda x,y: x+y,
                                      ret[publisher],
                                      [i, b, sup, sub]))
    return ret
    


def get_publisher_ids(download_html_folder):
    """Return a dictionary from publisher to its paper ID (number in filename)
    """
    ret = {}
    for name in os.listdir(download_html_folder):
        if name.endswith('.html'):
            filename = os.path.join(download_html_folder, name)
            id = name.split('.')[0]
            publisher = determine_publisher(open(filename).read())
            if publisher not in ret:
                ret[publisher] = []
            ret[publisher].append(id)
    return ret


if __name__ == '__test__':
    files = list(map(lambda x: os.path.join('../data/download_html/', x),
                     filter(lambda x: x.endswith('.html'),
                            os.listdir('../data/download_html/'))))
    for f in files:
        print('------ ' + f)
        l1, l2, l3 = html2text(f)
        print(determine_publisher(open(f).read()))
        print(len(l1))
        print(len(l2))
        print(len(l3))

    html2text('../data/download_html/55.html')
    determine_publisher(open('../data/download_html/68.html').read())

    get_publisher_ids('../data/download_html')
    count_tags('../data/download_html', '../data/align_html')
    detail = tag_detail('../data/download_html', '../data/align_html')

    for key in detail.keys():
        print(key)
        print(Counter(detail[key][3]).most_common()[:])

    springer_ids = [71, 53, 44, 77, 58]
    elsevier_ids = [66,50,54,68,80,76,45,
                    72,51,69,63,47,60,59,75,48]
    wiley_ids = [55,79,70,61,43,46]
    asm_ids = [57,65,49,64]
    nature_ids = [67,78,73,56,62]
    embo_ids = [89,42]
    bmc_ids = [74]
    pubmed_ids = [52]

    test_export('./test/springer', springer_ids)
    test_export('./test/elsevier', elsevier_ids)
    test_export('./test/wiley', wiley_ids)
    test_export('./test/asm', asm_ids)
    test_export('./test/nature', nature_ids)
    test_export('./test', embo_ids)
    test_export('./test', bmc_ids)
    test_export('./test', pubmed_ids)

