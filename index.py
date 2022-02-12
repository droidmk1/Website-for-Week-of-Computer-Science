from flask import Flask, render_template, request, redirect, url_for, flash, session
from random import randrange
from datetime import datetime
import uuid

# para las pruebas de bigquery
import os
from google.cloud import bigquery

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

# sql = f"""
# SELECT * FROM `web-demo-evento.db_web_demo.usuarios` ORDER BY 1
# """
# df_users = bq.query(sql).result().to_dataframe()

# print('tabla usuarios select * from',df_users)

app = Flask(__name__)

# settings
app.secret_key = 'mysecretkey'

@app.route('/', methods=['GET','POST'])
def home():
    # CheckLoginInSession
    if request.method == 'POST':
        session.clear()
        session['usuario'] = request.form['login-email']
        session.permanent = True
        CheckData()
        print('soy el usuario', session['usuario'])
        if session['Oldtime'] == 'new':
            return redirect(url_for('profile'))
    return render_template('home.html')

def CheckData():
        sql = f"""
        SELECT email, rol FROM `web-demo-evento.db_web_demo.usuarios` WHERE email = '{session['usuario']}'
        """
        df_users = bq.query(sql).result().to_dataframe()
        print(df_users)
        if len(df_users) == 0:
            print('el dato no esta en el registro')
            sql = f"""
            INSERT INTO `web-demo-evento.db_web_demo.usuarios` (`nombre`, `apellido`, `email`, `dni`, `profesion`, `foto`, `rol`, `estado`) VALUES ('', '', '{session['usuario']}', '', '', '', 3, 1);
            """
            session['rol'] = '3'
            bq.query(sql).result()
            print('rol desde if insert', session['rol'])
            print('tipo de dato', type(session['rol']))
            print('el dato se agrego al registro')
            session['Oldtime'] = 'new'
        else:
            session['Oldtime'] = 'old'
            session['rol'] = str(df_users['rol'][0])
            print('rol desde else select', session['rol'])
            print('tipo de dato', type(session['rol']))
            print('dato encontrado en el registro')

@app.route('/program')
def program():
    # if session['usuario']:
    #     print('que paso con: ', session['usuario'])
    # CheckLoginInSession
    # no todos los expositores se registran
    # SELECT tema, descripcion, horario, fecha, nombre, apellido FROM `web-demo-evento.db_web_demo.exposiciones` INNER JOIN `web-demo-evento.db_web_demo.usuarios` ON email_autor = email ORDER BY fecha ASC, horario;
    sql = f"""
        SELECT * FROM `web-demo-evento.db_web_demo.exposiciones` ORDER BY fecha ASC, horario;
    """
    df = bq.query(sql).result().to_dataframe()
    df = df.to_dict('r')
    return render_template('program.html', df=df)

@app.route('/Users')
def Users():
    # CheckLoginInSession
    if session['rol'] == '1':
        sql = """
        SELECT usuarios.nombre, usuarios.apellido, usuarios.email, usuarios.dni, usuarios.profesion, roles.rol FROM `web-demo-evento.db_web_demo.usuarios` usuarios
        INNER JOIN `web-demo-evento.db_web_demo.roles` roles ON usuarios.rol = roles.id ORDER BY nombre ASC, apellido;
        """
        df = bq.query(sql).result().to_dataframe()
        df = df.to_dict('r')

        sql1 = """
        SELECT * FROM `web-demo-evento.db_web_demo.roles`
        """
        df1 = bq.query(sql1).result().to_dataframe()
        df1 = df1.to_dict('r')
        return render_template('users.html', df=df, df1=df1)
    else:
        print('session incorrecta')
        return redirect(url_for('home'))

@app.route('/actionUser', methods=['POST'])
def actionUser():
    if request.method == 'POST':
        rol = request.form['rol']
        email = request.form['email']
        sql = f"""
        UPDATE `web-demo-evento.db_web_demo.usuarios` SET rol ={rol} WHERE email = '{email}'
        """
        bq.query(sql).result()
        return redirect(url_for('Users'))

@app.route('/organizers')
def organizers():
    # CheckLoginInSession
    return render_template('organizers.html')

