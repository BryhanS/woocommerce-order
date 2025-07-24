# %%

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
import os
from io import BytesIO

load_dotenv(verbose=True, override=True)

# %%
fecha_inicio = datetime(2025, 7, 1)
fecha_fin = datetime(2025, 7, 3)

# URL de inicio de sesión
login_url = f'{os.getenv("URL_SISTEMA")}/login'
user = os.getenv("EMAIL_USER")
password = os.getenv("EMAIL_PASS")


# Iniciar una sesión
with requests.Session() as c:
    # Obtener la página de inicio de sesión para capturar el token CSRF
    login_page = c.get(login_url)
    
    # Analizar el contenido HTML para extraer el token CSRF
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': '_token'})['value']
    
    # Datos de autenticación con el token CSRF
    payload = {
        'email': user,
        'password': password,
        '_token': csrf_token  # Incluye el token CSRF
    }
    
    # Realizar la solicitud POST para iniciar sesión
    response = c.post(login_url, data=payload)
    saved_coockies = response.cookies
    
    # Verificar si la autenticación fue exitosa
    if response.status_code == 200:
        print("Inicio de sesión exitoso.")
        # Hacer una solicitud GET a una página protegida
        protected_page_url = 'https://controlerp.catapu.com/protected_page'
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

def download_excel(day,document_type_id):
    params = {
        'apply_conversion_to_pen': False,
        'brand_id': '',
        'category_id': '',
        'date_end': day,
        'date_start':day,
        'document_type_id': document_type_id,
        'item_id': '',
        # 'month_end': '2024-08',
        # 'month_start': '2024-08',
        'page': 1,
        'period':'between_dates',
        'person_id': '',
        'type':'sale',
        'type_person':'customers',
        'user': '',
        'user_id': '',
        'user_type': '',
        'web_platform_id': ''
    }


    response = c.get('https://controlerp.catapu.com/reports/general-items/excel', params=params, cookies=saved_coockies)

    print('Código de estado:', response.status_code)
    print('Tipo de contenido:', response.headers.get('Content-Type'))

    try:
        data = response
        # print('Datos:', data)
    except requests.exceptions.JSONDecodeError as e:
        print(f'Error decodificando JSON: {e}')
        print('Contenido de la respuesta:', response.text)



    # with open(f'./report-{document_type_id}-{day}.xlsx', 'wb') as file:
    #     file.write(data.content)
    #     dtypes = {'ID TIPO':str ,'DOC ENTIDAD NÚMERO': str, 'SERIE': str, 'SERIES': str}
    #     dataframe = pd.read_excel(data.content, dtype=dtypes)
    #     return dataframe
    dtypes = {'ID TIPO':str ,'DOC ENTIDAD NÚMERO': str, 'SERIE': str, 'SERIES': str}
    dataframe = pd.read_excel(BytesIO(data.content), dtype=dtypes)
    return dataframe
# %%

dias = []

# Iterar desde la fecha inicial hasta la fecha final
while fecha_inicio <= fecha_fin:
    dias.append(fecha_inicio.strftime("%Y-%m-%d"))  # Formato: 'YYYY-MM-DD'
    fecha_inicio += timedelta(days=1)


# %%

array_document_type_id = ['01','03','07','08']
data_frame_array = []

for dia in dias:
    for  document_type_id in  array_document_type_id:
        data = download_excel(dia,document_type_id)
        if data is not None and not data.empty:
            data_frame_array.append(data)
    print(dia)

dataframes = [df for df in data_frame_array if not df.empty and not df.isna().all().all()]

# %%

df = pd.concat(dataframes, ignore_index=True)

# %%

mes = fecha_inicio.month    # 7
anio = fecha_inicio.year

df.to_excel(f'ventas_{mes:02d}{anio}.xlsx', index=False)