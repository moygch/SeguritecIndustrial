from flask import Flask, render_template, redirect, url_for, request, flash, session, make_response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from flask_session import Session
from sqlalchemy import and_, desc
from database import db_session, Database, engine
from pdfkit import *
from datetime import datetime, timedelta

import models
import locale

# Configurar el idioma a español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

app = Flask(__name__)

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

Database.metadata.create_all(engine)



# Obtiene la fecha y hora del sistema utilizando func.now()
# fecha_actual = db_session.query(func.now()).scalar()
fecha_actual = datetime.today()
print(f"La fecha_actual es : {fecha_actual}")

# Convierte la fecha_actual a cadena
fecha_actual_str = fecha_actual.strftime("%b-%Y-%d %H:%M:%S")
print(f"{fecha_actual_str}")
# fecha_actual_str = fecha_actual.strftime("%Y-%m-%d")


# Extrae el año
año = datetime.now().year


mes = datetime.now().month
print(f"el mes actual es {mes}")



#creamos una lista para acceder a los meses
meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
# accede al mes seleccionado
mes_seleccionado = meses[mes]

# Imprime el resultado)

# años para prueba de ph
cant_años = 5
nueva_fecha = int(año) -  cant_años

buscar = f"{año}-{mes}"

print(buscar)

fecha = f"{mes_seleccionado} de {año}"

# print(fecha)

@app.get('/')
def login():
    return render_template('/login/login.html')

@app.get('/man')
def man():
    return render_template('fomr.html')

@app.post('/post_man')
def post_man():
    man = request.form['manguera']
    fecha = fecha_actual_str

    return f"el valor del checkbox es {man} {fecha}"

@app.post('/login_post')
def login_post(): 
    user = request.form['user']
    password = request.form['password']                            
    if (user == None or user == '') or (password == None or password == ''):
        flash(('warning', 'Error todos los campos son requeridos'))
        return redirect(url_for('login'))
    else:
        usuario = db_session.query(models.Usuario).options(joinedload(models.Usuario.planta)).filter(
            and_(models.Usuario.usuario == user, models.Usuario.psw == password)).first()
        if usuario is None:
            flash(('error', 'Usuario y/o contraseña incorrectos!'))
            return redirect(url_for('login'))
        else:
            session['usuario_id'] = usuario.id
            # Verifica si el usuario tiene acceso al sistema
            if usuario.acceso == 'True':
                # Verifica el rol del usuario que inició sesión
                if usuario.tipo == 0:
                    # El usuario es administrador
                    print("El usuario es administrador")
                    return redirect(url_for('dashboard'))
                elif usuario.tipo == 1:
                    # El usuario es administrador de planta
                    print(f'El usuario es administrador de planta')
                    return redirect(url_for('dashboard_planta',))
                elif usuario.tipo == 2:
                    # El usuario es técnico
                    print("El usuario es técnico")
                    return redirect(url_for('dashboard_tenico'))
            elif usuario.acceso == 'False':
                flash(('error', 'El usuario no tiene acceso'))
                return redirect(url_for('login'))

@app.post('/login_registro')
def login_registro_post():
    nombre = request.form['nombre']
    apellidos = request.form['apellidos']
    usuario = request.form['usuario']
    tipo = request.form['tipo']
    psw = request.form['psw']

    # Verificar si el usuario ya existe
    usuario_existente = db_session.query(models.Usuario).filter_by(usuario=usuario).first()

    if usuario_existente:
        flash(('error', 'El usuario ya existe. Por favor, elige otro nombre de usuario.'))
    else:
        nuevo_registro_usuario = models.Usuario(
            nombre=nombre,
            apellidos=apellidos,
            usuario=usuario,
            tipo=tipo,
            psw=psw,
            acceso='False'
        )
        try:
            db_session.add(nuevo_registro_usuario)
            db_session.commit()
            flash(('success', 'Usuario registrado de manera exitosa'))
        except SQLAlchemyError as e:
            db_session.rollback()
            print('Error al registrar usuario: {}'.format(str(e)))
            flash(('Error al registrar usuario. Por favor, inténtalo de nuevo.', 'error'))
        finally:
            db_session.close()

    return redirect(url_for('login'))

