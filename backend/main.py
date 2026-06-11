from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import mysql.connector

from config import settings
from database import get_db_connection, check_db_status
from schemas import (
    Usuario, UsuarioCreate, UsuarioUpdate,
    Turno, TurnoCreate, TurnoUpdate,
    Maquina, MaquinaCreate, MaquinaUpdate,
    Seccion, SeccionCreate, SeccionUpdate,
    Producto, ProductoCreate, ProductoUpdate,
    Molde, MoldeCreate, MoldeUpdate,
    Premolde, PremoldeCreate, PremoldeUpdate,
    CatalogoDefectos, CatalogoDefectosCreate, CatalogoDefectosUpdate,
    Inspector, InspectorCreate, InspectorUpdate,
    TipoParada, TipoParadaCreate, TipoParadaUpdate,
    Produccion, ProduccionCreate, ProduccionUpdate,
    Inspeccion, InspeccionCreate, InspeccionUpdate,
    DetalleInspeccion, DetalleInspeccionCreate, DetalleInspeccionUpdate,
    AccionCorrectiva, AccionCorrectivaCreate, AccionCorrectivaUpdate,
    Parada, ParadaCreate, ParadaUpdate,
    ServerStatus,
    LoginRequest
)

app = FastAPI(
    title="Venvidrio - API Zona Caliente",
    version="2.0.0",
    description="API REST para el control de producción, inspección y paradas en Zona Caliente de Venvidrio."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- GENERAL: ESTATUS DE SISTEMA ---
@app.get("/api/status", response_model=ServerStatus, tags=["Sistema"])
def get_status():
    db_ok = check_db_status()
    return {
        "status": "online",
        "db_connected": db_ok,
        "version": "2.0.0",
        "project_name": "Venvidrio Zona Caliente API",
        "timestamp": datetime.now()
    }

@app.get("/api/init-data", tags=["Sistema"])
def get_init_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Usuarios
        cursor.execute("SELECT id_usuario, nombre, apellido, usuario, cargo, rol, estado, fecha_registro FROM usuarios ORDER BY id_usuario DESC")
        usuarios = cursor.fetchall()

        # 2. Turnos
        cursor.execute("SELECT id_turno, codigo_turno, CAST(hora_inicio AS CHAR) as hora_inicio, CAST(hora_fin AS CHAR) as hora_fin, descripcion FROM turnos")
        turnos = cursor.fetchall()

        # 3. Maquinas
        cursor.execute("SELECT * FROM maquinas ORDER BY codigo")
        maquinas = cursor.fetchall()

        # 4. Secciones
        cursor.execute("""
            SELECT s.id_seccion, s.id_maquina, s.numero_seccion, s.estado, m.codigo AS maquina_codigo 
            FROM secciones s
            JOIN maquinas m ON s.id_maquina = m.id_maquina
            ORDER BY m.codigo, s.numero_seccion
        """)
        secciones = cursor.fetchall()

        # 5. Productos
        cursor.execute("SELECT * FROM productos ORDER BY codigo_producto")
        productos = cursor.fetchall()

        # 6. Catalogo Defectos
        cursor.execute("SELECT * FROM catalogo_defectos ORDER BY codigo_defecto")
        catalogo_defectos = cursor.fetchall()

        # 7. Inspectores
        cursor.execute("SELECT * FROM inspectores ORDER BY cedula")
        inspectores = cursor.fetchall()

        # 8. Tipos Paradas
        cursor.execute("SELECT * FROM tipos_paradas ORDER BY nombre")
        tipos_paradas = cursor.fetchall()

        return {
            "usuarios": usuarios,
            "turnos": turnos,
            "maquinas": maquinas,
            "secciones": secciones,
            "productos": productos,
            "catalogo_defectos": catalogo_defectos,
            "inspectores": inspectores,
            "tipos_paradas": tipos_paradas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cargando datos iniciales: {e}")
    finally:
        cursor.close()
        conn.close()


@app.post("/api/auth/login", tags=["Autenticación"])
def login(data: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Buscar el usuario
        query = "SELECT id_usuario, nombre, apellido, usuario, clave, cargo, rol, estado FROM usuarios WHERE usuario = %s"
        cursor.execute(query, (data.usuario,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos."
            )
            
        if user["estado"] != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario se encuentra inactivo. Contacte al administrador."
            )
            
        # Verificación directa de clave (apropiado para piloto local con semillas)
        if user["clave"] != data.clave:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos."
            )
            
        # Retornar los detalles del usuario autenticado sin la contraseña
        return {
            "id_usuario": user["id_usuario"],
            "nombre": user["nombre"],
            "apellido": user["apellido"],
            "usuario": user["usuario"],
            "rol": user["rol"],
            "cargo": user["cargo"]
        }
    finally:
        cursor.close()
        conn.close()


# --- FUNCIONES AUXILIARES PARA CRUD GENÉRICO ---
def get_one_or_404(table: str, id_col: str, id_val: int, custom_select: str = None) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = custom_select or f"SELECT * FROM {table} WHERE {id_col} = %s"
        cursor.execute(query, (id_val,))
        res = cursor.fetchone()
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro no encontrado en '{table}' con {id_col}={id_val}."
            )
        return res
    finally:
        cursor.close()
        conn.close()

def delete_or_404(table: str, id_col: str, id_val: int):
    # Validar que exista primero
    get_one_or_404(table, id_col, id_val)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {table} WHERE {id_col} = %s", (id_val,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo eliminar el registro de {table}: {e}"
        )
    finally:
        cursor.close()
        conn.close()


# --- CRUD: USUARIOS ---
@app.get("/api/usuarios", response_model=List[Usuario], tags=["Usuarios"])
def list_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_usuario, nombre, apellido, usuario, cargo, rol, estado, fecha_registro FROM usuarios ORDER BY id_usuario DESC")
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.get("/api/usuarios/{id_val}", response_model=Usuario, tags=["Usuarios"])
def get_usuario(id_val: int):
    return get_one_or_404("usuarios", "id_usuario", id_val)

