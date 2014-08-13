import numpy as np  
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.grid_search import GridSearchCV
from multiprocessing import cpu_count
from sklearn.metrics import f1_score



def train(X, Y, do_grid):

    # Grid search
    do_grid = True
    if do_grid:

        estimates = LinearSVC() 
        C_range     = 10.0 ** np.arange( -5, 9 )
        parameters = [ {'C':C_range } ]
                
        # Find best classifier
        clf = GridSearchCV(estimates, parameters, score_func = f1_score, n_jobs = cpu_count()).estimator
        clf.fit(X , Y)

    else:

        clf = LinearSVC()
        clf.fit(X, Y)


    # Return chosen classifier
    return clf



def predict(clf, X):
    # Predict
    retVal = list(clf.predict(X))
    return retVal