# --------------------------PARTE ADMINISTRADOR GENERAL ---------------------------------------------
@app.get('/dashboard')
def dashboard():
    sesion_iniciada = session.get("usuario_id", False)
    sesion_user = session.get('usuario_id', None)
    user = db_session.query(models.Usuario).get(sesion_user)

    if not sesion_iniciada:
        return redirect(url_for("login"))
    
    clientes = db_session.query(models.Cliente).all()
    num_extintores = db_session.query(models.Extintor).count()
    
    return render_template('/admin/dashboard.html', clientes = clientes, user = user, num_extintores = num_extintores)

# -------------------------- RUTAS PARA USUARIOS ----------------------------
@app.get('/usuarios')
def usuarios():
    sesion_iniciada = session.get("usuario_id", False)
    sesion_user = session.get('usuario_id', None)
    user = db_session.query(models.Usuario).get(sesion_user)

    if not sesion_iniciada:
        print('no accesedio al dashboard')
        return redirect(url_for("login"))

    usuarios = db_session.query(models.Usuario).all()
    return render_template('/admin/usuarios.html', usuarios = usuarios, user = user, db_session = db_session, models = models)

@app.post('/usuario_registro')
def usuario_registro_post():
    usuario_id = session.get('usuario_id', False)

    if not usuario_id:
        return redirect(url_for('login'))

    nombre = request.form['nombre']
    apellidos = request.form['apellidos']
    usuario = request.form['usuario']
    tipo = request.form['tipo']
    psw = request.form['psw']

    # Verificar si el usuario ya existe
    usuario_existente = db_session.query(models.Usuario).filter_by(usuario=usuario).first()

    if usuario_existente:
        flash(('El usuario ya existe. Por favor, elige otro nombre de usuario.', 'error'))
    else:
        nuevo_registro_usuario = models.Usuario(
            nombre=nombre,
            apellidos=apellidos,
            usuario=usuario,
            tipo=tipo,
            psw=psw,
            acceso='False'
        )

        try:
            db_session.add(nuevo_registro_usuario)
            db_session.commit()
            flash(('Usuario agregado de manera exitosa', 'success'))
        except SQLAlchemyError as e:
            db_session.rollback()
            print('Error al agregar usuario: {}'.format(str(e)))
            flash(('Error al agregar usuario. Por favor, inténtalo de nuevo.', 'error'))
        finally:
            db_session.close()

    return redirect(url_for('usuarios'))

@app.get('/usuarios/<id>/delete')
def delete_usuario(id):
    usuario_id = session.get('usuario_id', False)

    if not usuario_id:
        return redirect(url_for('login'))

    usuario = db_session.query(models.Usuario).get(id)

    if usuario == None:
        return "No encontrado",404
    
    try:
        db_session.delete(usuario)
        db_session.commit()
        flash(('Usuario eliminado de manera exitosa', 'success'))

    except SQLAlchemyError as e:
        db_session.rollback()
        print('Error al agregar usuario: {}'.format(str(e)))
    finally:
        db_session.close()

    return redirect(url_for('usuarios'))

@app.post('/usuarios/<id>/update')
def update_usuario(id):
    sesion_iniciada = session.get("usuario_id", False)

    if not sesion_iniciada:
        return redirect(url_for("login"))

    usuario = db_session.query(models.Usuario).get(id)

    nombre = request.form['nombre_act']
    apellidos = request.form['apellidos_act']
    usuario_new = request.form['usuario_act']
    tipo = request.form['tipo_act']
    acceso = request.form['acceso']
    planta_acceso = request.form['planta_acceso']
    
    if nombre != None and nombre != '':
        usuario.nombre = nombre

    if apellidos != None and apellidos != '':
        usuario.apellidos = apellidos

    if usuario_new != None and usuario_new !='':
        usuario.usuario = usuario_new
    
    if tipo != None and tipo != '':
        usuario.tipo = tipo

    if acceso != None and acceso != '':
        usuario.acceso = acceso
    
    if planta_acceso != None and planta_acceso != '':
        usuario.id_planta = planta_acceso

    try:
        db_session.add(usuario)
        db_session.commit()
        flash(('Usuario actualizado de manera exitosa', 'success'))

    except SQLAlchemyError as e:
        db_session.rollback()
        print('Error al actualizar usuario: {}'.format(str(e)))
    finally:
        db_session.close()

    return redirect(url_for('usuarios'))

