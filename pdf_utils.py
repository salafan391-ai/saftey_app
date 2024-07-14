from utils import load_data
import pandas as pd
from deep_translator import GoogleTranslator
import requests
from tkinter import messagebox


def split_lines_process(conditions, end_index):
    splitted = []
    for line in conditions:
        while len(line) > end_index:
            # Find the next space after the specified end_index
            space_index = line.find(' ', end_index)
            if space_index == -1:
                # No space found, split at end_index
                splitted.append(line[:end_index])
                line = line[end_index:]
            else:
                # Split at the found space
                splitted.append(line[:space_index].strip())
                line = line[space_index:].strip()
        splitted.append(line)
    return splitted


def is_connected():
    try:
        # Attempt to connect to Google's homepage
        response = requests.get('http://www.google.com', timeout=5)
        # If the request is successful, return True
        return True
    except (requests.ConnectionError, requests.Timeout):
        # If there is a connection error or a timeout, return False
        return False


def translate_conditions():
    splitted_df = split_lines_process(
        load_data.conditions[0].condition_value, 75)
    translator = GoogleTranslator(source='auto', target='en')
    repair_df = pd.DataFrame(
        splitted_df, columns=['صيانة'])
    repair_df['الترجمة'] = repair_df['صيانة'].apply(translator.translate)
    repair_df.to_csv('repair_conditions.csv')
