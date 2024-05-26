import pygsheets
import pandas as pd
import json
import csv
from google.oauth2 import service_account
import functions as f

client = pygsheets.authorize(service_account_file='credentials.json')

excel = client.open_by_url('https://docs.google.com/spreadsheets/d/1pz_MPwerlbM5--sAdBykbcImsRL-zNGezqLI69oX-ac/edit?usp=sharing')
sheet = excel.worksheet_by_title('articulos')

db = sheet.get_as_df()
print(db) 


sheetName = f.obtainSheet('clientes')

sheetName.set_dataframe(db, start= (1,1))