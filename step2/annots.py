import config as cfg
import fitz
import os
import json
import numpy as np
import sys
from tqdm import tqdm
sys.path.append('../step1')
from highlights import word_concat, areaCriteria, sent_tokenize

def block2samples(page_block):
    samples = []
    labels, texts, rects = zip(*page_block)
    sents = sent_tokenize(texts)
        
    word_count = 0
    for sent in sents:
        words = sent.split(' ')
        num_words = len(words)

        tags = labels[word_count:word_count+num_words]
        if any(tags):
            samples.append((words, tags))
        
        word_count += num_words
    
    return samples

def parse_pdf(pdf_file):
    pdf = fitz.open(pdf_file)

    samples = []
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
            '''
            idx = 0
            for i in range(size):
                rect = highlights[i][0]
                br = rect.br
                if br.y >= point.y and \
                    np.abs(br.y - point.y) <= np.abs(highlights[idx][0].br.y - point.y) and \
                    np.abs(br.x - point.x) < np.abs(highlights[idx][0].br.x - point.x):
                    idx = i
            
            highlights[idx].append(text)
            '''
        
        # print(highlights)
        ## Test if texts are matched correctly        
        for hl in highlights:
            # One highlight can only be paired with single or none comments
            if not (len(hl) == 1 or len(hl) == 2):
                print("Possible alignment problem:", hl)
                # assert(False)
            '''
            if len(hl) > 1:
                annot = page.add_text_annot(hl[0].bl, hl[1], 'Comment')
                annot.set_opacity(0.5)
            '''

        # Get words
        # Assume words appearing in reading order (Usually holds for a science paper)
        words = page.get_text('words')

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
                    samples.extend(block2samples(page_block))
                    page_block = []
            
            label = ""
            for hl in highlights:
                if len(hl) > 1:
                    annot_rect = hl[0]
                    if areaCriteria(fitz.Rect(rect), annot_rect) > 0.5:
                        label = hl[1]
                        end = label.find(':')
                        if end != -1:
                            label = label[:end]
                        label = label.strip().lower()
                        # print(text, ':::' ,label)
            
            page_block.append((label, text, [(rect, line)]))
        
        if len(page_block) > 0:
            page_block = word_concat(page_block)
            samples.extend(block2samples(page_block))
            page_block = []
        
    pdf.save('test.pdf')
    pdf.close()
    return samples


if __name__ == '__main__':
    if not os.path.exists(cfg.dataset_folder):
        os.makedirs(cfg.dataset_folder)
    
    files = os.listdir(cfg.annot_pdf_folder)
    pbar = tqdm(total=len(files))
    for file in files:
        samples = parse_pdf(os.path.join(cfg.annot_pdf_folder, file))
        with open(os.path.join(cfg.dataset_folder, file+'.jsonl'), "w", encoding = "utf-8") as f:
            for sample in samples:
                f.write(json.dumps(sample) + '\n')
        pbar.update(1)
    pbar.close()