@app.post("/api/usuarios", response_model=Usuario, status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
def create_usuario(data: UsuarioCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, apellido, usuario, clave, cargo, rol, estado) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (data.nombre, data.apellido, data.usuario, data.clave, data.cargo, data.rol, data.estado)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT id_usuario, nombre, apellido, usuario, cargo, rol, estado, fecha_registro FROM usuarios WHERE id_usuario = %s", (new_id,))
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear: {e}")
    finally:
        cursor.close()
        conn.close()

@app.put("/api/usuarios/{id_val}", response_model=Usuario, tags=["Usuarios"])
def update_usuario(id_val: int, data: UsuarioUpdate):
    # Verificar existencia
    get_one_or_404("usuarios", "id_usuario", id_val)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        data_dict = data.model_dump(exclude_unset=True)
        if data_dict:
            fields = [f"{k} = %s" for k in data_dict.keys()]
            values = list(data_dict.values()) + [id_val]
            cursor.execute(f"UPDATE usuarios SET {', '.join(fields)} WHERE id_usuario = %s", tuple(values))
            conn.commit()
        cursor.execute("SELECT id_usuario, nombre, apellido, usuario, cargo, rol, estado, fecha_registro FROM usuarios WHERE id_usuario = %s", (id_val,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/usuarios/{id_val}", status_code=status.HTTP_204_NO_CONTENT, tags=["Usuarios"])
def delete_usuario(id_val: int):
    delete_or_404("usuarios", "id_usuario", id_val)


# --- CRUD: TURNOS ---
@app.get("/api/turnos", response_model=List[Turno], tags=["Turnos"])
def list_turnos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_turno, codigo_turno, CAST(hora_inicio AS CHAR) as hora_inicio, CAST(hora_fin AS CHAR) as hora_fin, descripcion FROM turnos")
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.get("/api/turnos/{id_val}", response_model=Turno, tags=["Turnos"])
def get_turno(id_val: int):
    custom = "SELECT id_turno, codigo_turno, CAST(hora_inicio AS CHAR) as hora_inicio, CAST(hora_fin AS CHAR) as hora_fin, descripcion FROM turnos WHERE id_turno = %s"
    return get_one_or_404("turnos", "id_turno", id_val, custom_select=custom)

@app.post("/api/turnos", response_model=Turno, status_code=status.HTTP_201_CREATED, tags=["Turnos"])
def create_turno(data: TurnoCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO turnos (codigo_turno, hora_inicio, hora_fin, descripcion) VALUES (%s, %s, %s, %s)",
            (data.codigo_turno, data.hora_inicio, data.hora_fin, data.descripcion)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        custom = "SELECT id_turno, codigo_turno, CAST(hora_inicio AS CHAR) as hora_inicio, CAST(hora_fin AS CHAR) as hora_fin, descripcion FROM turnos WHERE id_turno = %s"
        return get_one_or_404("turnos", "id_turno", new_id, custom_select=custom)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.put("/api/turnos/{id_val}", response_model=Turno, tags=["Turnos"])
def update_turno(id_val: int, data: TurnoUpdate):
    get_one_or_404("turnos", "id_turno", id_val)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        data_dict = data.model_dump(exclude_unset=True)
        if data_dict:
            fields = [f"{k} = %s" for k in data_dict.keys()]
            values = list(data_dict.values()) + [id_val]
            cursor.execute(f"UPDATE turnos SET {', '.join(fields)} WHERE id_turno = %s", tuple(values))
            conn.commit()
        cursor.close()
        custom = "SELECT id_turno, codigo_turno, CAST(hora_inicio AS CHAR) as hora_inicio, CAST(hora_fin AS CHAR) as hora_fin, descripcion FROM turnos WHERE id_turno = %s"
        return get_one_or_404("turnos", "id_turno", id_val, custom_select=custom)
    finally:
        conn.close()

@app.delete("/api/turnos/{id_val}", status_code=status.HTTP_204_NO_CONTENT, tags=["Turnos"])
def delete_turno(id_val: int):
    delete_or_404("turnos", "id_turno", id_val)


# --- CRUD: MÁQUINAS ---
@app.get("/api/maquinas", response_model=List[Maquina], tags=["Máquinas"])
def list_maquinas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM maquinas ORDER BY codigo")
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.get("/api/maquinas/{id_val}", response_model=Maquina, tags=["Máquinas"])
def get_maquina(id_val: int):
    return get_one_or_404("maquinas", "id_maquina", id_val)

@app.post("/api/maquinas", response_model=Maquina, status_code=status.HTTP_201_CREATED, tags=["Máquinas"])
def create_maquina(data: MaquinaCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO maquinas (codigo, descripcion, cantidad_secciones, estado) VALUES (%s, %s, %s, %s)",
            (data.codigo, data.descripcion, data.cantidad_secciones, data.estado)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM maquinas WHERE id_maquina = %s", (new_id,))
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/maquinas/{id_val}", response_model=Maquina, tags=["Máquinas"])
def update_maquina(id_val: int, data: MaquinaUpdate):
    get_one_or_404("maquinas", "id_maquina", id_val)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        data_dict = data.model_dump(exclude_unset=True)
        if data_dict:
            fields = [f"{k} = %s" for k in data_dict.keys()]
            values = list(data_dict.values()) + [id_val]
            cursor.execute(f"UPDATE maquinas SET {', '.join(fields)} WHERE id_maquina = %s", tuple(values))
            conn.commit()
        cursor.execute("SELECT * FROM maquinas WHERE id_maquina = %s", (id_val,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/maquinas/{id_val}", status_code=status.HTTP_204_NO_CONTENT, tags=["Máquinas"])
def delete_maquina(id_val: int):
    delete_or_404("maquinas", "id_maquina", id_val)


# --- CRUD: SECCIONES ---
@app.get("/api/secciones", response_model=List[Seccion], tags=["Secciones"])
def list_secciones():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # JOIN para traer el código de la máquina
    cursor.execute("""
        SELECT s.id_seccion, s.id_maquina, s.numero_seccion, s.estado, m.codigo AS maquina_codigo 
        FROM secciones s
        JOIN maquinas m ON s.id_maquina = m.id_maquina
        ORDER BY m.codigo, s.numero_seccion
    """)
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.get("/api/secciones/{id_val}", response_model=Seccion, tags=["Secciones"])
def get_seccion(id_val: int):
    custom = """
        SELECT s.id_seccion, s.id_maquina, s.numero_seccion, s.estado, m.codigo AS maquina_codigo 
        FROM secciones s
        JOIN maquinas m ON s.id_maquina = m.id_maquina
        WHERE s.id_seccion = %s
    """
    return get_one_or_404("secciones", "id_seccion", id_val, custom_select=custom)

@app.post("/api/secciones", response_model=Seccion, status_code=status.HTTP_201_CREATED, tags=["Secciones"])
def create_seccion(data: SeccionCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO secciones (id_maquina, numero_seccion, estado) VALUES (%s, %s, %s)",
            (data.id_maquina, data.numero_seccion, data.estado)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        custom = """
            SELECT s.id_seccion, s.id_maquina, s.numero_seccion, s.estado, m.codigo AS maquina_codigo 
            FROM secciones s
            JOIN maquinas m ON s.id_maquina = m.id_maquina
            WHERE s.id_seccion = %s
        """
        return get_one_or_404("secciones", "id_seccion", new_id, custom_select=custom)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.put("/api/secciones/{id_val}", response_model=Seccion, tags=["Secciones"])
def update_seccion(id_val: int, data: SeccionUpdate):
    get_one_or_404("secciones", "id_seccion", id_val)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        data_dict = data.model_dump(exclude_unset=True)
        if data_dict:
            fields = [f"{k} = %s" for k in data_dict.keys()]
            values = list(data_dict.values()) + [id_val]
            cursor.execute(f"UPDATE secciones SET {', '.join(fields)} WHERE id_seccion = %s", tuple(values))
            conn.commit()
        cursor.close()
        custom = """
            SELECT s.id_seccion, s.id_maquina, s.numero_seccion, s.estado, m.codigo AS maquina_codigo 
            FROM secciones s
            JOIN maquinas m ON s.id_maquina = m.id_maquina
            WHERE s.id_seccion = %s
        """
        return get_one_or_404("secciones", "id_seccion", id_val, custom_select=custom)
    finally:
        conn.close()

@app.delete("/api/secciones/{id_val}", status_code=status.HTTP_204_NO_CONTENT, tags=["Secciones"])
def delete_seccion(id_val: int):
    delete_or_404("secciones", "id_seccion", id_val)


# --- CRUD: PRODUCTOS ---
@app.get("/api/productos", response_model=List[Producto], tags=["Productos"])
def list_productos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos ORDER BY codigo_producto")
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.get("/api/productos/{id_val}", response_model=Producto, tags=["Productos"])
def get_producto(id_val: int):
    return get_one_or_404("productos", "id_producto", id_val)

@app.post("/api/productos", response_model=Producto, status_code=status.HTTP_201_CREATED, tags=["Productos"])
def create_producto(data: ProductoCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO productos (codigo_producto, nombre_producto, capacidad_ml, peso_teorico, cliente, estado) VALUES (%s, %s, %s, %s, %s, %s)",
            (data.codigo_producto, data.nombre_producto, data.capacidad_ml, data.peso_teorico, data.cliente, data.estado)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (new_id,))
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/productos/{id_val}", response_model=Producto, tags=["Productos"])
def update_producto(id_val: int, data: ProductoUpdate):
    get_one_or_404("productos", "id_producto", id_val)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        data_dict = data.model_dump(exclude_unset=True)
        if data_dict:
            fields = [f"{k} = %s" for k in data_dict.keys()]
            values = list(data_dict.values()) + [id_val]
            cursor.execute(f"UPDATE productos SET {', '.join(fields)} WHERE id_producto = %s", tuple(values))
            conn.commit()
        cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id_val,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/productos/{id_val}", status_code=status.HTTP_204_NO_CONTENT, tags=["Productos"])
def delete_producto(id_val: int):
    delete_or_404("productos", "id_producto", id_val)


# --- CRUD: MOLDES ---
@app.get("/api/moldes", response_model=List[Molde], tags=["Moldes"])
def list_moldes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM moldes ORDER BY codigo_molde")
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.get("/api/moldes/{id_val}", response_model=Molde, tags=["Moldes"])
def get_molde(id_val: int):
    return get_one_or_404("moldes", "id_molde", id_val)

@app.post("/api/moldes", response_model=Molde, status_code=status.HTTP_201_CREATED, tags=["Moldes"])
def create_molde(data: MoldeCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO moldes (codigo_molde, descripcion, fecha_instalacion, estado) VALUES (%s, %s, %s, %s)",
            (data.codigo_molde, data.descripcion, data.fecha_instalacion, data.estado)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM moldes WHERE id_molde = %s", (new_id,))
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/moldes/{id_val}", response_model=Molde, tags=["Moldes"])
def update_molde(id_val: int, data: MoldeUpdate):
    get_one_or_404("moldes", "id_molde", id_val)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        data_dict = data.model_dump(exclude_unset=True)
        if data_dict:
            fields = [f"{k} = %s" for k in data_dict.keys()]
            values = list(data_dict.values()) + [id_val]
            cursor.execute(f"UPDATE moldes SET {', '.join(fields)} WHERE id_molde = %s", tuple(values))
            conn.commit()
        cursor.execute("SELECT * FROM moldes WHERE id_molde = %s", (id_val,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/moldes/{id_val}", status_code=status.HTTP_204_NO_CONTENT, tags=["Moldes"])
def delete_molde(id_val: int):
    delete_or_404("moldes", "id_molde", id_val)


# --- CRUD: PREMOLDES ---
@app.get("/api/premoldes", response_model=List[Premolde], tags=["Premoldes"])
def list_premoldes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM premoldes ORDER BY codigo_premolde")
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.get("/api/premoldes/{id_val}", response_model=Premolde, tags=["Premoldes"])
def get_premolde(id_val: int):
    return get_one_or_404("premoldes", "id_premolde", id_val)

@app.post("/api/premoldes", response_model=Premolde, status_code=status.HTTP_201_CREATED, tags=["Premoldes"])
def create_premolde(data: PremoldeCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO premoldes (codigo_premolde, descripcion, fecha_instalacion, estado) VALUES (%s, %s, %s, %s)",
            (data.codigo_premolde, data.descripcion, data.fecha_instalacion, data.estado)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM premoldes WHERE id_premolde = %s", (new_id,))
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/premoldes/{id_val}", response_model=Premolde, tags=["Premoldes"])
def update_premolde(id_val: int, data: PremoldeUpdate):
    get_one_or_404("premoldes", "id_premolde", id_val)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        data_dict = data.model_dump(exclude_unset=True)
        if data_dict:
            fields = [f"{k} = %s" for k in data_dict.keys()]
            values = list(data_dict.values()) + [id_val]
            cursor.execute(f"UPDATE premoldes SET {', '.join(fields)} WHERE id_premolde = %s", tuple(values))
            conn.commit()
        cursor.execute("SELECT * FROM premoldes WHERE id_premolde = %s", (id_val,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/premoldes/{id_val}", status_code=status.HTTP_204_NO_CONTENT, tags=["Premoldes"])
def delete_premolde(id_val: int):
    delete_or_404("premoldes", "id_premolde", id_val)


# --- CRUD: CATÁLOGO DE DEFECTOS ---
@app.get("/api/catalogo_defectos", response_model=List[CatalogoDefectos], tags=["Catálogo de Defectos"])
def list_catalogo_defectos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM catalogo_defectos ORDER BY codigo_defecto")
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.get("/api/catalogo_defectos/{id_val}", response_model=CatalogoDefectos, tags=["Catálogo de Defectos"])
def get_catalogo_defecto(id_val: int):
    return get_one_or_404("catalogo_defectos", "id_defecto", id_val)

@app.post("/api/catalogo_defectos", response_model=CatalogoDefectos, status_code=status.HTTP_201_CREATED, tags=["Catálogo de Defectos"])
def create_catalogo_defecto(data: CatalogoDefectosCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO catalogo_defectos (codigo_defecto, nombre, categoria, descripcion, criticidad, estado) VALUES (%s, %s, %s, %s, %s, %s)",
            (data.codigo_defecto, data.nombre, data.categoria, data.descripcion, data.criticidad, data.estado)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM catalogo_defectos WHERE id_defecto = %s", (new_id,))
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/catalogo_defectos/{id_val}", response_model=CatalogoDefectos, tags=["Catálogo de Defectos"])
def update_catalogo_defecto(id_val: int, data: CatalogoDefectosUpdate):
    get_one_or_404("catalogo_defectos", "id_defecto", id_val)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        data_dict = data.model_dump(exclude_unset=True)
        if data_dict:
            fields = [f"{k} = %s" for k in data_dict.keys()]
            values = list(data_dict.values()) + [id_val]
            cursor.execute(f"UPDATE catalogo_defectos SET {', '.join(fields)} WHERE id_defecto = %s", tuple(values))
            conn.commit()
        cursor.execute("SELECT * FROM catalogo_defectos WHERE id_defecto = %s", (id_val,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/catalogo_defectos/{id_val}", status_code=status.HTTP_204_NO_CONTENT, tags=["Catálogo de Defectos"])
def delete_catalogo_defecto(id_val: int):
    delete_or_404("catalogo_defectos", "id_defecto", id_val)


# --- CRUD: INSPECTORES ---
@app.get("/api/inspectores", response_model=List[Inspector], tags=["Inspectores"])
def list_inspectores():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inspectores ORDER BY cedula")
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.get("/api/inspectores/{id_val}", response_model=Inspector, tags=["Inspectores"])
def get_inspector(id_val: int):
    return get_one_or_404("inspectores", "id_inspector", id_val)

@app.post("/api/inspectores", response_model=Inspector, status_code=status.HTTP_201_CREATED, tags=["Inspectores"])
def create_inspector(data: InspectorCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO inspectores (cedula, nombre, apellido, cargo, telefono, correo, estado) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (data.cedula, data.nombre, data.apellido, data.cargo, data.telefono, data.correo, data.estado)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM inspectores WHERE id_inspector = %s", (new_id,))
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/inspectores/{id_val}", response_model=Inspector, tags=["Inspectores"])
def update_inspector(id_val: int, data: InspectorUpdate):
    get_one_or_404("inspectores", "id_inspector", id_val)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        data_dict = data.model_dump(exclude_unset=True)
        if data_dict:
            fields = [f"{k} = %s" for k in data_dict.keys()]
            values = list(data_dict.values()) + [id_val]
            cursor.execute(f"UPDATE inspectores SET {', '.join(fields)} WHERE id_inspector = %s", tuple(values))
            conn.commit()
        cursor.execute("SELECT * FROM inspectores WHERE id_inspector = %s", (id_val,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/inspectores/{id_val}", status_code=status.HTTP_204_NO_CONTENT, tags=["Inspectores"])
def delete_inspector(id_val: int):
    delete_or_404("inspectores", "id_inspector", id_val)


# --- CRUD: TIPOS DE PARADAS ---
@app.get("/api/tipos_paradas", response_model=List[TipoParada], tags=["Tipos de Paradas"])
def list_tipos_paradas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tipos_paradas ORDER BY nombre")
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.get("/api/tipos_paradas/{id_val}", response_model=TipoParada, tags=["Tipos de Paradas"])
def get_tipo_parada(id_val: int):
    return get_one_or_404("tipos_paradas", "id_tipo_parada", id_val)

@app.post("/api/tipos_paradas", response_model=TipoParada, status_code=status.HTTP_201_CREATED, tags=["Tipos de Paradas"])
def create_tipo_parada(data: TipoParadaCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO tipos_paradas (nombre, descripcion) VALUES (%s, %s)",
            (data.nombre, data.descripcion)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM tipos_paradas WHERE id_tipo_parada = %s", (new_id,))
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/tipos_paradas/{id_val}", response_model=TipoParada, tags=["Tipos de Paradas"])
def update_tipo_parada(id_val: int, data: TipoParadaUpdate):
    get_one_or_404("tipos_paradas", "id_tipo_parada", id_val)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        data_dict = data.model_dump(exclude_unset=True)
        if data_dict:
            fields = [f"{k} = %s" for k in data_dict.keys()]
            values = list(data_dict.values()) + [id_val]
            cursor.execute(f"UPDATE tipos_paradas SET {', '.join(fields)} WHERE id_tipo_parada = %s", tuple(values))
            conn.commit()
        cursor.execute("SELECT * FROM tipos_paradas WHERE id_tipo_parada = %s", (id_val,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/tipos_paradas/{id_val}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tipos de Paradas"])
def delete_tipo_parada(id_val: int):
    delete_or_404("tipos_paradas", "id_tipo_parada", id_val)


# --- CRUD: PRODUCCIÓN ---
@app.get("/api/produccion", response_model=List[Produccion], tags=["Módulo Producción"])
def list_produccion():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, t.codigo_turno AS turno_codigo, m.codigo AS maquina_codigo, 
               pr.nombre_producto AS producto_nombre, u.usuario AS usuario_nombre
        FROM produccion p
        JOIN turnos t ON p.id_turno = t.id_turno
        JOIN maquinas m ON p.id_maquina = m.id_maquina
        JOIN productos pr ON p.id_producto = pr.id_producto
        JOIN usuarios u ON p.id_usuario = u.id_usuario
        ORDER BY p.fecha DESC, p.id_produccion DESC
    """)
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.get("/api/produccion/{id_val}", response_model=Produccion, tags=["Módulo Producción"])
def get_produccion(id_val: int):
    custom = """
        SELECT p.*, t.codigo_turno AS turno_codigo, m.codigo AS maquina_codigo, 
               pr.nombre_producto AS producto_nombre, u.usuario AS usuario_nombre
        FROM produccion p
        JOIN turnos t ON p.id_turno = t.id_turno
        JOIN maquinas m ON p.id_maquina = m.id_maquina
        JOIN productos pr ON p.id_producto = pr.id_producto
        JOIN usuarios u ON p.id_usuario = u.id_usuario
        WHERE p.id_produccion = %s
    """
    return get_one_or_404("produccion", "id_produccion", id_val, custom_select=custom)

@app.post("/api/produccion", response_model=Produccion, status_code=status.HTTP_201_CREATED, tags=["Módulo Producción"])
def create_produccion(data: ProduccionCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO produccion (fecha, id_turno, id_maquina, id_producto, id_usuario, 
                                      paletas_producidas, gruesas_producidas, gruesas_empacadas, gruesas_retenidas, observaciones) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (data.fecha, data.id_turno, data.id_maquina, data.id_producto, data.id_usuario,
             data.paletas_producidas, data.gruesas_producidas, data.gruesas_empacadas, data.gruesas_retenidas, data.observaciones)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        
        custom = """
            SELECT p.*, t.codigo_turno AS turno_codigo, m.codigo AS maquina_codigo, 
                   pr.nombre_producto AS producto_nombre, u.usuario AS usuario_nombre
            FROM produccion p
            JOIN turnos t ON p.id_turno = t.id_turno
            JOIN maquinas m ON p.id_maquina = m.id_maquina
            JOIN productos pr ON p.id_producto = pr.id_producto
            JOIN usuarios u ON p.id_usuario = u.id_usuario
            WHERE p.id_produccion = %s
        """
        return get_one_or_404("produccion", "id_produccion", new_id, custom_select=custom)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.put("/api/produccion/{id_val}", response_model=Produccion, tags=["Módulo Producción"])
def update_produccion(id_val: int, data: ProduccionUpdate):
    get_one_or_404("produccion", "id_produccion", id_val)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        data_dict = data.model_dump(exclude_unset=True)
        if data_dict:
            # Serializar fecha si está presente
            if "fecha" in data_dict and isinstance(data_dict["fecha"], date):
                data_dict["fecha"] = data_dict["fecha"].isoformat()
            fields = [f"{k} = %s" for k in data_dict.keys()]
            values = list(data_dict.values()) + [id_val]
            cursor.execute(f"UPDATE produccion SET {', '.join(fields)} WHERE id_produccion = %s", tuple(values))
            conn.commit()
        cursor.close()
        
        custom = """
            SELECT p.*, t.codigo_turno AS turno_codigo, m.codigo AS maquina_codigo, 
                   pr.nombre_producto AS producto_nombre, u.usuario AS usuario_nombre
            FROM produccion p
            JOIN turnos t ON p.id_turno = t.id_turno
            JOIN maquinas m ON p.id_maquina = m.id_maquina
            JOIN productos pr ON p.id_producto = pr.id_producto
            JOIN usuarios u ON p.id_usuario = u.id_usuario
            WHERE p.id_produccion = %s
        """
        return get_one_or_404("produccion", "id_produccion", id_val, custom_select=custom)
    finally:
        conn.close()

@app.delete("/api/produccion/{id_val}", status_code=status.HTTP_204_NO_CONTENT, tags=["Módulo Producción"])
def delete_produccion(id_val: int):
    delete_or_404("produccion", "id_produccion", id_val)


# --- CRUD: INSPECCIONES ---
@app.get("/api/inspecciones", response_model=List[Inspeccion], tags=["Módulo Inspección"])
def list_inspecciones():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT i.id_inspeccion, i.fecha, CAST(i.hora AS CHAR) as hora, i.id_turno, i.id_inspector, 
               i.id_maquina, i.id_seccion, i.id_producto, i.lote, i.temperatura_maquina, 
               i.observaciones, i.created_at,
               t.codigo_turno AS turno_codigo, 
               CONCAT(ins.nombre, ' ', ins.apellido) AS inspector_nombre, 
               m.codigo AS maquina_codigo, s.numero_seccion AS seccion_numero, 
               pr.nombre_producto AS producto_nombre
        FROM inspecciones i
        JOIN turnos t ON i.id_turno = t.id_turno
        JOIN inspectores ins ON i.id_inspector = ins.id_inspector
        JOIN maquinas m ON i.id_maquina = m.id_maquina
        JOIN secciones s ON i.id_seccion = s.id_seccion
        JOIN productos pr ON i.id_producto = pr.id_producto
        ORDER BY i.fecha DESC, i.hora DESC
    """)
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.get("/api/inspecciones/{id_val}", response_model=Inspeccion, tags=["Módulo Inspección"])
def get_inspeccion(id_val: int):
    custom = """
        SELECT i.id_inspeccion, i.fecha, CAST(i.hora AS CHAR) as hora, i.id_turno, i.id_inspector, 
               i.id_maquina, i.id_seccion, i.id_producto, i.lote, i.temperatura_maquina, 
               i.observaciones, i.created_at,
               t.codigo_turno AS turno_codigo, 
               CONCAT(ins.nombre, ' ', ins.apellido) AS inspector_nombre, 
               m.codigo AS maquina_codigo, s.numero_seccion AS seccion_numero, 
               pr.nombre_producto AS producto_nombre
        FROM inspecciones i
        JOIN turnos t ON i.id_turno = t.id_turno
        JOIN inspectores ins ON i.id_inspector = ins.id_inspector
        JOIN maquinas m ON i.id_maquina = m.id_maquina
        JOIN secciones s ON i.id_seccion = s.id_seccion
        JOIN productos pr ON i.id_producto = pr.id_producto
        WHERE i.id_inspeccion = %s
    """
    return get_one_or_404("inspecciones", "id_inspeccion", id_val, custom_select=custom)

@app.post("/api/inspecciones", response_model=Inspeccion, status_code=status.HTTP_201_CREATED, tags=["Módulo Inspección"])
def create_inspeccion(data: InspeccionCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO inspecciones (fecha, hora, id_turno, id_inspector, id_maquina, id_seccion, id_producto, lote, temperatura_maquina, observaciones) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (data.fecha, data.hora, data.id_turno, data.id_inspector, data.id_maquina, data.id_seccion, data.id_producto, data.lote, data.temperatura_maquina, data.observaciones)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        
        custom = """
            SELECT i.id_inspeccion, i.fecha, CAST(i.hora AS CHAR) as hora, i.id_turno, i.id_inspector, 
                   i.id_maquina, i.id_seccion, i.id_producto, i.lote, i.temperatura_maquina, 
                   i.observaciones, i.created_at,
                   t.codigo_turno AS turno_codigo, 
                   CONCAT(ins.nombre, ' ', ins.apellido) AS inspector_nombre, 
                   m.codigo AS maquina_codigo, s.numero_seccion AS seccion_numero, 
                   pr.nombre_producto AS producto_nombre
            FROM inspecciones i
            JOIN turnos t ON i.id_turno = t.id_turno
            JOIN inspectores ins ON i.id_inspector = ins.id_inspector
            JOIN maquinas m ON i.id_maquina = m.id_maquina
            JOIN secciones s ON i.id_seccion = s.id_seccion
            JOIN productos pr ON i.id_producto = pr.id_producto
            WHERE i.id_inspeccion = %s
        """
        return get_one_or_404("inspecciones", "id_inspeccion", new_id, custom_select=custom)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.put("/api/inspecciones/{id_val}", response_model=Inspeccion, tags=["Módulo Inspección"])
def update_inspeccion(id_val: int, data: InspeccionUpdate):
    get_one_or_404("inspecciones", "id_inspeccion", id_val)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        data_dict = data.model_dump(exclude_unset=True)
        if data_dict:
            if "fecha" in data_dict and isinstance(data_dict["fecha"], date):
                data_dict["fecha"] = data_dict["fecha"].isoformat()
            fields = [f"{k} = %s" for k in data_dict.keys()]
            values = list(data_dict.values()) + [id_val]
            cursor.execute(f"UPDATE inspecciones SET {', '.join(fields)} WHERE id_inspeccion = %s", tuple(values))
            conn.commit()
        cursor.close()
        
        custom = """
            SELECT i.id_inspeccion, i.fecha, CAST(i.hora AS CHAR) as hora, i.id_turno, i.id_inspector, 
                   i.id_maquina, i.id_seccion, i.id_producto, i.lote, i.temperatura_maquina, 
                   i.observaciones, i.created_at,
                   t.codigo_turno AS turno_codigo, 
                   CONCAT(ins.nombre, ' ', ins.apellido) AS inspector_nombre, 
                   m.codigo AS maquina_codigo, s.numero_seccion AS seccion_numero, 
                   pr.nombre_producto AS producto_nombre
            FROM inspecciones i
            JOIN turnos t ON i.id_turno = t.id_turno
            JOIN inspectores ins ON i.id_inspector = ins.id_inspector
            JOIN maquinas m ON i.id_maquina = m.id_maquina
            JOIN secciones s ON i.id_seccion = s.id_seccion
            JOIN productos pr ON i.id_producto = pr.id_producto
            WHERE i.id_inspeccion = %s
        """
        return get_one_or_404("inspecciones", "id_inspeccion", id_val, custom_select=custom)
    finally:
        conn.close()

@app.delete("/api/inspecciones/{id_val}", status_code=status.HTTP_204_NO_CONTENT, tags=["Módulo Inspección"])
def delete_inspeccion(id_val: int):
    delete_or_404("inspecciones", "id_inspeccion", id_val)


# --- CRUD: DETALLE INSPECCIÓN (DEFECTOS DETECTADOS) ---
@app.get("/api/detalle_inspeccion", response_model=List[DetalleInspeccion], tags=["Módulo Inspección"])
def list_detalle_inspeccion(id_inspeccion: Optional[int] = None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT d.*, c.nombre AS defecto_nombre, c.criticidad AS defecto_criticidad
        FROM detalle_inspeccion d
        JOIN catalogo_defectos c ON d.id_defecto = c.id_defecto
    """
    params = ()
    if id_inspeccion:
        query += " WHERE d.id_inspeccion = %s"
        params = (id_inspeccion,)
    
    cursor.execute(query, params)
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.get("/api/detalle_inspeccion/{id_val}", response_model=DetalleInspeccion, tags=["Módulo Inspección"])
def get_detalle_inspeccion(id_val: int):
    custom = """
        SELECT d.*, c.nombre AS defecto_nombre, c.criticidad AS defecto_criticidad
        FROM detalle_inspeccion d
        JOIN catalogo_defectos c ON d.id_defecto = c.id_defecto
        WHERE d.id_detalle = %s
    """
    return get_one_or_404("detalle_inspeccion", "id_detalle", id_val, custom_select=custom)

@app.post("/api/detalle_inspeccion", response_model=DetalleInspeccion, status_code=status.HTTP_201_CREATED, tags=["Módulo Inspección"])
def create_detalle_inspeccion(data: DetalleInspeccionCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO detalle_inspeccion (id_inspeccion, id_defecto, cantidad_detectada, porcentaje_defecto, observacion) VALUES (%s, %s, %s, %s, %s)",
            (data.id_inspeccion, data.id_defecto, data.cantidad_detectada, data.porcentaje_defecto, data.observacion)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        
        custom = """
            SELECT d.*, c.nombre AS defecto_nombre, c.criticidad AS defecto_criticidad
            FROM detalle_inspeccion d
            JOIN catalogo_defectos c ON d.id_defecto = c.id_defecto
            WHERE d.id_detalle = %s
        """
        return get_one_or_404("detalle_inspeccion", "id_detalle", new_id, custom_select=custom)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.put("/api/detalle_inspeccion/{id_val}", response_model=DetalleInspeccion, tags=["Módulo Inspección"])
def update_detalle_inspeccion(id_val: int, data: DetalleInspeccionUpdate):
    get_one_or_404("detalle_inspeccion", "id_detalle", id_val)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        data_dict = data.model_dump(exclude_unset=True)
        if data_dict:
            fields = [f"{k} = %s" for k in data_dict.keys()]
            values = list(data_dict.values()) + [id_val]
            cursor.execute(f"UPDATE detalle_inspeccion SET {', '.join(fields)} WHERE id_detalle = %s", tuple(values))
            conn.commit()
        cursor.close()
        
        custom = """
            SELECT d.*, c.nombre AS defecto_nombre, c.criticidad AS defecto_criticidad
            FROM detalle_inspeccion d
            JOIN catalogo_defectos c ON d.id_defecto = c.id_defecto
            WHERE d.id_detalle = %s
        """
        return get_one_or_404("detalle_inspeccion", "id_detalle", id_val, custom_select=custom)
    finally:
        conn.close()

@app.delete("/api/detalle_inspeccion/{id_val}", status_code=status.HTTP_204_NO_CONTENT, tags=["Módulo Inspección"])
def delete_detalle_inspeccion(id_val: int):
    delete_or_404("detalle_inspeccion", "id_detalle", id_val)


# --- CRUD: ACCIONES CORRECTIVAS ---
@app.get("/api/acciones_correctivas", response_model=List[AccionCorrectiva], tags=["Módulo Inspección"])
def list_acciones_correctivas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM acciones_correctivas ORDER BY fecha DESC")
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.get("/api/acciones_correctivas/{id_val}", response_model=AccionCorrectiva, tags=["Módulo Inspección"])
def get_accion_correctiva(id_val: int):
    return get_one_or_404("acciones_correctivas", "id_accion", id_val)

@app.post("/api/acciones_correctivas", response_model=AccionCorrectiva, status_code=status.HTTP_201_CREATED, tags=["Módulo Inspección"])
def create_accion_correctiva(data: AccionCorrectivaCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """INSERT INTO acciones_correctivas (fecha, id_inspeccion, problema_detectado, accion_realizada, responsable, fecha_cierre, estado) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (data.fecha, data.id_inspeccion, data.problema_detectado, data.accion_realizada, data.responsable, data.fecha_cierre, data.estado)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM acciones_correctivas WHERE id_accion = %s", (new_id,))
        return cursor.fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/acciones_correctivas/{id_val}", response_model=AccionCorrectiva, tags=["Módulo Inspección"])
def update_accion_correctiva(id_val: int, data: AccionCorrectivaUpdate):
    get_one_or_404("acciones_correctivas", "id_accion", id_val)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        data_dict = data.model_dump(exclude_unset=True)
        if data_dict:
            # Serializar fechas si están presentes
            for f in ["fecha", "fecha_cierre"]:
                if f in data_dict and isinstance(data_dict[f], date):
                    data_dict[f] = data_dict[f].isoformat()
            fields = [f"{k} = %s" for k in data_dict.keys()]
            values = list(data_dict.values()) + [id_val]
            cursor.execute(f"UPDATE acciones_correctivas SET {', '.join(fields)} WHERE id_accion = %s", tuple(values))
            conn.commit()
        cursor.execute("SELECT * FROM acciones_correctivas WHERE id_accion = %s", (id_val,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/acciones_correctivas/{id_val}", status_code=status.HTTP_204_NO_CONTENT, tags=["Módulo Inspección"])
def delete_accion_correctiva(id_val: int):
    delete_or_404("acciones_correctivas", "id_accion", id_val)


# --- CRUD: PARADAS ---
@app.get("/api/paradas", response_model=List[Parada], tags=["Máquinas"])
def list_paradas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id_parada, p.fecha, p.id_turno, p.id_maquina, p.id_seccion, p.id_tipo_parada, 
               p.hora_inicio, p.hora_fin, p.minutos_parada, p.descripcion,
               t.codigo_turno AS turno_codigo, m.codigo AS maquina_codigo, 
               s.numero_seccion AS seccion_numero, tp.nombre AS tipo_parada_nombre
        FROM paradas p
        JOIN turnos t ON p.id_turno = t.id_turno
        JOIN maquinas m ON p.id_maquina = m.id_maquina
        JOIN secciones s ON p.id_seccion = s.id_seccion
        JOIN tipos_paradas tp ON p.id_tipo_parada = tp.id_tipo_parada
        ORDER BY p.fecha DESC, p.id_parada DESC
    """)
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

@app.get("/api/paradas/{id_val}", response_model=Parada, tags=["Máquinas"])
def get_parada(id_val: int):
    custom = """
        SELECT p.id_parada, p.fecha, p.id_turno, p.id_maquina, p.id_seccion, p.id_tipo_parada, 
               p.hora_inicio, p.hora_fin, p.minutos_parada, p.descripcion,
               t.codigo_turno AS turno_codigo, m.codigo AS maquina_codigo, 
               s.numero_seccion AS seccion_numero, tp.nombre AS tipo_parada_nombre
        FROM paradas p
        JOIN turnos t ON p.id_turno = t.id_turno
        JOIN maquinas m ON p.id_maquina = m.id_maquina
        JOIN secciones s ON p.id_seccion = s.id_seccion
        JOIN tipos_paradas tp ON p.id_tipo_parada = tp.id_tipo_parada
        WHERE p.id_parada = %s
    """
    return get_one_or_404("paradas", "id_parada", id_val, custom_select=custom)

@app.post("/api/paradas", response_model=Parada, status_code=status.HTTP_201_CREATED, tags=["Máquinas"])
def create_parada(data: ParadaCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO paradas (fecha, id_turno, id_maquina, id_seccion, id_tipo_parada, hora_inicio, hora_fin, minutos_parada, descripcion) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (data.fecha, data.id_turno, data.id_maquina, data.id_seccion, data.id_tipo_parada, data.hora_inicio, data.hora_fin, data.minutos_parada, data.descripcion)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        
        custom = """
            SELECT p.id_parada, p.fecha, p.id_turno, p.id_maquina, p.id_seccion, p.id_tipo_parada, 
                   p.hora_inicio, p.hora_fin, p.minutos_parada, p.descripcion,
                   t.codigo_turno AS turno_codigo, m.codigo AS maquina_codigo, 
                   s.numero_seccion AS seccion_numero, tp.nombre AS tipo_parada_nombre
            FROM paradas p
            JOIN turnos t ON p.id_turno = t.id_turno
            JOIN maquinas m ON p.id_maquina = m.id_maquina
            JOIN secciones s ON p.id_seccion = s.id_seccion
            JOIN tipos_paradas tp ON p.id_tipo_parada = tp.id_tipo_parada
            WHERE p.id_parada = %s
        """
        return get_one_or_404("paradas", "id_parada", new_id, custom_select=custom)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.put("/api/paradas/{id_val}", response_model=Parada, tags=["Máquinas"])
def update_parada(id_val: int, data: ParadaUpdate):
    get_one_or_404("paradas", "id_parada", id_val)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        data_dict = data.model_dump(exclude_unset=True)
        if data_dict:
            # Serializar fechas y datetimes si están presentes
            if "fecha" in data_dict and isinstance(data_dict["fecha"], date):
                data_dict["fecha"] = data_dict["fecha"].isoformat()
            for key in ["hora_inicio", "hora_fin"]:
                if key in data_dict and isinstance(data_dict[key], datetime):
                    data_dict[key] = data_dict[key].isoformat()
            fields = [f"{k} = %s" for k in data_dict.keys()]
            values = list(data_dict.values()) + [id_val]
            cursor.execute(f"UPDATE paradas SET {', '.join(fields)} WHERE id_parada = %s", tuple(values))
            conn.commit()
        cursor.close()
        
        custom = """
            SELECT p.id_parada, p.fecha, p.id_turno, p.id_maquina, p.id_seccion, p.id_tipo_parada, 
                   p.hora_inicio, p.hora_fin, p.minutos_parada, p.descripcion,
                   t.codigo_turno AS turno_codigo, m.codigo AS maquina_codigo, 
                   s.numero_seccion AS seccion_numero, tp.nombre AS tipo_parada_nombre
            FROM paradas p
            JOIN turnos t ON p.id_turno = t.id_turno
            JOIN maquinas m ON p.id_maquina = m.id_maquina
            JOIN secciones s ON p.id_seccion = s.id_seccion
            JOIN tipos_paradas tp ON p.id_tipo_parada = tp.id_tipo_parada
            WHERE p.id_parada = %s
        """
        return get_one_or_404("paradas", "id_parada", id_val, custom_select=custom)
    finally:
        conn.close()

@app.delete("/api/paradas/{id_val}", status_code=status.HTTP_204_NO_CONTENT, tags=["Máquinas"])
def delete_parada(id_val: int):
    delete_or_404("paradas", "id_parada", id_val)
