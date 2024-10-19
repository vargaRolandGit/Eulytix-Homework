import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

df_votes = pd.read_csv("dataset.csv")

# create features (feature vector) based on party affiliation and voting records
df_votes['is_democrat'] = df_votes['party_affiliation'].apply(lambda x: 1 if x == 'D' else 0)
df_votes['is_republican'] = df_votes['party_affiliation'].apply(lambda x: 1 if x == 'R' else 0)
df_votes['voted_yea'] = df_votes['vote_record'].apply(lambda x: 1 if x == 'Yea' else 0)

grouped_votes = df_votes.groupby(['measure_number', 'result']).agg({
    'is_democrat': 'sum',
    'is_republican': 'sum',
    'voted_yea': 'sum'
}).reset_index()

# label Encoding for the target variable
grouped_votes['vote_passed'] = grouped_votes['result'].apply(lambda x: 1 if 'passed' in x.lower() else 0)

# define features (X) and target variable (y)
X = grouped_votes[['is_democrat', 'is_republican', 'voted_yea']]
y = grouped_votes['vote_passed']

# split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)

clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
print(f"Classification Report:\n {classification_report(y_test, y_pred)}")
