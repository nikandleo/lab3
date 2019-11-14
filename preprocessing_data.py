import re
import pandas as pd
from datetime import datetime

df = pd.read_csv('vacancies_one_new.csv')
df.drop(df.columns[0], axis=1, inplace=True)
min_days = df.days.min()
max_days = df.days.max()
df['days'] = (df['days'] - min_days) / (max_days - min_days)
max_min = df['max_salary'].min()
max_max = df['max_salary'].max()
min_min = df['min_salary'].min()
min_max = df['min_salary'].max()

min_arr = []
max_arr = []
for i in range(10):
    min_arr.append(min_min + i * ((min_max - min_min) / 9))
    max_arr.append(max_min + i * ((max_max - max_min) / 9))
min_bins = pd.cut(df.min_salary, min_arr, right=True)
min_cols = pd.crosstab(df.index, min_bins, dropna=False)
df = df.join(min_cols)
max_bins = pd.cut(df.max_salary, max_arr, right=True)
max_cols = pd.crosstab(df.index, max_bins, dropna=False)
df = df.join(max_cols)
df = pd.concat([df, pd.get_dummies(df['area'])], axis=1)
df = pd.concat([df, pd.get_dummies(df['experience'])], axis=1)
df = pd.concat([df, pd.get_dummies(df['schedule'])], axis=1)
df = pd.concat([df, pd.get_dummies(df['employment'])], axis=1)
df.drop(df[df.name == 'Разработчик'].index, inplace=True)
df.drop(df[df.name == 'Аналитик'].index, inplace=True)
df.drop(df[df.name == '1С'].index, inplace=True)
pd.DataFrame(df).to_csv('vacancies_one_new2.csv')
