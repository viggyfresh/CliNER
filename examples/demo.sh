#!/bin/sh


# Train model on an xml-formatted file
# Note, 'examples' directory only has one xml file (but clicon accepts globs)
clicon train "$CLICON_DIR/examples/*.xml" --format xml


# Use trained model to predict concepts for a given txt file
# Note, 'examples' directory only has one txt file (but clicon accepts globs)
clicon predict "$CLICON_DIR/examples/*.txt" --out $CLICON_DIR/data/test_predictions/ --format xml


# Evaluate how well the system classified.
# Note, in this case it is 100% because it trained/predicted on the same file.
clicon evaluate "$CLICON_DIR/examples/pretend.txt" --gold $CLICON_DIR/examples --predictions $CLICON_DIR/data/test_predictions/ --format xml
