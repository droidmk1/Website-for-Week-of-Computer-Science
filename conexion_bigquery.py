import os
from google.cloud import bigquery

import pandas as pd

import json

miProyecto = ''
bq = ''

def conexionBigQuery():
    global miProyecto, ruta_key

    miProyecto = 'web-demo-evento'
    print('ruta')
    ruta_key = 'web-demo-evento-ed59e4f7468a.json'

    try:
        if (os.environ['GOOGLE_APPLICATION_CREDENTIALS']):
            print('La variable de entorno existe')
    except Exception as e:
        print('La variable de entorno no existe')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(ruta_key)
        print('Se creo la variable de entorno')

    try:
        global bq
        bq = bigquery.Client(miProyecto)
        sql = """select true as conexion"""
        df = bq.query(sql).result().to_dataframe()

        if df['conexion'][0] == True:
            print('Estamos conectados a BigQuery')
        else:
            print('Algo paso pero no nos pudimos conectar')
        
    except Exception as e:
        print('[ERROR]: ',str(e))

conexionBigQuery()

sql = f"""
SELECT * FROM `web-demo-evento.db_web_demo.users` ORDER BY 1
"""
df_users = bq.query(sql).result().to_dataframe()

# print(df_users)

# print('Este es el nombre de mi proyecto %s la ruta es %s' % (miProyecto, ruta_key))

# print(f'Este es el nombre de mi proyecto {miProyecto} la ruta es {ruta_key}')

# print(df_users[['phone', 'email']])

archivo = open('example.json')
json_resultado = json.load(archivo)
#json_resultado = json.loads(json_resultado)
archivo.close()

print('primer json',json_resultado)
print('resultado con pretty: ',json.dumps(json_resultado, indent=4))

df_json = pd.read_json('example.json')
df_json = df_json.transpose()
print(df_json)

print(df_json.describe())

print(df_json.dtypes)

df_json_esquema = [
    {'name': 'Name', 'type':'string', 'mode':'NULLABLE'},
    {'name': 'Price', 'type':'integer', 'mode':'NULLABLE'},
    {'name': 'Model', 'type':'integer', 'mode':'NULLABLE'},
    {'name': 'Power', 'type':'integer', 'mode':'NULLABLE'}
]

df_json['Name'] = df_json['Name'].astype('str')
df_json['Price'] = df_json['Price'].astype('int64')
df_json['Model'] = df_json['Model'].astype('int64')
df_json['Power'] = df_json['Power'].astype('int64')

print(df_json.dtypes)

df_json.to_gbq('db_web_demo.carros', project_id = miProyecto, if_exists = 'append', table_schema = df_json_esquema)


