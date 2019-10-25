import re
import pandas as pd
import requests


def clear_text(val):
    val = re.sub(r'<.*?>', ' ', val)
    val = re.sub(r'\s+', ' ', val)
    val = val.strip()
    return val


def clear_columns(element):
    result = dict()
    result2 = dict()
    name_values = ['area', 'employer', 'experience', 'schedule', 'employment']  # колонки с полем name
    for key, value in element.items():
        if key in name_values:
            element[key] = value['name']
        elif key == 'salary':
            if value is not None:
                if value['currency'] == 'USD':
                    result['min_salary'] = value['from'] * 65 if value['from'] else value['from']
                    result['max_salary'] = value['to'] * 65 if value['to'] else value['to']
                elif value['currency'] == 'EUR':
                    result['min_salary'] = value['from'] * 70 if value['from'] else value['from']
                    result['max_salary'] = value['to'] * 70 if value['to'] else value['to']
                else:
                    result['min_salary'] = value['from']
                    result['max_salary'] = value['to']
            else:
                result['min_salary'] = None
                result['max_salary'] = None
        elif key == 'description':
            element[key] = clear_text(value)
            value = element[key]
            search_duty = re.search(r'Обязанности:(.*)Требования:', value)
            search_requirements = re.search(r'Требования:(.*)Условия:', value)
            search_condition = re.search(r'Условия:(.*)', value)
            result2['requirements'] = search_requirements.group(1) if search_requirements else None
            result2['duties'] = search_duty.group(1) if search_duty else None
            result2['conditions'] = search_condition.group(1) if search_condition else None
        elif key == 'key_skills':
            str = ''
            for item in value:
                str += item['name'] + '|'
            element[key] = str[:-1]
            element[key] = clear_text(element[key])
    element.pop('salary')
    element.update(result)
    element.update(result2)
    return element


x = []
all_zp = 0
all_n = 0
city_ids = ['4', '53', '104', '3', '78']
for j in range(5):
    for i in range(5):  # 5*50=250 вакансий (по 5 городов)
        url = 'https://api.hh.ru/vacancies'
        par = {'specialization': '1.221', 'area': city_ids[j], 'per_page': '50', 'page': i}  # Новосибирская область
        r = requests.get(url, params=par)
        e = r.json()
        x.append(e)
vacancies = []
needed = ['name', 'area', 'min_salary', 'max_salary', 'employer', 'published_at', 'experience', 'schedule',
          'employment', 'description', 'requirements', 'duties', 'conditions', 'key_skills']
for j in x:
    y = j['items']
    for i in y:
        s = i['salary']
        r = requests.get('https://api.hh.ru/vacancies/' + i['id'])
        elem = r.json()
        vacancies.append(clear_columns(elem))

df = pd.DataFrame(vacancies)

df1 = df[needed]  # беру только нужные колонки
pd.DataFrame(df1).to_csv('vacancies.csv')