@app.get('/dashboard/plantas')
def plantas():
    sesion_iniciada = session.get("usuario_id", False)
    sesion_user = session.get('usuario_id', None)
    user = db_session.query(models.Usuario).get(sesion_user)

    if not sesion_iniciada:
        return redirect(url_for("login"))
    
    plantas = db_session.query(models.Planta).all()
    clientes = db_session.query(models.Cliente).all()
    return render_template('/admin/plantas.html', plantas = plantas, clientes = clientes, user = user)

# ------------------------ RUTAS PARA PLANTAS -----------------------

@app.get('/ver_detalles')
def ver_detalles():
    sesion_iniciada = session.get("usuario_id", False)
    sesion_user = session.get('usuario_id', None)
    user = db_session.query(models.Usuario).get(sesion_user)

    if not sesion_iniciada:
        return redirect(url_for("login"))
    
    return render_template('/admin/ver_detalles.html', user = user)

@app.get('/planta/<id>')
def lista_plantas(id):

    sesion_iniciada = session.get("usuario_id", False)
    sesion_user = session.get('usuario_id', None)
    user = db_session.query(models.Usuario).get(sesion_user)

    if not sesion_iniciada:
        return redirect(url_for("login"))
    
    plantas = db_session.query(models.Planta).all()
    lista = db_session.query(models.Planta).filter_by(id_empresa=id).all()

    return render_template('/admin/datatables.html', lista=lista, plantas=plantas, user=user, db_session = db_session, models = models)

@app.post('/planta/alta')
def planta_post_registro():
    usuario_id = session.get('usuario_id', False)

    if not usuario_id:
        return redirect(url_for('login'))

    nombre = request.form['nombre']
    ubicacion = request.form['ubicacion']
    id_empresa = request.form['id_empresa']

    nueva_planta = models.Planta(
        nombre = nombre,
        ubicacion = ubicacion,
        id_empresa = id_empresa
    )

    try:
        db_session.add(nueva_planta)
        db_session.commit()
        flash(('Planta agregada de manera exitosa', 'success'))
    except SQLAlchemyError as e:
        db_session.rollback()
        print('Error al agregar planta: {}'.format(str(e)))
    finally:
        db_session.close()

    return redirect(url_for('lista_plantas', id = id_empresa))

@app.get('/planta/<id>/delete')
def delete_planta(id):
    usuario_id = session.get('usuario_id', False)

    if not usuario_id:
        return redirect(url_for('login'))

    planta = db_session.query(models.Planta).get(id)

    if planta == None:
        return "No encontrado",404
    
    try:
        db_session.delete(planta)
        db_session.commit()
        flash(('Planta eliminada de manera exitosa', 'success'))

    except SQLAlchemyError as e:
        db_session.rollback()
        print('Error al elimnar planta: {}'.format(str(e)))
    finally:
        db_session.close()

    return redirect(url_for('lista_plantas', id = planta.id_empresa))
    
@app.post('/planta/<id>/update')
def update_planta(id):
    sesion_iniciada = session.get("usuario_id", False)

    if not sesion_iniciada:
        return redirect(url_for("login"))
    
    planta = db_session.query(models.Planta).get(id)

    nombre = request.form['nombre_act']
    ubicacion = request.form['ubicacion_act']
    id_empresa = request.form['id_empresa']
    
    if nombre != None and nombre !='':
        planta.nombre = nombre
    
    if ubicacion != None and ubicacion != '':
        planta.ubicacion = ubicacion
    try:
        db_session.add(planta)
        db_session.commit()
        flash(('Planta actualizada de manera exitosa', 'success'))

    except SQLAlchemyError as e:
        db_session.rollback()
        print('Error al actualizar planta: {}'.format(str(e)))
    finally:
        db_session.close()

    return redirect(url_for('lista_plantas', id = id_empresa))

# -------------------------- RUTAS PARA EXTINTORES ----------------------
@app.get('/planta-extintores/<id>')
def extintores(id):

    sesion_iniciada = session.get("usuario_id", False)
    sesion_user = session.get('usuario_id', None)
    user = db_session.query(models.Usuario).get(sesion_user)

    if not sesion_iniciada:
        return redirect(url_for("login"))
    
    ultimo_registro = db_session.query(models.Extintor).order_by(desc(models.Extintor.n_serie)).first()
    nuevo_extintor = ultimo_registro.n_serie + 1    
    extintores = db_session.query(models.Extintor).filter_by(id_planta=id).all()
    
    return render_template('/admin/datatables-extintores.html', user = user, extintores = extintores, id_planta = id, nuevo_extintor = nuevo_extintor)

