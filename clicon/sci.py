import numpy as np  
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.grid_search import GridSearchCV
from multiprocessing import cpu_count
from sklearn.metrics import f1_score

LIN = 2**0
CRF = 2**1
SVM = 2**2
ALL = sum(2**i for i in range(3))

def bits(n):
    while n:
        b = n & (~n+1)
        yield b
        n ^= b


def train(X, Y, type, do_grid):

    # Search space
    C_range     = 10.0 ** np.arange( -5, 9 )
    gamma_range = 10.0 ** np.arange( -5 , 9 )


    # Grid search
    retVal = {}
    for t in bits(type):

        if do_grid:

            if t == SVM:
                estimates = SVC()
                gamma_range = 10.0 ** np.arange( -5 , 9 )
                parameters = [{'kernel':['rbf'], 'C':C_range, 'gamma':gamma_range}]    
                
            if t == LIN:
                estimates = LinearSVC() 
                parameters = [ {'C':C_range } ]
                
            # Find best classifier
            clf = GridSearchCV(estimates, parameters, score_func = f1_score, n_jobs = cpu_count() )
            clf.fit( X , Y )
            retVal[t] = clf

        else:

            clf = LinearSVC()
            clf.fit(X, Y)
            retVal[t] = clf


    # Return all chosen classifiers
    return retVal



def predict(clfs, X, type):

    retVal = {}

    for t in bits(type):
        # Predict
        clf = clfs[t]
        output = clf.predict(X)
        retVal[t] = output

    # Return all predictions
    return retVal


