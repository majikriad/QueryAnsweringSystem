from flask import Flask, url_for, request, render_template, jsonify, send_file
from flaskblog import app
from .Processing import IdentifyRelation, IdentifyRessource, dataset
import spotlight

@app.route('/', methods=['GET', 'POST'])
def index():
   
    return render_template('index.html')


@app.route('/Extract', methods=['GET', 'POST'])
def Extract():
   if request.method == 'POST':
      rawtext = request.form['rawtext']
      
      SpacyEntity,SpacyEntityLabel,SpacyPropertyMerged=IdentifyRessource.extract_entities_Spacy(rawtext)  
      PropertyCandidate,PropertyMerged,possiblecandidate,NamedEntityListMainly,NamedEntityMerged = IdentifyRessource.extract_entities_Manualy(rawtext)
      # IdentifyRessource.exact_match_entity(NamedEntityListMainly,NamedEntityMerged,SpacyEntity)
      EAT=IdentifyRessource.get_Expected_Answer_type(rawtext)
      IdentifyRessource.exact_match_property(PropertyCandidate, PropertyMerged,possiblecandidate,EAT,SpacyEntity)
       
   return render_template('index.html', rawtext=rawtext)

