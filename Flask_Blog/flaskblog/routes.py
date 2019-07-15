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

        ############################ RESOURCE INDENTIFICATION ###############################################
        IdentifyRessource.extract_entities_Manualy(rawtext)
     #    IdentifyRessource.extract_entities_automatic(rawtext)
     #    IdentifyRessource.check_string_similarity(rawtext)
        ###############

        # ,custom_tokens=custom_tokens)
        return render_template('index.html', rawtext=rawtext)
