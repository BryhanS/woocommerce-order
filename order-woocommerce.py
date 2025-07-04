# %%
from dotenv import load_dotenv  
import pandas as pd
from woocommerce import API
import os
from pandas import json_normalize
from dataclasses import dataclass, asdict
from typing import Optional

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
datos = wcapi.get("orders?status=processing&per_page=100").json()

# %%
@dataclass
class OrderRow:
    id: str
    status: str
    fecha_registro: str
    documento_identidad: str
    nombre_completo: str
    ruc: str
    razon_social: str
    tipo_documento: str
    numero_comprobante: str
    guia_remision: str
    direccion_facturacion: str
    direccion_envio: str
    direccion_envio_referencia: str
    distrito: str
    provincia: str
    departamento: str
    ri_producto: str
    monto_sin_comision: float
    monto_total: float
    telefono_mobil: str
    filler1: str
    filler2: str
    filler3: str
    mail: str
    send_mail: str
    payment_method: str
    tipo_aprobacion: str
    payment_number: str
    filler4: str
    filler5: str
    filler6: str
    tipo_entrega: str
    tipo_envio: str
    tipo_de_articulo: str
    largo: str
    ancho: str
    alto: str
    filler7: str


    @staticmethod
    def payment_name(method_pay):
        if method_pay == 'woo-mercado-pago-basic':
            return 'Mercado Pago'
        if method_pay == 'micuentawebstd':
            return 'Pago Link - Izipay'
        if method_pay == 'bcp_cuotealo':
            return 'Cuotealo'
        else:
            return 'Revisar'
    
    @staticmethod
    def get_meta_data(key,data):
        for meta_item in data['meta_data']:
            if meta_item['key'] == key:
                return meta_item['value']
        return None


    @staticmethod
    def get_payment_id(method_pay,data):
        if method_pay == 'woo-mercado-pago-basic':
            return OrderRow.get_meta_data('_Mercado_Pago_Payment_IDs',data)
        if method_pay == 'micuentawebstd':
            return OrderRow.get_meta_data('Transaction ID',data)
        else:
            return 'Revisar'

    @staticmethod
    def document_type(document):
        if document == '1':
            return 'FACTURA'
        else:
            return 'BOLETA'
        
    @staticmethod
    def codigo_interno(data):
        return "\n".join([item['sku'] for item in data])

    @staticmethod
    def feet(data):  
        feet = 0.0
        if len(data['fee_lines']) != 0:
            for item in data['fee_lines']:
                feet += float(item['total'])
        return feet
        

    @staticmethod
    def from_item(item):
        nombre_completo = (item['billing']['first_name'] + " " + item['billing']['last_name']).upper()
        nombre_completo_shipping = (item['shipping']['first_name'] + " " + item['shipping']['last_name']).upper()

        usuario_enviar = nombre_completo_shipping if nombre_completo == nombre_completo_shipping else " "

 
        tipo_documento = OrderRow.document_type(OrderRow.get_meta_data("_billing_check_factura",item))
        ruc = OrderRow.get_meta_data("_billing_ruc",item) if tipo_documento != 'BOLETA' else '-'
        razon_social = (item['billing']['company']).upper() if tipo_documento != 'BOLETA' else '-'
        documento_identidad = str(OrderRow.get_meta_data('_billing_dni',item))
        ri_producto = OrderRow.codigo_interno(item['line_items'])
        payment_method = OrderRow.payment_name(item['payment_method'])
        payment_number = str(OrderRow.get_payment_id(item['payment_method'],item))
        comision = OrderRow.feet(item)
        monto_total = float(item['total'])
        monto_sin_comision = monto_total - comision
        
        # print(type(item['total']))
        return OrderRow(
                id = item['id'],
                status = item['status'],
                fecha_registro = item['date_created'].split('T')[0],
                documento_identidad = documento_identidad,
                nombre_completo = nombre_completo,
                ruc = ruc,
                razon_social = razon_social,
                tipo_documento =  tipo_documento,
                direccion_facturacion = item['billing']['address_1'].upper(),
                direccion_envio = item['shipping']['address_1'].upper(),
                direccion_envio_referencia = item['customer_note'] + "-" + usuario_enviar if len(item['customer_note']) else '-',
                distrito = item['billing']['distrito'],
                provincia = item['billing']['provincia'],
                departamento = item['billing']['departamento'],
                ri_producto = ri_producto,
                monto_sin_comision = monto_sin_comision,
                monto_total = item['total'],
                telefono_mobil = item['billing']['phone'].replace(" ",""),
                mail = item['billing']['email'],
                payment_method = payment_method,
                tipo_aprobacion = 'Capturado',
                payment_number = payment_number,
                numero_comprobante = '',
                guia_remision = '',
                filler1 = '',
                filler2 = '',
                filler3 = '1',
                filler4 = '',
                filler5 = '',
                filler6 = '',
                filler7 = 'CELULAR',
                send_mail = '-',
                tipo_entrega = 'Entrega a domicilio',
                tipo_envio = 'PAQUETE',
                tipo_de_articulo = 'CAJA - CAJA',
                largo = '26',
                ancho = '16',
                alto = '12',                
            )

        

# %%
def genarate_rows_as_dicts(data):
    return [ asdict(OrderRow.from_item(item)) for item in data ]

# %%
json_data = genarate_rows_as_dicts(datos)
df_json = json_normalize(json_data)
df_json


# %%
df_json = df_json.sort_values(by=['id'],ascending=True)

if os.path.exists('reporte.csv'):
    os.remove('reporte.csv')
    df_json.to_csv('reporte.csv', sep=',', index=False, encoding='utf-8-sig')
else:
    df_json.to_csv('reporte.csv', sep=',', index=False, encoding='utf-8-sig')






