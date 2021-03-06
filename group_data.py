import re
import pandas as pd
from datetime import datetime

groups = [r'(\.net|c#)', r'android', r'(front|фронтэнд)', r'(back|php)', r'c\+\+|с\+\+', r'(database|data '
                                                                                         r'base|oracle|postgres)',
          r'(data|machine)', r'devops', r'(full stack|fullstack)', r'(game|unity|гейм)', r'ios',
          r'(javascript|angular|js|react)', r'java', r'(qa|engineer|тестировщик|тестирования)', r'python',
          r'(1с|1 с|1c|1 c)', 'golang|go ', r'системный администратор', r'(менеджер|manager)', r'(web|веб)',
          r'(программист|разработчик|developer)', r'аналитик', 'тех.*поддержк.*', r'.*']
new_names = ['.NET', 'Android', 'Frontend', 'Backend', 'C++', 'Database engineer', 'Big data', 'Devops', 'Fullstack',
             'Game designer', 'IOS', 'Javascript', 'Java', 'QA Testing', 'Python', '1С', 'Go',
             'Системный администратор', 'Менеджер', 'Веб-разработчик', 'Разработчик', 'Аналитик', 'Тех. поддержка',
             'Остальное']
df = pd.read_csv('vacancies_one.csv')
df.drop(df.columns[0], axis=1, inplace=True)
df.name = df.name.apply(lambda x: re.sub(r'[\s/|\\"*:\-]+', ' ', x.lower().strip()))
df['days'] = (datetime.now() - pd.to_datetime(
    pd.to_datetime(df['published_at']).apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S')))).dt.days
df['key_skills'] = df['key_skills'].fillna('Без ключевых навыков')
df['requirements'] = df['requirements'].fillna('Без требований')
df['duties'] = df['duties'].fillna('Без обязанностей')
df['conditions'] = df['conditions'].fillna('Без условий')
min_avg = df.groupby(['area']).min_salary.mean()
max_avg = df.groupby(['area']).max_salary.mean()
print(min_avg)
print(max_avg)
for index, row in df.iterrows():
    for idx, reg in enumerate(groups):
        if re.search(reg, row['name'].lower()) is not None:
            df.loc[index, 'name'] = new_names[idx]
            break
grouped = df.groupby(['name', 'area']).mean()
for index, row in df.iterrows():
    if row['min_salary'] != row['min_salary']:
        avg_m = grouped['min_salary'][row['name']][row['area']]
        if avg_m == avg_m:
            df.loc[index, 'min_salary'] = avg_m
        else:
            df.loc[index, 'min_salary'] = min_avg[row['area']]
    if row['max_salary'] != row['max_salary']:
        avg_m = grouped['max_salary'][row['name']][row['area']]
        if avg_m == avg_m:
            df.loc[index, 'max_salary'] = avg_m
        else:
            df.loc[index, 'max_salary'] = max_avg[row['area']]
pd.DataFrame(df).to_csv('vacancies_one_new.csv')
