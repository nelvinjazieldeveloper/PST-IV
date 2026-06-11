from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, time

# --- USUARIOS ---
class UsuarioBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    apellido: str = Field(..., max_length=100)
    usuario: str = Field(..., max_length=50)
    cargo: Optional[str] = Field(None, max_length=100)
    rol: Optional[str] = Field(None, max_length=50)
    estado: str = Field("ACTIVO")

class UsuarioCreate(UsuarioBase):
    clave: str = Field(..., max_length=255)

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    usuario: Optional[str] = None
    clave: Optional[str] = None
    cargo: Optional[str] = None
    rol: Optional[str] = None
    estado: Optional[str] = None

class Usuario(UsuarioBase):
    id_usuario: int
    fecha_registro: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- TURNOS ---
class TurnoBase(BaseModel):
    codigo_turno: str = Field(..., max_length=20)
    hora_inicio: str = Field(..., description="Hora de inicio en formato HH:MM:SS")
    hora_fin: str = Field(..., description="Hora de fin en formato HH:MM:SS")
    descripcion: Optional[str] = Field(None, max_length=150)

class TurnoCreate(TurnoBase):
    pass

class TurnoUpdate(BaseModel):
    codigo_turno: Optional[str] = None
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    descripcion: Optional[str] = None

class Turno(TurnoBase):
    id_turno: int

    class Config:
        from_attributes = True


# --- MÁQUINAS ---
class MaquinaBase(BaseModel):
    codigo: str = Field(..., max_length=20)
    descripcion: Optional[str] = Field(None, max_length=150)
    cantidad_secciones: Optional[int] = None
    estado: str = Field("ACTIVA")

class MaquinaCreate(MaquinaBase):
    pass

class MaquinaUpdate(BaseModel):
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    cantidad_secciones: Optional[int] = None
    estado: Optional[str] = None

class Maquina(MaquinaBase):
    id_maquina: int

    class Config:
        from_attributes = True


# --- SECCIONES ---
class SeccionBase(BaseModel):
    id_maquina: int
    numero_seccion: int
    estado: str = Field("ACTIVA")

class SeccionCreate(SeccionBase):
    pass

class SeccionUpdate(BaseModel):
    id_maquina: Optional[int] = None
    numero_seccion: Optional[int] = None
    estado: Optional[str] = None

class Seccion(SeccionBase):
    id_seccion: int
    maquina_codigo: Optional[str] = None

    class Config:
        from_attributes = True


# --- PRODUCTOS ---
class ProductoBase(BaseModel):
    codigo_producto: str = Field(..., max_length=50)
    nombre_producto: str = Field(..., max_length=150)
    capacidad_ml: Optional[float] = None
    peso_teorico: Optional[float] = None
    cliente: Optional[str] = Field(None, max_length=150)
    estado: str = Field("ACTIVO")

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    codigo_producto: Optional[str] = None
    nombre_producto: Optional[str] = None
    capacidad_ml: Optional[float] = None
    peso_teorico: Optional[float] = None
    cliente: Optional[str] = None
    estado: Optional[str] = None

class Producto(ProductoBase):
    id_producto: int

    class Config:
        from_attributes = True


# --- MOLDES ---
class MoldeBase(BaseModel):
    codigo_molde: str = Field(..., max_length=50)
    descripcion: Optional[str] = Field(None, max_length=150)
    fecha_instalacion: Optional[date] = None
    estado: str = Field("ACTIVO")

class MoldeCreate(MoldeBase):
    pass

class MoldeUpdate(BaseModel):
    codigo_molde: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_instalacion: Optional[date] = None
    estado: Optional[str] = None

class Molde(MoldeBase):
    id_molde: int

    class Config:
        from_attributes = True


# --- PREMOLDES ---
class PremoldeBase(BaseModel):
    codigo_premolde: str = Field(..., max_length=50)
    descripcion: Optional[str] = Field(None, max_length=150)
    fecha_instalacion: Optional[date] = None
    estado: str = Field("ACTIVO")

