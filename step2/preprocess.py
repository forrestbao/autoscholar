import json
import pickle
import numpy as np
import config as cfg
import pickle
import random

addBefore = 2
addAfter = 2

def words2sample(words):
    size = len(words)
    samples = []
    for i in range(size):
        st = max(0, i-addBefore)
        ed = min(size, i+addAfter+1)
        sample_string = " ".join(words[st: ed])
        sample_string = sample_string.encode("ascii", "ignore").decode()
        sample_int = [ord(ch) for ch in sample_string]
        # Truncate
        sample_int = sample_int[:cfg.PADDING_LENGTH]
        # Padding
        sample_int += [0] * (cfg.PADDING_LENGTH - len(sample_int))
        samples.append(sample_int)
    return samples

def build_class():
    classes = ['']
    with open('class.txt', 'r') as f:
        for line in f:
            classes.append(line.strip())
    
    classDict = dict(zip(classes, np.arange(len(classes))))
    return classes, classDict

if __name__ == '__main__':
    classes, classDict = build_class()
    print(classDict)
    num_classes = dict(zip(classes, [0]*len(classes)))

    X, y = [], []
    with open('all.jsonl', 'r') as f:
        for line in f:
            words, tags = json.loads(line)
            for tag in tags:
                num_classes[tag] += 1
            tags = [classDict[tag] for tag in tags]
            size = len(words)
            # 3-gram
            X.extend(words2sample(words))
            y.extend(tags)
    
    X = np.array(X, dtype=int)
    y = np.array(y, dtype=int)

    neg_X = X[np.where(y == 0)]
    neg_y = y[np.where(y == 0)]
    pos_X = X[np.where(y != 0)]
    pos_y = y[np.where(y != 0)]

    # num_neg = np.max([num_classes[k] for k in num_classes if k != ''])
    num_neg = len(pos_y)
    # Sample part of the negative samples to balance the dataset
    neg_sample = random.sample(range(len(neg_y)), num_neg) 
    neg_y = neg_y[neg_sample]
    neg_X = neg_X[neg_sample]
    
    X = np.vstack([pos_X, neg_X])
    y = np.concatenate([pos_y, neg_y])
    # X = pos_X
    # y = pos_y
    print(X.shape, y.shape, len(neg_y) / len(y))
    for i in range(20):
        print("".join([chr(ch) for ch in X[i]]), y[i])
    '''
    print(num_classes)
    print(len(X), num_classes[''] / len(X))
    '''
    with open(cfg.preprocessed_file, "wb") as f:
        pickle.dump((X, y), f)
