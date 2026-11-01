import streamlit as st
import json
import os
import uuid
from PIL import Image
from core import CatalogEngine
from data import RECETARIO_BASE

# ---------------------------------------------------------
# Configuración Inicial y CSS
# ---------------------------------------------------------
st.set_page_config(page_title="Recetario V2", page_icon="🍳", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #020617; color: #f8fafc; }
    .tarjeta-receta { 
        background-color: #0f172a; 
        padding: 1.5rem; 
        border-radius: 0.75rem; 
        border: 1px solid #1e293b;
        margin-bottom: 0.5rem;
    }
    .tarjeta-receta h3 { color: #f59e0b; margin-top: 0; padding-bottom: 0.5rem;}
    .metadatos { color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.8rem; }
    .etiqueta {
        background-color: #334155; color: #cbd5e1;
        padding: 0.2rem 0.6rem; border-radius: 999px;
        font-size: 0.75rem; font-weight: bold;
    }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Motor DB y Gestión de Imágenes
# ---------------------------------------------------------
engine = CatalogEngine()
engine.inicializar_semilla(RECETARIO_BASE) # Se ejecuta una vez si la DB está vacía

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def procesar_y_guardar_imagen(archivo_subido):
    if not archivo_subido: return None
    try:
        ext = archivo_subido.name.split('.')[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'webp']: ext = 'webp'
        ruta = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}.{ext}")
        
        img = Image.open(archivo_subido)
        if img.mode in ("RGBA", "P") and ext in ['jpg', 'jpeg']: img = img.convert("RGB")
        img.thumbnail((800, 800))
        img.save(ruta, optimize=True, quality=80)
        return ruta
    except Exception as e:
        st.error(f"Error imagen: {e}")
        return None

# ---------------------------------------------------------
# Funciones UI (Modal CRUD)
# ---------------------------------------------------------
@st.dialog("Gestión de Receta", width="large")
def modal_detalles_receta(receta):
    tab_ver, tab_editar = st.tabs(["👀 Ver Detalles", "✏️ Editar Receta"])
    
    # Manejo seguro de JSON
    try:
        ingredientes_lista = json.loads(receta.get("ingredientes") or "[]")
        pasos_lista = json.loads(receta.get("pasos") or "[]")
        etiquetas_lista = json.loads(receta.get("etiquetas") or "[]")
    except:
        ingredientes_lista, pasos_lista, etiquetas_lista = [], [], []

    with tab_ver:
        st.markdown(f"<h2 style='color: #f59e0b; margin-bottom: 0;'>{receta['nombre']}</h2>", unsafe_allow_html=True)
        st.caption(f"🌍 Origen: {receta['origen']} | ⏱️ {receta['tiempo_preparacion_min']} min | 📊 Dificultad: {receta['dificultad']} | 🍽️ Porciones: {receta.get('porciones', '')}")
        
        if etiquetas_lista:
            html_etiquetas = "".join([f"<span class='etiqueta' style='margin-right: 5px;'>{etq}</span>" for etq in etiquetas_lista])
            st.markdown(html_etiquetas, unsafe_allow_html=True)
        st.divider()

        col_izq, col_der = st.columns([1, 1.2])
        with col_izq:
            st.subheader("🛒 Ingredientes")
            for ing in ingredientes_lista: st.markdown(f"- {ing}")
            if receta.get("imagen_url"): st.image(receta["imagen_url"], use_container_width=True)

        with col_der:
            st.subheader("📝 Pasos")
            for i, paso in enumerate(pasos_lista, 1): st.markdown(f"**{i}.** {paso}")

        if receta.get("nota"): st.info(f"💡 **Nota del Chef:**\n{receta['nota']}")

        st.divider()
        _, col_btn = st.columns([3, 1])
        with col_btn:
            if st.button("🗑️ Eliminar", key=f"del_{receta['id']}", use_container_width=True):
                if receta.get("imagen_url") and os.path.exists(receta.get("imagen_url")):
                    try: os.remove(receta.get("imagen_url"))
                    except: pass
                engine.eliminar_receta(receta['id'])
                st.rerun()

    with tab_editar:
        with st.form(f"form_editar_{receta['id']}"):
            c1, c2 = st.columns(2)
            with c1:
                e_nombre = st.text_input("Nombre", value=receta['nombre'])
                e_categoria = st.text_input("Categoría", value=receta['categoria'])
                e_origen = st.text_input("Origen", value=receta['origen'])
            with c2:
                idx_dificultad = ["Fácil", "Media", "Alta"].index(receta['dificultad']) if receta['dificultad'] in ["Fácil", "Media", "Alta"] else 0
                e_dificultad = st.selectbox("Dificultad", ["Fácil", "Media", "Alta"], index=idx_dificultad)
                ct, cp = st.columns(2)
                with ct: e_tiempo = st.number_input("Tiempo", min_value=1, value=int(receta['tiempo_preparacion_min'] or 30))
                with cp: e_porciones = st.number_input("Porciones", min_value=1, value=int(receta['porciones'] or 2))
                    
            e_etiquetas = st.text_input("Etiquetas", value=", ".join(etiquetas_lista))
            e_ingredientes = st.text_area("Ingredientes", value="\n".join(ingredientes_lista), height=150)
            e_pasos = st.text_area("Pasos", value="\n".join(pasos_lista), height=150)
            e_nota = st.text_area("Nota", value=receta['nota'] or "")
            e_imagen = st.file_uploader("Reemplazar Fotografía", type=['jpg', 'jpeg', 'png', 'webp'])
            
            if st.form_submit_button("Guardar Cambios", type="primary"):
                if not e_nombre or not e_ingredientes or not e_pasos:
                    st.error("⚠️ Nombre, ingredientes y pasos obligatorios.")
                else:
                    ruta_final = receta['imagen_url']
                    if e_imagen:
                        nueva_ruta = procesar_y_guardar_imagen(e_imagen)
                        if nueva_ruta:
                            ruta_final = nueva_ruta
                            if receta.get("imagen_url") and os.path.exists(receta.get("imagen_url")):
                                try: os.remove(receta.get("imagen_url"))
                                except: pass

                    engine.actualizar_receta(receta['id'], {
                        "nombre": e_nombre, "categoria": e_categoria, "origen": e_origen,
                        "dificultad": e_dificultad, "tiempo_preparacion_min": e_tiempo, "porciones": e_porciones,
                        "ingredientes": [i.strip() for i in e_ingredientes.split('\n') if i.strip()],
                        "pasos": [p.strip() for p in e_pasos.split('\n') if p.strip()],
                        "etiquetas": [e.strip() for e in e_etiquetas.split(',') if e.strip()],
                        "nota": e_nota, "imagen_url": ruta_final
                    })
                    st.rerun()

# ---------------------------------------------------------
# Interfaz Principal
# ---------------------------------------------------------
st.markdown("<h1 style='color: #f59e0b;'>🍳 Recetario Ultra Ligero</h1>", unsafe_allow_html=True)
tab_catalogo, tab_nueva = st.tabs(["📚 Catálogo", "➕ Nueva Receta"])

with tab_catalogo:
    busqueda = st.text_input("🔍 Buscar receta...", placeholder="Ej. Chipá, Pizza, Postre...")
    recetas = engine.buscar(busqueda) if busqueda else engine.obtener_todos()

    if not recetas: st.warning("No se encontraron recetas.")
    for receta in recetas:
        st.markdown(f"""
        <div class="tarjeta-receta">
            <h3>{receta['nombre']}</h3>
            <div class="metadatos">⏳ {receta['tiempo_preparacion_min']} min &nbsp;|&nbsp; 📊 {receta['dificultad']} &nbsp;|&nbsp; 🌍 {receta['origen']}</div>
            <span class="etiqueta">{receta['categoria']}</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver / Editar", key=f"btn_{receta['id']}"): modal_detalles_receta(receta)

with tab_nueva:
    st.markdown("### Agregar Nueva Receta")
    with st.form("form_nueva", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            f_nombre = st.text_input("Nombre *", max_chars=100)
            f_categoria = st.text_input("Categoría")
            f_origen = st.text_input("Origen")
        with c2:
            f_dificultad = st.selectbox("Dificultad", ["Fácil", "Media", "Alta"])
            ct, cp = st.columns(2)
            with ct: f_tiempo = st.number_input("Tiempo (min)", min_value=1, value=30)
            with cp: f_porciones = st.number_input("Porciones", min_value=1, value=2)
                
        f_etiquetas = st.text_input("Etiquetas (separadas por coma)")
        f_ingredientes = st.text_area("Ingredientes * (Un ítem por línea)", height=150)
        f_pasos = st.text_area("Pasos * (Un paso por línea)", height=150)
        f_nota = st.text_area("Notas adicionales")
        f_imagen = st.file_uploader("Fotografía", type=['jpg', 'jpeg', 'png', 'webp'])
        
        if st.form_submit_button("Guardar Receta", type="primary"):
            if not f_nombre or not f_ingredientes or not f_pasos:
                st.error("⚠️ Nombre, ingredientes y pasos obligatorios.")
            else:
                engine.crear_receta({
                    "nombre": f_nombre, "categoria": f_categoria, "origen": f_origen,
                    "dificultad": f_dificultad, "tiempo_preparacion_min": f_tiempo, "porciones": f_porciones,
                    "ingredientes": [i.strip() for i in f_ingredientes.split('\n') if i.strip()],
                    "pasos": [p.strip() for p in f_pasos.split('\n') if p.strip()],
                    "etiquetas": [e.strip() for e in f_etiquetas.split(',') if e.strip()],
                    "nota": f_nota, "imagen_url": procesar_y_guardar_imagen(f_imagen)
                })
                st.success(f"✅ ¡Receta guardada!")
                st.rerun()