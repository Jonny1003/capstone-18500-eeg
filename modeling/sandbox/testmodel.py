from random import Random
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import pandas


loc = "/Users/jonathanke/Documents/CMU/18500/data/featurized/sandbox/alot_of_features.csv"

data = pandas.read_csv(loc)
data = data.sample(frac=1)
split = int(0.7 * data.shape[0])
print("Number of training samples:", split)
print("Total samples:", data.shape[0])
print("Number of test samples:", data.shape[0] - split)

training = data.head(split)
xTraining = training.iloc[:, 1:-1]
yTraining = training["label"]

test = data.tail(data.shape[0] - split)
xTest = test.iloc[:, 1:-1]
yTest = test['label']

print(xTraining)
print(xTest)

model = RandomForestClassifier(criterion="entropy", max_depth=5)
model.fit(xTraining, yTraining)
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


