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

    id_planta = Column(Integer, ForeignKey('plantas.id'), nullable=False)
    planta = relationship('Planta')

class Mantenimiento(Database):
    __tablename__ = 'mantenimientos'
    
    id = Column(Integer, primary_key=True)
    fecha = Column(Date)
    fecha_recarga = Column(Date)
    fecha_prox_recarga = Column(Date)
    manometro = Column(Integer)
    manguera = Column(Integer)
    seguro = Column(Integer)
    recarga = Column(Integer)
    limpieza = Column(Integer)
    ph = Column(String(7))
    señalamiento = Column(Integer)
    estado = Column(Integer)
    Observaciones = Column(String(200))
    
    id_extintor = Column(Integer, ForeignKey('extintores.id'), nullable=False)
    extintor = relationship('Extintor')