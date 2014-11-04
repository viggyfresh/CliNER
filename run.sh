file="00098-016139"

#python clicon/train.py -t test/text/$file.text  -c test/pipe/$file.pipe -f semeval

python clicon/predict.py -i test/text/$file.text -f semeval
