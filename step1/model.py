from math import pi, radians
import stanfordcorenlp
import feature as pre
import pickle
import sklearn
import config as cfg
import numpy as np
import random
from sklearn import preprocessing, model_selection
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from transformers import AutoTokenizer, AutoModel
import json

class NumpyEncoder(json.JSONEncoder):
    """ Custom encoder for numpy data types """
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):

            return int(obj)

        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)

        elif isinstance(obj, (np.complex_, np.complex64, np.complex128)):
            return {'real': obj.real, 'imag': obj.imag}

        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()

        elif isinstance(obj, (np.bool_)):
            return bool(obj)

        elif isinstance(obj, (np.void)): 
            return None

        return json.JSONEncoder.default(self, obj)

class SVM:
    def init(self):
        self.processor = None
        self.meta = {
            'stopwords': set(open(cfg.stopword_path, 'r').read().split()),
            'units': open(cfg.unit_file, 'r').read().split(),
            'IDF': None
        }
        self.clf = None
        self.scaler = preprocessing.StandardScaler()

    def __init__(self):        
        self.init()
        self.param = {
            "C": 10.0 ** np.arange(0,4),
            #"gamma": [0., 0.0001, 0.001, 0.01, 0.1],  # experience: epsilon>=0.1 is not good.
            "kernel": [
                "linear",
                "rbf",
                #"poly",  # polynomial kernel sucks. Never use it.
                "sigmoid",
                # "precomputed"
                ],
            #"degree": [5,], # because polynomial kernel sucks. Never use it.
            #"gamma": 10.0 ** numpy.arange(-4, 4),
        }
        self.best_param = {
            "C": 10.0,
            "kernel": "rbf"
        }
        self.model = SVC()

    def open_processors(self):
        self.processor = {}
        self.processor['nlp'] = stanfordcorenlp.StanfordCoreNLP(cfg.stanfordcorenlp_jar_location)
        self.processor['tokenizer'] = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
        self.processor['model'] = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')
    
    def close_processors(self):
        self.processor['nlp'].close()
        del self.processor['nlp']
        del self.processor['tokenizer']
        del self.processor['model']
        self.processor = None

    def preprocessing(self, train_csv):
        labels, texts = [], []
        print("Loading...")
        with open(train_csv, 'r') as f: 
            for Line in f:
                if len(Line) > 5: 
                    labels.append(int(Line[0]))
                    texts.append(Line[1:].strip())
        
        # Pre-Processing
        print('Pre-Processing...')
        self.open_processors()
        features, self.meta['IDF'] = pre.build_features(texts, **self.processor, **self.meta)
        self.close_processors() 
        
        # Standardization
        vectors_scaled = self.scaler.fit_transform(features)
        X, y = sklearn.utils.shuffle(vectors_scaled, labels)
        
        y = np.array(y)
        pos, neg = np.where(y == 1), np.where(y == 0)
        X_pos, y_pos = X[pos], y[pos]
        X_neg, y_neg = X[neg], y[neg]
        num_neg = np.min([len(y_pos) * cfg.NEGATIVE_RATIO, len(y_neg)])
        # Sample part of the negative samples
        neg_sample = random.sample(range(len(y_neg)), num_neg) 
        y_neg = y_neg[neg_sample]
        X_neg = X_neg[neg_sample]
        X = np.vstack([X_pos, X_neg])
        y = np.concatenate([y_pos, y_neg])
        X, y = sklearn.utils.shuffle(X, y)
        
        with open(cfg.preprocessed_file, "wb") as f:
            pickle.dump( (X, y), f)

    def train(self, grid_search=True):
        X, y = None, None
        with open(cfg.preprocessed_file, "rb") as f:
            X, y = pickle.load(f)
        # Training
        print("Training...")
        CORE_NUM = 6
        FOLDS = 5
        if grid_search:
            self.clf = model_selection.GridSearchCV(self.model, self.param, 
                scoring=["precision", "recall", "f1"],
                refit="f1",
                n_jobs=CORE_NUM, 
                cv=model_selection.ShuffleSplit(FOLDS))
            self.clf.fit(X, y)
            print(json.dumps(self.clf.cv_results_, indent=2, cls=NumpyEncoder))
            print("{}\t{}".format(self.clf.best_score_, self.clf.best_params_))
        else:
            self.clf = self.model
            self.clf.set_params(**self.best_param)
            self.clf.fit(X, y)
    
    def predict(self, texts):
        if self.processor is None:
            self.open_processors()
        
        features = pre.convert_features(texts, **self.meta, **self.processor)
        X = self.scaler.transform(features)
        y = self.clf.predict(X)
        return y

class RandomForest(SVM):
    def __init__(self):        
        self.init()
        self.param = {
            'n_estimators' : np.arange(1, 201, 20), 
            'max_samples': [0.1, 0.3, 0.5, 0.7, 0.9]
        }
        self.model = RandomForestClassifier()

class LinearModel(SVM):
    def __init__(self):
        self.init()
        self.param = {
            "C": 10.0 ** np.arange(0,4),
            "penalty": ['l1', 'l2', 'none'],
            "solver": ['saga'],
            "max_iter" : [1000]
        }
        self.model = LogisticRegression()

def save_model(model, path):
    with open(path, "wb") as f:
        pickle.dump(model, f)

def load_model(path):
    with open(path, "rb") as f:
        return pickle.load(f)
    

if __name__ == "__main__":
    model = SVM()
    model.preprocessing(cfg.train_tsv_file)
    save_model(model, cfg.model_file)
    model = load_model(cfg.model_file)
    model.train()
    save_model(model, cfg.model_file)

    print(model.predict(["Will this be hightligted ?"]))