import cPickle as pickle 
import numpy as np  
from ast import literal_eval
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.feature_extraction import DictVectorizer
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

def write_features( model_filename, rows, labels=None ):

	file_suffix = ".sci" 
	if labels is None:
		file_suffix += ".test.in"
	filename = model_filename + file_suffix
	with open(filename, "w") as f:                                    
		f.write( str(rows) + '\n' )
		if labels is not None:
			assert "Dimension mismatch", len(rows) == len(labels)
		f.write( str(labels) ) 
	f.close() 

def train(model_filename, type):

	X = []
	Y = []
	filename = model_filename + ".sci"
	with open(filename, "r") as f:
		X = literal_eval(f.readline().strip())
		Y = literal_eval(f.readline())
	f.close()
	print "vectorizing" 
	DictVect = DictVectorizer()
	
	X = DictVect.fit_transform(X)

        C_range = 10.0 ** np.arange( -5, 9 )
	gamma_range = 10.0 ** np.arange( -5 , 9 )

	print "grid search" 
	for t in bits(type):
		if t == SVM:
			estimates = SVC()
			gamma_range = 10.0 ** np.arange( -5 , 9 )
			parameters = [ {'kernel':['rbf'], 'C':C_range, 'gamma':gamma_range } ]    
			test_output_dest = filename +".svm.trained"
			
		if t == LIN:
			estimates = LinearSVC() 
			parameters = [ {'C':C_range } ]
			test_output_dest = filename + ".lin.trained" 
			
		clf = GridSearchCV(estimates, parameters, score_func = f1_score, n_jobs = cpu_count() )
		clf.fit( X , Y )
	#"try to make it so i don't have to use pickle!"                                                                                                                        
		print "dumping"
		pickle.dump( clf, open( test_output_dest , "wr" ) )
	print "dumping" 
	pickle.dump( DictVect, open( filename + ".vec", "wr" ) )

def predict(model_filename, type):
	filename = model_filename + ".sci"
	X = [] 
	with open(filename + ".test.in", "rd") as f:
                X = literal_eval(f.readline().strip())
        f.close()
	
	vec = pickle.load( open( filename + ".vec" ,"rd" ) )

	print "Vectorizing"
        #i don't like the transform here, but itll have to do for now.                                                                                                          
	X = vec.transform(X).toarray()
        X = np.array( X , object )

	for t in bits(type):
		print "Performing Grid Search"
		if t == SVM:
			clf = pickle.load( open( filename + ".svm.trained" , "rd" ) )
			predict_input = filename + ".svm.test.out"

		if t == LIN:
			clf = pickle.load( open( filename + ".lin.trained" , "rd" ) ) 
			predict_input = filename + ".lin.test.out"
	#i don't like the transform here, but itll have to do for now. 
	
		with open( predict_input, "w") as prediction:
			for label in clf.predict(X):
				prediction.write( str(label) + '\n' ) 
		prediction.close()

def read_labels(model_filename, type ):
        labels = {} 
	for t in bits(type):
		if t == SVM:
			filename = model_filename + ".sci.svm.test.out"
		if t == LIN:
			filename = model_filename + ".sci.lin.test.out"

		with open(filename) as f:
			lines = f.readlines()                                                                                                         
		labels[t] = [line.strip() for line in lines]

        return labels


	
