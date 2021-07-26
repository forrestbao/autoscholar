from model import CharRNN
import preprocess as pre
import numpy as np
from model import *

if __name__ == '__main__':
    classes, classDict = pre.build_class()
    
    model = CharRNN()
    model.load_model()

    sent = "The mobile phase consisted of methanol, acetonitrile and dichloromethane (42:42:16) with a flow rate of 1.0 mL/min at 30°C."
    words = sent.split(" ")
    sample = np.array(pre.words2sample(words), dtype=int)
    for s in sample:
        print("".join([chr(ch) if ch != ord('\a') else '|' for ch in s]))

    labels = model.predict(sample)
    tags = [classes[label] for label in labels]

    size = len(words)
    for i in range(size):
        print(words[i], ":::", tags[i]) 
