# Align and Generate data from browser downloaded publisher raw text with extracted html

import nltk
import re
from bs4 import BeautifulSoup
from full_text_html_extract import remove_citation
from nltk import edit_distance
import numpy as np
import argparse
import os

def contain_alpha(text):
    for ch in text:
        if ch.isalpha():
            return True
    return False

def contain_alnum(text):
    for ch in text:
        if ch.isalnum():
            return True
    return False

def handle_figsplit(sentences):
    new_sentences = []
    tmp_sentence = ""
    for sentence in sentences:
        # Wrong split for line end with figure
        sentence = sentence.strip()
        if len(re.findall(r'[Ff]ig(?:ure)?\.?$', sentence)) != 0:
            tmp_sentence += sentence + ' '
        elif tmp_sentence != "":
            new_sentences.append(tmp_sentence + sentence)
            tmp_sentence = ""
        else:
            new_sentences.append(sentence)
    return new_sentences

def handle_shortsplit(sentences):
    new_sentences = []
    tmp_sentence = ""
    for sentence in sentences:
        # Wrong split for line end with figure
        sentence = sentence.strip()
        if not contain_alpha(sentence):
            tmp_sentence += sentence + ' '
        elif tmp_sentence != "":
            new_sentences.append(tmp_sentence + sentence)
            tmp_sentence = ""
        else:
            new_sentences.append(sentence)
    return new_sentences

def remove_spaces(sentences):
    new_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        sentence = re.sub('  +', ' ', sentence)
        sentence = re.sub('^ +', '', sentence, flags=re.MULTILINE)
        sentence = re.sub(' +$', '', sentence, flags=re.MULTILINE)
        sentence = sentence.replace('\t', '  ')
        sentence = sentence.replace('\n', ' | ')
        if (len(sentence) < 2):
            continue
        new_sentences.append(sentence)
    return new_sentences

def extract_publisher_text(text):
    sent_split = nltk.data.load('tokenizers/punkt/english.pickle')
    p = text.split('\n\n')
    s = []
    for idx in range(len(p)):
        # Remove all hyperlink
        p[idx] = re.sub('<http.*?>', ' ', p[idx])
        # Remove reference
        p[idx] = re.sub('<#.*?>', ' ', p[idx])

        # Remove some italic special character for sentence split
        italics = re.findall('[ \n]/.*?/', p[idx])
        for case in italics:
            if case.find('.') != -1:
                p[idx] = p[idx].replace(case, ' ' + case[2:-1] + ' ')
        
        sentences = []
        p[idx] = p[idx].strip()

        if not (p[idx].endswith('.') or p[idx].endswith('.)')):
            sentences = [p[idx]]
        else:
            p[idx] = p[idx].replace('\n', ' ')
            sentences = sent_split.tokenize(p[idx])
            sentences = handle_figsplit(sentences)

        s.extend(sentences)
    
    s = remove_spaces(s)
    return s

def extract_highlights(path):
    sent_split = nltk.data.load('tokenizers/punkt/english.pickle')
    result = []
    with open(path, 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')
        highlights = soup.find_all('hl')
        for highlight in highlights:
            text = highlight.get_text()
            text = text.replace('-\n', '-')
            sentences = sent_split.tokenize(text)
            sentences = handle_shortsplit(sentences)
            sentences = handle_figsplit(sentences)
            result.extend(sentences)
    return result

def word_match(w1, w2):
    if w1 == w2:
        return True
    if w1.find(w2) != -1 or w2.find(w1) != -1:
        return True
    return False


def sentence_match(s1, s2):
    ''' Use LCS like DP to do local determine if two sentences is aligned.
    '''
    w1 = nltk.word_tokenize(s1)
    w2 = nltk.word_tokenize(s2)

    w1 = [''] + [token for token in w1 if contain_alnum(token)]
    w2 = [''] + [token for token in w2 if contain_alnum(token)]

    if len(w2) == 1:
        return False
       
    mat = np.zeros((len(w1), len(w2)))

    for i in range(1, mat.shape[0]):
        for j in range(1, mat.shape[1]):
            mat[i, j] = max(mat[i-1, j]-1, mat[i, j-1]-1, 0)
            if word_match(w1[i], w2[j]):
                mat[i, j] = max(mat[i, j], mat[i-1, j-1]+1)
    
    lcs = np.max(mat)
    return lcs / (mat.shape[1]-1) >= 0.7

def tmp_output(sent, path):
    with open(path, 'w') as f:
        f.write('\n_________________________\n'.join(sent))

def gen_data(publisher_path, extract_path, output_path):
    sent2 = extract_highlights(extract_path)
    sent1 = []
    with open(publisher_path, 'r') as f:
        text = f.read()
        sent1 = extract_publisher_text(text)
    
    tmp_output(sent1, output_path+'_pub.txt')
    tmp_output(sent2, output_path+'_ext.txt')
    tsv = []

    for s1 in sent1:
        hl = 0
        for s2 in sent2:
            if sentence_match(s1, s2):
                hl = 1
                break
        tsv.append((s1, hl))
        
    with open(output_path, 'w') as f:
        f.write("\n".join([str(label) + "\t" + sentence for sentence, label in tsv]))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('publisher_text', help='publisher html file or folder path')
    parser.add_argument('extract_html', help='extracted html file with <hl> from pdf or folder path ')
    parser.add_argument('output_tsv', help='output TSV file or folder path')
    args = parser.parse_args()
    if os.path.isfile(args.publisher_text) and os.path.isfile(args.extract_html):
        gen_data(args.publisher_text, args.extract_html, args.output_tsv)
    elif os.path.isdir(args.publisher_text) and \
        os.path.isdir(args.extract_html) and \
        os.path.isdir(args.output_tsv):
        
        publisher_dir = args.publisher_text
        extract_dir = args.extract_html
        csv_dir = args.output_tsv
        for f in [f for f in os.listdir(publisher_dir) if f.endswith('.html')]:
            id = f.split('.')[0]
            print('------ ' + id)
            publisher_text = os.path.join(publisher_dir, id + '.html')
            extract_html = os.path.join(extract_dir, id + '.html')
            output_file = os.path.join(csv_dir, id + '.csv')
            if not os.path.exists(extract_html):
                print('========', extract_html, 'does not exist')
            else:
                gen_data(publisher_text, extract_html, output_file)
                # print("Processing...")
    else:
        print("Arguments does not match or path(s) does not exist.")

if __name__ == "__main__":
    main()