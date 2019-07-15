import spacy
from spacy.attrs import IS_STOP, IS_PUNCT, IS_SPACE, IS_OOV
import nltk
import numpy
from SPARQLWrapper import SPARQLWrapper, JSON
from .dataset import dataset
from fuzzywuzzy import process
from spacy import displacy
import re
# ============================== Initialisation ==============================================================
nlp = spacy.load("en_core_web_sm")

whquestion = ["Where", "What", "When", "Who"]
whenquestion =['time','date','year','month','day','hour','minute','seconds']
wherequestion=['place','location','city','country','state','town']

rawtext = ''
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
Resources = dataset().get_resource()
Predicat = dataset().get_Predicates()
# =========================================FUNCTIONS=======================================================

#############################################EXTRACT ENTITIES ##################################

def get_Expected_Answer_type(rawtext):
    EAT=""
    doc=nlp(u""+rawtext.title())
    for token in doc:
        if token.text in whquestion:
            EAT=token.text
    return EAT

def extract_entities_Manualy(rawtext):
    SpacyEntity=[]
    SpacyEntityLabel=[]
    PropertyCandidate = []
    PropertyCandidatelemma = []
    doc = nlp(u""+rawtext.title())
    for ent in doc.ents:
        SpacyEntity.append(ent.text)
        SpacyEntityLabel.append(ent.label_)
    stopwords = open("stopwords.txt", "w")
    for token in doc:
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
              token.shape_, token.is_alpha, token.is_stop)
        if ((token.tag_ == "NNP" or token.tag_ == "NOUN") and (token.dep_ == "nsubj") or (token.dep_ == "nsubjpass") ) or ((token.pos_ == "VERB" or token.pos == "NOUN") and (token.dep_ == "ROOT")) and not (token.check_flag(IS_STOP)):
            PropertyCandidate.append(token.text.lower())
            PropertyCandidatelemma.append(token.lemma_)
    
       

    doc = nlp(u""+rawtext)
    for token in doc:
        if token.check_flag(IS_STOP) or token.dep_ == "prep" or token.pos_ == "ADP":
            stopwords.write(token.text+"\n")
            # il remplace aussi l'espace
            string = r"\b{} \b".format(token.text)
            string2 = r"\b{}\b".format(token.text)
            rawtext = re.sub(string, "", rawtext)
            rawtext = re.sub(string2, "", rawtext)


    possiblecandidate=PropertyCandidate    
    NamedEntityListMainly = []
    rawtext=rawtext.title()
    NamedEntityListMainly = rawtext.split()
    NamedEntityMerged = []
    # NamedEntityMerged = merge_entities(NamedEntityListMainly)
    PropertyMerged = []
    Entitytodelete = []
    # PropertyMerged = merge_Property(PropertyCandidate)
    # print(NamedEntityListMainly)
    # print(PropertyCandidate)
    for Entity in NamedEntityListMainly:
        # print(NamedEntityListMainly)
        # print("Mon entité ")
        # print(Entity)
        Ecore1=0
        Ecore2=0  
        Ecore1=(get_matches(Entity, Resources)[0][1])
        # print(str(Ecore1)+"  Entity Dakhel ressource")
        Ecore2=(get_matches(Entity, Predicat)[0][1])
        # print(str(Ecore2)+"  Entity Dakhel Predicat")
        if Ecore1 < Ecore2:    
            PropertyCandidate.append(Entity)
            Entitytodelete.append(Entity)
    
    NamedEntityListMainly=Diff(NamedEntityListMainly,Entitytodelete)
    Propertytodelete=[]
    #NamedEntityMerged = merge_entities(NamedEntityListMainly)
    for properties in PropertyCandidate:
        # print("ma propriété ")
        # print(properties)
        Score1=0
        Score2=0  
        Score1=(get_matches(properties, Predicat)[0][1])
        # print(str(Score1)+" Score1 Property Dakhel Predicat")
        Score2=(get_matches(properties, Resources)[0][1])
        # print(str(Score2)+" Score2 Property Dakhel Resource")
        if Score1 < Score2:    
            NamedEntityListMainly.append(properties)
            Propertytodelete.append(Entity)
    PropertyCandidate=Diff(PropertyCandidate,Propertytodelete)        
    NamedEntityListMainly=removeDuplicates(NamedEntityListMainly)
    PropertyCandidate=removeDuplicates(PropertyCandidate)          
    NamedEntityMerged = merge_entities(NamedEntityListMainly)
    
    PropertyMerged = merge_Property(PropertyCandidate)
    print("RESULTAT FINAL ? ")
    print(NamedEntityListMainly)
    print(NamedEntityMerged)
    print(PropertyCandidate)
    print(PropertyMerged)
    print(SpacyEntity)
    return PropertyCandidate, PropertyMerged,possiblecandidate,NamedEntityListMainly, NamedEntityMerged, SpacyEntity, SpacyEntityLabel

