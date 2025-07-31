from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///tu_base_de_datos.db"  # Cambia esto a tu URL de base de datos

engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Crear todas las tablas en la base de datos
Base.metadata.create_all(engine)

# Sesión de la base de datos
Session = sessionmaker(bind=engine)
if __name__ == '__main__':
    Base.metadata.create_all(engine)  # Esto creará las tablas
