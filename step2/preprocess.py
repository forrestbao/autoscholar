import json
import pickle
import numpy as np
import config as cfg
import pickle

addBefore = 1
addAfter = 1

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

    X, y = [], []
    with open('all.jsonl', 'r') as f:
        for line in f:
            words, tags = json.loads(line)
            tags = [classDict[tag] for tag in tags]
            size = len(words)
            # 3-gram
            X.extend(words2sample(words))
            y.extend(tags)
    
    X = np.array(X, dtype=int)
    y = np.array(y, dtype=int)
    for i in range(20):
        print("".join([chr(ch) for ch in X[i]]), y[i])
    with open(cfg.preprocessed_file, "wb") as f:
        pickle.dump((X, y), f)
