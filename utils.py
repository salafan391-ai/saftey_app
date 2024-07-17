from datetime import datetime, timedelta
from schema import Company, Data, Documents, Accounts
from typing import List, Optional
import json
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk

NOW = datetime.now()


YEAR_AFTER = timedelta(356.24)+NOW.date()


def check_age(birthdate: datetime):
    if (round((NOW.date()-birthdate).days/365.25)) < 19:
        messagebox.showerror(
            'خطأ', 'يجب أن يكون سن الموظف 19 سنة فأكبر')


def get_date(entry):
    return datetime.strptime(entry.entry.get(), '%m/%d/%Y').date()


def load_json_data(file_path: str) -> 'Data':
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return Data(**data)
    except FileNotFoundError:
        return Data(company_info=Company(), conditions=None)


data_file_path = 'data.json'
load_data = load_json_data(data_file_path)


def save_json_data(data: 'Data', file_path: str):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data.dict(), file, ensure_ascii=False, indent=4)


def add_account(data: 'Data', bank_name: str, iban: str, account_fullname: str, account_number: str):
    account = Accounts(
        bank_name=bank_name,
        account_iban=iban,
        account_fullname=account_fullname,
        account_number=account_number
    )
    if not data.company_info.accounts:
        data.company_info.accounts = []
    data.company_info.accounts.append(account)
    save_json_data(data, data_file_path)


def add_document(data: 'Data', name: str, path: str):
    document = Documents(name=name, path=path)
    if not data.company_info.documents:
        data.company_info.documents = []
    data.company_info.documents.append(document)
    save_json_data(data, data_file_path)


def update_company_info(data: 'Data', name: Optional[str] = None, phone: Optional[str] = None, tax_number: Optional[str] = None, logo: Optional[str] = None, permit_number: Optional[str] = None):
    if name:
        data.company_info.name = name
    if phone:
        data.company_info.phone = phone
    if tax_number:
        data.company_info.tax_number = tax_number
    if logo:
        data.company_info.logo = logo
    if permit_number:
        data.company_info.permit_number = permit_number
    save_json_data(data, data_file_path)


def delete_condition(id: int, condition_type: List[dict]):
    condition_type.pop(id)
    save_json_data(load_data, data_file_path)


def delete_account(id: int, accounts: List[dict]):
    accounts.pop(id)
    save_json_data(load_data, data_file_path)


def add_condition(condition_type: List[dict], new_condition: dict, condition_number: int):
    condition_type.insert(condition_number, new_condition)
    save_json_data(load_data, data_file_path)


def update_conditions(id: int, condition_type: List[dict], updated_condition: dict):
    condition_type[id] = updated_condition
    save_json_data(load_data, data_file_path)


class PlaceholderEntry(ttk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['foreground']

        self.bind("<FocusIn>", self.focus_in)
        self.bind("<FocusOut>", self.focus_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['foreground'] = self.placeholder_color

    def focus_in(self, *args):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self['foreground'] = self.default_fg_color

    def focus_out(self, *args):
        if not self.get():
            self.put_placeholder()


def get_index(name,documents):
    index = ''
    for i in range(len(documents)):
        if documents[i].name == name:
            index += str(i)
    documents.pop(int(index))
    save_json_data(load_data,data_file_path)


def get_images(name: str, data: object) -> str:
    filtered = list(filter(lambda x: x.name ==
                           name, data.company_info.documents))
    return filtered[0].path
