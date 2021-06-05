from math import pi
import stanfordcorenlp
import feature as pre
import pickle
import sklearn
import config as cfg
import numpy as np
from sklearn import preprocessing, model_selection
from sklearn.svm import SVC
import json

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class SVM:
    def init(self):
        self.nlp = None
        self.stopwords = set(open(cfg.stopword_path, 'r').read().split())
        self.units = open(cfg.unit_file, 'r').read().split()
        self.IDF = None
        self.clf = None
        self.scaler = preprocessing.StandardScaler()

    def __init__(self):        
        self.init()
        self.param = {
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
        self.model = SVC()

    def open_nlphandler(self):
        self.nlp = stanfordcorenlp.StanfordCoreNLP(cfg.stanfordcorenlp_jar_location)
    
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
        CORE_NUM = 4
        FOLDS = 5
        self.clf = model_selection.GridSearchCV(self.model, self.param, 
            scoring=["precision", "recall", "f1"],
            refit="f1",
            n_jobs=CORE_NUM, 
            cv=model_selection.ShuffleSplit(FOLDS))
        self.clf.fit(X, y)
        print(json.dumps(self.clf.cv_results_, indent=2, cls=NumpyEncoder))
        print("{}\t{}".format(self.clf.best_score_, self.clf.best_params_))
    
    def predict(self, texts):
        if self.nlp is None:
            self.open_nlphandler()
        
        features = pre.convert_features(texts, self.nlp, self.stopwords, self.units, self.IDF)
        X = self.scaler.transform(features)
        y = self.clf.predict(X)
        return y

def save_model(model, path):
    with open(path, "wb") as f:
        pickle.dump(model, f)

def load_model(path):
    with open(path, "rb") as f:
        return pickle.load(f)
    

if __name__ == "__main__":
    model = SVM()
    model.preprocessing(cfg.train_tsv_file)
    save_model(model, cfg.preprocessed_file)
    model.train()
    save_model(model, cfg.model_file)

    print(model.predict(["Will this be hightligted ?"]))