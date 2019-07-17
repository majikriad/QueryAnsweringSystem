import spacy
from spacy.attrs import IS_STOP, IS_PUNCT, IS_SPACE, IS_OOV
import nltk
import numpy
from SPARQLWrapper import SPARQLWrapper, JSON
from .dataset import dataset
from fuzzywuzzy import process
from spacy import displacy
import spotlight
import re
# ============================== Initialisation ==============================================================
nlp = spacy.load("en_core_web_sm")

 
whquestion = ["Where", "What", "When", "Who"]
whenquestion =['time','date','year','month','day','hour','minute']
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
def extract_entities_Spacy(rawtext):
    SpacyEntity=[]
    SpacyEntityLabel=[]
    doc = nlp(u""+rawtext)
    for token in doc:
        if token.check_flag(IS_STOP):
            string = r"\b{} \b".format(token.text)
            string2 = r"\b{}\b".format(token.text)
            rawtext = re.sub(string, "", rawtext)
            rawtext = re.sub(string2, "", rawtext)       
    for ent in doc.ents:
        SpacyEntity.append(ent.text)
        SpacyEntityLabel.append(ent.label_)
        for token in doc:
            string = r"\b{} \b".format(ent.text)
            string2 = r"\b{}\b".format(ent.text)
            rawtext = re.sub(string, "", rawtext)
            rawtext = re.sub(string2, "", rawtext)
    SpacyProperty=rawtext.split()
  
    if len(SpacyProperty)>1:
        for i in range(1,len(SpacyProperty)):
            SpacyProperty[i]=SpacyProperty[i].title()
    SpacyPropertyMerged=[]
    SpacyPropertyMerged=merge_Property(SpacyProperty)                  
    print("############EXTRACTING WITH SPACY ENTITY########")
    print(rawtext)
    print("############ENTITY ############")
    print(SpacyEntity)
    print("############PROPRETY############")
    print(SpacyProperty)
    
    return SpacyEntity,SpacyEntityLabel,SpacyPropertyMerged
        


       
def extract_entities_Manualy(rawtext):
    PropertyCandidate = []
    PropertyCandidatelemma = []
    doc = nlp(u""+rawtext)

    stopwords = open("stopwords.txt", "w")  
    for token in doc:
        if ((token.tag_ == "NNP" or token.tag_ == "NOUN") and (token.dep_ == "nsubj") or (token.dep_ == "nsubjpass") ) or ((token.pos_ == "VERB" or token.pos == "NOUN") and (token.dep_ == "ROOT")) and not (token.check_flag(IS_STOP)):
            PropertyCandidate.append(token.text)
            PropertyCandidatelemma.append(token.lemma_)
        if token.check_flag(IS_STOP) or token.dep_ == "prep" or token.pos_ == "ADP":
            stopwords.write(token.text+"\n")
            # il remplace aussi l'espace
            string = r"\b{} \b".format(token.text)
            string2 = r"\b{}\b".format(token.text)
            rawtext = re.sub(string, "", rawtext)
            rawtext = re.sub(string2, "", rawtext)
    possiblecandidate=PropertyCandidate    
    NamedEntityListMainly = []
    doc2 = nlp(u""+rawtext)
    for chunk in doc2.noun_chunks:
        NamedEntityListMainly.append(chunk.root.text)
    NamedEntityMerged = []
    PropertyMerged = []
    
    for Entity in NamedEntityListMainly:
        Ecore1=0
        Ecore1=get_matches(Entity, Resources)[0][1]
        EntitytoSelect=""
        if (Ecore1>79):
            EntitytoSelect=get_matches(Entity, Resources)[0][0]
            NamedEntityListMainly.remove(Entity)
            NamedEntityListMainly.append(EntitytoSelect)
    
    for Entity in NamedEntityListMainly:
        Ecore2=0
        Ecore2=get_matches(Entity, Predicat)[0][1]
        EntitytoRemove=""
        if (Ecore2>=90):
            EntitytoRemove=get_matches(Entity, Predicat)[0][0]
            NamedEntityListMainly.remove(Entity)
            PropertyCandidate.append(EntitytoRemove)
    PropertyCandidate[0]=PropertyCandidate[0].lower()
    NamedEntityListMainly=removeDuplicates(NamedEntityListMainly)
    PropertyCandidate=removeDuplicates(PropertyCandidate)       
    NamedEntityMerged = merge_entities(NamedEntityListMainly)
    PropertyMerged = merge_Property(PropertyCandidate)
    
    return PropertyCandidate, PropertyMerged,possiblecandidate,NamedEntityListMainly, NamedEntityMerged

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
    for Entities in NamedEntityListMainly:
        Entities=str(Entities)   
        check_ambiguity(Entities)

