# %%
from dotenv import load_dotenv
from datetime import datetime
import requests
import os
import math
import pandas as pd

# %%
load_dotenv()
os.system("rm *.csv")

# %%
# Usar las variables de entorno
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

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # The response data in JSON format
    data_final = response.json()
    print('API Data:', data_final)
else:
    # Print an error message if the request was not successful
    print(f'Error in the request. Status code: {response.status_code}')
    print('Error message:', response.text)


# %%

json_data = data_final

# %%
# print(json_data['data']['items'])

# %%

rows = []
for items in json_data['data']['items']:


    if items['category'] == 'iPhone':
        ri = items['internal_id']
        split = ri.split("-")
        if len(split) >= 2:
            modelo = f'{split[0]}-{split[1]}'
        else:
            modelo = 'revisar'
        precio = float(items['sale_unit_price'])

        nuevo_precio = precio + 40

        online = float(items['warehouses'][1]['stock'])
        polo = float(items['warehouses'][2]['stock'])
        total = online + polo
        rows.append([modelo,ri,total, nuevo_precio])




    

# %%
df = pd.DataFrame(rows, columns=["modelo", "sku", "cantidad", "precio"])
# df

# %%
new_df = df
new_df = new_df[new_df['cantidad'] > 0]

# %%
group_df = new_df.groupby(['modelo', 'precio'])['cantidad'].sum().reset_index()

# %%
df_model = group_df.copy()
df_model = df_model.groupby('modelo')['cantidad'].sum().reset_index()
df_model.to_csv('model-ri.csv', sep=',', index=False, encoding='utf-8')


# %%
group_df.groupby('modelo')['precio'].min()

# %%
df_min = group_df.groupby('modelo')['precio'].min().reset_index()
# df_min

# %%
df_join = df.merge(df_min, on='modelo' , how='left')
df_join = df_join.fillna(0)

# %% [markdown]
# 

# %%
df_join['price_new'] = df_join.apply(lambda x: x['precio_x'] if x['precio_x'] >= x['precio_y'] else x['precio_y'], axis=1)
# df_join.tail(50)

# %%
def precio_comparativo(precio):
    porcentaje = 0
    if precio < 1000:
        porcentaje = 0.20
    elif precio <= 2000:
        porcentaje = 0.15
    else:
        porcentaje = 0.20
    
    new_price = precio / (1 - porcentaje)
    precioComparado = math.ceil(new_price / 100) * 100 -1

    return precioComparado


# %%
df_join['comparativo'] = df_join.apply(lambda x: precio_comparativo(x['price_new']), axis=1)
# df_join

# %%
df_join = df_join.loc[:, ['sku', 'price_new','comparativo']]
# df_join

# %%
fecha_actual = datetime.now()
nombre_fecha = fecha_actual.strftime("%d%m%y")
csv_name = f'{nombre_fecha}-woocommerce.csv'


# %%
# df_join.to_csv(csv_name, sep=',', index=False, encoding='utf-8')

# %%


# %%
df_data = pd.read_csv('./data-sku/data-sku-woocommerce.csv', encoding='utf-8')
# df_data

# %%
df_result = pd.merge(df_data,df_join, left_on='SKU', right_on='sku', how='left', sort=False)

df_result = df_result.drop(columns=(['Precio rebajado','Precio normal','sku']))

# df_result.tail(10)

# %%
df_result = df_result.rename(columns={'price_new':'Precio rebajado', 'comparativo': 'Precio normal'})

# %%
# df_result

# %%
df_result.to_csv(csv_name, sep=',', index=False, encoding='utf-8-sig')


