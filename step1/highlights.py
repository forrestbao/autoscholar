import fitz
import json
import os
from tqdm import tqdm
import re
import config as cfg

class PDFEncoder(json.JSONEncoder):
    """ Custom encoder for numpy data types """
    def default(self, obj):
        if isinstance(obj, (fitz.Rect, fitz.Point)):
            return obj.__repr__()
        return json.JSONEncoder.default(self, obj)

def addHighlight(annotation_file, pdf_folder, output_folder):
    data = {}
    with open(annotation_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    pbar = tqdm(total=len(data))
    for doc in data:
        if doc['url'] is None:
           continue 
        doc_id = doc["doc_id"]
        highlights = {}
        texts = {}
        for annot in doc["annots"]:
            if annot['type'] == 'highlight':
                for pos in annot["positions"]:
                    rect = fitz.Rect([pos["top_left"]["x"],
                        pos["top_left"]["y"],
                        pos["bottom_right"]["x"],
                        pos["bottom_right"]["y"]])
                    #if rect.getArea() > 1e-5:
                    highlights.setdefault(pos["page"], []).append(rect)
            else:
                for pos in annot["positions"]:
                    assert(pos["top_left"]["x"] == pos["bottom_right"]["x"])
                    assert(pos["top_left"]["y"] == pos["bottom_right"]["y"])
                    point = fitz.Point(pos["top_left"]["x"], pos["top_left"]["y"])
                    texts.setdefault(pos["page"], []).append((point, annot["text"]))
        
        pdf = fitz.open(os.path.join(pdf_folder, doc_id+".pdf"))
        # print(doc_id)
        pcnt = 1
        for page in pdf:
            # page_rect = page.bound()
            page_rect = page.mediabox
            # print(pcnt)
            if pcnt in highlights and len(highlights[pcnt]) > 0:
                # print(json.dumps(highlights[pcnt], indent=2, cls=PDFEncoder))
                for rect in highlights[pcnt]:
                    # Transform from mendeley to pymupdf
                    rect[1], rect[3] = page_rect[3] - rect[3], page_rect[3] - rect[1]
                    rect[0], rect[2] = rect[0] - page_rect[0], rect[2] - page_rect[0]
                    if rect[1] > rect[3]:
                        rect[1], rect[3] = rect[3], rect[1]
                    page.add_highlight_annot(rect)
            if pcnt in texts and len(texts[pcnt]) > 0:
                # print(json.dumps(texts[pcnt], indent=2, cls=PDFEncoder))
                for point, text in texts[pcnt]:
                    point[1] = page_rect[3] - point[1]
                    point[0] = point[0] - page_rect[0]
                    page.add_text_annot(point, text)
            
            pcnt += 1
        
        pdf.save(os.path.join(output_folder, doc_id+".pdf"))
        pdf.close()
        pbar.update(1)
        #break
    pbar.close()

def addPredHighlight(pdf_file, output_file, predicted, debug=True):
    from itertools import chain
    pdf = fitz.open(pdf_file)
    pcnt = 0
    for page in pdf:
        hl = predicted[pcnt]
        for label, sent, sent_rect in hl:
            if debug:
                print(sent)
            
            # Add highight in word level
            # for rect in sent_rect:
            #     page.add_highlight_annot(fitz.Rect(rect))

            # Add highlight in line level (Put rects in the same line into a big rect)
            lrect, pline = fitz.Rect(sent_rect[0][0][0]), sent_rect[0][0][1]
            for rect, line in chain.from_iterable(sent_rect):
                if line == pline:
                    lrect.includeRect(fitz.Rect(rect))
                else:
                    page.add_highlight_annot(lrect)
                    lrect = fitz.Rect(rect)
                    pline = line
            page.add_highlight_annot(lrect)

        pcnt += 1
    pdf.save(output_file)
    pdf.close()

def areaCriteria(rect1, rect2):
    rect = fitz.Rect(rect1)
    rect.intersect(rect2)
    
    ac = rect.getArea()
    a1 = rect1.getArea()
    return ac / a1

def word_concat(page_block):
    result_block = []
    size = len(page_block)
    result_block.append(page_block[0])
    for i in range(1, size):
        label, text, box = page_block[i]
        plabel, ptext, pbox = page_block[i-1]
        line = box[0][1]
        pline = pbox[0][1]
        if ptext.endswith('-') and line == pline+1:
            # Concat word
            result_block.pop()
            text = ptext[:-1] + text
            label = label or plabel
            box = [pbox[0], box[0]]
        
        result_block.append((label, text, box))
    
    return result_block

def doc2word(pdf_file):
    pdf = fitz.open(pdf_file)

    doc_words = []
    for page in pdf:
        # Get rect of annoataions
        annots = []
        for annot in page.annots():
            if annot.type[1] == 'Highlight':
                annots.append(annot.rect)
        
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

    pdf.close()
    return doc_words

def sent_tokenize(texts):
    sent_end = (".", "?", "!")
    doc_sents = []
    sent = []
    for word in texts:
        sent.append(word)
        if word.endswith(sent_end):
            # Exceptional case rules:
            if len(re.findall(r'[Ff]ig(?:ure)?', word)) != 0:
                continue
            if len(sent) <= 2 or (len(word) == 2 and not word[0].isnumeric()):
                continue
            if word == 'al.':
                continue
            doc_sents.append(" ".join(sent))
            sent = []
    if sent != []:
        doc_sents.append(" ".join(sent))
    return doc_sents

def word2sentence(doc_words):
    pages = len(doc_words)
    doc_sents = []
    for page_words in doc_words:
        page_sents = []
        for block in page_words:
            labels, texts, rects = zip(*block)
            sents = sent_tokenize(texts)
            
            word_count = 0
            for sent in sents:
                words = sent.split(' ')
                num_words = len(words)

                label = int(any(labels[word_count:word_count+num_words]))
                sent_rect = rects[word_count:word_count+num_words]
                page_sents.append((label, sent, sent_rect))

                # print(sent)
                # print(texts[word_count:word_count+num_words])
                # print('')

                word_count += num_words
            assert(word_count == len(texts))
        doc_sents.append(page_sents)
        
    return doc_sents

def main(genPDF=False):
    if genPDF:
        print('Generating highlighted pdf from mendeley...')
        if not os.path.exists(cfg.hl_pdf_folder):
            os.makedirs(cfg.hl_pdf_folder)
        addHighlight(cfg.annotation_file, cfg.pdf_download_path, cfg.hl_pdf_folder)

    if not os.path.exists(cfg.dataset_folder):
        os.makedirs(cfg.dataset_folder)

    
    files = os.listdir(cfg.hl_pdf_folder)
    pbar = tqdm(total=len(files))
    for file in files:
        doc_words = doc2word(os.path.join(cfg.hl_pdf_folder, file))
        doc_sents = word2sentence(doc_words)

        with open(os.path.join(cfg.dataset_folder, file+'.tsv'), "w", encoding="utf-8") as f:
            for page_sents in doc_sents:
                for label, sent, _ in page_sents:
                    f.write(str(label) + '\t' + sent)
                    f.write('\n')
        
        pbar.update(1)
    pbar.close()


if __name__ == '__main__':
    main(cfg.GENERATE_HL_PDF)