def Diff(li1, li2): 
    return (list(set(li1) - set(li2))) 

def removeDuplicates(listofElements):
    
    uniqueList = []
    for elem in listofElements:
        if elem not in uniqueList:
            uniqueList.append(elem)        
    return uniqueList

def merge_entities(NamedEntityList):
    NamedEntityList=list(map((lambda Entity:Entity.title()), NamedEntityList))
    NamedEntityListMerged = ""
    NamedEntityListMerged = "_".join(NamedEntityList)
    return NamedEntityListMerged


def merge_Property(PropertyCandidate):

    PropertyCandidateMerged = ""
    PropertyCandidateMerged = "".join(PropertyCandidate)
    return PropertyCandidateMerged

def get_matches(query, choice, limit=1):
    results = process.extract(query, choice, limit=limit)
    return results


def check_string_similarity(rawtext):
    print("on essaye de trouver le ressource avec check similarity")
    catch_entity = []
    doc = nlp(u""+rawtext.title())
    for chunk in doc.noun_chunks:
        print(chunk)
        for token in chunk:
            if (token.pos_ == "PROPN" and token.tag_ == "NNP"):
                catch_entity.append(token.text)


def exact_match_entity(NamedEntityListMainly, NamedEntityMerged,SpacyEntity):
    for Ent in SpacyEntity:
        Ent=SpacyEntity.pop()
        Ent=Ent.replace(' ','_')
        Query_label(Ent)     
        redirects(Ent)  
    Entity=str(NamedEntityMerged)
    if len(NamedEntityMerged)!=0:
        Query_label(Entity)     
        redirects(Entity)          
    # for Entities in NamedEntityListMainly:
    #     Entities=str(Entities)   
    #     check_ambiguity(Entities)

# def exact_match_property(PropertyCandidate, PropertyMerged,possiblecandidate,EAT,Entity):
     
#     if (EAT=="Where"):
#         Properties=wherequestion
#         Query_where(Entity,Properties)
#     elif (EAT=="When"):
#         Properties=whenquestion
#         Query_when(Entity,Properties)
#     elif (EAT=="Who"):
#         Query_Name(Entity)       
#     elif (EAT=="") and len(PropertyMerged)!=0:
#         Query_Property_Merged(Entity,PropertyMerged)
        
                
# def Query_when(Entity,Properties):    
    
#     for Property in Properties:
#          sparql.setQuery("""
#     PREFIX dbr:<http://dbpedia.org/resource/> PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> PREFIX dbo:<http://dbpedia.org/ontology/> PREFIX foaf:<http://xmlns.com/foaf/0.1/>
#     SELECT ?label
#     WHERE { 
#     {<http://dbpedia.org/resource/"""+Entity+"""> <http://dbpedia.org/ontology/"""+Property+"""> ?label }
#     UNION
#     {<http://dbpedia.org/resource/"""+Entity+"""> <http://dbpedia.org/property/"""+Property+"""> ?label }
#     }
#     """)
#     sparql.setReturnFormat(JSON)
#     results = sparql.query().convert()
#     for result in results["results"]["bindings"]:
#         print(result["label"]["value"])
# def Query_where(Entity,Properties):
    