@app.post('/nuevo-extintor')
def nuevo_extintor():
    sesion_iniciada = session.get("usuario_id", False)

    if not sesion_iniciada:
        return redirect(url_for("login"))
    
    ultimo_registro = db_session.query(models.Extintor).order_by(desc(models.Extintor.n_serie)).first()
    nuevo_extintor = ultimo_registro.n_serie + 1   

    tipo = request.form['tipo']
    capacidad = request.form['capacidad']
    ubicacion = request.form['ubicacion']
    ph = request.form['ph']
    id_planta = request.form['id_planta']  

    reg_extintor = models.Extintor(
        n_serie = nuevo_extintor,
        tipo = tipo,
        capacidad = capacidad,
        ubicacion = ubicacion,
        ph_def = ph,
        id_planta = id_planta
    )

    try:
        db_session.add(reg_extintor)
        db_session.commit()
        flash(('Extintor agregado de manera exitosa', 'success'))
    except SQLAlchemyError as e:
        db_session.rollback()
        print('Error al agregar extintor: {}'.format(str(e)))
    finally:
        db_session.close()

    return redirect(url_for('extintores', id = id_planta))

@app.post('/extintor/<id>/update')
def update_extintor(id):
    sesion_iniciada = session.get("usuario_id", False)

    if not sesion_iniciada:
        return redirect(url_for("login"))

    extintor = db_session.query(models.Extintor).get(id)

    if not extintor:
        flash(('Extintor no encontrado', 'error'))
        return redirect(url_for('extintores', id=id_planta))

    n_serie_nuevo = request.form['n_serie']
    tipo = request.form['tipo']
    capacidad = request.form['capacidad']
    ubicacion = request.form['ubicacion']
    ph = request.form['ph']
    id_planta = request.form['id_planta']

    # Verifica si el nuevo número de serie coincide con otro extintor
    extintor_existente = db_session.query(models.Extintor).filter_by(n_serie=n_serie_nuevo).first()

    if extintor_existente and extintor_existente.id != id:
        flash(('El nuevo número de serie coincide con otro extintor, no se puede actualizar', 'warning'))
    else:
        # Actualiza los campos directamente
        if n_serie_nuevo != None and n_serie_nuevo != '':
            extintor.n_serie = n_serie_nuevo
        extintor.tipo = tipo
        extintor.capacidad = capacidad
        extintor.ubicacion = ubicacion
        extintor.ph_def = ph

        try:
            db_session.commit()
            flash(('Extintor actualizado de manera exitosa', 'success'))
        except SQLAlchemyError as e:
            db_session.rollback()
            flash(('Error al actualizar extintor: {}'.format(str(e)), 'error'))
        finally:
            db_session.close()

    return redirect(url_for('extintores', id=id_planta))

@app.get('/extintor/<id>/delete')
def delete_extintor(id):
    usuario_id = session.get('usuario_id', False)

    if not usuario_id:
        return redirect(url_for('login'))

    extintor = db_session.query(models.Extintor).get(id)

    if extintor == None:
        return "No encontrado",404
    
    try:
        db_session.delete(extintor)
        db_session.commit()
        flash(('Extintor eliminado de manera exitosa', 'success'))

    except SQLAlchemyError as e:
        db_session.rollback()
        print('Error al elimnar extintor: {}'.format(str(e)))
    finally:
        db_session.close()

    return redirect(url_for('extintores', id = extintor.id_planta))

@app.get('/mantenimientos')
def manteniminetos():
    return f"aqui van los matenimientos"

