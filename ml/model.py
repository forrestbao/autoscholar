import sklearn
from sklearn import preprocessing, grid_search, cross_validation
from sklearn.svm import SVC

class RegressionModel(object):
    """A help class to store model's name and the actual model."""

    def __init__(self, name, **kwargs):
        self.name = name
        self.model = eval(name)(**kwargs)

    def __str__(self):
        return self.name


class RegressionModelFactory(object):
    """A factory to create new instances of RegressionModel."""

    def __init__(self, name, **kwargs):
        self.name = name
        self.kwargs = kwargs

    def __str__(self):
        return "{} ({})".format(self.name, self.kwargs)

    def __call__(self):
        """Create a new RegressionModel instance each time."""
        return RegressionModel(self.name, **self.kwargs)

def grid_search_cv(training_data, model_gen, params, SCORINGS, CORE_NUM, FOLDS):
    """Do a grid search to find best params for the given model.

    :param training_data: A 2-tuple, (vectors, label). 
    :param model_gen: A RegressionModel generator.
    :param params: All parameters the grid search needs to find. It's a subset
        of all the optional params on each model. i.e. for KNeighborsRegressor
        model, it's a subset of

        ```
        {
            "n_neighbors": [1, 5, 10, ...],
            "weights": ["uniform", ...],
            "algorithm": ["auto", ...],
            "leaf_size": [30, 50, ...],
            "p": [2, 5, ...],
            "metric": ["minkowski", ...],
            "metric_params": [...],
        }
        ```

    """
    print("model: {}".format(model_gen))
    print("scoring\tbest_score\tbest_params")
    vectors, label = training_data
    model = model_gen()
    for scoring in SCORINGS:
        clf = grid_search.GridSearchCV(model.model, params, scoring=scoring, n_jobs=CORE_NUM, cv=FOLDS)
        clf.fit(vectors, label)
        print("{}\t{}\t{}\t{}".format(scoring, clf.best_score_, clf.best_params_))

def grid_search_tasks(std_training_data):
    """One function to run grid search on different models

    CORE_NUM: int, number of CPU cores to be used
    FOLDS: int, number of folds for cross validate

    """
    import numpy
#    knn_model_gen = RegressionModelFactory("KNeighborsRegressor", n_neighbors=10, weights="distance")
    svr_model_gen = RegressionModelFactory("SVC")
#    dtree_model_gen = RegressionModelFactory("DecisionTreeRegressor", random_state=0)

    KNN_PARAMS = {
        "n_neighbors": range(1, 16),
        "weights": ["distance", "uniform"],
        "algorithm": ["ball_tree", "kd_tree", "brute"],
        "metric": ["euclidean", "chebyshev", "minkowski", ]
    }

    SVR_PARAMS = {
        "C": 10.0 ** numpy.arange(-4,4),
#        "epsilon": [0., 0.0001, 0.001, 0.01, 0.1],  # experience: epsilon>=0.1 is not good.
        "kernel": [
       "linear",
#        "rbf",
#        "poly",  # polynomial kernel sucks. Never use it.
#        "sigmoid",
        # "precomputed"
        ],
#        "degree": [5,], # because polynomial kernel sucks. Never use it.
        "gamma": 10.0 ** numpy.arange(-4, 4),
  }

    DTREE_PARAMS = {
#        "criterion": ["mse"],
        "splitter": ["best", "random"],
        "min_samples_split": range(2, 16),
        "min_samples_leaf": range(1, 16),
        "max_features": ["sqrt", "log2"],
#        "random_state": [0, 1, 10, 100],
    }

    SCORINGS = ["mean_squared_error",
#                "mean_absolute_error"
    ]


    TRAINING_PARMAS = [
#        (knn_model_gen, KNN_PARAMS),
        (svr_model_gen, SVR_PARAMS),
#      (dtree_model_gen, DTREE_PARAMS),
    ]

    FOLDS = 10
    CORE_NUM = 8

    [grid_search_cv(std_training_data, k, v, SCORINGS, CORE_NUM, FOLDS) for k, v in TRAINING_PARMAS]

def standardize_features(training_data):
    """Standarize feature vectors for each influx

    Later, a new feature vector X for i-th influx can be normalized as:
    Scalers[i].transform(X)

    """
    vectors, labels = training_data
    vectors_scaled = preprocessing.scale(vectors)
    std_training_data = (vectors_scaled, labels)

    return std_training_data

def cv_run(training_data):
    traning_data = standardize_features(training_data)
    vectors, labels = training_data
    X, y = sklearn.utils.shuffle(vectors, labels)
    grid_search_tasks((X,y))

if __name__  == "__main__":
    import pickle
    training_data = pickle.load(open("train.pickle",'rb'))
    cv_run(training_data)
