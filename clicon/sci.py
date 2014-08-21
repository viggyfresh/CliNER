import numpy as np  
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.grid_search import GridSearchCV
from multiprocessing import cpu_count
from sklearn.metrics import f1_score



def train(X, Y, do_grid):

    # Search space
    C_range     = 10.0 ** np.arange( -5, 9 )
    gamma_range = 10.0 ** np.arange( -5 , 9 )


    # Grid search
    if do_grid:

        '''
        estimates = SVC()
        gamma_range = 10.0 ** np.arange( -5 , 9 )
        parameters = [{'kernel':['rbf'], 'C':C_range, 'gamma':gamma_range}]    
        '''
            
        estimates = LinearSVC() 
        parameters = [ {'C':C_range } ]
            
        # Find best classifier
        clf = GridSearchCV(estimates, parameters, score_func = f1_score, 
                           n_jobs = cpu_count()                        )
        clf.fit(X, Y)

    else:

        clf = LinearSVC()
        clf.fit(X, Y)


    # Return all chosen classifiers
    return clf



def predict(clf, X):

    # Predict
    output = clf.predict(X)
    return output