@app.route('/logout')
def logout():
    # remove session data
    # session.pop('loggein', None)
    session.pop('usuario', None)
    session.pop('rol', None)
    session.pop('NombreUsuario', None)
    session.pop('old', None)
    session.clear()
    print('Session variables remove')
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if session['usuario']:
        sql = f"""
        SELECT * FROM `web-demo-evento.db_web_demo.usuarios` WHERE email = '{session['usuario']}'
        """
        df_users = bq.query(sql).result().to_dataframe()
        session['NombreUsuario'] = df_users['nombre'][0]+" "+df_users['apellido'][0]
        dni = df_users['dni'][0]
        profesion = df_users['profesion'][0]
        nombre = df_users['nombre'][0]
        apellido = df_users['apellido'][0]
    else:
        return redirect(url_for('home'))
    return render_template('profile.html', dni = dni, profesion = profesion, nombre = nombre, apellido = apellido)


@app.route('/UpdateProfile', methods = ['POST'])
def UpdateProfile():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        dni = request.form['dni']
        profesion = request.form['profesion']
        print(nombre)
        print(apellido)
        print(dni)
        print(profesion)
        sql = f"""
        UPDATE `web-demo-evento.db_web_demo.usuarios` SET nombre = '{nombre}', apellido = '{apellido}', dni = '{dni}', profesion = '{profesion}' WHERE email = '{session['usuario']}'
        """
        bq.query(sql).result()
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('home'))

@app.route('/InsertProgram')
def InsertProgram():
    if session['rol'] == '1':
        sql = f"""
            SELECT * FROM `web-demo-evento.db_web_demo.exposiciones` ORDER BY fecha ASC, horario;
        """
        df = bq.query(sql).result().to_dataframe()
        df = df.to_dict('r')
        # n = len(df['tema'])
        # print('tamaño de temas', n)
        print(df)
        print(type(df))
        return render_template('InsertProgram.html', df=df)
    else:
        return redirect(url_for('home'))

@app.route('/UpdateProgram', methods=['POST'])
def UpdateProgram():
    if request.method == 'POST':
        id_expo = str(uuid.uuid4())
        print('este sera el id_expo', id_expo)
        tema = request.form['tema']
        descripcion = request.form['descripcion']
        horario = request.form['horario']
        fecha = request.form['fecha']
        email_autor = request.form['email_autor']
        pregunta1 = request.form['pregunta1']
        pregunta2 = request.form['pregunta2']
        correct_preg1 = request.form['correct_preg1']
        correct_preg2 = request.form['correct_preg2']
        incorrect_preg1 = request.form['incorrect_preg1']
        incorrect_preg2 = request.form['incorrect_preg2']

        sql = f"""
            INSERT INTO `web-demo-evento.db_web_demo.exposiciones` (`id_expo`, `tema`, `descripcion`, `horario`, `fecha`, `email_autor`,`asistencia`) VALUES ('{id_expo}', '{tema}', '{descripcion}', '{horario}:00', '{fecha}', '{email_autor}','no');
        """
        bq.query(sql).result()

        sql1 = f"""
            INSERT INTO `web-demo-evento.db_web_demo.preguntas` (`id_expo`, `pregunta`, `correcta`, `incorrecta`) VALUES ('{id_expo}', '{pregunta1}', '{correct_preg1}', '{incorrect_preg1}'), ('{id_expo}', '{pregunta2}', '{correct_preg2}', '{incorrect_preg2}');
        """
        bq.query(sql1).result()
        return redirect(url_for('InsertProgram'))
    else:
        return redirect(url_for('home'))

@app.route('/DeleteExpo', methods=['POST'])
def DeleteExpo():
    if request.method == 'POST':
        id_expo = request.form['id_expo']
        sql = f"""
            DELETE FROM `web-demo-evento.db_web_demo.exposiciones` WHERE id_expo = '{ id_expo }'
        """
        bq.query(sql).result()
    return redirect('InsertProgram')

