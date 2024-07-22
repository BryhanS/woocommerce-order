# %%
from dotenv import dotenv_values
from datetime import datetime, timedelta
import os
import requests
import zipfile
from os import path
import asyncio
import aiohttp
import aiofiles
import nest_asyncio

if not path.exists('./Documentos'):
    os.mkdir('Documentos')
    os.mkdir('Documentos/Online')
    os.mkdir('Documentos/Tienda')


os.system("rm ./Documentos/Online/*.pdf")
os.system("rm ./Documentos/Tienda/*.pdf")
os.system("rm *.zip")


config = dotenv_values(".env")

# Usar las variables de entorno
api_key = config["API_KEY_SISTEMA"]
url = config["URL_SISTEMA"]

day = datetime.now().date()
day_week = day.strftime("%A")
intial_date = ""
final_date = ""


if day_week == 'Monday':
    intial_date = (day - timedelta(days=3)).strftime("%Y%m%d")
    final_date = (day - timedelta(days=1)).strftime("%Y%m%d")    
else:
    intial_date = (day - timedelta(days=1)).strftime("%Y%m%d")
    final_date = (day - timedelta(days=1)).strftime("%Y%m%d")    



url_path = f'{url}api/documents/lists/{intial_date}/{final_date}'


# Headers with the API token
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',  # Adjust the content type as needed
}

# Make a GET request with headers
response = requests.get(url_path, headers=headers)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # The response data in JSON format
    data_final = response.json()
    # print('API Data:', data_final)s
else:
    # Print an error message if the request was not successful
    print(f'Error in the request. Status code: {response.status_code}')
    print('Error message:', response.text)



json_data = data_final


rows = []

def path_download(numComprobantePago):
    if numComprobantePago == "B001" or numComprobantePago == "F001":
        return './Documentos/Tienda'
    else:
        return './Documentos/Online'

    
for documentos in json_data['data']:
    numComprobantePago = documentos["number"].split('-')[0]
    download_pdf = documentos["download_pdf"]
    download_path = path_download(numComprobantePago)
    filename = documentos["filename"]
    down_name = f"{download_path}/{filename}.pdf"
    rows.append({
        'pdf_url': download_pdf,
        'pdf_path':  down_name
    })

def zip_dir(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))

# Ruta de la carpeta que deseas comprimir
folder_to_zip = './Documentos'

# Ruta y nombre del archivo ZIP resultante
zip_file_path = f'./{intial_date}-{final_date}.zip'

# Comprimir la carpeta

nest_asyncio.apply()

async def download_file(session,url, path):
    async with session.get(url) as response:
        if response.status == 200:
            async with aiofiles.open(path, 'wb') as f:
                content = await response.read()
                await f.write(content)
            print(f"Descargado: {path}")
        else:
            print(f"fallo en la descargar de {url} con status")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for row in rows:
            task = download_file(session, row['pdf_url'], row['pdf_path'])
            tasks.append(task)
        await asyncio.gather(*tasks)
        zip_dir(folder_to_zip, zip_file_path)

if __name__ == "__main__":
    asyncio.run(main())


