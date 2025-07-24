# %%
from dotenv import load_dotenv
from datetime import datetime
import os
import math
import pandas as pd
from pandas import json_normalize
from dataclasses import dataclass, asdict, field
from typing import List
import asyncio
import aiohttp
import json
import nest_asyncio
nest_asyncio.apply()

load_dotenv(verbose=True,override=True)

# %%

API_KEY = os.getenv("API_KEY_SISTEMA")
URL = os.getenv("URL_SISTEMA")+'api/document/search-items'

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json',
}

# %%
@dataclass
class ProductERP:
    modelo: str
    sku:str
    cantidad: float
    precio: float
    description: str
    online: float

    @staticmethod
    def warehouses_stock(array_warehouse):
        warehouses = [
            {"warehouse_description": "Almacén Oficina Principal","warehouse_id": 1},
            {"warehouse_description": "Almacén - Online","warehouse_id": 2},
            {"warehouse_description": "Almacén - Caminos del Inca","warehouse_id": 3},
            {"warehouse_description": "Almacén - Taller","warehouse_id": 4},
            {"warehouse_description": "Almacén - Reparacion","warehouse_id": 5},
            {"warehouse_description": "Almacén - Caminos del Inca - Transito","warehouse_id": 6},
            {"warehouse_description": "Almacén - Reparacion  - Piezas","warehouse_id": 7},
            {"warehouse_description": "Almacén - Logistica Inversa","warehouse_id": 8},
            {"warehouse_description": "Almacén - Miraflores","warehouse_id": 9}
        ]

        stocks = []

        for warehouse in warehouses:
            found = False
            for one_warehouse in array_warehouse:
                if one_warehouse["warehouse_id"] == warehouse["warehouse_id"]:
                    stocks.append(float(one_warehouse["stock"]))
                    found = True 
                    break
            if not found:
                stocks.append(float(0))
        return stocks


    @staticmethod
    def from_data_row(item):
        ri = item['internal_id']
        modelo = f"{ri.split('-')[0]}-{ri.split('-')[1]}-"
        # online = float(item['warehouses'][1]['stock'])
        # polo = float(item['warehouses'][2]['stock'])
        princial, online, polo, taller, reparacion, transito_polo, taller_piezas, logistica_inversa, miraflores = ProductERP.warehouses_stock(item['warehouses'])
        total = online + polo + miraflores
        precio = float(item['sale_unit_price']) + 40
        description = 'in_stock' if polo > 0 else 'out_of_stock'
        return ProductERP(
                modelo,
                ri,
                total,
                precio,
                description,
                online
            )

def genarate_rows_as_dicts(data: dict):
    return [ asdict(ProductERP.from_data_row(item)) for item in data['data']['items'] if item['category'] == 'iPhone' ]

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

async def conecction(session: aiohttp.ClientSession, URL: str):
    async with session.get(URL) as response:
        if response.status != 200:
            print(f'error in the request{response.text}')
        return await response.json()



async def main():
    async with aiohttp.ClientSession(headers=headers) as session:
        response = await conecction(session,URL)
        return response

# %%

response = asyncio.run(main())
# %%
data = genarate_rows_as_dicts(response)

df = pd.json_normalize(data)
new_def = df.copy()
new_def = new_def[new_def['cantidad'] > 0]

new_def
# %%

group_df = new_def.groupby(['modelo', 'precio'])['cantidad'].sum().reset_index()
df_min = group_df.groupby('modelo')['precio'].min().reset_index()

# %% 
df_join = df.merge(df_min, on='modelo', how='left')
df_join = df_join.fillna(0)
df_join['precio_new'] = df_join.apply(lambda x: x['precio_x'] if x['precio_x'] >= x['precio_y'] else x['precio_y'], axis=1)
df_join['comparativo'] = df_join.apply(lambda x: precio_comparativo(x['precio_new']), axis=1)
df_join = df_join.loc[:, ['sku','precio_new','comparativo','description','online']]

df_join

# %%
# df_woocommerce = pd.read_csv('/home/bryhans/python-scripts/data/date-woocommerce.csv',encoding='utf-8')
df_woocommerce = pd.read_csv('./data/date-woocommerce.csv',encoding='utf-8')

df_woocommerce = df_woocommerce.loc[:,['ID','SKU','Nombre','Categorías']]
# %%

df_father = df_woocommerce.copy()
df_father = df_father[df_father['Categorías'] == 'iPhones']

# %%

df_woocommerce = df_woocommerce[df_woocommerce['Categorías'] != 'iPhones']


# %%

df_table_jon = df_woocommerce.merge(df_father, on='Nombre', how='left')
df_table_jon = df_table_jon.reindex(['ID_y','ID_x','SKU_y','SKU_x'],axis=1)
df_table_jon.rename(columns={'ID_y':'id_father','ID_x':'id_child','SKU_y':'modelo', 'SKU_x':'codigo_interno'}, inplace=True)

df_table_jon

# %%

df_complete = df_table_jon.merge(df_join, left_on='codigo_interno', right_on='sku', how='left')
df_complete
# %%

# filter = new_def['modelo'].unique()

# df_complete = df_complete[df_complete.modelo.isin(filter)]

# %%
data_arry = df_complete.to_dict(orient='records')


# comentar depuest
# data_arry
# modelo_buscado = 'iPhone-13-'
# filtrados = [item for item in data_arry if item.get('modelo') == 'IP-15P-' or item.get('modelo') == 'IP-15PM-']
# data_arry = filtrados


# %%

object_data = []


def float_numeric(value):
    digit = float(value)
    return str(digit)
    

# Iteramos sobre data_arry
for item in data_arry:
    # Buscamos si ya existe un objeto con el id_father actual en object_data
    existing_entry = next((entry for entry in object_data if entry['id_father'] == item['id_father']), None)
    
    if existing_entry:
        # Si ya existe, agregamos la información a la lista 'update'
        existing_entry['update'].append({
            'id': item['id_child'],
            'price': float_numeric(item['precio_new']),
            'regular_price': float_numeric(item['comparativo']),
            'sale_price': float_numeric(item['precio_new']),
            'description': " ",
            "stock_quantity": int(item['online']),
            "stock_status": 'instock' if item['online'] > 0 else 'outofstock'

        })
    else:
        # Si no existe, creamos una nueva entrada en object_data
        object_data.append({
            'id_father': item['id_father'],
            'update': [{
                'id': item['id_child'],
                'price': float_numeric(item['precio_new']),
                'regular_price': float_numeric(item['comparativo']),
                'sale_price': float_numeric(item['precio_new']),
                'description': " ",
                "stock_quantity": int(item['online']),
                "stock_status": 'instock' if item['online'] > 0 else 'outofstock'
            }]
        })


# %%
from woocommerce import API

url = os.getenv("URL")
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")


# %%
print(url)
# %%


wcapi = API(
    url=url,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    wp_api=True,
    version="wc/v3",
    timeout=120
)

response_data = []

for item in object_data:
    data = {"update": item['update']}
    response = wcapi.post(f"products/{item['id_father']}/variations/batch", data).json()
    if response:
        print(f"{datetime.now()}-{item['id_father']} codigo actualizado")
        response_data.append(response)


# %%
df_complete.to_csv('pruba_woocommer.csv',index=False,encoding='utf-8')

with open('response.json', 'w', encoding='utf-8') as f:
    json.dump(response_data, f, ensure_ascii=False, indent=4)