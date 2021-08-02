import highlights as hl
from model import *
import config as cfg
import os

def process_file(clf, pdf_file, output_file, debug=True):
    doc_words = hl.doc2word(pdf_file)
    doc_sents = hl.word2sentence(doc_words)

    predicted = []
    cnt = 0
    for page_sents in doc_sents:
        label, sent, sent_rect = zip(*page_sents)
        label = clf.predict(sent)
        
        hl_sents = [(label[i], sent[i], sent_rect[i]) for i in range(len(label)) if label[i] == 1]
        predicted.append(hl_sents)
        cnt += len(hl_sents)
    
    if debug:
        print("Num of sentences to highlight:", cnt)

    if cnt > 0:
        hl.addPredHighlight(pdf_file, output_file, predicted, debug)

def main():
    files = os.listdir(cfg.input_folder)
    clf = load_model(cfg.model_file)

    if not os.path.exists(cfg.output_folder):
        os.makedirs(cfg.output_folder)

    for file in files:
        if not file.endswith(".pdf"):
            continue
        print("Processing...", file)
        pdf_file = os.path.join(cfg.input_folder, file)
        output_file = os.path.join(cfg.output_folder, file)
        process_file(clf, pdf_file, output_file, debug=True)

    clf.close_processors()

if __name__ == '__main__':
    main()