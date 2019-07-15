from flask import Flask, url_for, request, render_template, jsonify, send_file
from flaskblog import app
from .Processing import IdentifyRelation, IdentifyRessource, dataset


@app.route('/', methods=['GET', 'POST'])
def index():
   
    return render_template('index.html')


@app.route('/Extract', methods=['GET', 'POST'])
def Extract():
   if request.method == 'POST':
      rawtext = request.form['rawtext']  
      PropertyCandidate,PropertyMerged,possiblecandidate,NamedEntityListMainly,NamedEntityMerged,SpacyEntity, SpacyEntityLabel = IdentifyRessource.extract_entities_Manualy(rawtext)
      IdentifyRessource.exact_match_entity(NamedEntityListMainly,NamedEntityMerged,SpacyEntity)
      EAT=IdentifyRessource.get_Expected_Answer_type(rawtext)
      # IdentifyRessource.exact_match_property(PropertyCandidate, PropertyMerged,possiblecandidate,EAT)
   return render_template('index.html', rawtext=rawtext)
