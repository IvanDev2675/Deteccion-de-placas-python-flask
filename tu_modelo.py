from sqlalchemy import Column, Integer, String
from tu_base_de_datos import Base  # Importa tu clase Base de SQLAlchemy

class Vehiculo(Base):
    __tablename__ = 'vehiculos'

    id = Column(Integer, primary_key=True)
    placa = Column(String, unique=True)
    nombre_duenio = Column(String)
    edad_duenio = Column(Integer)
    telefono_duenio = Column(String)

    def __repr__(self):
        return f"<Vehiculo(placa='{self.placa}', duenio='{self.nombre_duenio}')>"
