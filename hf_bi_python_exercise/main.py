# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 21:46:47 2024

@author: subaranwal
"""

import re
import csv
import nltk
import json
import pandas as pd 
import numpy as np
from urllib.request import urlopen
from difflib import get_close_matches

def download_bi_recipes():
    url = "https://bnlf-tests.s3.eu-central-1.amazonaws.com/recipes.json"

    response = urlopen(url)
    data = response.read()
    
    my_json = data.decode('utf-8').replace("}\n{", "},\n{")
    my_json = "[" + my_json + "]"
    # print(my_json)
    
    json_object = json.loads(my_json)
    
    with open('hf_bi_python_excercise/bi_recipes.json', 'w', encoding='utf-8') as f:
        json.dump(json_object, f, ensure_ascii=False, indent=4)
        
    return json_object

def extract_chili_recipe():
    chilies_recipes = []
    pattern = "[cC]hi.*"
    for i in range(0, len(json_object)):
        recipe_ingredient = json_object[i]['ingredients']
        words = nltk.word_tokenize(recipe_ingredient)
        
        filtered_words = [x for x in words if re.match(pattern, x)]
        if not filtered_words:
            continue
        
        chilies_exist = get_close_matches('chilies', filtered_words)
        if not chilies_exist:
            continue
        # print(json_object[i]['ingredients'])
        
        chilies_recipes.append(json_object[i])
        # print("-------------")
    
    # print(chilies_recipes)
    return chilies_recipes

def insert_difficulty():
    df = pd.DataFrame.from_dict(chilies_recipes)

    for i in range(0, len(df['ingredients'])):
        df['ingredients'][i] = df['ingredients'][i].replace("\n", ' & ')
        
    df['name'] = '"' + df.name + '"'
    df['ingredients'] = '"' + df.ingredients + '"'
    df['description'] = '"' + df.description + '"'
    
    df['CT'] = df['cookTime'].map(lambda x: x.lstrip('PT'))
    df['PT'] = df['prepTime'].map(lambda x: x.lstrip('PT'))
    # print(df['CT'])
    
    for i in range(0, len(df['CT'])):
        s1 = df['CT'][i]
        if 'M' in s1 and 'H' in s1:
            df['CT'][i] = 60 * int(s1.split('H')[0]) + int(s1.split('H')[1].rstrip('M'))
        elif 'H' in s1:
            df['CT'][i] = 60 * int(s1.rstrip('H'))
        elif 'M' in s1:
            df['CT'][i] = int(s1.rstrip('M'))
        else:
            df['CT'][i] = 0
            
    # print(df['CT'])
    
    for i in range(0, len(df['PT'])):
        s1 = df['PT'][i]
        if 'M' in s1 and 'H' in s1:
            df['PT'][i] = 60 * int(s1.split('H')[0]) + int(s1.split('H')[1].rstrip('M'))
        elif 'H' in s1:
            df['PT'][i] = 60 * int(s1.rstrip('H'))
        elif 'M' in s1:
            df['PT'][i] = int(s1.rstrip('M'))
        else:
            df['PT'][i] = 0
    
    conditions = [
        (df['CT'] + df['PT'] > 60),
        (df['CT'] + df['PT'] > 30) & (df['CT'] + df['PT'] <= 60 ),
        (df['CT'] + df['PT'] > 0) & (df['CT'] + df['PT'] <= 30 ),
        (df['CT'] + df['PT'] <= 0)
        ]
    
    values = ['Hard', 'Medium', 'Easy', 'Unknown']
    
    df['difficulty'] = np.select(conditions, values)
    df['total_time'] = df['CT'] + df['PT']
    df = df.drop(['CT', 'PT'], axis=1)
    df = df.drop_duplicates()
    # df
    
    df.to_csv('hf_bi_python_excercise/Chilies.csv', sep='|', index=False, quoting=csv.QUOTE_NONE, escapechar="\\", encoding='utf-8')
    
    return df

def total_time_aggregated():
    df1 = df.groupby('difficulty', as_index=False)['total_time'].sum()
    df1 = df1.query('difficulty != "Unknown"')
    df1.to_csv('hf_bi_python_excercise/Results.csv', sep='|', index=False)
    return df1
    
if __name__ == "__main__":
    #Q1
    json_object = download_bi_recipes()
    #Q2a
    chilies_recipes = extract_chili_recipe()
    #Q2b
    df = insert_difficulty()
    #Q2c
    df1 = total_time_aggregated()