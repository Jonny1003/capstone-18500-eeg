from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import pandas
import joblib
import matplotlib.pyplot as plt

# classifies artifacts against baseline features using only AF3 max and AF4 max


loc = "/Users/jonathanke/Documents/CMU/18500/data/featurized/sandbox/artifact_baseline_max.csv"

data = pandas.read_csv(loc)
data = data.sample(frac=1)
split = int(0.7 * data.shape[0])
print("Number of training samples:", split)
print("Total samples:", data.shape[0])
print("Number of test samples:", data.shape[0] - split)

training = data.head(split)
xTraining = training.iloc[:, 1:3]
yTraining = training["label"]

test = data.tail(data.shape[0] - split)
xTest = test.iloc[:, 1:3]
yTest = test['label']

print(xTraining)
print(xTest)

model = RandomForestClassifier(criterion="entropy", max_depth=2)
model.fit(xTraining, yTraining)

joblib.dump(model, "rf_model_artifact_baseline.joblib")

print("RF Predictions:")
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

model2 = LogisticRegression(solver='liblinear', max_iter=50, verbose=1)
model2.fit(xTraining, yTraining)
print("LR Predictions:")
pred2 = model2.predict(xTest)
print(pred2)
print("Actual:")
print(act)
ct = 0
for i,v in enumerate(pred2):
    if act[i] != v:
        ct += 1
print("Error:", ct / len(yTest))

# fig, ax = plt.subplots()
# colors = ['b' if v == 'artifact' else 'r' for v in data['label']]
# ax.scatter(data['AF3_max'], data['AF4_max'], c=colors)
# plt.show()





