from database import Database
from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from sqlalchemy.orm import relationship

class Usuario(Database):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(30))
    apellidos = Column(String(100))
    usuario = Column(String(100))
    tipo = Column(Integer)
    psw = Column(String(30))
    
    # Agregamos la columna para la relación con la planta
    id_planta = Column(Integer, ForeignKey('plantas.id'))
    planta = relationship('Planta')
    
    acceso = Column(String(5))

class Cliente(Database):
    __tablename__ = 'clientes'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))    

class Planta(Database):
    __tablename__ = 'plantas'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    ubicacion = Column(String(100))
    
    id_empresa = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    empresa = relationship('Cliente')
    
class Extintor(Database):
    __tablename__ = 'extintores'

    id =  Column(Integer, primary_key=True)
    n_serie =  Column(Integer)
    tipo = Column(String(8))
    capacidad = Column(Float(3))
    ubicacion = Column(String(40))
    ph_def = Column(String(7))

    id_planta = Column(Integer, ForeignKey('plantas.id'), nullable=False)
    planta = relationship('Planta')

class Mantenimiento(Database):
    __tablename__ = 'mantenimientos'
    
    id = Column(Integer, primary_key=True)
    fecha_recarga = Column(Date)
    fecha_prox_recarga = Column(Date)
    manometro = Column(String(10))
    manguera = Column(String(10))
    seguro = Column(String(10))
    recarga = Column(String(10))
    ph = Column(String(10))
    limpieza = Column(String(50))
    
    id_extintor = Column(Integer, ForeignKey('extintores.id'), nullable=False)
    extintor = relationship('Extintor')
   
class Ph(Database):
    __tablename__ = 'ph'

    id = Column(Integer, primary_key=True)
    ph_ant = Column(String(10))
    ph_new = Column(String(10))
    fecha = Column(Date)

    id_extintor = Column(Integer, ForeignKey('extintores.id'), nullable=False)
    extintor = relationship('Extintor')