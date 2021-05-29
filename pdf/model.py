from math import pi
import stanfordcorenlp
import feature as pre
import pickle
import sklearn
import numpy as np
from sklearn import preprocessing, model_selection
from sklearn.svm import SVC

class SVM:
    def __init__(self):
        stopword_path = 'sci_stopwords.txt'
        unit_file = 'units.txt'
        
        self.nlp = None
        self.stopwords = set(open(stopword_path, 'r').read().split())
        self.units = open(unit_file, 'r').read().split()
        self.IDF = None
        self.scaler = preprocessing.StandardScaler()
        self.clf = None

    def open_nlphandler(self):
        stanfordcorenlp_jar_location = '/mnt/d/stanford-corenlp-full-2018-02-27/'
        self.nlp = stanfordcorenlp.StanfordCoreNLP(stanfordcorenlp_jar_location)
    
    def close_nlphandler(self):
        self.nlp.close()
        self.nlp = None

    def preprocessing(self, train_csv):
        labels, texts = [], []
        print("Loading...")
        with open(train_csv, 'r') as f: 
            for Line in f:
                if len(Line) > 5: 
                    labels.append(int(Line[0]))
                    texts.append(Line[1:])
        
        # Pre-Processing
        print('Pre-Processing...')
        self.open_nlphandler()
        features, self.IDF = pre.build_features(texts, self.nlp, self.stopwords, self.units)
        self.close_nlphandler() 
        
        # Standardization
        vectors_scaled = self.scaler.fit_transform(features)
        X, y = sklearn.utils.shuffle(vectors_scaled, labels)
        with open("train.pickle", "wb") as f:
            pickle.dump( (X, y), f)

    def train(self):
        X, y = None, None
        with open("train.pickle", "rb") as f:
            X, y = pickle.load(f)
        # Training
        print("Training...")
        svm = SVC()
        params = {
            "C": 10.0 ** np.arange(-2,2),
            #"gamma": [0., 0.0001, 0.001, 0.01, 0.1],  # experience: epsilon>=0.1 is not good.
            "kernel": [
                # "linear",
                "rbf",
                #"poly",  # polynomial kernel sucks. Never use it.
                #"sigmoid",
                # "precomputed"
                ],
            #"degree": [5,], # because polynomial kernel sucks. Never use it.
            #"gamma": 10.0 ** numpy.arange(-4, 4),
        }
        CORE_NUM = 4
        FOLDS = 5
        self.clf = model_selection.GridSearchCV(svm, params, scoring="precision", n_jobs=CORE_NUM, cv=FOLDS)
        self.clf.fit(X, y)
        print("{}\t{}".format(self.clf.best_score_, self.clf.best_params_))
    
    def predict(self, texts):
        if self.nlp is None:
            self.open_nlphandler()
        
        features = pre.convert_features(texts, self.nlp, self.stopwords, self.units, self.IDF)
        X = self.scaler.transform(features)
        y = self.clf.predict(X)
        return y

def save_model(model, path='saved.pickle'):
    with open(path, "wb") as f:
        pickle.dump(model, f)

def load_model(path='saved.pickle'):
    with open(path, "rb") as f:
        return pickle.load(f)
    

if __name__ == "__main__":
    model = SVM()
    model.preprocessing("all.tsv")
    save_model(model)
    model.train()
    save_model(model)

    print(model.predict(["Will this be hightligted ?"]))