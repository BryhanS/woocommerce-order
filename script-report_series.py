# %%
import requests
from bs4 import BeautifulSoup
import json
import asyncio
import aiohttp
import nest_asyncio
import pandas as pd
from dotenv import load_dotenv
import os
from pandas import json_normalize
from dataclasses import dataclass, asdict
from typing import Optional
nest_asyncio.apply()

# %%
load_dotenv(verbose=True,override=True)
os.system("rm *.csv")

# %%
# Usar las variables de entorno
api_key = os.getenv("API_KEY_SISTEMA")
url = os.getenv("URL_SISTEMA")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

login_url = f'{url}login'


# %%

# Iniciar una sesión
with requests.Session() as c:
    # Obtener la página de inicio de sesión para capturar el token CSRF
    login_page = c.get(login_url)
    
    # Analizar el contenido HTML para extraer el token CSRF
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': '_token'})['value']
    
    # Datos de autenticación con el token CSRF
    payload = {
        'email': EMAIL_USER,
        'password': EMAIL_PASS,
        '_token': csrf_token  # Incluye el token CSRF
    }
    
    # Realizar la solicitud POST para iniciar sesión
    response = c.post(login_url, data=payload)
    saved_coockies = response.cookies
    print(saved_coockies)
    
    # Verificar si la autenticación fue exitosa
    if response.status_code == 200:
        print("Inicio de sesión exitoso.")
        # Hacer una solicitud GET a una página protegida
        protected_page_url = f'{url}protected_page'
        protected_response = c.get(protected_page_url)
        
        if protected_response.status_code == 200:
            print("Acceso a la página protegida exitoso.")
            # Procesar la respuesta de la página protegida
            print(protected_response.text)
        else:
            print(f"Error al acceder a la página protegida: {protected_response.status_code}")
    else:
        print(f"Error al iniciar sesión: {response.status_code}")
        print(response.text)


# %%

params = {
    'column': 'series',
    'page': 1,
}

response = c.get(f'{url}item-lots/records', params=params, cookies=saved_coockies)
data = response.json()
last_page = data['meta']['last_page']


# %%
report_url = f'{url}item-lots/records'

async def save_json(session, page):

    params = {
    'column': 'series',
    'page': page,
    }
    async with session.get(report_url, params=params, cookies=saved_coockies) as response:
        if response.status == 200:
            data = await response.json()
            return data['data']
        else:
            print(f"fallo en la descargar de {report_url} con status")



async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        page = 1
        while page <= last_page:
            task = save_json(session,page)
            tasks.append(task)
            page+=1
        results = await asyncio.gather(*tasks)
        data_array = []
        data_array.extend(results)
        flat_list = [item for sublist in data_array for item in sublist]

        return flat_list

# %%
series_data = asyncio.run(main()) 


# %%

api_key = os.getenv("API_KEY_SISTEMA")
url = os.getenv("URL_SISTEMA")+'api/document/search-items'
URL_SEARCH = os.getenv("URL_SISTEMA")+'api/document/search-items'


# Headers with the API token
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',  # Adjust the content type as needed
}
# Make a GET request with headers
response = requests.get(URL_SEARCH, headers=headers)
print(response)
# Check if the request was successful (status code 200)
if response.status_code == 200:
    try:
        data_final = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Error: La respuesta no contiene un JSON válido.")
        print("Contenido de la respuesta:", response.text)
else:
    # Print an error message if the request was not successful
    print(f'Error in the request. Status code: {response.status_code}')
    print('Error message:', response.text)



# %%

items =  data_final['data']['items']


# %%
@dataclass
class SeriesRow:
    imei: str
    item_ri: str
    item_description: str
    warehouse: str

    @staticmethod
    def search_ri(item_id,items):
        for item in items:
            if item['item_id'] == item_id:
                return item['internal_id']
                break

    @staticmethod
    def serie_item(item,items):
        return SeriesRow(
            imei = item['series'],
            item_ri = SeriesRow.search_ri(item['item_id'],items),
            item_description = item['item_description'],
            warehouse = item['warehouse_id'],
        )


# %%
def genarate_rows_as_dicsts(data, items):
    return [ asdict(SeriesRow.serie_item(item, items)) for item in data ]

# %%
data_json = genarate_rows_as_dicsts(series_data,items)

# %%
df_json = pd.json_normalize(data_json)

# %%
if os.path.exists('reporte_series.csv'):
    os.remove('reporte_series.csv')
    df_json.to_csv('reporte_series.csv', sep=',', index=False, encoding='utf-8-sig')
else:
    df_json.to_csv('reporte_series.csv', sep=',', index=False, encoding='utf-8-sig')