#     for Property in Properties:
#        sparql.setQuery("""
#     PREFIX dbr:<http://dbpedia.org/resource/> PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> PREFIX dbo:<http://dbpedia.org/ontology/> PREFIX foaf:<http://xmlns.com/foaf/0.1/>
#     SELECT ?label
#     WHERE { 
#     {<http://dbpedia.org/resource/"""+Entity+"""> <http://dbpedia.org/ontology/"""+Property+"""> ?label }
#     UNION
#     {<http://dbpedia.org/resource/"""+Entity+"""> <http://dbpedia.org/property/"""+Property+"""> ?label }
#     }
#     """)
#     sparql.setReturnFormat(JSON)
#     results = sparql.query().convert()
#     for result in results["results"]["bindings"]:
#         print(result["label"]["value"])         

# def Query_Property_Merged(Entity,PropertyMerged):
#     Property=str(PropertyMerged) 
#     sparql.setQuery("""
#     PREFIX dbr:<http://dbpedia.org/resource/> PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> PREFIX dbo:<http://dbpedia.org/ontology/> PREFIX foaf:<http://xmlns.com/foaf/0.1/>
#     SELECT ?label
#     WHERE { 
#     {<http://dbpedia.org/resource/"""+Entity+"""> <http://dbpedia.org/ontology/"""+Property+"""> ?label }
#     UNION
#     {<http://dbpedia.org/resource/"""+Entity+"""> <http://dbpedia.org/property/"""+Property+"""> ?label }
#     }
#     """)
#     sparql.setReturnFormat(JSON)
#     results = sparql.query().convert()
#     for result in results["results"]["bindings"]:
#         print(result["label"]["value"])

# def Query_Name(Entity):
#     sparql.setQuery("""
#     PREFIX dbr:<http://dbpedia.org/resource/> PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> PREFIX dbo:<http://dbpedia.org/ontology/> PREFIX foaf:<http://xmlns.com/foaf/0.1/>
#     SELECT ?name
#     WHERE { 
#     {<http://dbpedia.org/resource/"""+Entity+"""> <http://xmlns.com/foaf/0.1/name> ?name }
#     """)
#     sparql.setReturnFormat(JSON)
#     results = sparql.query().convert()
#     for result in results["results"]["bindings"]:
#         print(result["name"]["value"])   
                 
def Query_label(Entity):
    Entity=Entity.title()
    sparql.setQuery("""
    PREFIX dbr:<http://dbpedia.org/resource/> PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> PREFIX dbo:<http://dbpedia.org/ontology/> PREFIX foaf:<http://xmlns.com/foaf/0.1/>
    SELECT ?label
    WHERE { <http://dbpedia.org/resource/"""+Entity+"""> rdfs:label ?label }

    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        print(result["label"]["value"])
           

############################# REDIRECT ###############################################################


def redirects(Entity):
    # Entity=Entity.title()
    # print("rani f redirect")
    # print(Entity)
    sparql.setQuery("""
                PREFIX dbr:<http://dbpedia.org/resource/>
                PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
                PREFIX dbo:<http://dbpedia.org/ontology/>
                PREFIX foaf:<http://xmlns.com/foaf/0.1/>
                SELECT ?redirect
                WHERE{
                <http://dbpedia.org/resource/"""+Entity+"""> <http://dbpedia.org/ontology/wikiPageRedirects>  ?redirect.}

        """)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    
    for result in results["results"]["bindings"]:
        print(result["redirect"]["value"])
            

#################################### CHECK AMBIGUITY ############################################


def check_ambiguity(Entity):
    Entity=Entity.title()
    sparql.setQuery("""
                PREFIX dbr:<http://dbpedia.org/resource/>
                PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
                PREFIX dbo:<http://dbpedia.org/ontology/>
                PREFIX foaf:<http://xmlns.com/foaf/0.1/>
                SELECT ?disambiguation
                WHERE{
                {<http://dbpedia.org/resource/"""+Entity+"""> <http://dbpedia.org/ontology/wikiPageDisambiguation>  ?disambiguation.}
                    UNION
                {<http://dbpedia.org/resource/"""+Entity+"""_(disambiguation)> <http://dbpedia.org/ontology/wikiPageDisambiguates>  ?disambiguation.}
                }

        """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    for result in results["results"]["bindings"]:
        print(result["disambiguation"]["value"])
    
