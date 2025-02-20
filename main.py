#create a basic flask app
import flask
from flask import request, jsonify, render_template
from ml_models import classifiers, regressors
from pipeline import pipeline_default
import pandas as pd
import os

def formatresult(topmodels, filenames):
    result = {}

# Iterate through each metric in topmodels
    for metric in topmodels.keys():
        if metric.endswith('score'):
            metric_name = metric.split(' ')[0]  # Extracting metric name without 'score'
            top_model = topmodels[metric_name]
            score = topmodels[metric]
        else:
            metric_name = metric
            top_model = topmodels[metric]
            score = topmodels[f"{metric_name} score"]

        # Get the filename of the graph
        for filename in filenames:
            if metric_name in filename:
                graph_filename = filename
                break
        # Create the dictionary for the current metric
        result[metric_name] = {
            "graph": graph_filename,
            "top": top_model,
            "score": score
        }
    return result


app = flask.Flask(__name__)
app.config["DEBUG"] = True

#defaults
task = 'classification'
feature_set = 'tfidf'
vectorizer = 'count'
features = ['text']
label = 'label'
model = classifiers
file = ""

# A route to return all of the available entries in our catalog.
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

#route that gets a csv file and returns a list of headers
@app.route('/headers', methods=['GET', 'POST'])
def api_headers():
    print("HEY HEYYY")
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    # fetching file from the request and saving it
    global file
    file = request.files['dataset']

    # if data folder doesn't exists
    isExist = os.path.exists("Data")
    if not isExist:
        os.makedirs("Data")

    file.save("./Data/"+file.filename)
    df = pd.read_csv("./Data/"+file.filename)

    if 'task' in request.args:
        global task
        task = request.args['task']
    else:
        task = 'sentiment-analysis'


    potential_features = list(df.columns)
    potential_labels = list(df.columns)
    # for column in list(df.columns):
        # if column == label:
        #     potential_features.remove(column)
        #     potential_labels = [column]
        # else:
        #     if task != 'regression':
        #         if df[column].dtype.name == 'category':
        #             potential_labels.append(column)
        #     else:
        #         if df[column].dtype.name == 'float64':
        #             potential_labels.append(column)
    return render_template('index.html', task=task, features=potential_features, label=potential_labels)

# route that gets all the arguments and returns evaluation metrics with graph
@app.route('/models', methods=['GET', 'POST'])
def api_evaluate():
    print("MODELS")
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    global file

    file = request.files['dataset']

    # if data folder doesn't exists
    isExist = os.path.exists("Data")
    if not isExist:
        os.makedirs("Data")

    file.save("./Data/" + file.filename)
    df = pd.read_csv("./Data/" + file.filename)


    if 'task' in request.form:
        task = request.form['task']

    if 'feature_set' in request.args:
        global feature_set
        feature_set = request.args['feature_set']
    else:
        feature_set = 'tfidf'

    if 'vectorizer' in request.args:
        global vectorizer
        vectorizer = request.args['vectorizer']
    else:
        vectorizer = 'count'

    if 'features' in request.args:
        global features
        features = request.args['features']
    else:
        features = list(df.columns)[:-1]

    if 'label' in request.args:
        global label
        label = request.args['label']
    else:
        label = df.columns[-1]

    if 'model' in request.args:
        global model
        model = request.args['model']
    else:
        if task == 'regression':
            model = regressors
        else:
            model = classifiers

    #load data
    # df = pd.read_csv(file)
    #pipeline: clean data, extract features, train model, evaluate model
    #get evaluation metrics
    top_models, filenames = pipeline_default(df, task, feature_set, vectorizer, features, label, model)
    # results =  {metric: {graph: filename, top_model: modelname, top_model_score: score}}
    print("LALALALALALALALALALALA\\\\\\\\\\\\\\\\\\\\\\\\\\\///////////////////////")
    print(top_models)
    print(filenames)
    results = formatresult(top_models, filenames)
    print(results)
    return render_template('index.html', result = results)
    # return jsonify(top_models, filenames)

if __name__ == '__main__':
    app.run()