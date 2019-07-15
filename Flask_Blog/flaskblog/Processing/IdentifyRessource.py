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
whquestion = ["where", "what", "when", "who"]
rawtext = ''
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
Resources = dataset().get_resource()
Predicat = dataset().get_Predicates()
# =========================================FUNCTIONS=======================================================

#############################################EXTRACT ENTITIES ##################################


def extract_entities_Manualy(rawtext):

    PropertyCandidate = []
    PropertyCandidatelemma = []
    doc = nlp(u""+rawtext.title())
    stopwords = open("stopwords.txt", "w")
    for token in doc:
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
              token.shape_, token.is_alpha, token.is_stop)
        if (token.tag_ == "NNP" or token.tag_ == "NOUN") and (token.dep_ == "nsubj") or (token.dep_ == "nsubjpass") and not (token.check_flag(IS_STOP)):
            # Neighbor = list(token.lefts)[-1]
            # print(Neighbor)
            # if (Neighbor.pos_ == "compound"):
            #     PropertyCandidate.append(Neighbor.text)

            PropertyCandidate.append(token.text.lower())
            PropertyCandidatelemma.append(token.lemma_)

        if (token.pos_ == "VERB" or token.pos == "NOUN") and (token.dep_ == "ROOT") and not (token.check_flag(IS_STOP)):
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

    print("Les propriété candidates:")
    possiblecandidate=PropertyCandidate
    print(possiblecandidate)
    NamedEntityListMainly = []
    NamedEntityListMainly = rawtext.split()
    NamedEntityMerged = []
    NamedEntityMerged = merge_entities(NamedEntityListMainly)
    PropertyMerged = []
    PropertyMerged = merge_Property(PropertyCandidate)
    for Entity in NamedEntityListMainly:
        if (get_matches(Entity, Resources)[0][1]) < 90:
            if (get_matches(Entity, Predicat)[0][1]) >= 90:
                PropertyCandidate.append(Entity)
            NamedEntityListMainly.remove(Entity)

    print("le resultat de la similarité des entités")
    print(NamedEntityListMainly)
    print(PropertyCandidate)

    for properties in PropertyCandidate:
        if (get_matches(properties, Predicat)[0][1]) < 90:
            if (get_matches(properties, Resources)[0][1]) >= 90:
                NamedEntityListMainly.append(properties)
            PropertyCandidate.remove(properties)
    print(NamedEntityListMainly)
    print(PropertyCandidate)

    return PropertyCandidate, PropertyMerged, NamedEntityListMainly, NamedEntityMerged


############################ MERGING ENTITIES ########################################
# def extract_entities_automatic(rawtext):
#     NamedentityListAutomatic = []
#     NamedentityLabelAutomatic = []
#     doc = nlp(u""+rawtext)

#     for ent in doc.ents:
#         print(ent.text, ent.label_)
#     #     NamedentityListAutomatic.append(token.root.text)
#     #     NamedentityLabelAutomatic.append(token.label_)
#     # print(NamedentityListAutomatic)
#     # print(NamedentityLabelAutomatic)


def merge_entities(NamedEntityList):

    NamedEntityListMerged = ""

    NamedEntityListMerged = "_".join(NamedEntityList)
    print(NamedEntityListMerged)
    return NamedEntityListMerged


def merge_Property(PropertyCandidate):

    PropertyCandidateMerged = ""

    PropertyCandidateMerged = "".join(PropertyCandidate)
    print(PropertyCandidateMerged)
    return PropertyCandidateMerged

# EXACT MATCH ################################################"


def exact_match(NamedEntityListMerged, NamedEntityList):
    print(NamedEntityList)
    ##################### CAS 1 ###########################################
    if len(NamedEntityListMerged) != 0:
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
    # print(len(NamedEntityList))
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
        redirect = []
        for result in results["results"]["bindings"]:
            redirect = result["redirect"]["value"]
            # print(redirect)


############################## STRING SIMILARITY #################################################
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
            # print(token.text,token.pos_,token.tag_,token.dep_)
            if (token.pos_ == "PROPN" and token.tag_ == "NNP"):
                catch_entity.append(token.text)

    # for entity in catch_entity:
    #     PossibleEntity = get_matches(entity, Resources)
    #     print(PossibleEntity)

#################################### CHECK AMBIGUITY ############################################


def check_ambiguity(NamedEntityList):

 # print(len(NamedEntityList))
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
        disambiguation = []
        for result in results["results"]["bindings"]:
            disambiguation = result["disambiguation"]["value"]
            # print(disambiguation)