def exact_match_property(PropertyCandidate, PropertyMerged,possiblecandidate,EAT,SpacyEntity):
    
    Entity=""
    for Entity in SpacyEntity:
        Entity=SpacyEntity.pop()
        Entity=Entity.replace(' ','_')
    
    
    if (EAT=="Where"):
        Properties=wherequestion
        Query_where(Entity,Properties)
    elif (EAT=="When"):
        Properties=whenquestion
        Query_when(Entity,Properties)
    elif (EAT=="Who"):
        Query_Name(Entity)       
    elif (EAT=="") and len(PropertyMerged)!=0:
        Query_Property_Merged(Entity,PropertyMerged)
        
                
def Query_when(Entity,Properties):    
    print("RAhou yedkhol Hna ou pas when")
    for Property in Properties:
        Property=Property.title()
        sparql.setQuery("""
        PREFIX dbr:<http://dbpedia.org/resource/> PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> PREFIX dbo:<http://dbpedia.org/ontology/> PREFIX foaf:<http://xmlns.com/foaf/0.1/>
        SELECT ?label
        WHERE{  
        {<http://dbpedia.org/resource/"""+Entity+"""> ?property ?label}
        UNION
        {<http://dbpedia.org/resource/"""+Entity+"""> ?property ?label}
        FILTER regex(?property, "^.*"""+Property+"""*")
        }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            print(result["label"]["value"])
def Query_where(Entity,Properties):
    print("RAhou yedkhol Hna ou pas where")
    for Property in Properties:
        Property=Property.title()    
        sparql.setQuery("""
        PREFIX dbr:<http://dbpedia.org/resource/> PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> PREFIX dbo:<http://dbpedia.org/ontology/> PREFIX foaf:<http://xmlns.com/foaf/0.1/>
        SELECT ?label
        WHERE{  
        {<http://dbpedia.org/resource/"""+Entity+"""> ?property ?label}
        UNION
        {<http://dbpedia.org/resource/"""+Entity+"""> ?property ?label}
        FILTER regex(?property, "^.*"""+Property+"""*")
        }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            print(result["label"]["value"])         

def Query_Property_Merged(Entity,PropertyMerged):
    Property=str(PropertyMerged) 
    print(Property)
    sparql.setQuery("""
    PREFIX dbr:<http://dbpedia.org/resource/> PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> PREFIX dbo:<http://dbpedia.org/ontology/> PREFIX foaf:<http://xmlns.com/foaf/0.1/>
    SELECT ?label
    WHERE{  
    {<http://dbpedia.org/resource/"""+Entity+"""> ?property ?label}
    UNION
    {<http://dbpedia.org/resource/"""+Entity+"""> ?property ?label}
    FILTER regex(?property, "^.*"""+Property+"""*")
    }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        print(result["label"]["value"])

def Query_Name(Entity):
    sparql.setQuery("""
    PREFIX dbr:<http://dbpedia.org/resource/> PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> PREFIX dbo:<http://dbpedia.org/ontology/> PREFIX foaf:<http://xmlns.com/foaf/0.1/>
    SELECT ?name
    WHERE { 
    {<http://dbpedia.org/resource/"""+Entity+"""> <http://xmlns.com/foaf/0.1/name> ?name }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        print(result["name"]["value"])   
                 
def Query_label(Entity):
    Entity=Entity.title()
    sparql.setQuery("""
    PREFIX dbr:<http://dbpedia.org/resource/> 
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX dbo:<http://dbpedia.org/ontology/> 
    PREFIX foaf:<http://xmlns.com/foaf/0.1/>
    SELECT ?label
    WHERE { <http://dbpedia.org/resource/"""+Entity+"""> rdfs:label ?label 
    filter (lang(?label) = "en")   
     }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        print(result["label"]["value"])
           

############################# REDIRECT ###############################################################


def redirects(Entity):
    # Entity=Entity.title()
    print("rani f redirect")
    print(Entity)
    sparql.setQuery("""
                PREFIX dbr:<http://dbpedia.org/resource/>
                PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
                PREFIX dbo:<http://dbpedia.org/ontology/>
                PREFIX foaf:<http://xmlns.com/foaf/0.1/>
                SELECT ?redirect
                WHERE{?x <http://dbpedia.org/ontology/wikiPageRedirects> ?redirect
                FILTER regex(?redirect, "^.*"""+Entity+"""*")
               }
                LIMIT 10
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
                LIMIT 10
        """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    for result in results["results"]["bindings"]:
        print(result["disambiguation"]["value"])
    
