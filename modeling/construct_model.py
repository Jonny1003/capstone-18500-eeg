from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
import pandas
import joblib
import matplotlib.pyplot as plt

import sys
import json
import os 

from featurize import *
from constants import *

MODEL_SPEC_PARAMS = [
    'model', 'rf_max_depth', 'lr_max_iter', 'lr_solver', 
    'proportion_training', 'features', 'data_sources', 
    'label_mapping']

def feature_data_path(model_spec):
    return f"../data/featurized/{model_spec.get('name')}.csv"


def create_feature_set(model_spec):
    features = model_spec.get('features')
    datasets = model_spec.get('data_sources')
    data = []
    for artifact in datasets:
        src = getPathToCompiledDataSet(artifact)
        label = artifact
        if artifact in model_spec['label_mapping']:
            label = model_spec['label_mapping'][artifact]
        more_data = computeFeatures(src, features, label)
        data.append(more_data)
    featureTable = pandas.concat(data)
    featureTable.to_csv(feature_data_path(model_spec))

def train_model(model_spec):
    if DEBUG:
        print("Building Logistic Regression Model...\n")
    
    data = pandas.read_csv(feature_data_path(model_spec))

    # randomize data before training
    data = data.sample(frac=1)
    split = int(model_spec.get('proportion_training') * data.shape[0])
    if DEBUG:
        print("Number of training samples:", split)
        print("Total samples:", data.shape[0])
        print("Number of test samples:", data.shape[0] - split)

    training = data.head(split)
    xTraining = training.iloc[:, 1:-1]
    yTraining = training["label"]

    test = data.tail(data.shape[0] - split)
    xTest = test.iloc[:, 1:-1]
    yTest = test['label']

    if DEBUG:
        print("Traning data:")
        print(xTraining)
        print("Testing data:")
        print(xTest)

    if model_spec['model'] == 'lr':
        # reweight logistic regression model 
        # due to imbalance of data
        # total_samples = data.shape[0]
        # labels = data['label'].unique()
        # weights = dict()
        # for label in labels:
        #     weights[label] = total_samples / data[data['label'] == label].count()
        # print(weights)

        model = LogisticRegression(
            solver=model_spec.get('lr_solver'), 
            max_iter=model_spec.get('lr_max_iter'),
            verbose=1, 
            class_weight='balanced')
    elif model_spec['model'] == 'rf':
        model = RandomForestClassifier(
            criterion="entropy", 
            max_depth=model_spec.get('rf_max_depth'))

    model.fit(xTraining, yTraining)

    print("LR Predictions:")
    pred = model.predict(xTest)
    print(pred)
    print("Actual:")
    act = list(yTest)
    print(act)
    ct = 0
    for i,v in enumerate(pred):
        if act[i] != v:
            ct += 1
    print("Error:", ct / len(yTest))

    # create output files
    output_path = os.path.join(os.getcwd(), f"{model_spec.get('name')}_output")
    if model_spec.get('name') + "_output" not in os.listdir(os.getcwd()):
        os.mkdir(output_path)
    else:
        for f in os.listdir(output_path):
            os.remove(os.path.join(output_path, f))
            

    joblib.dump(model, f"{model_spec.get('name')}.joblib")

    # Create a quick error report
    with open(os.path.join(output_path, 'report.log'), 'w') as log:
        log.write(f'Prediction Error: {ct / len(yTest)}\n')
        label_types = data['label'].unique()
        log.write(f'Label distribution:\n')
        for label in label_types:
            num_occurences = data[data['label'] == label]['label'].count()
            log.write(f'\t{label}: {num_occurences}\n')
        if model_spec['model'] == 'lr':
            roc_auc = roc_auc_score(yTest, model.decision_function(xTest))
            log.write(f'ROC AUC Score: {roc_auc}\n')
    
    # Create graphs of data 
    colorChoices = ['b', 'g', 'r', 'c', 'm', 'y']
    ind = 0
    colorMap = dict()
    for v in data['label']:
        if v not in colorMap:
            colorMap[v] = colorChoices[ind]
            ind += 1

    for i, featureX in enumerate(model_spec.get('features')):
        for featureY in model_spec.get('features')[i+1:]:
            _, ax = plt.subplots()
            for v in colorMap.keys():
                featureData = data[data['label'] == v]
                ax.scatter(featureData[featureX], featureData[featureY], c=colorMap[v], label=v)
            ax.legend()
            plt.xlabel(featureX)
            plt.ylabel(featureY)
            plt.savefig(os.path.join(output_path, f"{featureX}_{featureY}.png"))
            plt.close()


if __name__ == '__main__':
    # take command line arg to construct model
    model_json = sys.argv[1]
    if len(sys.argv) >= 3 and sys.argv[2] == 'false':
        compute_features = False 
    else:
        compute_features = True

    if not model_json.endswith('.json'):
        print("ERROR: Please provide a valid .json file!")
        sys.exit(-1)
    
    with open(model_json) as model_file:
        model_spec = json.load(model_file) 
        for spec in MODEL_SPEC_PARAMS:
            if spec not in model_spec:
                print(f"ERROR: {spec} is not found in the model JSON spec! Please add it!")
                sys.exit(-1)

        model_spec['name'] = model_json.rstrip('.json')
        
        if DEBUG:
            print("Model spec:", model_spec)

        if compute_features:
            create_feature_set(model_spec)

        if model_spec['model'] not in ['lr', 'rf']:
            print("ERROR: Invalid model specification...")
            sys.exit(-1)

        train_model(model_spec)


        




    
