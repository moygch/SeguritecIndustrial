from flask import Flask, render_template, redirect, url_for, request, flash, session, make_response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from flask_session import Session
from sqlalchemy import and_, desc, func
from database import db_session, Database, engine

from fpdf import FPDF

import models

app = Flask(__name__)

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

Database.metadata.create_all(engine)

# Obtiene la fecha y hora del sistema utilizando func.now()
fecha_actual = db_session.query(func.now()).scalar()
print(f"La fecha_actual es : {fecha_actual}")

# Convierte la fecha_actual a cadena
fecha_actual_str = fecha_actual.strftime("%Y-%m-%d %H:%M:%S")

# Extrae el año
año = fecha_actual_str[:4]

# Extrae el mes
mes = fecha_actual_str[5:7]
mes_actual = int(mes)



#creamos una lista para acceder a los meses
meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
# accede al mes seleccionado
mes_seleccionado = meses[mes_actual]

# Imprime el resultado)

# años para prueba de ph
cant_años = 5
nueva_fecha = int(año) -  cant_años

buscar = f"{nueva_fecha}-{mes_actual}"

print(buscar)



print(f"la fecha convertida es {año} {mes_seleccionado}")


@app.get('/')
def login():
    return render_template('/login/login.html')

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
                    return redirect(url_for('dashboard'))
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

@app.post('/nuevo-extintor-planta')
def nuevo_extintor_planta():
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

    return redirect(url_for('extintores_plantas', id = id_planta))

@app.post('/extintor_planta/<id>/update')
def update_extintor_planta(id):
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

    return redirect(url_for('extintores_plantas', id = id_planta))

@app.get('/extintor_planta/<id>/delete')
def delete_extintor_planta(id):
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

    return redirect(url_for('extintores_plantas', id = extintor.id_planta))

@app.route('/extintores_ph/<id>')
def extintores_ph_planta(id):
    sesion_iniciada = session.get("usuario_id", False)
    sesion_user = session.get('usuario_id', None)
    user = db_session.query(models.Usuario).get(sesion_user)

    if not sesion_iniciada:
        return redirect(url_for("login"))
    
    extintores = db_session.query(models.Extintor).filter(models.Extintor.ph_def.like(f'{buscar}%')).filter_by(id_planta=id).all()

    for extintor in extintores:
        print(f"{extintor.id} {extintor.n_serie}")


    # Renderizar la plantilla con los extintores que necesitan mantenimiento
    return render_template('/planta/extintores_mantenimiento_ph.html', user = user, extintores = extintores)

@app.get('/ver/<id>')
def ver(id):

    extintor = db_session.query(models.Extintor).filter_by(n_serie = id)

    for extintor in extintor:
        
    
        return f"Este es el exintor{extintor.id}{extintor.n_serie} {extintor.capacidad}KG {extintor.planta.empresa.nombre} {extintor.planta.nombre} {extintor.planta.ubicacion}"

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
@app.route('/generar_pdf/')
def generar_pdf():
    class MyPDF(FPDF):
        def header(self):
            # Encabezado
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Informe', 0, 1, 'C')

        def chapter_title(self, title):
            # Título del capítulo
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, title, 0, 1, 'L')
            self.ln(4)

        def chapter_body(self, body):
            # Cuerpo del capítulo
            self.set_font('Arial', '', 12)
            self.multi_cell(0, 10, body)

    # Crear instancia de la clase MyPDF
    pdf = MyPDF()

    # Agregar página
    pdf.add_page()

    # Título del informe
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Mi Informe', 0, 1, 'C')
    pdf.ln(10)

    # Tabla con encabezado
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(30, 10, 'Nombre', 1)
    pdf.cell(30, 10, 'Ubicación', 1)
    pdf.ln()

    # Datos de ejemplo
    data = [
        ('Planta 1', 'Ubicación 1'),
        ('Planta 2', 'Ubicación 2'),
        # Puedes agregar más filas según tus datos
    ]

    pdf.set_font('Arial', '', 12)

    for row in data:
        pdf.cell(30, 10, row[0], 1)
        pdf.cell(30, 10, row[1], 1)
        pdf.ln()
        
    
    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=informe.pdf'

    return response

app.run("0.0.0.0",8000,debug=True)