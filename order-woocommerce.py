# %%
from dotenv import load_dotenv  
import pandas as pd
from woocommerce import API
import os

# %%
load_dotenv()
url = os.getenv("URL")
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")


# %%
wcapi = API(
    url=url,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    wp_api=True,
    version="wc/v3"
)

# %%
datos = wcapi.get("orders?per_page=50").json()


# %%
# row = []

# for items in datos:

#     if items['status'] != "on-hold":
#         continue

#     id = items['id']
#     nombre_completo = items['billing']['first_name'] + " " + items['billing']['last_name']
#     address = items['billing']['address_1']
#     distrito = items['billing']['distrito']
#     provincia = items['billing']['provincia'] 
#     departamento = items['billing']['departamento']
#     monto = items['total']
#     phone = items['billing']['phone']

    
#     row.append([id,nombre_completo,address,distrito,provincia,departamento,monto,phone])








# %%
row = []

for items in datos:

    if items['status'] != "processing":
        continue

    id = items['id']
    status = items['status']
    registro = items['date_created'].split('T')[0]
    nombre_completo = items['billing']['first_name'] + " " + items['billing']['last_name']
    address = items['billing']['address_1']
    distrito = items['billing']['distrito']
    provincia = items['billing']['provincia'] 
    departamento = items['billing']['departamento']
    monto = items['total']
    phone = items['billing']['phone']
    sku = items['line_items'][0]['sku']


    
    row.append([id,status,registro,'-', nombre_completo,'-','-','-','-',address,'-',sku,distrito,provincia,departamento,monto,phone[-9:]])

# %%
df = pd.DataFrame(row)
df = df.sort_values(by=0, ascending=True)

# %%
if os.path.exists('reporte.csv'):
    os.remove('reporte.csv')
    df.to_csv('reporte.csv', sep=',', index=False, encoding='utf-8-sig')

else:
    df.to_csv('reporte.csv', sep=',', index=False, encoding='utf-8-sig')

    



