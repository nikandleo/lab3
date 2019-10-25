import re
import pandas as pd
import os
import math
from datetime import datetime


def shrinkAndSortList(lst):
    tup_list = []
    ind, index = 0, 0
    while index < len(lst):
        element_count = 0
        while ind < len(lst) and lst[ind] == lst[index]:
            element_count += 1
            ind += 1
        tup_list.append((lst[index], element_count))
        index += element_count

    lst = len(tup_list)
    for j in range(0, lst):
        for z in range(0, lst - j - 1):
            if tup_list[z][1] < tup_list[z + 1][1]:
                temp = tup_list[z]
                tup_list[z] = tup_list[z + 1]
                tup_list[z + 1] = temp
    return tup_list


def count_days(data):
    a = pd.to_datetime(data.published_at).apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
    days = [date.days for date in datetime.now() - pd.to_datetime(a)]
    return pd.DataFrame(data=[sum(days) / len(days), max(days), min(days)],
                        index=['avg', 'max', 'min'])


def count_skills(group, ):
    skills = dict()
    for skill in group.key_skills.values:
        if skill == skill:
            skills_list = skill.split('|')
            for val in skills_list:
                val = val.strip()
                if val not in skills:
                    skills[val] = 0
                skills[val] += 1
    keys, values = [], []
    for key, value in skills.items():
        keys.append(key)
        values.append(value)
    return pd.DataFrame(data=values, index=keys)


def write(record, item_folder):
    data, keys = [], []
    for key, value in record.items():
        data.append(value)
        keys.append(key)
    pd.concat(data, keys=keys).to_csv(item_folder, sep='\t', header=None)


def calculate(record, data, item, path_to_result):
    left_border = item['from_value']
    right_border = item['to_value']
    record['days'] = count_days(data)
    record['experience'] = data.experience.value_counts()
    record['employment'] = data.employment.value_counts()
    record['schedule'] = data.schedule.value_counts()
    record['skills'] = count_skills(data)
    path = os.path.join(path_to_result, (str(left_border) + " " + str(right_border)).strip())
    os.mkdir(path)
    write(record, os.path.join(path, "task.csv"))
    data.to_csv(os.path.join(path, "vacancies.csv"))


def split_data(dtf, left_border='', right_border=''):
    min_sal = math.ceil(left_border) if isinstance(left_border, float) else left_border
    max_sal = math.ceil(right_border) if isinstance(right_border, float) else right_border
    return {'data': dtf, 'from_value': min_sal, 'to_value': max_sal}


def dummy_skills(dtf, item, path_to_result):
    left_border = item['from_value']
    right_border = item['to_value']
    path = os.path.join(path_to_result, (str(left_border) + " " + str(right_border)).strip())
    os.mkdir(path)
    arr_skills = dtf['key_skills'].str.cat(sep='|').split('|')
    top10skills = shrinkAndSortList(arr_skills)[:10]
    topskills = [x[0] for x in top10skills]
    dtf['new_skills'] = dtf.key_skills.apply(lambda x: x.split("|"))
    for skill in topskills:
        dtf[skill] = dtf.new_skills.apply(lambda x: int(skill in x))
    dtf.drop(['new_skills'], axis=1, inplace=True)
    dtf['Другое'] = dtf.apply(lambda row: int(sum(list(row.loc[topskills])) == 0), axis=1)
    dtf.to_csv(os.path.join(path, "vacancies.csv"))


def task1(dfs, path_to_result):
    for item in dfs:
        data = item['data']
        if len(data) != 0:
            record = dict()
            record['vacancies_name'] = data.name.value_counts()
            calculate(record, data, item, path_to_result)


def task2(origin_data, salary_separated, path_to_result):
    vacancies = set(origin_data.name)
    separate_vacancies = []
    for name in vacancies:
        separate_vacancies.append(split_data(origin_data.loc[(origin_data.name == name)], name))
    for item in separate_vacancies:
        data = item['data']
        if len(data) != 0:
            record = dict()
            border_salary = dict()
            for salary in salary_separated:
                key = str(salary["from_value"]) + " - " + str(salary["to_value"])
                cnt = len(salary['data'][salary['data'].name == item['from_value']])
                if cnt != 0:
                    border_salary[key] = cnt
            record['salaries'] = pd.Series(border_salary)
            dummy_skills(data, item, path_to_result)
            # calculate(record, data, item, path_to_result)


df = pd.read_csv('vacancies_new2.csv')  # vacancies.csv for result/2
df.name = df.name.apply(lambda x: re.sub(r'[\s/|\\"*:\-]+', ' ', x.lower().strip()))
df = df.sort_values(by=['max_salary'])
df = df.sort_values(by=['min_salary'])
# separate data
to_value = df['max_salary'].max()
from_value = df['max_salary'].min()
step = (to_value - from_value) / 9
df_list = []
lower_value = 0
undefined_group = split_data(df[df['max_salary'].isnull()], 'NAN', 'NAN')
for i in range(0, 9):
    upper_value = from_value + step * i
    select = df.loc[(df['max_salary'] < upper_value) & (df['max_salary'] >= lower_value)]
    df_list.append(split_data(select, lower_value, upper_value))
    lower_value = upper_value
df_list.append(split_data(df.loc[(df['max_salary'] >= lower_value)], left_border=lower_value))
df_list.append(undefined_group)

# task1(df_list, 'result/1')
# task2(df, df_list, 'result/2')
# task2(df, df_list, 'result/3')
task2(df, df_list, 'result/4')