# ------------------------ ADMINISTRADOR DE PLANTAS --------------------
@app.get('/dashboard-admin-planta')
def dashboard_planta():
    sesion_iniciada = session.get("usuario_id", False)
    sesion_user = session.get('usuario_id', None)
    user = db_session.query(models.Usuario).get(sesion_user)

    if not sesion_iniciada:
        return redirect(url_for("login"))
    
    num_extintores = db_session.query(models.Extintor).filter_by(id_planta = user.id_planta).count()
    extintores = db_session.query(models.Extintor).filter_by(id_planta=user.id_planta).all()

    num_extintores = len(extintores)
    co2 = sum(1 for extintor in extintores if extintor.tipo == 'CO2')
    pqs = sum(1 for extintor in extintores if extintor.tipo == 'PQS')
    h2o = sum(1 for extintor in extintores if extintor.tipo == 'H2O')
    clean = sum(1 for extintor in extintores if extintor.tipo == 'CLEAN')

    planta = db_session.query(models.Planta).filter_by(id = user.id_planta)  
    
    return render_template('/planta/dashboard_plantas.html', user = user, num_extintores = num_extintores,
                            planta = planta, co2 = co2, pqs = pqs, h2o = h2o, clean = clean)

@app.get('/planta-extintores-plantas/<id>')
def extintores_plantas(id):

    sesion_iniciada = session.get("usuario_id", False)
    sesion_user = session.get('usuario_id', None)
    user = db_session.query(models.Usuario).get(sesion_user)

    if not sesion_iniciada:
        return redirect(url_for("login"))
    
    ultimo_registro = db_session.query(models.Extintor).order_by(desc(models.Extintor.n_serie)).first()
    nuevo_extintor = ultimo_registro.n_serie + 1    
    extintores = db_session.query(models.Extintor).filter_by(id_planta=id).all()
    
    return render_template('/planta/datatables-extintores_plantas.html', user = user, 
                           extintores = extintores, id_planta = id, nuevo_extintor = nuevo_extintor)


@app.get('/extintores_revision/<id>')
def revision_mensual_planta(id):
    sesion_iniciada = session.get("usuario_id", False)
    sesion_user = session.get('usuario_id', None)
    user = db_session.query(models.Usuario).get(sesion_user)

    if not sesion_iniciada:
        return redirect(url_for("login"))
    
    extintores = db_session.query(models.Mantenimiento).join(models.Extintor).filter(models.Mantenimiento.fecha.like(f'2024-01%')).filter(models.Extintor.id_planta == id).all()

    fecha_recarga_formateada = None
    fecha_prox_formateada = None

    for extintor in extintores:
        fecha_recarga_formateada = extintor.fecha_recarga.strftime("%b-%y")
        fecha_prox_formateada = extintor.fecha_prox_recarga.strftime("%b-%y")
        print(f"{extintor.id} {extintor.extintor.n_serie} {fecha_recarga_formateada}")

    return render_template('/planta/extintores_mantenimiento_ph.html', user = user,  fecha = fecha, extintores = extintores,
                           fecha_recarga_formateada = fecha_recarga_formateada, fecha_prox_formateada = fecha_prox_formateada)

# ------------------- TECNICOS --------------
@app.get('/dashboard_tecnico')
def dashboard_tenico():
    sesion_iniciada = session.get("usuario_id", False)
    sesion_user = session.get('usuario_id', None)
    user = db_session.query(models.Usuario).get(sesion_user)

    extintores = db_session.query(models.Extintor).filter_by(id_planta=user.id_planta).all()

    num_extintores = len(extintores)
    co2 = sum(1 for extintor in extintores if extintor.tipo == 'CO2')
    pqs = sum(1 for extintor in extintores if extintor.tipo == 'PQS')
    h2o = sum(1 for extintor in extintores if extintor.tipo == 'H2O')
    clean = sum(1 for extintor in extintores if extintor.tipo == 'ClEAN')

    if not sesion_iniciada:
        return redirect(url_for("login"))
    
    return render_template('/tecnicos/dashboard_tecnicos.html', user = user, num_extintores = num_extintores,
                           co2 = co2, pqs = pqs, h2o = h2o, clean = clean)

@app.get('/tecnico-extintores-plantas/<id>')
def extintores_plantas_tecnico(id):

    sesion_iniciada = session.get("usuario_id", False)
    sesion_user = session.get('usuario_id', None)
    user = db_session.query(models.Usuario).get(sesion_user)

    if not sesion_iniciada:
        return redirect(url_for("login"))
    
    ultimo_registro = db_session.query(models.Extintor).order_by(desc(models.Extintor.n_serie)).first()
    nuevo_extintor = ultimo_registro.n_serie + 1    
    extintores = db_session.query(models.Extintor).filter_by(id_planta=id).all()
    
    return render_template('/tecnicos/datatables-extintores.html', user = user, 
                           extintores = extintores, id_planta = id, nuevo_extintor = nuevo_extintor)