@app.route('/EditExpo', methods=['POST'])
def EditExpo():
    if request.method == 'POST':
        print('soy el id_expo', request.form['id_expo'])
        id_expo = request.form['id_expo']
        sql = f"""
        SELECT * FROM `web-demo-evento.db_web_demo.exposiciones` WHERE id_expo = '{id_expo}'
        """
        df_expo = bq.query(sql).result().to_dataframe()
        tema = df_expo['tema'][0]
        descripcion = df_expo['descripcion'][0]
        horario = df_expo['horario'][0]
        fecha = df_expo['fecha'][0]
        email_autor = df_expo['email_autor'][0]
        print('soy el df', df_expo)

        sql1 = f"""
        SELECT * FROM `web-demo-evento.db_web_demo.preguntas` WHERE id_expo = '{id_expo}'
        """
        df_preg = bq.query(sql1).result().to_dataframe()
        pregunta1 = df_preg['pregunta'][0]
        correcta1 = df_preg['correcta'][0]
        incorrecta1 = df_preg['incorrecta'][0]
        pregunta2 = df_preg['pregunta'][1]
        correcta2 = df_preg['correcta'][1]
        incorrecta2 = df_preg['incorrecta'][1]
        print(pregunta1)
        print(correcta1)
        print(incorrecta1)
        print(pregunta2)
        print(correcta2)
        print(incorrecta2)

    else:
        return redirect(url_for('home'))
    return render_template('EditExpo.html', tema=tema, descripcion=descripcion, horario=horario, fecha=fecha, email_autor=email_autor, pregunta1=pregunta1, correcta1=correcta1, incorrecta1=incorrecta1, pregunta2=pregunta2, correcta2=correcta2, incorrecta2=incorrecta2, id_expo=id_expo)

@app.route('/MisExpos')
def MisExpos():
    if session['rol'] == '2' or '1':
        sql = f"""
        SELECT tema, descripcion, horario, fecha FROM `web-demo-evento.db_web_demo.exposiciones` WHERE email_autor = '{session['usuario']}'
        """
        df = bq.query(sql).result().to_dataframe()
        df = df.to_dict('r')
        return render_template('MisExpos.html', df=df)

@app.route('/MisAssists')
def MisAssists():
    sql = f"""
    SELECT tema, descripcion, horario, fecha FROM `web-demo-evento.db_web_demo.asistencias` asistencias INNER JOIN `web-demo-evento.db_web_demo.exposiciones` exposiciones ON asistencias.id_expo = exposiciones.id_expo WHERE email = '{session['usuario']}'
    """
    df = bq.query(sql).result().to_dataframe()
    df = df.to_dict('r')
    return render_template('MisAssists.html', df=df)

@app.route('/actionedit', methods=['POST'])
def actionedit():
    if session['rol'] == '1':
        if request.method == 'POST':
            id_expo = request.form['id_expo']
            print('este es el id_expo', id_expo)
            tema = request.form['tema']
            descripcion = request.form['descripcion']
            horario = request.form['horario']
            if horario[-3:] == ':00':
                horario = horario[:-3]
            else:
                print('todo bien')
            fecha = request.form['fecha']
            email_autor = request.form['email_autor']
            pregunta1 = request.form['pregunta1']
            pregunta2 = request.form['pregunta2']
            correct_preg1 = request.form['correct_preg1']
            correct_preg2 = request.form['correct_preg2']
            incorrect_preg1 = request.form['incorrect_preg1']
            incorrect_preg2 = request.form['incorrect_preg2']

            sql0 = f"""
                UPDATE `web-demo-evento.db_web_demo.exposiciones` SET tema = '{tema}', descripcion = '{descripcion}', horario = '{horario}:00', fecha = '{fecha}', email_autor = '{email_autor}' WHERE id_expo = '{id_expo}';
            """
            bq.query(sql0).result()

            sql = f"""
                DELETE FROM `web-demo-evento.db_web_demo.preguntas` WHERE id_expo = '{ id_expo }'
            """
            bq.query(sql).result()

            sql = f"""
                DELETE FROM `web-demo-evento.db_web_demo.asistencias` WHERE id_expo = '{ id_expo }'
            """
            bq.query(sql).result()

            sql1 = f"""
                INSERT INTO `web-demo-evento.db_web_demo.preguntas` (`id_expo`, `pregunta`, `correcta`, `incorrecta`) VALUES ('{id_expo}', '{pregunta1}', '{correct_preg1}', '{incorrect_preg1}'), ('{id_expo}', '{pregunta2}', '{correct_preg2}', '{incorrect_preg2}');
            """
            bq.query(sql1).result()
    return redirect('InsertProgram')

