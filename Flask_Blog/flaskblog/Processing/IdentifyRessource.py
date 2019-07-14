import spacy
from spacy.attrs import IS_STOP, IS_PUNCT, IS_SPACE, IS_OOV
import nltk
import numpy
from SPARQLWrapper import SPARQLWrapper, JSON
from .dataset import dataset
from fuzzywuzzy import process
from spacy import displacy

#============================== Initialisation ==============================================================
nlp = spacy.load("en_core_web_sm")
whquestion = ["where", "what", "when", "who"]
rawtext = ''
sparql= SPARQLWrapper("http://dbpedia.org/sparql")
Resources = dataset().get_resource()
# =========================================FUNCTIONS=======================================================

#############################################EXTRACT ENTITIES ##################################
def extract_entities(rawtext):

    doc = nlp(u""+rawtext.title())
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
    for chunk in doc.noun_chunks:
        doc=nlp(u""+chunk.text)
        for word in doc.ents: 
            NamedEntityList.append(word.root.text)
            NamedEntityLabel.append(word.label_)
            ExplanationList = spacy.explain(word.label_)
            NamedEntityDescription.append(ExplanationList)
        
    # print(NamedEntityLabel)
    # print(NamedEntityList)
    # print(NamedEntityDescription)
    return NamedEntityList, NamedEntityLabel, NamedEntityDescription


############################ MERGING ENTITIES ########################################

def merge_entities(NamedEntityList):
    NamedEntityListMerged=""
    
    NamedEntityListMerged="_".join(NamedEntityList)
    print(NamedEntityListMerged)
    return NamedEntityListMerged


##########################EXACT MATCH ################################################"
def exact_match(NamedEntityListMerged,NamedEntityList):
    print(NamedEntityList)
    ##################### CAS 1 ###########################################
    if len(NamedEntityListMerged)!=0:
        for EntityM in NamedEntityList:
            try:
                Resources.index(EntityM)
                print("Entity found "+EntityM)      
            except ValueError:
                print("Entity Not found")
    #################### CAS 2 ##############################################
    # if len(NamedEntityList)!=0:
    #     for Entity in NamedEntityList:
    #         try: 
    #             Resources.index(Entity)
    #             print("Entity found "+Entity)
    #         except ValueError:
    #             print("Entity Not found")
    ############# LE CAS 3 ####################################################################
        #         sparql.setQuery("""
        #         PREFIX dbr:<http://dbpedia.org/resource/> PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> PREFIX dbo:<http://dbpedia.org/ontology/> PREFIX foaf:<http://xmlns.com/foaf/0.1/>
        #         SELECT ?label
        #         WHERE { <http://dbpedia.org/resource/"""+Entity+"""> rdfs:label ?label }

        # """)
        #         sparql.setReturnFormat(JSON)
        #         results = sparql.query().convert()
        #         for result in results["results"]["bindings"]:
        #             print(result["label"]["value"])
  
############################# REDIRECT ###############################################################                
def redirects_property(NamedEntityList):
    #print(len(NamedEntityList))
    for Entity in NamedEntityList:
        
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
        redirect=[]
        for result in results["results"]["bindings"]:
            redirect=result["redirect"]["value"]
            #print(redirect)
        
           
############################## STRING SIMILARITY #################################################        
def get_matches(query,choice,limit=5):
     results=process.extract(query,choice,limit=limit)   
     return results
   
def check_string_similarity(rawtext):
    catch_entity=[]
    doc = nlp(u""+rawtext.title())
    for chunk in doc.noun_chunks:        
        for token in chunk:    
            #print(token.text,token.pos_,token.tag_,token.dep_)
            if (token.pos_=="PROPN" and token.tag_=="NNP"):
                catch_entity.append(token.text)
    for entity in catch_entity:
        PossibleEntity=get_matches(entity,Resources)
        #print(PossibleEntity)
                        
#################################### CHECK AMBIGUITY ############################################
def check_ambiguity(NamedEntityList):

 #print(len(NamedEntityList))
    for Entity in NamedEntityList:       
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
        disambiguation=[]
        for result in results["results"]["bindings"]:
            disambiguation=result["disambiguation"]["value"]
            #print(disambiguation)