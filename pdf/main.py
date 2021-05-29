import highlights as hl
from model import load_model, SVM

def main():
    pdf_file = '../mendeley/pdfs/001bd556-cc53-3005-930d-3de41a7929be.pdf'
    output_file = 'predicted.pdf'

    clf = load_model('saved.pickle')

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
    
    clf.close_nlphandler()

    print("Num of sentences to highlight:", cnt)
    if cnt > 0:
        hl.addPredHighlight(pdf_file, output_file, predicted)

if __name__ == '__main__':
    main()