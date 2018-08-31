#!/usr/bin/env python

# The libpoppler biding used is https://github.com/izderadicka/pdfparser
# install via

# pip install cython
# pip install git+https://github.com/izderadicka/pdfparser

import pdfparser.poppler as poppler

if __name__ == '__test__':
    doc = poppler.Document(b'./test.pdf')
    for page in doc:
        print('Page', page.page_no, 'size =', page.size)
        for f in page:
            print(' '*1, 'Flow')
            for b in f:
                print(' '*2, 'Block', 'bbox=', b.bbox.as_tuple())
                for l in b:
                    print(' '*3, l.text.encode('UTF-8'), '(%0.2f, %0.2f, %0.2f, %0.2f)'% l.bbox.as_tuple())
                    #assert l.char_fonts.comp_ratio < 1.0
                    for i in range(len(l.text)):
                        print(l.text[i].encode('UTF-8'),
                              '(%0.2f, %0.2f, %0.2f, %0.2f)' %
                              l.char_bboxes[i].as_tuple(),
                              l.char_fonts[i].name,
                              l.char_fonts[i].size,
                              l.char_fonts[i].color,)
