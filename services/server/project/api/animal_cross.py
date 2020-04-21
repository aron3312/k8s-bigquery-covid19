import os
import pandas as pd
import json
from flask import Blueprint, jsonify, render_template,send_file
import numpy as np

animal_cross_blueprint = Blueprint('animal_cross', __name__)
@animal_cross_blueprint.route('/animal-cs', methods=['GET'])
def index():
    return "yo"

if __name__ == '__main__':
    app.run()
