# %%
from dotenv import load_dotenv
import requests
import os
import pandas as pd
import platform
import duckdb

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


# %%
rows = []
for items in data_final['data']['items']:
    if items['category'] == 'iPhone':
        ri = items['internal_id']
        split = ri.split("-")
        if len(split) >= 2:
            modelo = f'{split[0]}-{split[1]}-{split[2]}'
            modelo_grado = f'{split[0]}-{split[1]}-{split[2]}-{split[3]}'

        else:
            modelo = 'revisar'
        precio = float(items['sale_unit_price'])
        nuevo_precio = precio + 40
        princial, online, polo, taller, reparacion, transito_polo, taller_piezas, logistica_inversa, miraflores = warehouses_stock(items['warehouses'])
        rows.append([ri,miraflores,nuevo_precio])


# %%

df = pd.DataFrame(rows, columns=["sku", "cantidad", "precio"])
df_filter = duckdb.query("""
        WITH df_filter as (
                SELECT * FROM df 
                WHERE cantidad > 0 AND sku LIKE 'DESC-%')
        SELECT
            replace(sku, 'DESC-', '') as sku,
            cantidad,
            precio,
            FROM df_filter   
 """).to_df()
woocommerce = pd.read_csv('./data/woocommerce.csv')

# %%

df_html = duckdb.query("""
    SELECT 
        df_filter.sku,
        woocommerce.Nombre,
        woocommerce."Valor(es) del atributo 1",
        woocommerce."Valor(es) del atributo 2",
        woocommerce."Valor(es) del atributo 3",
        CAST(df_filter.precio AS INTEGER) as precio
    FROM df_filter
    LEFT JOIN woocommerce ON woocommerce.SKU = df_filter.sku
    ORDER BY df_filter.precio ASC , woocommerce.Nombre ASC
""").to_df()
df_html
# %%

with open('descuentos.html', 'w') as file:
    for _, row in df_html.iterrows():
        nombre = row['Nombre']
        valor_atributo_1 = row['Valor(es) del atributo 1']
        valor_atributo_2 = row['Valor(es) del atributo 2']
        valor_atributo_3 = row['Valor(es) del atributo 3']
        precio = row['precio']

        # Generar el HTML
        html_content = f"""
            <div
            class="elementor-element elementor-element-1607c76 e-flex e-con-boxed e-con e-parent e-lazyloaded"
            data-id="1607c76"
            data-element_type="container"
            
            >
            <div class="e-con-inner">
                <div
                class="elementor-element elementor-element-6cc1a30 e-grid e-con-full e-con e-child"
                data-id="6cc1a30"
                data-element_type="container"
                
                >
                <div
                    class="elementor-element elementor-element-15ba5ad elementor-widget elementor-widget-text-editor"
                    data-id="15ba5ad"
                    data-element_type="widget"
                    data-widget_type="text-editor.default"
                >
                    <div class="elementor-widget-container">
                    <p><strong>{nombre} sin Face ID</strong></p>
                    </div>
                </div>
                <div
                    class="elementor-element elementor-element-fa99b10 elementor-widget elementor-widget-text-editor"
                    data-id="fa99b10"
                    data-element_type="widget"
                    data-widget_type="text-editor.default"
                >
                    <div class="elementor-widget-container">
                    <p style="text-align: center"><strong>{valor_atributo_1}</strong></p>
                    </div>
                </div>
                <div
                    class="elementor-element elementor-element-df0a806 elementor-widget elementor-widget-text-editor"
                    data-id="df0a806"
                    data-element_type="widget"
                    data-widget_type="text-editor.default"
                >
                    <div class="elementor-widget-container">
                    <p><strong>{valor_atributo_2}</strong></p>
                    </div>
                </div>
                <div
                    class="elementor-element elementor-element-e82dfd9 elementor-widget elementor-widget-text-editor"
                    data-id="e82dfd9"
                    data-element_type="widget"
                    data-widget_type="text-editor.default"
                >
                    <div class="elementor-widget-container">
                    <p><strong>{valor_atributo_3}</strong></p>
                    </div>
                </div>
                <div
                    class="elementor-element elementor-element-9f7e4f5 elementor-widget elementor-widget-text-editor"
                    data-id="9f7e4f5"
                    data-element_type="widget"
                    data-widget_type="text-editor.default"
                >
                    <div class="elementor-widget-container">
                    <p style="text-align: center">
                        <span style="color: #009bdb; font-size: 14pt"
                        ><strong>S/ {precio}</strong></span
                        >
                    </p>
                    </div>
                </div>
                </div>
            </div>
            </div>

        """
        # file.write(html_content + '\n')
        file.write(html_content)

