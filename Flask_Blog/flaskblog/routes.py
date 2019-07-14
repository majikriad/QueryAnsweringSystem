from flask import Flask,url_for,request,render_template,jsonify,send_file
from flaskblog import app 
from .Processing import IdentifyRelation,IdentifyRessource,dataset

@app.route('/', methods=['GET','POST'])
def index():
     return render_template('index.html')
@app.route('/Extract',methods=['GET','POST'])
def Extract():
     if request.method == 'POST':
          rawtext=request.form['rawtext']
          
          ############################ RESOURCE INDENTIFICATION ###############################################  
          NamedEntityList, NamedEntityLabel, NamedEntityDescription=IdentifyRessource.extract_entities(rawtext)
          NamedEntityListMerged=[]
          if len(NamedEntityList) > 1:
               NamedEntityListMerged=IdentifyRessource.merge_entities(NamedEntityList)
          IdentifyRessource.exact_match(NamedEntityListMerged,NamedEntityList)
          
          IdentifyRessource.redirects_property(NamedEntityList)
         
          IdentifyRessource.check_ambiguity(NamedEntityList)
          
          IdentifyRessource.check_string_similarity(rawtext)
 
          ########################## RELATION IDENTIFICATION ######################################################
          QuestionEntityRemoved=IdentifyRelation.remove_NE_from_filquest(rawtext,NamedEntityList)
          Candidate=IdentifyRelation.remove_stpwords_from_query(QuestionEntityRemoved)
          #IdentifyRelation.exact_match(Candidate)
          #ExpectedAnswerType=IdentifyRelation.get_Expected_Answer_type(rawtext)
          
          #########################QUERY TEMPLATE######################################################
          
          return render_template('index.html',rawtext=rawtext)#,custom_tokens=custom_tokens)