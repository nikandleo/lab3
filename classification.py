import pandas as pd
from sklearn import preprocessing, metrics
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.utils import shuffle
from process_data import shrinkAndSortList


def label_encode(dframe, le=None):
    if le is None:
        le = preprocessing.LabelEncoder()
        le.fit(dframe.name)
    labels = le.transform(dframe.name)

    return labels, le


df = pd.read_csv('vacancies_one_new2.csv').drop(['Unnamed: 0'], axis=1)
df1 = df.loc[df['Самара'] != 1]
class_labels, labenc = label_encode(df1)
pd.DataFrame({'group_name': df1.name, 'class_label': class_labels}) \
    .drop_duplicates() \
    .sort_values(['class_label']) \
    .to_csv('names.csv', index=False)
df = df.drop(['area', 'min_salary', 'max_salary', 'published_at', 'experience', 'schedule', 'employment',
              'description', 'employer', 'requirements', 'duties', 'conditions'], axis=1)

arr_skills = df1['key_skills'].str.cat(sep='|').split('|')
arr_skills.sort()
top10skills = shrinkAndSortList(arr_skills)[:150]
topskills = [x[0] for x in top10skills]
df['new_skills'] = df.key_skills.apply(lambda x: x.split("|"))
for skill in topskills:
    df[skill] = df.new_skills.apply(lambda x: int(skill in x))
df.drop(['new_skills'], axis=1, inplace=True)
df['Другое'] = df.apply(lambda row: int(sum(list(row.loc[topskills])) == 0), axis=1)
del df['key_skills']

df1 = df.loc[df['Самара'] != 1]
df2 = df.loc[df['Самара'] == 1]
X = df1.iloc[:, df.columns != 'name'].values
test_labels, temp = label_encode(df2, labenc)
y = class_labels
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30)
X_train = X
X_test = df2.iloc[:, df.columns != 'name'].values
y_train = y
y_test = test_labels
SVC_model = SVC()
KNN_model = KNeighborsClassifier(n_neighbors=7)
LogisticRegression_model = LogisticRegression()
SVC_model.fit(X_train, y_train)
KNN_model.fit(X_train, y_train)
LogisticRegression_model.fit(X_train, y_train)
SVC_prediction = SVC_model.predict(X_test)
KNN_prediction = KNN_model.predict(X_test)
LogisticRegression_prediction = LogisticRegression_model.predict(X_test)
print('SVC')
print(accuracy_score(SVC_prediction, y_test))
cv_results = cross_validate(SVC_model, X_train, y_train, cv=3)
print(sorted(cv_results.keys()))
print(cv_results['test_score'])

print('KNN')
print(accuracy_score(KNN_prediction, y_test))
cv_results1 = cross_validate(KNN_model, X_train, y_train, cv=3)
print(sorted(cv_results1.keys()))
print(cv_results1['test_score'])

print('LogisticRegression')
print(accuracy_score(LogisticRegression_prediction, y_test))
cv_results2 = cross_validate(LogisticRegression_model, X_train, y_train, cv=3)
print(sorted(cv_results2.keys()))
print(cv_results2['test_score'])

pd.DataFrame({'Предсказанная моделью группа': labenc.inverse_transform(y_test),
              'Определенная по алгоритму группа': labenc.inverse_transform(LogisticRegression_prediction)}) \
    .to_csv('result.csv')
