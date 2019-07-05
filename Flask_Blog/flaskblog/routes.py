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
          IdentifyRessource.extract_entities(rawtext)
          return render_template('index.html',rawtext=rawtext)#,custom_tokens=custom_tokens)
     