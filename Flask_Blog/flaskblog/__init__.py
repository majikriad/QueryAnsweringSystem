from flask import Flask,url_for,request,render_template,jsonify,send_file
import spacy
import os
# Initialisation de SpaCy et de Flask 

app= Flask(__name__)

from flaskblog import routes
from flaskblog.Processing import IdentifyRelation,IdentifyRessource,dataset,QueryTemplate