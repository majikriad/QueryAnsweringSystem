import spacy
import nltk
import numpy
from SPARQLWrapper import SPARQLWrapper, JSON
from .dataset import dataset
#============================== Initialisation ==============================================================
nlp = spacy.load("en_core_web_sm")
whquestion = ["where", "what", "when", "who"]

rawtext = ''
sparql= SPARQLWrapper("http://dbpedia.org/sparql")
Resources = dataset().get_resource()
# =========================================FUNCTIONS=======================================================


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
    
    for word in doc.ents:
        NamedEntityList.append(word.root.text)
        NamedEntityLabel.append(word.label_)
        ExplanationList = spacy.explain(word.label_)
        NamedEntityDescription.append(ExplanationList)
    
    print(NamedEntityLabel)
    print(NamedEntityList)
    print(NamedEntityDescription)
    return NamedEntityList, NamedEntityLabel, NamedEntityDescription




def merge_entities(NamedEntityList):
    NamedEntityListMerged = ''.join(NamedEntityList)
    print(NamedEntityListMerged)


def exact_match(NamedEntityListMerged,NamedEntityList):
    
    
   
   
    if len(NamedEntityListMerged)!=0:
        for EntityM in NamedEntityListMerged:
            try:
                Resources.index(EntityM)
                print("Entity found "+EntityM)      
            except ValueError:
                print("Entity Not found")
    
    if len(NamedEntityList)!=0:
        for Entity in NamedEntityList:
            try: 
                Resources.index(Entity)
                print("Entity found "+Entity)
            except ValueError:
                print("Entity Not found")
        #         sparql.setQuery("""
        #         PREFIX dbr:<http://dbpedia.org/resource/> PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> PREFIX dbo:<http://dbpedia.org/ontology/> PREFIX foaf:<http://xmlns.com/foaf/0.1/>
        #         SELECT ?label
        #         WHERE { <http://dbpedia.org/resource/"""+Entity+"""> rdfs:label ?label }

        # """)
        #         sparql.setReturnFormat(JSON)
        #         results = sparql.query().convert()
        #         for result in results["results"]["bindings"]:
        #             print(result["label"]["value"])
  
                
def redirect(NamedEntityList):
    print(len(NamedEntityList))
    for Entity in NamedEntityList:
        
        #WHERE { <http://dbpedia.org/resource/"""+Entity+""" <http://dbpedia.org/ontology/wikiPageRedirects> ?redirect}
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
            
            redirect=result["redirect"]["value"]
        return redirect
    
    
def check_string_similarity(rawtext):
    doc = nlp(u""+rawtext.title())
    for token in doc:
        print(token)

#def check_ambiguity():
    
if __name__ == '__main__':
    Resources = dataset().get_resource()
    print(Resources)
