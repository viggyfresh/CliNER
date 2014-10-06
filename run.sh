clicon train "$CLICON_DIR/data/train/txt/*.txt" --annotations "$CLICON_DIR/data/train/con/*.con"

clicon predict "$CLICON_DIR/data/test_data/*.txt"

clicon evaluate "$CLICON_DIR/data/test_data/*.txt" --predictions "$CLICON_DIR/data/test_predictions" --gold "$CLICON_DIR/data/reference_standard_for_test_data/concepts"

