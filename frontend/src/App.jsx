import React, { useState, useEffect } from 'react';
import { 
  HashRouter as Router, 
  Routes, 
  Route, 
  Navigate, 
  NavLink 
} from 'react-router-dom';
import { 
  Flame, LogOut, Settings, Database, TrendingUp, Search, 
  Octagon, Cpu, Package, AlertCircle, Users, RefreshCw, 
  Pencil, Trash2, PlusCircle, Wrench, ExternalLink 
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// --- COMPONENTE: ENCABEZADO DE PÁGINA CON ESTADO DEL SERVIDOR ---
function PageHeader({ title, description, serverStatus }) {
  return (
    <header className="page-header-custom" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', borderBottom: '1px solid var(--border)', paddingBottom: '1.25rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>{title}</h1>
        {description && <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.25rem' }}>{description}</p>}
      </div>

      <div className="server-widget" style={{ padding: '0.5rem 1rem' }}>
        <span className={`status-dot ${serverStatus.online ? 'online' : 'offline'}`}></span>
        <div style={{ fontSize: '0.85rem' }}>
          <div style={{ fontWeight: 600 }}>API: {serverStatus.online ? 'CONECTADO' : 'DESCONECTADO'}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            DB: <span style={{ color: serverStatus.db_connected ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }}>
              {serverStatus.db_connected ? 'venvidrio' : 'SIN CONEXIÓN'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}

// --- COMPONENTE: BARRA DE NAVEGACIÓN LATERAL FLOTANTE (SIDEBAR) ---
function Sidebar({ currentUser, onLogout }) {
  const isAdmin = currentUser?.rol === 'Administrador';

  return (
    <div className="sidebar">
      <div className="sidebar-brand">
        <Flame size={24} className="header-flame" />
        <span className="brand-text">Venvidrio</span>
      </div>
      
      <div className="sidebar-menu">
        <div className="menu-section-title">Operaciones</div>
        <NavLink to="/produccion" className="sidebar-link">
          <TrendingUp size={18} />
          <span>Producción</span>
        </NavLink>
        <NavLink to="/inspecciones" className="sidebar-link">
          <Search size={18} />
          <span>Inspecciones</span>
        </NavLink>
        <NavLink to="/paradas" className="sidebar-link">
          <Octagon size={18} />
          <span>Paradas</span>
        </NavLink>

        {isAdmin && (
          <>
            <div className="menu-section-title">Administración</div>
            <NavLink to="/usuarios" className="sidebar-link">
              <Users size={18} />
              <span>Usuarios</span>
            </NavLink>
            <NavLink to="/turnos" className="sidebar-link">
              <RefreshCw size={18} />
              <span>Turnos</span>
            </NavLink>
            <NavLink to="/maquinas" className="sidebar-link">
              <Cpu size={18} />
              <span>Máquinas</span>
            </NavLink>
            
            <div className="menu-section-title">Catálogos</div>
            <NavLink to="/productos" className="sidebar-link">
              <Package size={18} />
              <span>Productos</span>
            </NavLink>
            <NavLink to="/defectos" className="sidebar-link">
              <AlertCircle size={18} />
              <span>Defectos</span>
            </NavLink>
            <NavLink to="/inspectores" className="sidebar-link">
              <Users size={18} />
              <span>Inspectores</span>
            </NavLink>
            <NavLink to="/moldes" className="sidebar-link">
              <Settings size={18} />
              <span>Moldes</span>
            </NavLink>
            <NavLink to="/premoldes" className="sidebar-link">
              <Settings size={18} />
              <span>Premoldes</span>
            </NavLink>
            <NavLink to="/tipos-paradas" className="sidebar-link">
              <Wrench size={18} />
              <span>Tipos Parada</span>
            </NavLink>
          </>
        )}
      </div>

      <div className="sidebar-footer">
        <div className="sidebar-user-badge">
          <div className="user-avatar">
            {currentUser?.nombre ? currentUser.nombre[0].toUpperCase() : 'U'}
          </div>
          <div className="user-details">
            <div className="user-name" style={{ fontWeight: 600, fontSize: '0.85rem' }}>{currentUser?.nombre} {currentUser?.apellido}</div>
            <div className="user-role" style={{ fontSize: '0.75rem', color: 'var(--accent-primary)', fontWeight: 700 }}>{currentUser?.rol}</div>
          </div>
        </div>
        <button className="sidebar-logout-btn" onClick={onLogout} title="Cerrar Sesión">
          <LogOut size={16} />
          <span>Cerrar Sesión</span>
        </button>
      </div>
    </div>
  );
}

// --- COMPONENTE: INICIO (KPIs Y DASHBOARD GENERAL) ---
function HomeView({ produccion, serverStatus }) {
  const totalPaletas = produccion.reduce((acc, curr) => acc + (parseFloat(curr.paletas_producidas) || 0), 0);
  const totalGruesasProducidas = produccion.reduce((acc, curr) => acc + (parseFloat(curr.gruesas_producidas) || 0), 0);
  const totalGruesasEmpacadas = produccion.reduce((acc, curr) => acc + (parseFloat(curr.gruesas_empacadas) || 0), 0);
  const totalGruesasRetenidas = produccion.reduce((acc, curr) => acc + (parseFloat(curr.gruesas_retenidas) || 0), 0);
  const eficienciaPromedio = totalGruesasProducidas > 0 
    ? ((totalGruesasEmpacadas / totalGruesasProducidas) * 100).toFixed(1) 
    : 0;

  return (
    <>
      <PageHeader title="Panel Zona Caliente" description="Resumen de indicadores clave de formación y calidad en tiempo real." serverStatus={serverStatus} />
      
      {/* GRID DE INDICADORES */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-title">Eficiencia de Empaque</div>
          <div className="stat-value">{eficienciaPromedio}%</div>
          <div className="stat-desc">Promedio general de empaque</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">Paletas Producidas</div>
          <div className="stat-value">{totalPaletas.toFixed(1)}</div>
          <div className="stat-desc">Volumen total en paletas</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">Gruesas Empacadas</div>
          <div className="stat-value">{totalGruesasEmpacadas.toLocaleString()}</div>
          <div className="stat-desc">Unidades listas para envío</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">Retenidas por Calidad</div>
          <div className="stat-value" style={{ color: totalGruesasRetenidas > 0 ? 'var(--warning)' : 'var(--text-primary)' }}>
            {totalGruesasRetenidas.toLocaleString()}
          </div>
          <div className="stat-desc">En observación o cuarentena</div>
        </div>
      </div>

      <div className="panel-card" style={{ marginTop: '2rem', padding: '2.5rem' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
          <Flame className="header-flame" size={24} /> Módulo Zona Caliente - Venvidrio
        </h2>
        <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6', fontSize: '1rem', maxWidth: '800px' }}>
          Bienvenido al sistema unificado de control de planta. Utilice el menú lateral flotante para ingresar partes diarios de producción, registrar controles físicos de calidad (inspecciones) y registrar paradas de secciones IS.
        </p>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '1.5rem' }}>
          * Las tablas de configuración y catálogos de base de datos están restringidas al personal Administrador del sistema.
        </p>
      </div>
    </>
  );
}

// --- COMPONENTE: PROTECCIÓN DE RUTAS DE ADMINISTRACIÓN ---
function ProtectedRoute({ children, currentUser }) {
  if (!currentUser || currentUser.rol !== 'Administrador') {
    return <Navigate to="/" replace />;
  }
  return children;
}

// --- COMPONENTE: CRUD GENÉRICO PARA TABLAS DE CONFIGURACIÓN ---
function GenericCRUD({ endpoint, title, idField, fields, displayColumns, serverStatus, onMutation }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formState, setFormState] = useState({});
  const [editingId, setEditingId] = useState(null);
  const [saving, setSaving] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/${endpoint}`);
      if (!response.ok) throw new Error('Error al cargar datos');
      const json = await response.json();
      setData(json);
      setError(null);
    } catch (err) {
      setError('No se pudo conectar con el servidor para esta tabla.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const initialForm = {};
    fields.forEach(f => {
      initialForm[f.name] = f.defaultValue !== undefined ? f.defaultValue : '';
    });
    setFormState(initialForm);
    setEditingId(null);
  }, [endpoint]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    
    const payload = {};
    fields.forEach(f => {
      let val = formState[f.name];
      if (editingId && f.name === 'clave' && !val) {
        return; // Excluir contraseña si se deja en blanco al editar
      }
      if (f.type === 'number') {
        val = val === '' ? null : parseFloat(val);
      }
      payload[f.name] = val;
    });

    try {
      let url = `${API_BASE_URL}/api/${endpoint}`;
      let method = 'POST';
      if (editingId) {
        url = `${API_BASE_URL}/api/${endpoint}/${editingId}`;
        method = 'PUT';
      }

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errJson = await response.json();
        throw new Error(errJson.detail || 'Error al procesar la solicitud.');
      }

      const initialForm = {};
      fields.forEach(f => {
        initialForm[f.name] = f.defaultValue !== undefined ? f.defaultValue : '';
      });
      setFormState(initialForm);
      setEditingId(null);
      loadData();
      if (onMutation) onMutation();
    } catch (err) {
      alert(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (record) => {
    setEditingId(record[idField]);
    const editForm = {};
    fields.forEach(f => {
      if (f.name === 'clave') {
        editForm[f.name] = ''; // Dejar contraseña vacía por defecto
      } else {
        editForm[f.name] = record[f.name] !== null && record[f.name] !== undefined ? record[f.name].toString() : '';
      }
    });
    setFormState(editForm);
  };

  const handleDelete = async (id) => {
    if (!confirm('¿Está seguro de eliminar este registro? Esta acción es irreversible.')) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/${endpoint}/${id}`, {
        method: 'DELETE'
      });
      if (!response.ok) {
        const errJson = await response.json();
        throw new Error(errJson.detail || 'No se pudo eliminar el registro.');
      }
      loadData();
      if (onMutation) onMutation();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <>
      <PageHeader title={`Mantenimiento: ${title}`} description={`Pantalla de configuración y CRUD de la tabla '${endpoint}'.`} serverStatus={serverStatus} />
      
      <div className="main-content split-view">
        {/* LISTA */}
        <div className="panel-card">
          <div className="panel-header">
            <h2>Listado de {title}</h2>
            <button className="btn btn-secondary" onClick={loadData}><RefreshCw size={14} /> Recargar</button>
          </div>

          {loading ? (
            <div className="empty-state"><p>Cargando registros...</p></div>
          ) : error ? (
            <div className="alert alert-danger">{error}</div>
          ) : data.length === 0 ? (
            <div className="empty-state"><p>No hay datos registrados en esta tabla.</p></div>
          ) : (
            <div className="table-responsive">
              <table className="table-custom">
                <thead>
                  <tr>
                    {displayColumns.map(col => <th key={col.name}>{col.label}</th>)}
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map(record => (
                    <tr key={record[idField]}>
                      {displayColumns.map(col => {
                        let val = record[col.name];
                        if (col.type === 'badge') {
                          const isAct = val === 'ACTIVO' || val === 'ACTIVA';
                          return (
                            <td key={col.name}>
                              <span className={`badge ${isAct ? 'badge-success' : 'badge-danger'}`}>
                                {val}
                              </span>
                            </td>
                          );
                        }
                        return <td key={col.name}>{val}</td>;
                      })}
                      <td>
                        <button className="btn-icon edit" onClick={() => handleEdit(record)} title="Editar"><Pencil size={14} /></button>
                        <button className="btn-icon delete" onClick={() => handleDelete(record[idField])} title="Eliminar"><Trash2 size={14} /></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* FORMULARIO */}
        <div className="panel-card form-panel">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
            {editingId ? <><Pencil size={18} /> Editar {title.slice(0, -1)}</> : <><PlusCircle size={18} /> Registrar {title.slice(0, -1)}</>}
          </h2>
          <form onSubmit={handleSubmit}>
            {fields.map(f => (
              <div className="form-group" key={f.name}>
                <label>
                  {f.label} {f.required && !(f.name === 'clave' && editingId) && '*'}
                </label>
                {f.type === 'select' ? (
                  <select 
                    className="form-control" 
                    value={formState[f.name] || ''} 
                    onChange={e => setFormState({ ...formState, [f.name]: e.target.value })}
                    required={f.required}
                  >
                    <option value="">-- Seleccionar --</option>
                    {f.options.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                  </select>
                ) : (
                  <input 
                    type={f.type || 'text'} 
                    className="form-control" 
                    value={formState[f.name] || ''} 
                    onChange={e => setFormState({ ...formState, [f.name]: e.target.value })}
                    placeholder={f.placeholder || ''}
                    required={f.required && !(f.name === 'clave' && editingId)}
                  />
                )}
              </div>
            ))}
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1.5rem' }}>
              <button type="submit" className="btn btn-primary" style={{ flex: 1 }} disabled={saving}>
                {saving ? 'Guardando...' : 'Guardar Datos'}
              </button>
              {editingId && (
                <button type="button" className="btn btn-secondary" onClick={() => {
                  setEditingId(null);
                  const initialForm = {};
                  fields.forEach(f => {
                    initialForm[f.name] = f.defaultValue !== undefined ? f.defaultValue : '';
                  });
                  setFormState(initialForm);
                }}>
                  Cancelar
                </button>
              )}
            </div>
          </form>
        </div>
      </div>
    </>
  );
}

// --- COMPONENTE PRINCIPAL ---
export default function App() {
  // --- AUTENTICACIÓN ---
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem('venvidrio_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loginForm, setLoginForm] = useState({ usuario: '', clave: '' });
  const [loginError, setLoginError] = useState(null);
  const [loggingIn, setLoggingIn] = useState(false);

  // --- CONFIGURACIÓN Y ESTADO DE CONEXIÓN ---
  const [serverStatus, setServerStatus] = useState({ online: false, db_connected: false });
  const [notification, setNotification] = useState(null);

  // --- LISTAS MAESTRAS (DROPDOWNS) ---
  const [usuarios, setUsuarios] = useState([]);
  const [turnos, setTurnos] = useState([]);
  const [maquinas, setMaquinas] = useState([]);
  const [secciones, setSecciones] = useState([]);
  const [productos, setProductos] = useState([]);
  const [catalogoDefectos, setCatalogoDefectos] = useState([]);
  const [inspectores, setInspectores] = useState([]);
  const [tiposParadas, setTiposParadas] = useState([]);

  // --- LISTAS TRANSACCIONALES ---
  const [produccion, setProduccion] = useState([]);
  const [inspecciones, setInspecciones] = useState([]);
  const [paradas, setParadas] = useState([]);

  // --- FORMULARIOS TRANSACCIONALES ---
  const [produccionForm, setProduccionForm] = useState({
    fecha: new Date().toISOString().split('T')[0],
    id_turno: '', id_maquina: '', id_producto: '', id_usuario: '',
    paletas_producidas: 0, gruesas_producidas: 0, gruesas_empacadas: 0, gruesas_retenidas: 0,
    observaciones: ''
  });
  const [editingProduccionId, setEditingProduccionId] = useState(null);

  const [inspeccionForm, setInspeccionForm] = useState({
    fecha: new Date().toISOString().split('T')[0],
    hora: new Date().toTimeString().split(' ')[0],
    id_turno: '', id_inspector: '', id_maquina: '', id_seccion: '', id_producto: '',
    lote: '', temperatura_maquina: 1100, observaciones: ''
  });
  const [editingInspeccionId, setEditingInspeccionId] = useState(null);

  const [paradaForm, setParadaForm] = useState({
    fecha: new Date().toISOString().split('T')[0],
    id_turno: '', id_maquina: '', id_seccion: '', id_tipo_parada: '',
    hora_inicio: '', hora_fin: '', minutos_parada: 0, descripcion: ''
  });
  const [editingParadaId, setEditingParadaId] = useState(null);

  // --- CARGA DE DATOS INICIALES ---
  useEffect(() => {
    checkSystemStatus();
    loadInitData();
    const statusInterval = setInterval(checkSystemStatus, 60000);
    return () => clearInterval(statusInterval);
  }, []);

  // Preseleccionar usuario en producción
  useEffect(() => {
    if (currentUser && !produccionForm.id_usuario) {
      setProduccionForm(prev => ({ ...prev, id_usuario: currentUser.id_usuario.toString() }));
    }
  }, [currentUser]);

  // Carga perezosa (lazy) de listas operativas al autenticarse
  useEffect(() => {
    if (currentUser) {
      fetchData('produccion', setProduccion);
      fetchData('inspecciones', setInspecciones);
      fetchData('paradas', setParadas);
    }
  }, [currentUser]);

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  const checkSystemStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/status`);
      if (response.ok) {
        const data = await response.json();
        setServerStatus({ online: true, db_connected: data.db_connected });
      } else {
        setServerStatus({ online: false, db_connected: false });
      }
    } catch {
      setServerStatus({ online: false, db_connected: false });
    }
  };

  const loadInitData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/init-data`);
      if (response.ok) {
        const data = await response.json();
        setUsuarios(data.usuarios || []);
        setTurnos(data.turnos || []);
        setMaquinas(data.maquinas || []);
        setSecciones(data.secciones || []);
        setProductos(data.productos || []);
        setCatalogoDefectos(data.catalogo_defectos || []);
        setInspectores(data.inspectores || []);
        setTiposParadas(data.tipos_paradas || []);
      }
    } catch (err) {
      console.error('Error cargando iniciales:', err);
    }
  };

  const fetchData = async (endpoint, setter) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/${endpoint}`);
      if (response.ok) {
        const json = await response.json();
        setter(json);
      }
    } catch (err) {
      console.error(`Error cargando ${endpoint}:`, err);
    }
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoginError(null);
    setLoggingIn(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm)
      });
      if (response.ok) {
        const user = await response.json();
        setCurrentUser(user);
        localStorage.setItem('venvidrio_user', JSON.stringify(user));
        showNotification(`¡Sesión iniciada como ${user.nombre}!`);
      } else {
        const err = await response.json();
        setLoginError(err.detail || 'Usuario o contraseña incorrectos.');
      }
    } catch {
      setLoginError('No se pudo conectar con el servidor backend.');
    } finally {
      setLoggingIn(false);
    }
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('venvidrio_user');
    setLoginForm({ usuario: '', clave: '' });
    showNotification('Sesión finalizada.');
  };

  // --- TRANSACCIONAL: PRODUCCIÓN ---
  const handleProduccionSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingProduccionId 
        ? `${API_BASE_URL}/api/produccion/${editingProduccionId}`
        : `${API_BASE_URL}/api/produccion`;
      
      const response = await fetch(url, {
        method: editingProduccionId ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fecha: produccionForm.fecha,
          id_turno: parseInt(produccionForm.id_turno, 10),
          id_maquina: parseInt(produccionForm.id_maquina, 10),
          id_producto: parseInt(produccionForm.id_producto, 10),
          id_usuario: parseInt(produccionForm.id_usuario, 10),
          paletas_producidas: parseFloat(produccionForm.paletas_producidas) || 0,
          gruesas_producidas: parseFloat(produccionForm.gruesas_producidas) || 0,
          gruesas_empacadas: parseFloat(produccionForm.gruesas_empacadas) || 0,
          gruesas_retenidas: parseFloat(produccionForm.gruesas_retenidas) || 0,
          observaciones: produccionForm.observaciones
        })
      });

      if (response.ok) {
        showNotification(editingProduccionId ? 'Producción actualizada.' : 'Producción registrada.');
        setEditingProduccionId(null);
        setProduccionForm({
          fecha: new Date().toISOString().split('T')[0],
          id_turno: '', id_maquina: '', id_producto: '', id_usuario: currentUser.id_usuario.toString(),
          paletas_producidas: 0, gruesas_producidas: 0, gruesas_empacadas: 0, gruesas_retenidas: 0, observaciones: ''
        });
        fetchData('produccion', setProduccion);
      } else {
        const err = await response.json();
        alert(`Error: ${err.detail}`);
      }
    } catch {
      alert('Error en conexión con el backend.');
    }
  };

  const handleDeleteProduccion = async (id) => {
    if (!confirm('¿Seguro que desea eliminar el registro de producción?')) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/produccion/${id}`, { method: 'DELETE' });
      if (response.ok) {
        showNotification('Registro eliminado.');
        fetchData('produccion', setProduccion);
      }
    } catch {
      alert('Error al conectar para eliminar.');
    }
  };

  // --- TRANSACCIONAL: INSPECCIONES ---
  const handleInspeccionSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingInspeccionId 
        ? `${API_BASE_URL}/api/inspecciones/${editingInspeccionId}`
        : `${API_BASE_URL}/api/inspecciones`;

      const response = await fetch(url, {
        method: editingInspeccionId ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fecha: inspeccionForm.fecha,
          hora: inspeccionForm.hora,
          id_turno: parseInt(inspeccionForm.id_turno, 10),
          id_inspector: parseInt(inspeccionForm.id_inspector, 10),
          id_maquina: parseInt(inspeccionForm.id_maquina, 10),
          id_seccion: parseInt(inspeccionForm.id_seccion, 10),
          id_producto: parseInt(inspeccionForm.id_producto, 10),
          lote: inspeccionForm.lote,
          temperatura_maquina: parseFloat(inspeccionForm.temperatura_maquina) || 0,
          observaciones: inspeccionForm.observaciones
        })
      });

      if (response.ok) {
        showNotification(editingInspeccionId ? 'Inspección actualizada.' : 'Inspección registrada.');
        setEditingInspeccionId(null);
        setInspeccionForm({
          fecha: new Date().toISOString().split('T')[0], hora: new Date().toTimeString().split(' ')[0],
          id_turno: '', id_inspector: '', id_maquina: '', id_seccion: '', id_producto: '', lote: '', temperatura_maquina: 1100, observaciones: ''
        });
        fetchData('inspecciones', setInspecciones);
      } else {
        const err = await response.json();
        alert(`Error: ${err.detail}`);
      }
    } catch {
      alert('Error en conexión con el backend.');
    }
  };

  const handleDeleteInspeccion = async (id) => {
    if (!confirm('¿Seguro que desea eliminar esta inspección?')) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/inspecciones/${id}`, { method: 'DELETE' });
      if (response.ok) {
        showNotification('Inspección eliminada.');
        fetchData('inspecciones', setInspecciones);
      }
    } catch {
      alert('Error en conexión.');
    }
  };

  // --- TRANSACCIONAL: PARADAS ---
  const handleParadaSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingParadaId 
        ? `${API_BASE_URL}/api/paradas/${editingParadaId}`
        : `${API_BASE_URL}/api/paradas`;

      const response = await fetch(url, {
        method: editingParadaId ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fecha: paradaForm.fecha,
          id_turno: parseInt(paradaForm.id_turno, 10),
          id_maquina: parseInt(paradaForm.id_maquina, 10),
          id_seccion: parseInt(paradaForm.id_seccion, 10),
          id_tipo_parada: parseInt(paradaForm.id_tipo_parada, 10),
          hora_inicio: paradaForm.hora_inicio || null,
          hora_fin: paradaForm.hora_fin || null,
          minutos_parada: parseInt(paradaForm.minutos_parada, 10) || 0,
          descripcion: paradaForm.descripcion
        })
      });

      if (response.ok) {
        showNotification(editingParadaId ? 'Parada actualizada.' : 'Parada registrada.');
        setEditingParadaId(null);
        setParadaForm({
          fecha: new Date().toISOString().split('T')[0],
          id_turno: '', id_maquina: '', id_seccion: '', id_tipo_parada: '', hora_inicio: '', hora_fin: '', minutos_parada: 0, descripcion: ''
        });
        fetchData('paradas', setParadas);
      } else {
        const err = await response.json();
        alert(`Error: ${err.detail}`);
      }
    } catch {
      alert('Error en conexión.');
    }
  };

  const handleDeleteParada = async (id) => {
    if (!confirm('¿Seguro que desea eliminar este registro de parada?')) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/paradas/${id}`, { method: 'DELETE' });
      if (response.ok) {
        showNotification('Registro de parada eliminado.');
        fetchData('paradas', setParadas);
      }
    } catch {
      alert('Error de conexión.');
    }
  };

  // --- CONFIGURACIÓN DE CAMPOS PARA CRUD GENÉRICO ---
  const usuariosFields = [
    { name: 'nombre', label: 'Nombre', required: true },
    { name: 'apellido', label: 'Apellido', required: true },
    { name: 'usuario', label: 'Nombre de Usuario', required: true },
    { name: 'clave', label: 'Contraseña (Nueva)', type: 'password', required: true },
    { name: 'cargo', label: 'Cargo' },
    { name: 'rol', label: 'Rol', type: 'select', required: true, defaultValue: 'Operador', options: [
      { value: 'Administrador', label: 'Administrador' },
      { value: 'Operador', label: 'Operador' },
      { value: 'Inspector', label: 'Inspector' }
    ]},
    { name: 'estado', label: 'Estado', type: 'select', required: true, defaultValue: 'ACTIVO', options: [
      { value: 'ACTIVO', label: 'Activo' },
      { value: 'INACTIVO', label: 'Inactivo' }
    ]}
  ];
  const usuariosCols = [
    { name: 'id_usuario', label: 'ID' },
    { name: 'usuario', label: 'Usuario' },
    { name: 'nombre', label: 'Nombre' },
    { name: 'apellido', label: 'Apellido' },
    { name: 'rol', label: 'Rol' },
    { name: 'cargo', label: 'Cargo' },
    { name: 'estado', label: 'Estado', type: 'badge' }
  ];

  const turnosFields = [
    { name: 'codigo_turno', label: 'Código de Turno', required: true, placeholder: 'Ej: Turno D' },
    { name: 'hora_inicio', label: 'Hora de Inicio (HH:MM:SS)', required: true, placeholder: 'Ej: 06:00:00' },
    { name: 'hora_fin', label: 'Hora de Fin (HH:MM:SS)', required: true, placeholder: 'Ej: 14:00:00' },
    { name: 'descripcion', label: 'Descripción' }
  ];
  const turnosCols = [
    { name: 'id_turno', label: 'ID' },
    { name: 'codigo_turno', label: 'Código' },
    { name: 'hora_inicio', label: 'Inicio' },
    { name: 'hora_fin', label: 'Fin' },
    { name: 'descripcion', label: 'Descripción' }
  ];

  const maquinasFields = [
    { name: 'codigo', label: 'Código de Máquina', required: true, placeholder: 'Ej: MAQ-IS-04' },
    { name: 'descripcion', label: 'Descripción' },
    { name: 'cantidad_secciones', label: 'Cantidad de Secciones', type: 'number', required: true, defaultValue: '8' },
    { name: 'estado', label: 'Estado', type: 'select', required: true, defaultValue: 'ACTIVA', options: [
      { value: 'ACTIVA', label: 'Activa' },
      { value: 'INACTIVA', label: 'Inactiva' },
      { value: 'MANTENIMIENTO', label: 'Mantenimiento' }
    ]}
  ];
  const maquinasCols = [
    { name: 'id_maquina', label: 'ID' },
    { name: 'codigo', label: 'Código' },
    { name: 'descripcion', label: 'Descripción' },
    { name: 'cantidad_secciones', label: 'Secciones' },
    { name: 'estado', label: 'Estado', type: 'badge' }
  ];

  const productosFields = [
    { name: 'codigo_producto', label: 'Código de Producto', required: true, placeholder: 'Ej: PROD-CERV-250' },
    { name: 'nombre_producto', label: 'Nombre del Producto', required: true, placeholder: 'Ej: Malta 250ml' },
    { name: 'capacidad_ml', label: 'Capacidad (ml)', type: 'number' },
    { name: 'peso_teorico', label: 'Peso Teórico (g)', type: 'number' },
    { name: 'cliente', label: 'Cliente', placeholder: 'Ej: Cervecería Polar' },
    { name: 'estado', label: 'Estado', type: 'select', required: true, defaultValue: 'ACTIVO', options: [
      { value: 'ACTIVO', label: 'Activo' },
      { value: 'INACTIVO', label: 'Inactivo' }
    ]}
  ];
  const productosCols = [
    { name: 'codigo_producto', label: 'Código' },
    { name: 'nombre_producto', label: 'Nombre' },
    { name: 'capacidad_ml', label: 'Cap. (ml)' },
    { name: 'peso_teorico', label: 'Peso (g)' },
    { name: 'cliente', label: 'Cliente' },
    { name: 'estado', label: 'Estado', type: 'badge' }
  ];

  const defectosFields = [
    { name: 'codigo_defecto', label: 'Código de Defecto', placeholder: 'Ej: DEF-C006' },
    { name: 'nombre', label: 'Nombre del Defecto', required: true, placeholder: 'Ej: Grieta en base' },
    { name: 'categoria', label: 'Categoría', required: true, placeholder: 'Ej: Formación' },
    { name: 'descripcion', label: 'Descripción' },
    { name: 'criticidad', label: 'Criticidad', type: 'select', required: true, defaultValue: 'MAYOR', options: [
      { value: 'CRITICO', label: 'Crítico' },
      { value: 'MAYOR', label: 'Mayor' },
      { value: 'MENOR', label: 'Menor' }
    ]},
    { name: 'estado', label: 'Estado', type: 'select', required: true, defaultValue: 'ACTIVO', options: [
      { value: 'ACTIVO', label: 'Activo' },
      { value: 'INACTIVO', label: 'Inactivo' }
    ]}
  ];
  const defectosCols = [
    { name: 'codigo_defecto', label: 'Código' },
    { name: 'nombre', label: 'Nombre' },
    { name: 'categoria', label: 'Categoría' },
    { name: 'criticidad', label: 'Criticidad' },
    { name: 'estado', label: 'Estado', type: 'badge' }
  ];

  const inspectoresFields = [
    { name: 'cedula', label: 'Cédula', required: true, placeholder: 'Ej: V-12345678' },
    { name: 'nombre', label: 'Nombre', required: true },
    { name: 'apellido', label: 'Apellido', required: true },
    { name: 'cargo', label: 'Cargo', placeholder: 'Ej: Inspector Guardia' },
    { name: 'telefono', label: 'Teléfono' },
    { name: 'correo', label: 'Correo Electrónico', type: 'email' },
    { name: 'estado', label: 'Estado', type: 'select', required: true, defaultValue: 'ACTIVO', options: [
      { value: 'ACTIVO', label: 'Activo' },
      { value: 'INACTIVO', label: 'Inactivo' }
    ]}
  ];
  const inspectoresCols = [
    { name: 'cedula', label: 'Cédula' },
    { name: 'nombre', label: 'Nombre' },
    { name: 'apellido', label: 'Apellido' },
    { name: 'cargo', label: 'Cargo' },
    { name: 'estado', label: 'Estado', type: 'badge' }
  ];

  const moldesFields = [
    { name: 'codigo_molde', label: 'Código de Molde', required: true, placeholder: 'Ej: MOL-CERV-330' },
    { name: 'descripcion', label: 'Descripción' },
    { name: 'fecha_instalacion', label: 'Fecha de Instalación', type: 'date' },
    { name: 'estado', label: 'Estado', type: 'select', required: true, defaultValue: 'ACTIVO', options: [
      { value: 'ACTIVO', label: 'Activo' },
      { value: 'INACTIVO', label: 'Inactivo' }
    ]}
  ];
  const moldesCols = [
    { name: 'id_molde', label: 'ID' },
    { name: 'codigo_molde', label: 'Código Molde' },
    { name: 'descripcion', label: 'Descripción' },
    { name: 'fecha_instalacion', label: 'Instalación' },
    { name: 'estado', label: 'Estado', type: 'badge' }
  ];

  const premoldesFields = [
    { name: 'codigo_premolde', label: 'Código de Premolde', required: true, placeholder: 'Ej: PREM-CERV-330' },
    { name: 'descripcion', label: 'Descripción' },
    { name: 'fecha_instalacion', label: 'Fecha de Instalación', type: 'date' },
    { name: 'estado', label: 'Estado', type: 'select', required: true, defaultValue: 'ACTIVO', options: [
      { value: 'ACTIVO', label: 'Activo' },
      { value: 'INACTIVO', label: 'Inactivo' }
    ]}
  ];
  const premoldesCols = [
    { name: 'id_premolde', label: 'ID' },
    { name: 'codigo_premolde', label: 'Código Premolde' },
    { name: 'descripcion', label: 'Descripción' },
    { name: 'fecha_instalacion', label: 'Instalación' },
    { name: 'estado', label: 'Estado', type: 'badge' }
  ];

  const tiposParadasFields = [
    { name: 'nombre', label: 'Nombre del Tipo de Parada', required: true, placeholder: 'Ej: Fallo Mecánico' },
    { name: 'descripcion', label: 'Descripción de Parada' }
  ];
  const tiposParadasCols = [
    { name: 'id_tipo_parada', label: 'ID' },
    { name: 'nombre', label: 'Tipo Parada' },
    { name: 'descripcion', label: 'Descripción' }
  ];

  // PANTALLA DE LOGIN SI NO HAY SESIÓN ACTIVA
  if (!currentUser) {
    return (
      <div className="login-overlay">
        <div className="login-card">
          <div className="login-title-section">
            <Flame size={48} className="login-logo-icon" />
            <h2>Venvidrio - Acceso</h2>
            <p>Sistema Operativo Zona Caliente</p>
          </div>
          
          {loginError && (
            <div className="alert alert-danger" style={{ fontSize: '0.85rem', padding: '0.75rem 1rem' }}>
              {loginError}
            </div>
          )}
          
          <form onSubmit={handleLoginSubmit}>
            <div className="form-group">
              <label>Usuario *</label>
              <input 
                type="text" 
                className="form-control" 
                placeholder="Nombre de usuario" 
                value={loginForm.usuario}
                onChange={e => setLoginForm({ ...loginForm, usuario: e.target.value })}
                required
              />
            </div>
            
            <div className="form-group">
              <label>Contraseña *</label>
              <input 
                type="password" 
                className="form-control" 
                placeholder="••••••••" 
                value={loginForm.clave}
                onChange={e => setLoginForm({ ...loginForm, clave: e.target.value })}
                required
              />
            </div>
            
            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1.5rem' }} disabled={loggingIn}>
              {loggingIn ? 'Iniciando sesión...' : 'Iniciar Sesión'}
            </button>
          </form>
          
          <div style={{ marginTop: '1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'center' }}>
            <p>Usuarios de prueba (Semillas):</p>
            <p style={{ marginTop: '0.25rem' }}>Administrador: <strong>admin</strong> / admin123</p>
            <p style={{ marginTop: '0.25rem' }}>Operador: <strong>jmendoza</strong> / operario123</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--bg-primary)' }}>
        {/* NOTIFICACIONES */}
        {notification && (
          <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 2000, animation: 'slideInRight 0.3s ease' }}>
            <div className={`alert alert-${notification.type}`} style={{ display: 'flex', alignItems: 'center', gap: '1rem', backdropFilter: 'blur(10px)' }}>
              <span>{notification.message}</span>
              <button onClick={() => setNotification(null)} style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', fontSize: '1.1rem' }}>&times;</button>
            </div>
          </div>
        )}

        {/* SIDEBAR FLOTANTE */}
        <Sidebar currentUser={currentUser} onLogout={handleLogout} />

        {/* CONTENIDO PRINCIPAL DE LA APLICACIÓN */}
        <div className="main-layout">
          <Routes>
            <Route path="/" element={<HomeView produccion={produccion} serverStatus={serverStatus} />} />
            
            {/* OPERACIÓN: PRODUCCIÓN */}
            <Route path="/produccion" element={
              <>
                <PageHeader title="Control de Producción" description="Registro del volumen diario de botellas y paletas empacadas." serverStatus={serverStatus} />
                <div className="main-content split-view">
                  {/* Listado */}
                  <div className="panel-card">
                    <div className="panel-header">
                      <h2>Historial de Producción</h2>
                      <button className="btn btn-secondary" onClick={() => fetchData('produccion', setProduccion)}><RefreshCw size={14} /> Recargar</button>
                    </div>

                    {produccion.length === 0 ? (
                      <div className="empty-state"><p>No hay registros de producción.</p></div>
                    ) : (
                      <div className="table-responsive">
                        <table className="table-custom">
                          <thead>
                            <tr>
                              <th>Fecha</th>
                              <th>Máquina</th>
                              <th>Turno</th>
                              <th>Producto</th>
                              <th>Paletas</th>
                              <th>Empacado (Gruesas)</th>
                              <th>Acciones</th>
                            </tr>
                          </thead>
                          <tbody>
                            {produccion.map(p => (
                              <tr key={p.id_produccion}>
                                <td>{p.fecha}</td>
                                <td><strong>{p.maquina_codigo}</strong></td>
                                <td>{p.turno_codigo}</td>
                                <td>{p.producto_nombre}</td>
                                <td>{p.paletas_producidas}</td>
                                <td>{p.gruesas_empacadas} / {p.gruesas_producidas}</td>
                                <td>
                                  <button className="btn-icon edit" onClick={() => {
                                    setEditingProduccionId(p.id_produccion);
                                    setProduccionForm({
                                      fecha: p.fecha, id_turno: p.id_turno, id_maquina: p.id_maquina, id_producto: p.id_producto, id_usuario: p.id_usuario,
                                      paletas_producidas: p.paletas_producidas, gruesas_producidas: p.gruesas_producidas,
                                      gruesas_empacadas: p.gruesas_empacadas, gruesas_retenidas: p.gruesas_retenidas,
                                      observaciones: p.observaciones || ''
                                    });
                                  }} title="Editar Registro"><Pencil size={14} /></button>
                                  {currentUser?.rol === 'Administrador' && (
                                    <button className="btn-icon delete" onClick={() => handleDeleteProduccion(p.id_produccion)} title="Eliminar Registro"><Trash2 size={14} /></button>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>

                  {/* Formulario */}
                  <div className="panel-card form-panel">
                    <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                      {editingProduccionId ? <><Pencil size={18} /> Editar Producción</> : <><PlusCircle size={18} /> Registrar Producción</>}
                    </h2>
                    <form onSubmit={handleProduccionSubmit}>
                      <div className="form-group">
                        <label>Fecha de Operación *</label>
                        <input type="date" className="form-control" value={produccionForm.fecha} onChange={e => setProduccionForm({ ...produccionForm, fecha: e.target.value })} required />
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Máquina IS *</label>
                          <select className="form-control" value={produccionForm.id_maquina} onChange={e => setProduccionForm({ ...produccionForm, id_maquina: e.target.value })} required>
                            <option value="">-- Seleccionar --</option>
                            {maquinas.filter(m => m.estado !== 'INACTIVA').map(m => <option key={m.id_maquina} value={m.id_maquina}>{m.codigo}</option>)}
                          </select>
                        </div>
                        <div className="form-group">
                          <label>Turno *</label>
                          <select className="form-control" value={produccionForm.id_turno} onChange={e => setProduccionForm({ ...produccionForm, id_turno: e.target.value })} required>
                            <option value="">-- Seleccionar --</option>
                            {turnos.map(t => <option key={t.id_turno} value={t.id_turno}>{t.codigo_turno}</option>)}
                          </select>
                        </div>
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Producto *</label>
                          <select className="form-control" value={produccionForm.id_producto} onChange={e => setProduccionForm({ ...produccionForm, id_producto: e.target.value })} required>
                            <option value="">-- Seleccionar --</option>
                            {productos.map(p => <option key={p.id_producto} value={p.id_producto}>{p.nombre_producto}</option>)}
                          </select>
                        </div>
                        <div className="form-group">
                          <label>Usuario Operador *</label>
                          <select className="form-control" value={produccionForm.id_usuario} onChange={e => setProduccionForm({ ...produccionForm, id_usuario: e.target.value })} required>
                            <option value="">-- Seleccionar --</option>
                            {usuarios.map(u => <option key={u.id_usuario} value={u.id_usuario}>{u.usuario} ({u.nombre})</option>)}
                          </select>
                        </div>
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Paletas Producidas</label>
                          <input type="number" step="0.1" className="form-control" value={produccionForm.paletas_producidas} onChange={e => setProduccionForm({ ...produccionForm, paletas_producidas: parseFloat(e.target.value) || 0 })} />
                        </div>
                        <div className="form-group">
                          <label>Gruesas Producidas</label>
                          <input type="number" className="form-control" value={produccionForm.gruesas_producidas} onChange={e => setProduccionForm({ ...produccionForm, gruesas_producidas: parseFloat(e.target.value) || 0 })} />
                        </div>
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Gruesas Empacadas</label>
                          <input type="number" className="form-control" value={produccionForm.gruesas_empacadas} onChange={e => setProduccionForm({ ...produccionForm, gruesas_empacadas: parseFloat(e.target.value) || 0 })} />
                        </div>
                        <div className="form-group">
                          <label>Gruesas Retenidas</label>
                          <input type="number" className="form-control" value={produccionForm.gruesas_retenidas} onChange={e => setProduccionForm({ ...produccionForm, gruesas_retenidas: parseFloat(e.target.value) || 0 })} />
                        </div>
                      </div>
                      <div className="form-group">
                        <label>Observaciones de Operación</label>
                        <textarea className="form-control" rows="3" value={produccionForm.observaciones} onChange={e => setProduccionForm({ ...produccionForm, observaciones: e.target.value })} placeholder="Fugas, fallos mecánicos, etc..."></textarea>
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                        <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>{editingProduccionId ? 'Guardar Cambios' : 'Registrar Producción'}</button>
                        {editingProduccionId && <button type="button" className="btn btn-secondary" onClick={() => {
                          setEditingProduccionId(null);
                          setProduccionForm({ fecha: new Date().toISOString().split('T')[0], id_turno: '', id_maquina: '', id_producto: '', id_usuario: currentUser.id_usuario.toString(), paletas_producidas: 0, gruesas_producidas: 0, gruesas_empacadas: 0, gruesas_retenidas: 0, observaciones: '' });
                        }}>Cancelar</button>}
                      </div>
                    </form>
                  </div>
                </div>
              </>
            } />

            {/* OPERACIÓN: INSPECCIONES */}
            <Route path="/inspecciones" element={
              <>
                <PageHeader title="Inspecciones de Calidad" description="Registro de fisuras, defectos y temperatura en Zona Caliente." serverStatus={serverStatus} />
                <div className="main-content split-view">
                  {/* Listado */}
                  <div className="panel-card">
                    <div className="panel-header">
                      <h2>Controles de Calidad</h2>
                      <button className="btn btn-secondary" onClick={() => fetchData('inspecciones', setInspecciones)}><RefreshCw size={14} /> Recargar</button>
                    </div>

                    {inspecciones.length === 0 ? (
                      <div className="empty-state"><p>No hay inspecciones registradas.</p></div>
                    ) : (
                      <div className="table-responsive">
                        <table className="table-custom">
                          <thead>
                            <tr>
                              <th>Fecha/Hora</th>
                              <th>Máquina/Sec.</th>
                              <th>Inspector</th>
                              <th>Producto</th>
                              <th>Lote</th>
                              <th>Temp. (°C)</th>
                              <th>Acciones</th>
                            </tr>
                          </thead>
                          <tbody>
                            {inspecciones.map(i => (
                              <tr key={i.id_inspeccion}>
                                <td>{i.fecha} {i.hora}</td>
                                <td><strong>{i.maquina_codigo}</strong> - Sec. {i.seccion_numero}</td>
                                <td>{i.inspector_nombre}</td>
                                <td>{i.producto_nombre}</td>
                                <td>{i.lote}</td>
                                <td>{i.temperatura_maquina}°C</td>
                                <td>
                                  <button className="btn-icon edit" onClick={() => {
                                    setEditingInspeccionId(i.id_inspeccion);
                                    setInspeccionForm({
                                      fecha: i.fecha, hora: i.hora, id_turno: i.id_turno, id_inspector: i.id_inspector,
                                      id_maquina: i.id_maquina, id_seccion: i.id_seccion, id_producto: i.id_producto,
                                      lote: i.lote || '', temperatura_maquina: i.temperatura_maquina, observaciones: i.observaciones || ''
                                    });
                                  }} title="Editar Registro"><Pencil size={14} /></button>
                                  {currentUser?.rol === 'Administrador' && (
                                    <button className="btn-icon delete" onClick={() => handleDeleteInspeccion(i.id_inspeccion)} title="Eliminar Registro"><Trash2 size={14} /></button>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>

                  {/* Formulario */}
                  <div className="panel-card form-panel">
                    <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                      {editingInspeccionId ? <><Pencil size={18} /> Editar Control</> : <><PlusCircle size={18} /> Registrar Control</>}
                    </h2>
                    <form onSubmit={handleInspeccionSubmit}>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Fecha *</label>
                          <input type="date" className="form-control" value={inspeccionForm.fecha} onChange={e => setInspeccionForm({ ...inspeccionForm, fecha: e.target.value })} required />
                        </div>
                        <div className="form-group">
                          <label>Hora *</label>
                          <input type="text" className="form-control" value={inspeccionForm.hora} onChange={e => setInspeccionForm({ ...inspeccionForm, hora: e.target.value })} required />
                        </div>
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Máquina IS *</label>
                          <select className="form-control" value={inspeccionForm.id_maquina} onChange={e => setInspeccionForm({ ...inspeccionForm, id_maquina: e.target.value, id_seccion: '' })} required>
                            <option value="">-- Seleccionar --</option>
                            {maquinas.map(m => <option key={m.id_maquina} value={m.id_maquina}>{m.codigo}</option>)}
                          </select>
                        </div>
                        <div className="form-group">
                          <label>Sección de Máquina *</label>
                          <select className="form-control" value={inspeccionForm.id_seccion} onChange={e => setInspeccionForm({ ...inspeccionForm, id_seccion: e.target.value })} required disabled={!inspeccionForm.id_maquina}>
                            <option value="">-- Seleccionar Sección --</option>
                            {secciones.filter(s => s.id_maquina === parseInt(inspeccionForm.id_maquina, 10)).map(s => (
                              <option key={s.id_seccion} value={s.id_seccion}>Sección #{s.numero_seccion}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Turno *</label>
                          <select className="form-control" value={inspeccionForm.id_turno} onChange={e => setInspeccionForm({ ...inspeccionForm, id_turno: e.target.value })} required>
                            <option value="">-- Seleccionar --</option>
                            {turnos.map(t => <option key={t.id_turno} value={t.id_turno}>{t.codigo_turno}</option>)}
                          </select>
                        </div>
                        <div className="form-group">
                          <label>Inspector de Guardia *</label>
                          <select className="form-control" value={inspeccionForm.id_inspector} onChange={e => setInspeccionForm({ ...inspeccionForm, id_inspector: e.target.value })} required>
                            <option value="">-- Seleccionar --</option>
                            {inspectores.map(i => <option key={i.id_inspector} value={i.id_inspector}>{i.nombre} {i.apellido}</option>)}
                          </select>
                        </div>
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Producto *</label>
                          <select className="form-control" value={inspeccionForm.id_producto} onChange={e => setInspeccionForm({ ...inspeccionForm, id_producto: e.target.value })} required>
                            <option value="">-- Seleccionar --</option>
                            {productos.map(p => <option key={p.id_producto} value={p.id_producto}>{p.nombre_producto}</option>)}
                          </select>
                        </div>
                        <div className="form-group">
                          <label>Lote de Producción</label>
                          <input type="text" className="form-control" value={inspeccionForm.lote} onChange={e => setInspeccionForm({ ...inspeccionForm, lote: e.target.value })} placeholder="Ej: L10-A" />
                        </div>
                      </div>
                      <div className="form-group">
                        <label>Temperatura Molde / Gota (°C)</label>
                        <input type="number" className="form-control" value={inspeccionForm.temperatura_maquina} onChange={e => setInspeccionForm({ ...inspeccionForm, temperatura_maquina: parseFloat(e.target.value) || 0 })} />
                      </div>
                      <div className="form-group">
                        <label>Observaciones Físicas</label>
                        <textarea className="form-control" rows="3" value={inspeccionForm.observaciones} onChange={e => setInspeccionForm({ ...inspeccionForm, observaciones: e.target.value })} placeholder="Ej: corona incompleta, fisura en base..."></textarea>
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                        <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>{editingInspeccionId ? 'Guardar Cambios' : 'Registrar Inspección'}</button>
                        {editingInspeccionId && <button type="button" className="btn btn-secondary" onClick={() => {
                          setEditingInspeccionId(null);
                          setInspeccionForm({ fecha: new Date().toISOString().split('T')[0], hora: new Date().toTimeString().split(' ')[0], id_turno: '', id_inspector: '', id_maquina: '', id_seccion: '', id_producto: '', lote: '', temperatura_maquina: 1100, observaciones: '' });
                        }}>Cancelar</button>}
                      </div>
                    </form>
                  </div>
                </div>
              </>
            } />

            {/* OPERACIÓN: PARADAS */}
            <Route path="/paradas" element={
              <>
                <PageHeader title="Tiempos de Parada" description="Registro de detención por sección IS en máquina formadora." serverStatus={serverStatus} />
                <div className="main-content split-view">
                  {/* Listado */}
                  <div className="panel-card">
                    <div className="panel-header">
                      <h2>Control de Tiempos de Parada</h2>
                      <button className="btn btn-secondary" onClick={() => fetchData('paradas', setParadas)}><RefreshCw size={14} /> Recargar</button>
                    </div>

                    {paradas.length === 0 ? (
                      <div className="empty-state"><p>No se registran paradas de secciones.</p></div>
                    ) : (
                      <div className="table-responsive">
                        <table className="table-custom">
                          <thead>
                            <tr>
                              <th>Fecha</th>
                              <th>Máquina / Secc.</th>
                              <th>Tipo Parada</th>
                              <th>Minutos</th>
                              <th>Detalle</th>
                              <th>Acciones</th>
                            </tr>
                          </thead>
                          <tbody>
                            {paradas.map(p => (
                              <tr key={p.id_parada}>
                                <td>{p.fecha}</td>
                                <td><strong>{p.maquina_codigo}</strong> - Secc. {p.seccion_numero}</td>
                                <td><span className="badge badge-warning">{p.tipo_parada_nombre}</span></td>
                                <td><strong>{p.minutos_parada} min</strong></td>
                                <td>{p.descripcion}</td>
                                <td>
                                  <button className="btn-icon edit" onClick={() => {
                                    setEditingParadaId(p.id_parada);
                                    setParadaForm({
                                      fecha: p.fecha, id_turno: p.id_turno, id_maquina: p.id_maquina, id_seccion: p.id_seccion,
                                      id_tipo_parada: p.id_tipo_parada, hora_inicio: p.hora_inicio ? p.hora_inicio.substring(0, 16) : '',
                                      hora_fin: p.hora_fin ? p.hora_fin.substring(0, 16) : '', minutos_parada: p.minutos_parada,
                                      descripcion: p.descripcion || ''
                                    });
                                  }} title="Editar Registro"><Pencil size={14} /></button>
                                  {currentUser?.rol === 'Administrador' && (
                                    <button className="btn-icon delete" onClick={() => handleDeleteParada(p.id_parada)} title="Eliminar Registro"><Trash2 size={14} /></button>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>

                  {/* Formulario */}
                  <div className="panel-card form-panel">
                    <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                      {editingParadaId ? <><Pencil size={18} /> Editar Parada</> : <><PlusCircle size={18} /> Registrar Parada</>}
                    </h2>
                    <form onSubmit={handleParadaSubmit}>
                      <div className="form-group">
                        <label>Fecha del Evento *</label>
                        <input type="date" className="form-control" value={paradaForm.fecha} onChange={e => setParadaForm({ ...paradaForm, fecha: e.target.value })} required />
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Máquina IS *</label>
                          <select className="form-control" value={paradaForm.id_maquina} onChange={e => setParadaForm({ ...paradaForm, id_maquina: e.target.value, id_seccion: '' })} required>
                            <option value="">-- Seleccionar --</option>
                            {maquinas.map(m => <option key={m.id_maquina} value={m.id_maquina}>{m.codigo}</option>)}
                          </select>
                        </div>
                        <div className="form-group">
                          <label>Sección Afectada *</label>
                          <select className="form-control" value={paradaForm.id_seccion} onChange={e => setParadaForm({ ...paradaForm, id_seccion: e.target.value })} required disabled={!paradaForm.id_maquina}>
                            <option value="">-- Seleccionar --</option>
                            {secciones.filter(s => s.id_maquina === parseInt(paradaForm.id_maquina, 10)).map(s => (
                              <option key={s.id_seccion} value={s.id_seccion}>Sección #{s.numero_seccion}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Turno *</label>
                          <select className="form-control" value={paradaForm.id_turno} onChange={e => setParadaForm({ ...paradaForm, id_turno: e.target.value })} required>
                            <option value="">-- Seleccionar --</option>
                            {turnos.map(t => <option key={t.id_turno} value={t.id_turno}>{t.codigo_turno}</option>)}
                          </select>
                        </div>
                        <div className="form-group">
                          <label>Tipo de Parada *</label>
                          <select className="form-control" value={paradaForm.id_tipo_parada} onChange={e => setParadaForm({ ...paradaForm, id_tipo_parada: e.target.value })} required>
                            <option value="">-- Seleccionar --</option>
                            {tiposParadas.map(tp => <option key={tp.id_tipo_parada} value={tp.id_tipo_parada}>{tp.nombre}</option>)}
                          </select>
                        </div>
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Hora Inicio</label>
                          <input type="datetime-local" className="form-control" value={paradaForm.hora_inicio} onChange={e => setParadaForm({ ...paradaForm, hora_inicio: e.target.value })} />
                        </div>
                        <div className="form-group">
                          <label>Hora Fin</label>
                          <input type="datetime-local" className="form-control" value={paradaForm.hora_fin} onChange={e => setParadaForm({ ...paradaForm, hora_fin: e.target.value })} />
                        </div>
                      </div>
                      <div className="form-group">
                        <label>Minutos Totales Detenido *</label>
                        <input type="number" className="form-control" value={paradaForm.minutos_parada} onChange={e => setParadaForm({ ...paradaForm, minutos_parada: parseInt(e.target.value, 10) || 0 })} required />
                      </div>
                      <div className="form-group">
                        <label>Descripción / Observación</label>
                        <textarea className="form-control" rows="3" value={paradaForm.descripcion} onChange={e => setParadaForm({ ...paradaForm, descripcion: e.target.value })} placeholder="Ej: Se atasca pinza de extracción, requiere reajuste técnico."></textarea>
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                        <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>{editingParadaId ? 'Guardar Parada' : 'Registrar Parada'}</button>
                        {editingParadaId && <button type="button" className="btn btn-secondary" onClick={() => {
                          setEditingParadaId(null);
                          setParadaForm({ fecha: new Date().toISOString().split('T')[0], id_turno: '', id_maquina: '', id_seccion: '', id_tipo_parada: '', hora_inicio: '', hora_fin: '', minutos_parada: 0, descripcion: '' });
                        }}>Cancelar</button>}
                      </div>
                    </form>
                  </div>
                </div>
              </>
            } />

            {/* RUTAS DE ADMINISTRACIÓN: CRUD GENÉRICOS DE CONFIGURACIÓN */}
            <Route path="/usuarios" element={
              <ProtectedRoute currentUser={currentUser}>
                <GenericCRUD 
                  endpoint="usuarios" title="Usuarios" idField="id_usuario" 
                  fields={usuariosFields} displayColumns={usuariosCols} 
                  serverStatus={serverStatus} onMutation={loadInitData} 
                />
              </ProtectedRoute>
            } />

            <Route path="/turnos" element={
              <ProtectedRoute currentUser={currentUser}>
                <GenericCRUD 
                  endpoint="turnos" title="Turnos" idField="id_turno" 
                  fields={turnosFields} displayColumns={turnosCols} 
                  serverStatus={serverStatus} onMutation={loadInitData} 
                />
              </ProtectedRoute>
            } />

            <Route path="/maquinas" element={
              <ProtectedRoute currentUser={currentUser}>
                <GenericCRUD 
                  endpoint="maquinas" title="Máquinas" idField="id_maquina" 
                  fields={maquinasFields} displayColumns={maquinasCols} 
                  serverStatus={serverStatus} onMutation={loadInitData} 
                />
              </ProtectedRoute>
            } />

            <Route path="/productos" element={
              <ProtectedRoute currentUser={currentUser}>
                <GenericCRUD 
                  endpoint="productos" title="Productos" idField="id_producto" 
                  fields={productosFields} displayColumns={productosCols} 
                  serverStatus={serverStatus} onMutation={loadInitData} 
                />
              </ProtectedRoute>
            } />

            <Route path="/defectos" element={
              <ProtectedRoute currentUser={currentUser}>
                <GenericCRUD 
                  endpoint="catalogo_defectos" title="Defectos" idField="id_defecto" 
                  fields={defectosFields} displayColumns={defectosCols} 
                  serverStatus={serverStatus} onMutation={loadInitData} 
                />
              </ProtectedRoute>
            } />

            <Route path="/inspectores" element={
              <ProtectedRoute currentUser={currentUser}>
                <GenericCRUD 
                  endpoint="inspectores" title="Inspectores" idField="id_inspector" 
                  fields={inspectoresFields} displayColumns={inspectoresCols} 
                  serverStatus={serverStatus} onMutation={loadInitData} 
                />
              </ProtectedRoute>
            } />

            <Route path="/moldes" element={
              <ProtectedRoute currentUser={currentUser}>
                <GenericCRUD 
                  endpoint="moldes" title="Moldes" idField="id_molde" 
                  fields={moldesFields} displayColumns={moldesCols} 
                  serverStatus={serverStatus} onMutation={loadInitData} 
                />
              </ProtectedRoute>
            } />

            <Route path="/premoldes" element={
              <ProtectedRoute currentUser={currentUser}>
                <GenericCRUD 
                  endpoint="premoldes" title="Premoldes" idField="id_premolde" 
                  fields={premoldesFields} displayColumns={premoldesCols} 
                  serverStatus={serverStatus} onMutation={loadInitData} 
                />
              </ProtectedRoute>
            } />

            <Route path="/tipos-paradas" element={
              <ProtectedRoute currentUser={currentUser}>
                <GenericCRUD 
                  endpoint="tipos_paradas" title="Tipos de Paradas" idField="id_tipo_parada" 
                  fields={tiposParadasFields} displayColumns={tiposParadasCols} 
                  serverStatus={serverStatus} onMutation={loadInitData} 
                />
              </ProtectedRoute>
            } />

            {/* REDIRECCIONAMIENTO GLOBAL */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          
          {/* FOOTER */}
          <footer style={{ marginTop: '3rem', borderTop: '1px solid var(--border)', paddingTop: '1.5rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            <p>Sistema Web de Gestión de Planta - Módulo de Zona Caliente.</p>
            <p style={{ marginTop: '0.25rem' }}>Venvidrio C.A. © 2026 - Control de Producción y Calidad de Envases.</p>
          </footer>
        </div>
      </div>
    </Router>
  );
}
