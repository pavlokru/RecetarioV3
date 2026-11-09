import streamlit as st
import json
import os
import uuid
from PIL import Image
from core import CatalogEngine
from data import RECETARIO_BASE

# ---------------------------------------------------------
# Configuración Inicial y CSS Variable (CDC Google Fonts)
# ---------------------------------------------------------
st.set_page_config(page_title="Recetario V2", page_icon=":material/restaurant_menu:", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    .material-symbols-rounded {
        font-family: 'Material Symbols Rounded' !important;
        font-variation-settings: 'FILL' 1, 'wght' 200, 'GRAD' 0, 'opsz' 24 !important;
        vertical-align: middle;
    }

    .icon-fill-accent { font-variation-settings: 'FILL' 1, 'wght' 600, 'GRAD' 0, 'opsz' 24 !important; color: #f59e0b; }
    .icon-thin-meta { font-variation-settings: 'FILL' 1, 'wght' 300, 'GRAD' -25, 'opsz' 20 !important; color: #89a9b2; font-size: 1.1rem; }

    .block-container { max-width: 1200px !important; padding-top: 2rem !important; padding-bottom: 2rem !important; }
    .stApp { background-color: #020617; color: #f8fafc; }
    header { visibility: hidden; }
   /* Textura de Fondo */
   
    .stApp { 
        background-color: #020617; 
        background-image: radial-gradient(#1e293b 1.5px, transparent 1.5px);
        background-size: 24px 24px;
        color: #f8fafc; 
    }
    header { visibility: hidden; } 
    /* ---------------------------------------------------------
       Etiqueta Única (Botón Horizontal de una sola línea)
       --------------------------------------------------------- */
    .etiqueta-unica {
        background-color: #334155; 
        color: #cbd5e1;
        padding: 0.35rem 0.8rem; 
        border-radius: 999px;
        font-size: 0.75rem; 
        font-weight: bold;
        display: inline-flex; 
        align-items: center;
        width: fit-content; 
        max-width: 100%; /* Evita que desborde la tarjeta */
        margin-bottom: 0.8rem;
        border: 1px solid #475569;
        box-sizing: border-box;
    }
    .etiqueta-unica span.text {
        white-space: nowrap; 
        overflow: hidden; 
        text-overflow: ellipsis; /* Añade "..." si es muy largo */
        display: inline-block;
        max-width: 100%;
    }
    
    /* Configuración de Inputs */
    div[data-testid="stWidgetLabel"] p, label[data-testid="stWidgetLabel"] { color: #2a568c !important; font-weight: 600 !important; }
    div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input { color: #676a88 !important; }
    div[data-testid="stButton"] button p { color: #676a88 !important; font-weight: 600; }

    /* ---------------------------------------------------------
       Checkboxes para Ingredientes y Pasos (Alineados a la Izquierda)
       --------------------------------------------------------- */
    /* Alineación de Checkboxes */
    div[data-testid="stCheckbox"] label p { 
        text-align: left !important; 
        white-space: normal !important; 
        color: #dc7cc1;
    }
    /* Efecto de tachado (strikethrough) al completar Ingrediente o Paso */
    div[data-testid="stCheckbox"] input:checked + div p {
        text-decoration: line-through;
        color: #dc7cc1 !important;
    }

    /* Centrado general adaptativo en Móviles */
    @media (max-width: 768px) {
        .block-container { padding-top: 1rem !important; display: flex; flex-direction: column; justify-content: center; }
        h1, h2, h3 { text-align: center !important; }
        
        /* Centrar textos normales, excluyendo explícitamente los checkboxes */
        .stMarkdown > div > p { text-align: center !important; }
        
        /* Centrar el contenedor del botón de etiquetas en móvil */
        .etiqueta-unica { margin: 0 auto 0.8rem auto !important; }
        div[data-testid="stVerticalBlock"] > div { margin-bottom: 0.3rem; }
    }

    
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Motor DB y Gestión de Imágenes
# ---------------------------------------------------------
engine = CatalogEngine()
engine.inicializar_semilla(RECETARIO_BASE)

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
        st.error(f"Error procesando la imagen: {e}")
        return None

# ---------------------------------------------------------
# Funciones UI (Modal CRUD)
# ---------------------------------------------------------
@st.dialog("Gestión de Receta", width="large")
def modal_detalles_receta(receta):
    tab_ver, tab_editar = st.tabs([":material/visibility: Ver Detalles", ":material/edit_document: Editar Receta"])
    
    try:
        ingredientes_lista = json.loads(receta.get("ingredientes") or "[]")
        pasos_lista = json.loads(receta.get("pasos") or "[]")
        etiquetas_lista = json.loads(receta.get("etiquetas") or "[]")
    except json.JSONDecodeError:
        ingredientes_lista, pasos_lista, etiquetas_lista = [], [], []

    with tab_ver:




        
        st.markdown(f"<h2 style='color: #f59e0b; margin-bottom: 0;'><span class='material-symbols-rounded icon-fill-accent' style='font-size: 2rem; margin-right: 10px;'>restaurant_menu</span><span style='color: #676a88; margin-right: 8px;'>#{receta['id']}</span>{receta['nombre']}</h2>", unsafe_allow_html=True)
        porciones_display = receta.get('porciones') or "Variable"
        st.caption(f":material/public: Origen: {receta['origen']} | :material/timer: {receta['tiempo_preparacion_min']} min | :material/bar_chart: Dificultad: {receta['dificultad']} | :material/restaurant: Porciones: {porciones_display}")

        # Agrupar Categoría y Etiquetas en un solo botón/linea para la vista de Gestión
        todas_las_etiquetas = []
        if receta['categoria']: todas_las_etiquetas.append(receta['categoria'])
        todas_las_etiquetas.extend(etiquetas_lista)
        
        if todas_las_etiquetas:
            etiquetas_str = " &nbsp;•&nbsp; ".join(todas_las_etiquetas)
            st.markdown(f"<div class='etiqueta-unica'><span class='material-symbols-rounded' style='font-size: 1rem; margin-right: 6px; flex-shrink: 0;'>sell</span><span class='text'>{etiquetas_str}</span></div>", unsafe_allow_html=True)
        
        st.divider()
        col_izq, col_der = st.columns([1, 1.2])
        
        with col_izq:
            st.subheader(":material/kitchen: Ingredientes")
            # Implementación de Checkboxes para Ingredientes
            for i, ing in enumerate(ingredientes_lista, 1): 
                st.checkbox(ing, key=f"chk_ing_{receta['id']}_{i}")
                
            st.write("") # Espaciador antes de la imagen
            if receta.get("imagen_url"): 
                st.image(receta["imagen_url"], use_container_width=True)

        with col_der:
            st.subheader(":material/format_list_numbered: Pasos")
            # Implementación de Checkboxes para Pasos
            for i, paso in enumerate(pasos_lista, 1): 
                st.checkbox(f"**Paso {i}:** {paso}", key=f"chk_paso_{receta['id']}_{i}")

        if receta.get("nota"): 
            st.info(f"**:material/tips_and_updates: Nota del Chef:**\n{receta['nota']}")

        st.divider()
        _, col_btn = st.columns([3, 1])
        with col_btn:
            if st.button("Eliminar", key=f"del_{receta['id']}", use_container_width=True, icon=":material/delete_forever:"):
                if receta.get("imagen_url") and os.path.exists(receta.get("imagen_url")):
                    try: os.remove(receta.get("imagen_url"))
                    except OSError: pass
                engine.eliminar_receta(receta['id'])
                st.rerun()

    with tab_editar:
        with st.form(f"form_editar_{receta['id']}"):
            c1, c2 = st.columns(2)
            with c1:
                e_nombre = st.text_input(":material/signature: Nombre", value=receta['nombre'])
                e_categoria = st.text_input(":material/category: Categoría", value=receta['categoria'])
                e_origen = st.text_input(":material/public: Origen", value=receta['origen'])
            with c2:
                idx_dificultad = ["Fácil", "Media", "Alta"].index(receta['dificultad']) if receta['dificultad'] in ["Fácil", "Media", "Alta"] else 0
                e_dificultad = st.selectbox(":material/bar_chart: Dificultad", ["Fácil", "Media", "Alta"], index=idx_dificultad)
                ct, cp = st.columns(2)
                with ct: e_tiempo = st.number_input(":material/timer: Tiempo (min)", min_value=1, value=int(receta['tiempo_preparacion_min'] or 30))
                with cp: e_porciones = st.number_input(":material/restaurant: Porciones", min_value=1, value=receta.get('porciones'), placeholder="Vacío si es flexible")
                    
            e_etiquetas = st.text_input(":material/sell: Etiquetas", value=", ".join(etiquetas_lista))
            e_ingredientes = st.text_area(":material/kitchen: Ingredientes (1 por línea)", value="\n".join(ingredientes_lista), height=150)
            e_pasos = st.text_area(":material/format_list_numbered: Pasos", value="\n".join(pasos_lista), height=150)
            e_nota = st.text_area(":material/sticky_note_2: Nota (ej. cantidades a gusto)", value=receta['nota'] or "")
            e_imagen = st.file_uploader(":material/add_a_photo: Reemplazar Fotografía", type=['jpg', 'jpeg', 'png', 'webp'])
            
            if st.form_submit_button("Guardar Cambios", type="primary", icon=":material/save:"):
                if not e_nombre or not e_ingredientes or not e_pasos:
                    st.error("⚠️ Nombre, ingredientes y pasos son obligatorios.")
                else:
                    ruta_final = receta['imagen_url']
                    if e_imagen:
                        nueva_ruta = procesar_y_guardar_imagen(e_imagen)
                        if nueva_ruta:
                            ruta_final = nueva_ruta
                            if receta.get("imagen_url") and os.path.exists(receta.get("imagen_url")):
                                try: os.remove(receta.get("imagen_url"))
                                except OSError: pass

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
st.markdown("""
    <h1 style='color: #f59e0b; padding-bottom: 1rem; display: flex; align-items: center; gap: 10px;'>
        <span class='material-symbols-rounded icon-fill-accent' style='font-size: 3.5rem;'>skillet</span> 
        Recetario Personalizado
    </h1>
""", unsafe_allow_html=True)

tab_catalogo, tab_nueva = st.tabs([":material/menu_book: **Catálogo**", ":material/add_circle: **Nueva Receta**"])
with tab_catalogo:




    busqueda = st.text_input(":material/search: **Buscar receta...**", placeholder="Ej. Pan de Yuca, Pizza, Postre...")
    recetas = engine.buscar(busqueda) if busqueda else engine.obtener_todos()

    if not recetas: 
        st.info("No se encontraron recetas en el catálogo.")
    else:
        cols = st.columns(2)
        for idx, receta in enumerate(recetas):
            with cols[idx % 2]:
                with st.container(border=True):
                    col_info, col_img = st.columns([2.5, 1], vertical_alignment="center")
                    
                    with col_info:
                        st.markdown(f"<h3 style='color: #f59e0b; margin-top: 0; padding-bottom: 0rem; font-size: 2.4rem;'><span style='color: #94a3b8;opacity: 0.6; font-size: 1.2rem; margin-right: 5px;'>#{receta['id']}</span>{receta['nombre']}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color: #94a3b8; font-size: 0.8rem; margin-bottom: 0.5rem;'><span class='material-symbols-rounded icon-thin-meta'>timer</span> {receta['tiempo_preparacion_min']} min<br><span class='material-symbols-rounded icon-thin-meta'>face</span> {receta['dificultad']}</p>", unsafe_allow_html=True)
                        
                        # ELIMINADO: Todo el bloque de "etiquetas_str" y "etiqueta-unica" de la vista principal
                        
                    with col_img:
                        if receta.get("imagen_url") and os.path.exists(receta["imagen_url"]):
                            st.image(receta["imagen_url"], use_container_width=True)
                        else:
                            st.markdown("<div style='text-align: center; color: #36220e; opacity: 0.5; margin-top: 0rem;'><span class='material-symbols-rounded' style='font-size: 6rem; font-variation-settings: \"FILL\" 0, \"wght\" 700;'>coffee</span></div>", unsafe_allow_html=True)

                    col_espacio, col_boton = st.columns([2, 1])

                with col_boton:
                 
                     if st.button("Ver/Editar", key=f"btn_overlay_{receta['id']}", use_container_width=True):
                      modal_detalles_receta(receta)

with tab_nueva:
    st.markdown("### Agregar Nueva Receta")
    with st.form("form_nueva", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            f_nombre = st.text_input(":material/signature: Nombre *", max_chars=100)
            f_categoria = st.text_input(":material/category: Categoría")
            f_origen = st.text_input(":material/public: Origen")
        with c2:
            f_dificultad = st.selectbox(":material/bar_chart: Dificultad", ["Fácil", "Media", "Alta"])
            ct, cp = st.columns(2)
            with ct: f_tiempo = st.number_input(":material/timer: Tiempo (min)", min_value=1, value=30)
            with cp: f_porciones = st.number_input(":material/restaurant: Porciones", min_value=1, value=None, placeholder="Vacío si es variable")
                
        f_etiquetas = st.text_input(":material/sell: Etiquetas (separadas por coma)")
        
        col_text_1, col_text_2 = st.columns(2)
        with col_text_1: f_ingredientes = st.text_area(":material/kitchen: Ingredientes *", height=150, placeholder="Ej: Harina 000 500g (100%)\nAgua 300ml (60%)")
        with col_text_2: f_pasos = st.text_area(":material/format_list_numbered: Pasos *", height=150)
            
        f_nota = st.text_area(":material/sticky_note_2: Notas adicionales (ej: condimentos a gusto)")
        f_imagen = st.file_uploader(":material/add_a_photo: Fotografía", type=['jpg', 'jpeg', 'png', 'webp'])
        
        if st.form_submit_button("Guardar Receta", type="primary", icon=":material/check_circle:"):
            if not f_nombre or not f_ingredientes or not f_pasos:
                st.error("⚠️ Nombre, ingredientes y pasos son obligatorios.")
            else:
                engine.crear_receta({
                    "nombre": f_nombre, "categoria": f_categoria, "origen": f_origen,
                    "dificultad": f_dificultad, "tiempo_preparacion_min": f_tiempo, "porciones": f_porciones,
                    "ingredientes": [i.strip() for i in f_ingredientes.split('\n') if i.strip()],
                    "pasos": [p.strip() for p in f_pasos.split('\n') if p.strip()],
                    "etiquetas": [e.strip() for e in f_etiquetas.split(',') if e.strip()],
                    "nota": f_nota, "imagen_url": procesar_y_guardar_imagen(f_imagen)
                })
                st.success(f"✅ ¡Receta guardada exitosamente!")
                st.rerun()