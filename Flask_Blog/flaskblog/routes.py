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
          IdentifyRelation.get_typed_quest(rawtext)  
          NamedEntityList, NamedEntityLabel, NamedEntityDescription=IdentifyRessource.extract_entities(rawtext)
          NamedEntityListMerged=[]
          if len(NamedEntityList) > 2:
               NamedEntityListMerged=IdentifyRessource.merge_entities(NamedEntityList)
          IdentifyRessource.exact_match(NamedEntityListMerged,NamedEntityList)
          IdentifyRessource.redirect(NamedEntityList)
          IdentifyRessource.check_string_similarity(rawtext)
          return render_template('index.html',rawtext=rawtext)#,custom_tokens=custom_tokens)