@app.post('/revision_mensual')
def revision_post():
    sesion_iniciada = session.get("usuario_id", False)

    if not sesion_iniciada:
        return redirect(url_for("login"))
    
    fecha_recarga = request.form.get('fecha_recarga')
    fecha_prox = request.form['recarga_new']                               
    manometro = request.form['manometro']
    manguera = request.form['manguera']
    seguro = request.form['estado']
    estado = request.form['estado']
    recarga = request.form['recarga']
    señalamiento = request.form['señalamiento']
    ph = request.form['ph']
    limpieza = request.form['limpieza']
    observaciones = request.form['observaciones']
    id_extintor = request.form['id_extintor']
    id_planta = request.form['id_planta']
    n_serie = request.form['n_serie']


    # Número de serie a verificar
    numero_serie_a_verificar = int(n_serie)

    # Realiza la consulta
    extintores_del_mes = (
        db_session.query(models.Mantenimiento)
        .filter(models.Mantenimiento.fecha.like(f'{buscar}%')).all()
    )

    # # Verifica si el número de serie coincide
    numero_serie_coincide = any(extintor.extintor.n_serie == numero_serie_a_verificar for extintor in extintores_del_mes)

    if numero_serie_coincide:
        flash(('El número de serie coincide con un extintor del mes actual.', 'warning'))
        return redirect(url_for('extintores_plantas_tecnico', id = id_planta))
    else:        
        revision = models.Mantenimiento(
            fecha = datetime.today(),
            fecha_recarga = fecha_recarga,
            fecha_prox_recarga = fecha_prox,
            manometro = manometro,
            manguera = manguera,
            seguro = seguro,
            recarga = recarga,
            limpieza = limpieza,
            ph = ph,
            señalamiento = señalamiento,
            estado = estado,
            Observaciones = observaciones,
            id_extintor = id_extintor
        )

        try:
            db_session.add(revision)
            db_session.commit()
            flash(('Revision realizada de manera exitosa', 'success'))
        except SQLAlchemyError as e:
            db_session.rollback()
            print('Error al revisar extintor: {}'.format(str(e)))
        finally:
            db_session.close()

        return redirect(url_for('extintores_plantas_tecnico', id = id_planta))
    
@app.get('/extintores_revision_tecnico/<id>')
def revision_mensual_tecnico(id):
    sesion_iniciada = session.get("usuario_id", False)
    sesion_user = session.get('usuario_id', None)
    user = db_session.query(models.Usuario).get(sesion_user)

    if not sesion_iniciada:
        return redirect(url_for("login"))
    
    extintores = db_session.query(models.Mantenimiento).join(models.Extintor).filter(models.Mantenimiento.fecha.like(f'2024-01%')).filter(models.Extintor.id_planta == id).all()

    fecha_recarga_formateada = None
    fecha_prox_formateada = None

    for extintor in extintores:
        fecha_recarga_formateada = extintor.fecha_recarga.strftime("%b-%y")
        fecha_prox_formateada = extintor.fecha_prox_recarga.strftime("%b-%y")
        print(f"{extintor.id} {extintor.extintor.n_serie} {fecha_recarga_formateada}")

    return render_template('/tecnicos/extintores_mantenimiento_ph.html', user = user,  fecha = fecha, extintores = extintores,
                           fecha_recarga_formateada = fecha_recarga_formateada, fecha_prox_formateada = fecha_prox_formateada)

# --------------------MODULO DE CERRAR SESION PARA TODOS ----------------------------
@app.get('/logout')
def logout():
    try:
        # Elimina todas las claves de la sesión
        session.clear()

        # Invalida la cookie de sesión en el cliente
        response = redirect(url_for('login'))

        # Configura la cookie de sesión para que expire inmediatamente
        response.set_cookie('session', '', expires = 0)

        print('¡Has cerrado sesión exitosamente!', 'success')
        return response
    except Exception as e:
        # Manejar cualquier excepción que pueda ocurrir al cerrar la sesión
        print(f'Error al cerrar sesión: {str(e)}', 'error')
        return redirect(url_for('login'))



# -------------------------------- Reportes PDF ----------------------------------

app.run("0.0.0.0",8000,debug=True)