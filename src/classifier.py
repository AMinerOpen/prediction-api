# -*- coding: utf-8 -*-
'''
Introduction:
    Classifier is a class which is used to classify subjects.
    It depends on the classification of Natural Science Foundation of China(NSFC).
Usage:
    >>> nsfc = Classifier()
    >>> pub_titles = ['Annotating gene sets by mining large literature collections with protein networks.']
    >>> subject = nsfc.classify(pub_titles)
'''

import os
import fastText
import re
import jieba
from config import model_path
from utils.translator import youdao_translate

data_path = os.path.join(model_path, 'nsfc')


class Classifier:

    def __init__(self, path=data_path):
        self._clf = [
            fastText.load_model(os.path.join(path, 'clf0.bin')),
            fastText.load_model(os.path.join(path, 'clf1.bin')),
            fastText.load_model(os.path.join(path, 'clf2.bin')),
        ]
        self._zh_chars = re.compile('[^\u4e00-\u9fff]')
        self._id2name = dict()
        with open(os.path.join(data_path, 'nsfc_subject.csv'), encoding='utf-8') as f:
            for line in f:
                _id, _name = line[:-1].split(',') # encode csv
                self._id2name[_id] = _name

    def _get_name(self, code):
        # Get the name from the given subject code
        return self._id2name[code]

    def _get_code(self, label):
        '''
        In the model, we use '__label__' + NSFC subject code as labels.
        This function can extract the subject code from a label.
        '''
        return label[9:]

    def _tokenize(self, pubs):
        # Convert a sequence of characters into a sequence of tokens
        text_zh = youdao_translate(pubs)
        words = []
        for s in text_zh:
            # delete all characters which are not Chinese
            all_zh = self._zh_chars.sub('', s)
            words.extend(jieba.lcut(all_zh))
        return words

    def classify(self, pub_titles, level=0, ntop=5):
        '''
        Use publication titles to classify which subjects these publications belong to
        :param pub_titles: A list of publication titles
        :param level: Classification level(1,2,3), for other numbers you will get all of levels
        :param ntop: How many subjects in each level does the classifier select
        :return: A dictionary:
                 'level{x}'(x = 1, 2, 3)':
                     {
                        'code': subject code
                        'name': subject name
                        'p': probability
                     }
        '''
        ret = {}
        words = self._tokenize(pub_titles)
        text = ' '.join(words)
        for i in range(0, 3):
            if i + 1 == level or level not in [1, 2, 3]:
            #  level number equals its index plus one
                level_name = 'level{}'.format(i+1)
                ret[level_name] = self._clf[i].predict(text, ntop)
        # format
        for key, value in ret.items():
            new_value = []
            for label, prob in zip(value[0],value[1]):  # combine each label and its prob into a pair
                subject_code = self._get_code(label)
                new_value.append({
                    'code':subject_code,
                    'name': self._get_name(subject_code),
                    'p': prob
                })
            ret[key] = new_value
        return ret


if __name__ == '__main__':
    nsfc = Classifier()
    pub_titles = ['Annotating gene sets by mining large literature collections with protein networks.']
    subject = nsfc.classify(pub_titles)
    print(subject)