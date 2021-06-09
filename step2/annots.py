import config as cfg
import fitz
import os
import numpy as np

def parse_pdf(pdf_file):
    pdf = fitz.open(pdf_file)

    doc_words = []
    for page in pdf:
        # Get rect of annoataions
        highlights = []
        comments = []
        for annot in page.annots():
            # print(annot, annot.rect)
            if annot.type[1] == 'Highlight':
                highlights.append([annot.rect])
            elif annot.type[1] == 'Text':
                comments.append((annot.info['content'], annot.rect.tl))
        
        size = len(highlights)
        for text, point in comments:
            # 1. Check whether point is in a Rect
            found = False
            for i in range(size):
                rect = highlights[i][0]
                if rect.contains(point):
                    highlights[i].append(text)
                    found = True
                    break
            if found:
                continue
            # 2. Give the text to the closest highlight(bottom right) below the point
            idx = 0
            for i in range(size):
                rect = highlights[i][0]
                br = rect.br
                if br.y >= point.y and \
                    np.abs(br.y - point.y) <= np.abs(highlights[idx][0].br.y - point.y) and \
                    np.abs(br.x - point.x) < np.abs(highlights[idx][0].br.x - point.x):
                    idx = i
            
            highlights[idx].append(text)
        
        # print(highlights)
        ## Test if texts are matched correctly
        '''
        for hl in highlights:
            if len(hl) > 1:
                annot = page.add_text_annot(hl[0].bl, hl[1], 'Comment')
                annot.set_opacity(0.5)
        '''
        '''

        # Get words
        # Assume words appearing in reading order (Usually holds for a science paper)
        words = page.get_text('words')

        page_words = []
        page_block = []
        block_no = -1
        for word in words:
            rect = word[:4]
            text = word[4]  # No '\t' or '\n' will be in text
            # Block separated
            block = word[5]
            # Use line info to concatenate word cross line
            line = word[6]
            if block != block_no:
                block_no = block
                if len(page_block) > 0:
                    page_block = word_concat(page_block)
                    page_words.append(page_block)
                    page_block = []
            
            label = int(any([(areaCriteria(fitz.Rect(rect), annot_rect) > 0.5) for annot_rect in annots]))
            page_block.append((label, text, [(rect, line)]))
        
        if len(page_block) > 0:
            page_block = word_concat(page_block)
            page_words.append(page_block)
            page_block = []
        
        doc_words.append(page_words)
        '''
    # pdf.save('test.pdf')
    pdf.close()
    # return doc_words
    
    

if __name__ == '__main__':
    parse_pdf(os.path.join(cfg.annot_pdf_folder, '738709a7-0f69-3c1c-875a-75dabc3a94be.pdf'))