class PremoldeCreate(PremoldeBase):
    pass

class PremoldeUpdate(BaseModel):
    codigo_premolde: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_instalacion: Optional[date] = None
    estado: Optional[str] = None

class Premolde(PremoldeBase):
    id_premolde: int

    class Config:
        from_attributes = True


# --- CATÁLOGO DE DEFECTOS ---
class CatalogoDefectosBase(BaseModel):
    codigo_defecto: Optional[str] = Field(None, max_length=20)
    nombre: str = Field(..., max_length=150)
    categoria: str = Field(..., max_length=100)
    descripcion: Optional[str] = None
    criticidad: str = Field(..., description="CRITICO, MAYOR o MENOR")
    estado: str = Field("ACTIVO")

class CatalogoDefectosCreate(CatalogoDefectosBase):
    pass

class CatalogoDefectosUpdate(BaseModel):
    codigo_defecto: Optional[str] = None
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    criticidad: Optional[str] = None
    estado: Optional[str] = None

class CatalogoDefectos(CatalogoDefectosBase):
    id_defecto: int
    fecha_registro: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- INSPECTORES ---
class InspectorBase(BaseModel):
    cedula: Optional[str] = Field(None, max_length=20)
    nombre: str = Field(..., max_length=100)
    apellido: str = Field(..., max_length=100)
    cargo: Optional[str] = Field(None, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    correo: Optional[str] = Field(None, max_length=100)
    estado: str = Field("ACTIVO")

class InspectorCreate(InspectorBase):
    pass

class InspectorUpdate(BaseModel):
    cedula: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    cargo: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    estado: Optional[str] = None

class Inspector(InspectorBase):
    id_inspector: int
    fecha_registro: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- TIPOS DE PARADAS ---
class TipoParadaBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = None

class TipoParadaCreate(TipoParadaBase):
    pass

class TipoParadaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class TipoParada(TipoParadaBase):
    id_tipo_parada: int

    class Config:
        from_attributes = True


# --- PRODUCCIÓN ---
class ProduccionBase(BaseModel):
    fecha: date
    id_turno: int
    id_maquina: int
    id_producto: int
    id_usuario: int
    paletas_producidas: Optional[float] = None
    gruesas_producidas: Optional[float] = None
    gruesas_empacadas: Optional[float] = None
    gruesas_retenidas: Optional[float] = None
    observaciones: Optional[str] = None

class ProduccionCreate(ProduccionBase):
    pass

class ProduccionUpdate(BaseModel):
    fecha: Optional[date] = None
    id_turno: Optional[int] = None
    id_maquina: Optional[int] = None
    id_producto: Optional[int] = None
    id_usuario: Optional[int] = None
    paletas_producidas: Optional[float] = None
    gruesas_producidas: Optional[float] = None
    gruesas_empacadas: Optional[float] = None
    gruesas_retenidas: Optional[float] = None
    observaciones: Optional[str] = None

class Produccion(ProduccionBase):
    id_produccion: int
    # Campos adicionales para resolver nombres en lecturas
    turno_codigo: Optional[str] = None
    maquina_codigo: Optional[str] = None
    producto_nombre: Optional[str] = None
    usuario_nombre: Optional[str] = None

    class Config:
        from_attributes = True


# --- INSPECCIONES ---
class InspeccionBase(BaseModel):
    fecha: date
    hora: str = Field(..., description="Hora de inspección en formato HH:MM:SS")
    id_turno: int
    id_inspector: int
    id_maquina: int
    id_seccion: int
    id_producto: int
    lote: Optional[str] = Field(None, max_length=50)
    temperatura_maquina: Optional[float] = None
    observaciones: Optional[str] = None

class InspeccionCreate(InspeccionBase):
    pass

class InspeccionUpdate(BaseModel):
    fecha: Optional[date] = None
    hora: Optional[str] = None
    id_turno: Optional[int] = None
    id_inspector: Optional[int] = None
    id_maquina: Optional[int] = None
    id_seccion: Optional[int] = None
    id_producto: Optional[int] = None
    lote: Optional[str] = None
    temperatura_maquina: Optional[float] = None
    observaciones: Optional[str] = None

class Inspeccion(InspeccionBase):
    id_inspeccion: int
    created_at: Optional[datetime] = None
    
    # Nombres adicionales
    turno_codigo: Optional[str] = None
    inspector_nombre: Optional[str] = None
    maquina_codigo: Optional[str] = None
    seccion_numero: Optional[int] = None
    producto_nombre: Optional[str] = None

    class Config:
        from_attributes = True


# --- DETALLE INSPECCIÓN (DEFECTOS ENCONTRADOS) ---
class DetalleInspeccionBase(BaseModel):
    id_inspeccion: int
    id_defecto: int
    cantidad_detectada: Optional[int] = 0
    porcentaje_defecto: Optional[float] = None
    observacion: Optional[str] = None

class DetalleInspeccionCreate(DetalleInspeccionBase):
    pass

class DetalleInspeccionUpdate(BaseModel):
    id_inspeccion: Optional[int] = None
    id_defecto: Optional[int] = None
    cantidad_detectada: Optional[int] = None
    porcentaje_defecto: Optional[float] = None
    observacion: Optional[str] = None

class DetalleInspeccion(DetalleInspeccionBase):
    id_detalle: int
    defecto_nombre: Optional[str] = None
    defecto_criticidad: Optional[str] = None

    class Config:
        from_attributes = True


# --- ACCIONES CORRECTIVAS ---
class AccionCorrectivaBase(BaseModel):
    fecha: date
    id_inspeccion: int
    problema_detectado: str
    accion_realizada: str
    responsable: Optional[str] = Field(None, max_length=150)
    fecha_cierre: Optional[date] = None
    estado: str = Field("ABIERTA")

class AccionCorrectivaCreate(AccionCorrectivaBase):
    pass

class AccionCorrectivaUpdate(BaseModel):
    fecha: Optional[date] = None
    id_inspeccion: Optional[int] = None
    problema_detectado: Optional[str] = None
    accion_realizada: Optional[str] = None
    responsable: Optional[str] = None
    fecha_cierre: Optional[date] = None
    estado: Optional[str] = None

class AccionCorrectiva(AccionCorrectivaBase):
    id_accion: int

    class Config:
        from_attributes = True


# --- PARADAS ---
class ParadaBase(BaseModel):
    fecha: date
    id_turno: int
    id_maquina: int
    id_seccion: int
    id_tipo_parada: int
    hora_inicio: Optional[datetime] = None
    hora_fin: Optional[datetime] = None
    minutos_parada: Optional[int] = None
    descripcion: Optional[str] = None

class ParadaCreate(ParadaBase):
    pass

class ParadaUpdate(BaseModel):
    fecha: Optional[date] = None
    id_turno: Optional[int] = None
    id_maquina: Optional[int] = None
    id_seccion: Optional[int] = None
    id_tipo_parada: Optional[int] = None
    hora_inicio: Optional[datetime] = None
    hora_fin: Optional[datetime] = None
    minutos_parada: Optional[int] = None
    descripcion: Optional[str] = None

class Parada(ParadaBase):
    id_parada: int
    turno_codigo: Optional[str] = None
    maquina_codigo: Optional[str] = None
    seccion_numero: Optional[int] = None
    tipo_parada_nombre: Optional[str] = None

    class Config:
        from_attributes = True


# --- ESTADO GENERAL ---
class ServerStatus(BaseModel):
    status: str
    db_connected: bool
    version: str
    project_name: str
    timestamp: datetime


# --- AUTENTICACIÓN ---
class LoginRequest(BaseModel):
    usuario: str = Field(..., min_length=2, max_length=50)
    clave: str = Field(..., min_length=2, max_length=255)
