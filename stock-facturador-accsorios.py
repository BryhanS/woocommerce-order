# %%
from dotenv import load_dotenv
from datetime import datetime
import requests
import os
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
url = os.getenv("URL_SISTEMA")+'api/document/search-items'


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
def warehouses_stock(array_warehouse):
    warehouses = [
        {"warehouse_description": "Almacén Oficina Principal","warehouse_id": 1},
        {"warehouse_description": "Almacén - Online","warehouse_id": 2},
        {"warehouse_description": "Almacén - Caminos del Inca","warehouse_id": 3},
        {"warehouse_description": "Almacén - Taller","warehouse_id": 4},
        {"warehouse_description": "Almacén - Reparacion","warehouse_id": 5},
        {"warehouse_description": "Almacén - Caminos del Inca - Transito","warehouse_id": 6},
        {"warehouse_description": "Almacén - Reparacion  - Piezas","warehouse_id": 7}
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


# %%
rows = []
for items in data_final['data']['items']:
    # if items['category'] == 'iPhone':
    ri = items['internal_id']
    precio = float(items['sale_unit_price'])
    nuevo_precio = precio + 40
    princial, online, polo, taller, reparacion, transito_polo, taller_piezas = warehouses_stock(items['warehouses'])
    rows.append([ri,princial,online,polo, taller, reparacion, transito_polo,taller_piezas])

# %%



df = pd.DataFrame(rows, columns=["sku","almacen_principal", "tienda_online", "tienda_caminos","almacen_taller", "almacen_reparacion", "almacen_transito_caminos","almacen_taller_piezas"])
df.head(20)
# description_warehouse = ["almacen_principal", "tienda_online", "tienda_caminos", "almacen_taller", "almacen_reparacion", "almacen_transito_caminos", "almacen_taller_piezas"]
# df = pd.melt(df, id_vars=['modelo', 'modelo_grado','sku'], value_vars=description_warehouse,var_name='ubicacion',value_name='inventario')
df.to_csv('stock-facturador-accsorios.csv', sep=',', index=False, encoding='utf-8-sig')


# %%
fecha_actual = datetime.now()
nombre_fecha = fecha_actual.strftime("%d%m%y")
csv_name = f'{nombre_fecha}-stock-accesorios.csv'

# %%
df.to_csv(csv_name, sep=',', index=False, encoding='utf-8-sig')




