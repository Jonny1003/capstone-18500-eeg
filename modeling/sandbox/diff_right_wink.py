from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import pandas
import joblib
import matplotlib.pyplot as plt

# classifies out right winks from blinks, left winks, and right winks


loc = "/Users/jonathanke/Documents/CMU/18500/data/featurized/sandbox/blink_winks.csv"

data = pandas.read_csv(loc)
data = data.sample(frac=1)
original_data = data
data = data.replace(
    to_replace={
        'blink': 'none', 
        'left_wink': 'none', 
    })
data = data.drop(labels=['AF_max_time_diff', 
    'AF_max_diff', 'AF_ratio'], axis='columns')

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

model = RandomForestClassifier(criterion="entropy", max_depth=2)
model.fit(xTraining, yTraining)

joblib.dump(model, "rf_model_right_wink.joblib")

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

joblib.dump(model2, "lr_model_right_wink.joblib")

fig, ax = plt.subplots()
colors = ['b' if v == 'blink' else 'r' if v == 'right_wink' else 'g' for v in original_data['label']]
ax.scatter(original_data['AF_adj_max_diff'], original_data['AF_adj_max_ratio'], c=colors)
plt.show()





