#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_word_features
---------------------------------

Tests for the word features module.
"""


from clicon.features.word_features import WordFeatures

def test_is_date():
    w = WordFeatures()
    return w.is_date('2014-08-25')  # should return True
