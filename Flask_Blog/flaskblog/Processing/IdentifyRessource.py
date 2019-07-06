import spacy
import nltk
import numpy

from .dataset import dataset
# load NLP instance
nlp = spacy.load("en_core_web_sm")
whquestion = ["where", "what", "when", "who"]

# import sibilling package data

rawtext = ''

# =========================================FUNCTIONS=======================================================


def extract_entities(rawtext):
    doc = nlp(u""+rawtext)
    # sents = list(doc.sents)
    # if len(sents) > 1 :
    #     try:
    #         raise NameError('Double Sentence')
    #     except NameError:
    #         print('There is more than one sentence !')
    #         raise
    NamedEntityList = []
    NamedEntityLabel = []
    NamedEntityDescription = []
    for word in doc.ents:
        NamedEntityList.append(word.text)
        NamedEntityLabel.append(word.label_)
        ExplanationList = spacy.explain(word.label_)
        NamedEntityDescription.append(ExplanationList)
    if len(NamedEntityList) > 2:
        merge_entities(NamedEntityList)
    return NamedEntityList, NamedEntityLabel, NamedEntityDescription

    # print(NamedEntityLabel)
    # print(NamedEntityList)
    # print(NamedEntityDescription)


def merge_entities(NamedEntityList):

    NamedEntityListMerged = ''.join(NamedEntityList)
    print(NamedEntityListMerged)


def get_ressource():
    Resources = dataset().get_resource()


# def check_ambiguity
if __name__ == '__main__':
    Resources = dataset().get_resource()
    print(Resources)