@app.route('/settings')
def settings():
    # CheckLoginInSession
    if session['usuario']:
        return render_template('settings.html')

@app.route('/asistencias')
def asistencias():
    # CheckLoginInSession
    if session['usuario']:
        sql = f"""
        SELECT id_expo, tema FROM `web-demo-evento.db_web_demo.exposiciones` WHERE asistencia = 'si'
        """
        df = bq.query(sql).result().to_dataframe()
        df = df.to_dict('r')
        return render_template('asistencias.html', df=df)
    else:
        return redirect(url_for('home'))

@app.route('/check', methods=['POST'])
def check():
    if request.method == "POST":
        id_expo = request.form['id_expo']
        print(id_expo)
        sql = f"""
        SELECT pregunta, correcta, incorrecta FROM `web-demo-evento.db_web_demo.preguntas` WHERE id_expo = '{id_expo}'
        """
        df = bq.query(sql).result().to_dataframe()
        df1 = df.transpose()
        df1 = df1.reset_index()
        pregunta1 = df1[0][0]
        p1_alter1 = df1[0][1]
        p1_alter2 = df1[0][2]
        print(pregunta1)
        print(p1_alter1)
        print(p1_alter2)
        if randrange(2) == 1:
            print('suerte')
        else:
            bad = p1_alter1
            p1_alter1 = p1_alter2
            p1_alter2 = bad
            print('variables cambiadas')
            print(p1_alter1)
            print(p1_alter2)
            print('mala suerte')
        pregunta2 = df1[1][0]
        p2_alter1 = df1[1][1]
        p2_alter2 = df1[1][2]
        print(pregunta2)
        print(p2_alter1)
        print(p2_alter2)
        if randrange(2) == 1:
            print('suerte')
        else:
            bad = p2_alter1
            p2_alter1 = p2_alter2
            p2_alter2 = bad
            print('variables cambiadas')
            print(p2_alter1)
            print(p2_alter2)
            print('mala suerte')
        
    return render_template('check.html',pregunta1=pregunta1,pregunta2=pregunta2,p1_alter1=p1_alter1,p1_alter2=p1_alter2,p2_alter1=p2_alter1,p2_alter2=p2_alter2,id_expo=id_expo)

@app.route('/update_asistencias', methods = ['POST'])
def update_asistencias():
    if request.method == "POST":
        id_expo = request.form['id_expo']
        asistencia = request.form['asistencia']
        print('valor de asistencia antes',asistencia)
        if asistencia == 'si':
            asistencia = 'no'
        else:
            asistencia = 'si'
        print('valor de asistencia despues',asistencia)
        sql = f"""
            UPDATE `web-demo-evento.db_web_demo.exposiciones` SET asistencia ='{asistencia}' WHERE id_expo = '{id_expo}'
        """
        bq.query(sql).result()
    return redirect('InsertProgram')

@app.route('/Marcar_asistencia', methods = ['POST'])
def Marcar_asistencia():
    if request.method == "POST":
        id_expo = request.form['id_expo']
        respuesta1 = request.form['respuesta1']
        respuesta2 = request.form['respuesta2']
        sql1 = f"""
            SELECT id_expo FROM`web-demo-evento.db_web_demo.asistencias` WHERE email = '{session['usuario']}' AND id_expo = '{id_expo}'
        """
        df = bq.query(sql1).result().to_dataframe()
        if len(df) == 0:
            sql = f"""
            INSERT INTO `web-demo-evento.db_web_demo.asistencias` (`id_expo`,`email`,`respuesta1`,`respuesta2`) VALUES ('{id_expo}','{session['usuario']}','{respuesta1}','{respuesta2}')
            """
            bq.query(sql).result()
            msg = 'Assists Mark ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            flash(msg)
        else:
            msg = 'Assists Found'
            flash(msg)
    return redirect('asistencias')

if __name__ == '__main__':
    app.run(debug = True)
    
    # configuracion solo para subir al servidor
    # app.run(host='0.0.0.0', port=8080)