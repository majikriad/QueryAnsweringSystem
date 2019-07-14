import os
import spacy
from spacy.attrs import IS_STOP, IS_PUNCT, IS_SPACE, IS_OOV
from .dataset import dataset
from .IdentifyRessource import extract_entities
import re

#==========================================Intialisation================================== 
nlp = spacy.load('en_core_web_sm')
rawtext=''
PredicatList=dataset().get_Predicates()
# Create a list of WH questions 
whquestion = ["where","when", "who"]
whenquestion =['time','date','year','month','day','hour','minute','seconds']
wherequestion=['place','location','city','country','state','town']
who='PERSON'
#========================================FUNCTIONS============================
def get_typed_quest(inputText):
    rawtext=inputText


    
#def get_fetched_ressource

def get_Expected_Answer_type(rawtext):
    doc=nlp(u""+rawtext)
    
    for token in doc:
        if token.text in whquestion: 
            print("we expect "+token.text+" question")
            EAT=token.text
    return EAT
        
def remove_stpwords_from_query(rawtext):
    doc=nlp(u""+rawtext)
    stopwords=open("stopwords.txt","w")
    for token in doc:
        if token.check_flag(IS_STOP):
            stopwords.write(token.text+"\n")
            string = r"\b{} \b".format(token.text) # il remplace aussi l'espace 
            rawtext=re.sub(string ,"" ,rawtext)   
    #print(rawtext)               
    return rawtext.split()
            

def remove_NE_from_filquest(rawtext,NamedEntityList):
    
    for Entity in NamedEntityList:
        if (rawtext.find(Entity)):
            rawtext=rawtext.replace(Entity,'')
    #print(rawtext)
    return rawtext
            
#def exact_match(Candidate):
    #print(Candidate)
    # for key in PredicatList.keys():      
    #     # for c in Candidate:
    #     #     if c==key:
    #     #         print("found")
    #     #     else: 
    #     #         print("not found")
        
# def check_semantic_similarity(Candidate):

# def exact_substring_match(Candidate):
    
#def get_relation_identification():
    