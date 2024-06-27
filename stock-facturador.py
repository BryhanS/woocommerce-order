# %%
from dotenv import load_dotenv
from datetime import datetime
import requests
import os
import math
import pandas as pd
import platform

# %%
load_dotenv()

os_name = platform.system()
if os_name == 'Windows':
    os.system("del *csv")
else:
    os.system("rm *.csv")
    
api_key = os.getenv("API_KEY_SISTEMA")
url = os.getenv("URL_SISTEMA")


# %%
# Headers with the API token
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',  # Adjust the content type as needed
}

# Make a GET request with headers
response = requests.get(url, headers=headers)
print(response)
# Check if the request was successful (status code 200)
if response.status_code == 200:
    # The response data in JSON format
    data_final = response.json()
    # print('API Data:', data_final)
else:
    # Print an error message if the request was not successful
    print(f'Error in the request. Status code: {response.status_code}')
    print('Error message:', response.text)

# %% [markdown]
# json_data = data_final

# %%
rows = []
for items in data_final['data']['items']:


    if items['category'] == 'iPhone':
        ri = items['internal_id']
        split = ri.split("-")
        if len(split) >= 2:
            modelo = f'{split[0]}-{split[1]}-{split[2]}'
        else:
            modelo = 'revisar'
        precio = float(items['sale_unit_price'])

        nuevo_precio = precio + 40

        online = float(items['warehouses'][1]['stock'])
        polo = float(items['warehouses'][2]['stock'])
        total = online + polo
        rows.append([modelo,ri,online,polo,total])

# %%
df = pd.DataFrame(rows, columns=["modelo", "sku", "tienda_online", "tienda_polo","total"])
df = df.drop(columns='total')
df = pd.melt(df, id_vars=['modelo','sku'], value_vars=['tienda_online','tienda_polo'],var_name='ubicacion',value_name='inventario')
# df[df['inventario'] < 0]
df = df[df['inventario'] != 0]


# %%


# %%
# df['Grado'] = df['sku'].str.split("-").str[3]
# df['Color'] = df['sku'].str.split("-").str[4]
# df


# %%

# def change_grado(x):
#     grado = {'A+':'1.A+', 'A':'2.A', 'B':'3.B', 'C':'4.C'}
#     if x in grado:
#         return grado[x]
#     else:
#         return 'No existe grado'


# %%
# df['Grado'] = df['Grado'].apply(change_grado)
# df

# %%
# new_df =  pd.pivot_table(df,values='inventario', index=['modelo','Color'],columns=['ubicacion','Grado'], aggfunc='sum').reset_index()
# new_df

# %%
fecha_actual = datetime.now()
nombre_fecha = fecha_actual.strftime("%d%m%y")
csv_name = f'{nombre_fecha}-stock.csv'

# %%
df.to_csv(csv_name, sep=',', index=False, encoding='utf-8-sig')

# %%



