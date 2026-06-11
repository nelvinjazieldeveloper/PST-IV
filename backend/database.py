import mysql.connector
from mysql.connector import pooling
from mysql.connector.errors import Error
import logging
import os
from config import settings

logger = logging.getLogger("uvicorn.error")

# Intentar crear la base de datos antes de inicializar el pool
def init_db_and_tables():
    try:
        # Conexión temporal sin especificar base de datos para crearla si no existe
        conn = mysql.connector.connect(
            host=settings.MYSQL_HOST,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            port=settings.MYSQL_PORT
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.close()
        conn.close()
        logger.info(f"Base de datos '{settings.MYSQL_DATABASE}' verificada/creada con éxito.")
    except Exception as e:
        logger.warning(f"No se pudo verificar o crear la base de datos desde el backend: {e}. Asegúrate de que MySQL está corriendo.")

    # Conectar y ejecutar el script init.sql para crear y poblar las tablas
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sql_path = os.path.join(base_dir, "database", "init.sql")
        
        if os.path.exists(sql_path):
            conn = mysql.connector.connect(
                host=settings.MYSQL_HOST,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                port=settings.MYSQL_PORT,
                database=settings.MYSQL_DATABASE
            )
            cursor = conn.cursor()
            
            with open(sql_path, "r", encoding="utf-8") as f:
                sql_content = f.read()
                
            # Limpiar comentarios y separar sentencias por ';'
            cleaned_sql = []
            for line in sql_content.split("\n"):
                stripped = line.strip()
                if stripped and not stripped.startswith("--"):
                    cleaned_sql.append(line)
            
            sql_statements = "\n".join(cleaned_sql).split(";")
            
            for statement in sql_statements:
                stmt = statement.strip()
                if stmt:
                    try:
                        cursor.execute(stmt)
                    except Exception as ex:
                        # Loggear pero no bloquear el flujo si ya existen
                        logger.debug(f"Aviso al ejecutar sentencia: {stmt[:60]}... | Detalle: {ex}")
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("Estructura de base de datos Venvidrio inicializada desde init.sql.")
        else:
            logger.warning(f"No se encontró el archivo init.sql en la ruta esperada: {sql_path}")
    except Exception as e:
        logger.error(f"Error al inicializar las tablas de Venvidrio: {e}")

# Ejecutar inicialización preliminar
init_db_and_tables()

# Inicialización del Pool de Conexiones
db_pool = None
try:
    db_pool = pooling.MySQLConnectionPool(
        pool_name="venvidrio_pool",
        pool_size=10,  # Aumentamos a 10 por el volumen de tablas maestras y transacciones
        host=settings.MYSQL_HOST,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE,
        port=settings.MYSQL_PORT
    )
    logger.info("Pool de conexiones de MySQL (Venvidrio) inicializado correctamente.")
except Error as e:
    logger.error(f"Error al inicializar el pool de conexiones de MySQL: {e}")

def get_db_connection():
    """
    Obtiene una conexión limpia desde el pool.
    Se debe usar en un bloque 'with' o cerrarla explícitamente.
    """
    global db_pool
    if db_pool is None:
        try:
            db_pool = pooling.MySQLConnectionPool(
                pool_name="venvidrio_pool",
                pool_size=10,
                host=settings.MYSQL_HOST,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                database=settings.MYSQL_DATABASE,
                port=settings.MYSQL_PORT
            )
            logger.info("Pool de conexiones de MySQL inicializado en reintento.")
        except Error as e:
            raise Exception(f"La base de datos MySQL no está disponible. Error del pool: {e}")
            
    try:
        return db_pool.get_connection()
    except Error as e:
        logger.error(f"Error al obtener conexión del pool: {e}")
        raise Exception(f"Error al conectar con la base de datos: {e}")

def check_db_status() -> bool:
    """Verifica si la base de datos responde a un ping básico."""
    try:
        conn = get_db_connection()
        ping_res = conn.is_connected()
        conn.close()
        return ping_res
    except Exception:
        return False
