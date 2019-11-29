import plotly.graph_objects as go
import plotly.express as exp
import pandas as pd
from wordcloud import WordCloud
import plotly.express as px
import collections
from numpy import percentile
from sklearn import svm
import matplotlib.pyplot as plt


def draw_word_cloud(text):
    wc = WordCloud(background_color='white', width=1000, height=800)
    wc.generate_from_frequencies(text)
    plt.imshow(wc)
    plt.axis('off')
    plt.show()


def get_all_skills(dtf):
    all_skills = dtf.key_skills.apply(lambda x: [val.lower() for val in x.split("|")])
    freq = collections.Counter()
    for row in all_skills:
        for item in row:
            freq[item] += 1
    return freq


def draw_and_find_outliers(dtf):
    fig = px.box(dtf, y="max_salary", notched=True)
    fig.show()
    fig = px.box(dtf, y="min_salary", notched=True)
    fig.show()
    clf = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
    clf.fit(dtf)
    y_pred_train = clf.predict(dtf)
    return [i for i, elem in enumerate(y_pred_train.tolist()) if elem == -1]


def replace_outliers(dtf, field):
    data = dtf[field]
    perc_25 = percentile(data, 25)
    perc_75 = percentile(data, 75)
    cut_off = (perc_75 - perc_25) * 1.5
    low_bound = perc_25 - cut_off
    high_bound = perc_75 + cut_off
    outliers = [x for x in data if x < low_bound or x > high_bound]
    dtf[field] = dtf[field].apply(lambda x: (low_bound if low_bound > x else high_bound) if x in outliers else x)
    return dtf


def part_1(data):
    fig = go.Figure(data=go.Heatmap(
        z=data.values,
        x=data.keys(),
        y=data.keys()))
    fig.show()
    dat = data.unstack()
    attr = dat.sort_values(ascending=False).to_frame()
    attr.reset_index(inplace=True)
    attr.columns = ['first_attribute', 'second_attribute', 'correlation']
    attr = attr.loc[attr.first_attribute != attr.second_attribute][0:10:2]
    attr = attr.sort_values(by='first_attribute')
    fig = exp.line(attr, x='first_attribute', y='correlation', text='second_attribute')
    fig.show()
    fig = exp.histogram(attr, x='first_attribute', y='correlation', histfunc='max')
    fig.show()
    fig = exp.scatter_matrix(attr, color='second_attribute')
    fig.show()
    draw_word_cloud(skills)


def part_2(data):
    outliers = draw_and_find_outliers(data)
    df_field = replace_outliers(data, 'max_salary')
    df_field = replace_outliers(df_field, 'min_salary')
    outliers2 = draw_and_find_outliers(df_field)
    rem_obj = [val1 for val1, val2 in zip(outliers, outliers2) if val1 == val2]
    data.drop(data.index[[rem_obj]]).to_csv('best_data.csv')


df = pd.read_csv('vacancies_one_new2.csv').drop(['Unnamed: 0'], axis=1)
skills = get_all_skills(df)
df = df.drop(
    ['duties', 'conditions', 'requirements', 'description', 'name', 'area', 'min_salary', 'max_salary',
     'employer', 'published_at', 'experience', 'employment', 'schedule', 'key_skills', 'days',
     ], axis=1)
correlation = df.corr().abs()
part_1(correlation)

df = pd.read_csv('vacancies_one_new2.csv').drop(['Unnamed: 0'], axis=1)[['min_salary', 'max_salary']].dropna(axis=0)
part_2(df)
