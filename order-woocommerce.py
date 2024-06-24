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
    version="wc/v3",
    timeout=120
)

# %%
datos = wcapi.get("orders?per_page=50").json()
# print(wcapi.get("orders?per_page=100").json())


# %%
def payment_name(method_pay):
    if method_pay == 'woo-mercado-pago-basic':
        return 'Mercado Pago'
    if method_pay == 'micuentawebstd':
        return 'Pago Link - Izipay'
    if method_pay == 'bcp_cuotealo':
        return 'Cuotealo'
    else:
        return 'Revisar'
    

#'_billing_dni'
def get_meta_data(key,data):
    for meta_item in data['meta_data']:
        if meta_item['key'] == key:
            return meta_item['value']
    return None


def get_payment_id(method_pay,data):
    if method_pay == 'woo-mercado-pago-basic':
        return get_meta_data('_Mercado_Pago_Payment_IDs',data)
    if method_pay == 'micuentawebstd':
        return get_meta_data('Transaction ID',data)
    else:
        return 'Revisar'

def document_type(document):
    if document == '1':
        return 'FACTURA'
    else:
        return 'BOLETA'


# %%
row = []
    # order-shipped
    # if items['status'] != "on-hold":


for items in datos:

    if items['status'] != "processing":
    # if items['status'] != "on hold":
        continue

    id = items['id']
    status = items['status']
    registro = items['date_created'].split('T')[0]
    nombre_completo = (items['billing']['first_name'] + " " + items['billing']['last_name']).upper()
    type_of_document = document_type(get_meta_data("_billing_check_factura",items))
    ruc = get_meta_data("_billing_ruc",items) if type_of_document != 'BOLETA' else '-'
    ruc_name =  (items['billing']['company']).upper() if type_of_document != 'BOLETA' else '-'


    address = items['billing']['address_1'].upper()
    reference = items['customer_note'] if len(items['customer_note']) else '-'
    distrito = items['billing']['distrito']
    provincia = items['billing']['provincia'] 
    departamento = items['billing']['departamento']
    monto = items['total']
    phone = items['billing']['phone'].replace(" ","")
    sku = items['line_items'][0]['sku']
    email = items['billing']['email']
    payment_method = payment_name(items['payment_method'])
    dni = str(get_meta_data('_billing_dni',items))
    payment_number = str(get_payment_id(items['payment_method'],items))
    
    row.append([id,status,registro,dni, nombre_completo,ruc,ruc_name,type_of_document,'-','-',address,reference,distrito,provincia,departamento,sku,monto,phone[-9:],'-','-','1',email,'-',payment_method,'Capturado',payment_number])


df = pd.DataFrame(row)
df = df.sort_values(by=0, ascending=True)
df

# %%
if os.path.exists('reporte.csv'):
    os.remove('reporte.csv')
    df.to_csv('reporte.csv', sep=',', index=False, encoding='utf-8-sig')
else:
    df.to_csv('reporte.csv', sep=',', index=False, encoding='utf-8-sig')

    



