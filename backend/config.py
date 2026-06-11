import os
from dotenv import load_dotenv

# Cargar variables desde archivo .env si existe, sobrescribiendo variables de entorno del sistema
load_dotenv(override=True)

class Settings:
    PROJECT_NAME: str = "PST Inventory Management API"
    PROJECT_VERSION: str = "1.0.0"

    # Configuración de base de datos MySQL
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "venvidrio")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", 3306))
    
    # Configuración del servidor de desarrollo
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")

settings = Settings()
