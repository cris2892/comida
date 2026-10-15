import os
import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y ESTILO
# ==============================================================================
st.set_page_config(
    page_title="Calculadora Metabólica & Macros",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de CSS para diseño moderno, tarjetas oscuras con bordes sutiles y badges de macros
st.markdown("""
<style>
    /* Estilos globales */
    .main {
        background-color: #0e1117;
    }
    
    /* Tarjetas Métricas Personalizadas */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px 0 rgba(0, 0, 0, 0.25);
    }
    .metric-title {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .metric-val {
        font-size: 1.65rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 4px;
    }
    
    /* Badges de Macros */
    .badge-p {
        background-color: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.35);
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-c {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-g {
        background-color: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.35);
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-kcal {
        background-color: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.35);
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    /* Contenedores de Perfil */
    .profile-card-he {
        border-left: 4px solid #3b82f6;
        background: rgba(30, 58, 138, 0.12);
        padding: 14px 16px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 12px;
    }
    .profile-card-she {
        border-left: 4px solid #ec4899;
        background: rgba(131, 24, 67, 0.12);
        padding: 14px 16px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BASE DE DATOS DE ALIMENTOS (POR CADA 100G CRUDO / SECO / NETO)
# ==============================================================================
BASE_ALIMENTOS = [
    # Carnes y Aves (en crudo)
    {"nombre": "Pechuga de pollo sin piel", "categoria": "Carnes y Aves", "kcal": 112.0, "p": 23.0, "c": 0.0, "g": 2.0},
    {"nombre": "Cuadril / Nalga / Bola de lomo magra", "categoria": "Carnes y Aves", "kcal": 132.0, "p": 21.5, "c": 0.0, "g": 4.8},
    {"nombre": "Lomo vacuno magro", "categoria": "Carnes y Aves", "kcal": 125.0, "p": 22.0, "c": 0.0, "g": 3.8},
    {"nombre": "Carne picada magra (5% grasa)", "categoria": "Carnes y Aves", "kcal": 137.0, "p": 21.4, "c": 0.0, "g": 5.0},
    {"nombre": "Vacío magro / Colita de cuadril", "categoria": "Carnes y Aves", "kcal": 155.0, "p": 20.5, "c": 0.0, "g": 7.8},
    {"nombre": "Carré o Solomillo de cerdo magro", "categoria": "Carnes y Aves", "kcal": 128.0, "p": 22.0, "c": 0.0, "g": 4.0},
    
    # Pescados, Huevos y Fiambres
    {"nombre": "Filet de merluza / Pescado blanco", "categoria": "Pescados, Huevos y Fiambres", "kcal": 86.0, "p": 18.0, "c": 0.0, "g": 1.3},
    {"nombre": "Atún al natural escurrido", "categoria": "Pescados, Huevos y Fiambres", "kcal": 108.0, "p": 24.0, "c": 0.0, "g": 1.0},
    {"nombre": "Huevo entero (1 u ≈ 55g)", "categoria": "Pescados, Huevos y Fiambres", "kcal": 143.0, "p": 12.6, "c": 0.7, "g": 9.5},
    {"nombre": "Claras de huevo líquidas", "categoria": "Pescados, Huevos y Fiambres", "kcal": 52.0, "p": 11.0, "c": 0.7, "g": 0.2},
    {"nombre": "Jamón cocido natural magro", "categoria": "Pescados, Huevos y Fiambres", "kcal": 105.0, "p": 19.0, "c": 1.5, "g": 2.5},

    # Lácteos
    {"nombre": "Yogur griego natural sin azúcar", "categoria": "Lácteos", "kcal": 71.0, "p": 9.5, "c": 4.0, "g": 1.8},
    {"nombre": "Labneh casero / Queso blanco descremado", "categoria": "Lácteos", "kcal": 85.0, "p": 11.0, "c": 4.0, "g": 2.8},
    {"nombre": "Queso Port Salut Light / Magro", "categoria": "Lácteos", "kcal": 225.0, "p": 24.0, "c": 1.0, "g": 14.0},
    {"nombre": "Leche descremada (100 ml)", "categoria": "Lácteos", "kcal": 35.0, "p": 3.4, "c": 5.0, "g": 0.1},

    # Cereales, Harinas, Legumbres y Tubérculos (en seco / crudo)
    {"nombre": "Arroz blanco o parboil (en seco)", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 356.0, "p": 7.0, "c": 79.0, "g": 0.6},
    {"nombre": "Fideos / Pasta seca", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 352.0, "p": 12.0, "c": 72.0, "g": 1.5},
    {"nombre": "Avena arrollada tradicional (en seco)", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 380.0, "p": 13.5, "c": 66.0, "g": 6.5},
    {"nombre": "Harina de trigo 000 / 0000", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 364.0, "p": 10.3, "c": 76.0, "g": 1.0},
    {"nombre": "Harina integral de trigo", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 340.0, "p": 13.0, "c": 72.0, "g": 2.5},
    {"nombre": "Harina de avena", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 380.0, "p": 14.0, "c": 65.0, "g": 7.0},
    {"nombre": "Harina de maíz / Polenta (en seco)", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 350.0, "p": 8.0, "c": 77.0, "g": 1.0},
    {"nombre": "Fécula de maíz / Maicena", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 355.0, "p": 0.3, "c": 88.0, "g": 0.1},
    {"nombre": "Harina de arroz", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 366.0, "p": 6.0, "c": 80.0, "g": 1.4},
    {"nombre": "Fécula de mandioca / Tapioca", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 358.0, "p": 0.2, "c": 88.0, "g": 0.0},
    {"nombre": "Harina de almendras (baja en carbos)", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 590.0, "p": 21.4, "c": 18.0, "g": 50.0},
    {"nombre": "Lentejas secas", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 335.0, "p": 24.0, "c": 56.0, "g": 1.2},
    {"nombre": "Garbanzos secos", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 364.0, "p": 19.0, "c": 61.0, "g": 6.0},
    {"nombre": "Panko / Pan rallado", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 350.0, "p": 10.0, "c": 74.0, "g": 1.5},
    {"nombre": "Pan integral de molde", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 250.0, "p": 10.0, "c": 43.0, "g": 3.5},
    {"nombre": "Tortilla de trigo mediana (1 u ≈ 40g)", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 310.0, "p": 8.0, "c": 52.0, "g": 7.5},
    {"nombre": "Papa en crudo (pelada/lavada)", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 77.0, "p": 2.0, "c": 17.0, "g": 0.1},
    {"nombre": "Batata / Boniato en crudo", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 86.0, "p": 1.6, "c": 20.0, "g": 0.1},
    {"nombre": "Calabaza cabutia en crudo", "categoria": "Cereales, Legumbres y Tubérculos", "kcal": 34.0, "p": 1.0, "c": 8.0, "g": 0.1},

    # Grasas, Frutas y Vegetales
    {"nombre": "Aceite de oliva virgen extra", "categoria": "Grasas, Frutas y Vegetales", "kcal": 884.0, "p": 0.0, "c": 0.0, "g": 100.0},
    {"nombre": "Palta / Aguacate", "categoria": "Grasas, Frutas y Vegetales", "kcal": 160.0, "p": 2.0, "c": 8.5, "g": 14.7},
    {"nombre": "Almendras o Nueces", "categoria": "Grasas, Frutas y Vegetales", "kcal": 610.0, "p": 18.0, "c": 14.0, "g": 54.0},
    {"nombre": "Pasta de maní 100% natural", "categoria": "Grasas, Frutas y Vegetales", "kcal": 588.0, "p": 25.0, "c": 20.0, "g": 50.0},
    {"nombre": "Banana (sin cáscara)", "categoria": "Grasas, Frutas y Vegetales", "kcal": 89.0, "p": 1.1, "c": 22.8, "g": 0.3},
    {"nombre": "Manzana / Pera / Naranja", "categoria": "Grasas, Frutas y Vegetales", "kcal": 52.0, "p": 0.3, "c": 13.8, "g": 0.2},
    {"nombre": "Mix vegetales verdes / Brócoli / Tomate / Cebolla", "categoria": "Grasas, Frutas y Vegetales", "kcal": 28.0, "p": 2.0, "c": 5.0, "g": 0.2}
]

# Archivos de persistencia local
ARCHIVO_ALIMENTOS_CUSTOM = "alimentos_custom.json"
ARCHIVO_RECETAS = "recetas_guardadas.json"
ARCHIVO_CONFIG_USUARIO = "config_usuario.json"

CONFIG_DEFAULT = {
    "peso_el": 119.0,
    "altura_el": 180,
    "edad_el": 34,
    "opcion_act_el": "📉 Déficit Moderado (Base 2150 kcal)",
    "custom_kcal_el": 2150.0,
    "custom_p_el": 188.0,
    "custom_c_el": 210.0,
    "custom_g_el": 60.0,
    "modo_pers_el": "Calorías Totales Directas (kcal)",
    "peso_ella": 69.0,
    "altura_ella": 150,
    "edad_ella": 33,
    "opcion_act_ella": "📉 Déficit Moderado (Base 1300 kcal)",
    "custom_kcal_ella": 1300.0,
    "custom_p_ella": 115.0,
    "custom_c_ella": 120.0,
    "custom_g_ella": 38.0,
    "modo_pers_ella": "Calorías Totales Directas (kcal)",
    "horas_sem": 3.0,
    "opcion_mets": "4.0 METs - Caminata paso constante/ligero (4.8 - 5.0 km/h)",
    "tipo_reparto": "Dinámica según Metas Calóricas"
}

def normalizar_opcion_act_el(op):
    if not op:
        return "📉 Déficit Moderado (Base 2150 kcal)"
    if "Superávit" in op or "Superavit" in op:
        return "📈 Superávit (+300 kcal Ganancia / Volumen)"
    if "Mantenimiento" in op:
        return "⚖️ Mantenimiento Metabólico (TDEE)"
    if "Personalizado" in op:
        return "🛠️ Personalizado (Ajustar a mano kcal o macros)"
    if "Activo" in op or "2400" in op:
        return "📉 Déficit Ligero (Base 2400 kcal)"
    return "📉 Déficit Moderado (Base 2150 kcal)"

def normalizar_opcion_act_ella(op):
    if not op:
        return "📉 Déficit Moderado (Base 1300 kcal)"
    if "Superávit" in op or "Superavit" in op:
        return "📈 Superávit (+250 kcal Ganancia / Volumen)"
    if "Mantenimiento" in op:
        return "⚖️ Mantenimiento Metabólico (TDEE)"
    if "Personalizada" in op or "Personalizado" in op:
        return "🛠️ Personalizada (Ajustar a mano kcal o macros)"
    if "Activa" in op or "1500" in op:
        return "📉 Déficit Ligero (Base 1500 kcal)"
    return "📉 Déficit Moderado (Base 1300 kcal)"

def cargar_config_usuario():
    cfg = dict(CONFIG_DEFAULT)
    if os.path.exists(ARCHIVO_CONFIG_USUARIO):
        try:
            with open(ARCHIVO_CONFIG_USUARIO, "r", encoding="utf-8") as f:
                guardado = json.load(f)
                cfg.update(guardado)
        except Exception:
            pass
    cfg["opcion_act_el"] = normalizar_opcion_act_el(cfg.get("opcion_act_el"))
    cfg["opcion_act_ella"] = normalizar_opcion_act_ella(cfg.get("opcion_act_ella"))
    return cfg

def guardar_config_usuario(cfg):
    try:
        with open(ARCHIVO_CONFIG_USUARIO, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def cargar_alimentos_custom():
    if os.path.exists(ARCHIVO_ALIMENTOS_CUSTOM):
        try:
            with open(ARCHIVO_ALIMENTOS_CUSTOM, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def guardar_alimentos_custom(lista):
    try:
        with open(ARCHIVO_ALIMENTOS_CUSTOM, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error al guardar alimentos personalizados: {e}")

def cargar_recetas_guardadas():
    if os.path.exists(ARCHIVO_RECETAS):
        try:
            with open(ARCHIVO_RECETAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def guardar_recetas_guardadas(recetas_dict):
    try:
        with open(ARCHIVO_RECETAS, "w", encoding="utf-8") as f:
            json.dump(recetas_dict, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error al guardar recetas favoritas: {e}")

ARCHIVO_SEMANA = "semana_alimentos.json"
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

def cargar_semana_alimentos():
    base = {d: [] for d in DIAS_SEMANA}
    if os.path.exists(ARCHIVO_SEMANA):
        try:
            with open(ARCHIVO_SEMANA, "r", encoding="utf-8") as f:
                data = json.load(f)
                for d in DIAS_SEMANA:
                    if d in data:
                        base[d] = data[d]
                return base
        except Exception:
            return base
    return base

def guardar_semana_alimentos(dict_semana):
    try:
        with open(ARCHIVO_SEMANA, "w", encoding="utf-8") as f:
            json.dump(dict_semana, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error al guardar plan semanal: {e}")

# Inicialización en session_state con persistencia local
if "alimentos_custom" not in st.session_state:
    st.session_state.alimentos_custom = cargar_alimentos_custom()

if "recetas_guardadas" not in st.session_state:
    st.session_state.recetas_guardadas = cargar_recetas_guardadas()

if "semana_alimentos" not in st.session_state:
    st.session_state.semana_alimentos = cargar_semana_alimentos()

if "dia_semana_sel" not in st.session_state:
    st.session_state.dia_semana_sel = "Lunes"

# Ingredientes de la receta activa en la olla
if "receta" not in st.session_state:
    st.session_state.receta = []

# DataFrame consolidado de alimentos
def get_catalogo_alimentos():
    todos = BASE_ALIMENTOS + st.session_state.alimentos_custom
    df = pd.DataFrame(todos)
    return df

df_alimentos = get_catalogo_alimentos()

# ==============================================================================
# SIDEBAR: PARÁMETROS BIOMÉTRICOS & ACTIVIDAD FÍSICA
# ==============================================================================
st.sidebar.markdown("## ⚙️ Parámetros Biométricos")

cfg_usuario = cargar_config_usuario()

# --- PERFIL BIOMÉTRICO: ÉL ---
st.sidebar.markdown("### 👨 Perfil: Él")
col_el1, col_el2 = st.sidebar.columns(2)
with col_el1:
    peso_el = st.number_input("Peso (kg)", min_value=50.0, max_value=170.0, value=float(cfg_usuario.get("peso_el", 119.0)), step=0.5, key="peso_el")
with col_el2:
    altura_el = st.number_input("Altura (cm)", min_value=130, max_value=220, value=int(cfg_usuario.get("altura_el", 180)), step=1, key="altura_el")

edad_el = st.sidebar.number_input("Edad (años)", min_value=18, max_value=99, value=int(cfg_usuario.get("edad_el", 34)), step=1, key="edad_el")

st.sidebar.markdown("---")

# --- PERFIL BIOMÉTRICO: ELLA ---
st.sidebar.markdown("### 👩 Perfil: Ella")
col_ella1, col_ella2 = st.sidebar.columns(2)
with col_ella1:
    peso_ella = st.number_input("Peso (kg)", min_value=35.0, max_value=140.0, value=float(cfg_usuario.get("peso_ella", 69.0)), step=0.5, key="peso_ella")
with col_ella2:
    altura_ella = st.number_input("Altura (cm)", min_value=120, max_value=200, value=int(cfg_usuario.get("altura_ella", 150)), step=1, key="altura_ella")

edad_ella = st.sidebar.number_input("Edad (años)", min_value=18, max_value=99, value=int(cfg_usuario.get("edad_ella", 33)), step=1, key="edad_ella")

st.sidebar.markdown("---")

# --- ACTIVIDAD SEMANAL (CAMINATAS & METs) ---
st.sidebar.markdown("### 🚶 Actividad Semanal (Caminatas)")
horas_sem = st.sidebar.slider("Horas de caminata por semana", min_value=0.0, max_value=14.0, value=float(cfg_usuario.get("horas_sem", 3.0)), step=0.5,
                              help="Ejemplo: 3 horas semanales = Lunes, Jueves y Viernes 1h c/u.")

intensidad_mets_dict = {
    "4.0 METs - Caminata paso constante/ligero (4.8 - 5.0 km/h)": 4.0,
    "3.0 METs - Caminata suave (4.0 km/h)": 3.0,
    "4.8 METs - Caminata rápida (5.5 - 6.0 km/h)": 4.8
}
idx_mets = list(intensidad_mets_dict.keys()).index(cfg_usuario.get("opcion_mets")) if cfg_usuario.get("opcion_mets") in intensidad_mets_dict else 0
opcion_mets = st.sidebar.selectbox("Intensidad (METs)", list(intensidad_mets_dict.keys()), index=idx_mets)
mets_val = intensidad_mets_dict[opcion_mets]

# ==============================================================================
# CÁLCULOS METABÓLICOS BASE (MIFFLIN-ST JEOR & TDEE)
# ==============================================================================
# Él
tmb_el = (10.0 * peso_el) + (6.25 * altura_el) - (5.0 * edad_el) + 5.0
sed_el = tmb_el * 1.2
quema_1h_el = mets_val * peso_el * 1.0
techo_cam_el = sed_el + quema_1h_el
tdee_prom_el = sed_el + ((quema_1h_el * horas_sem) / 7.0)

# Ella
tmb_ella = (10.0 * peso_ella) + (6.25 * altura_ella) - (5.0 * edad_ella) - 161.0
sed_ella = tmb_ella * 1.2
quema_1h_ella = mets_val * peso_ella * 1.0
techo_cam_ella = sed_ella + quema_1h_ella
tdee_prom_ella = sed_ella + ((quema_1h_ella * horas_sem) / 7.0)

st.sidebar.markdown("---")

# --- OBJETIVO & META CALÓRICA: ÉL ---
st.sidebar.markdown("### 🎯 Objetivo & Meta Calórica (Él)")
lista_act_el = [
    "📉 Déficit Moderado (Base 2150 kcal)",
    "📉 Déficit Ligero (Base 2400 kcal)",
    "⚖️ Mantenimiento Metabólico (TDEE)",
    "📈 Superávit (+300 kcal Ganancia / Volumen)",
    "🛠️ Personalizado (Ajustar a mano kcal o macros)"
]
idx_act_el = lista_act_el.index(cfg_usuario.get("opcion_act_el")) if cfg_usuario.get("opcion_act_el") in lista_act_el else 0
opcion_act_el = st.sidebar.selectbox("Meta Nutricional (Él)", lista_act_el, index=idx_act_el, key="sel_act_el")

# Variables personalizadas Él para persistencia
custom_kcal_el_val = float(cfg_usuario.get("custom_kcal_el", 2150.0))
custom_p_el_val = float(cfg_usuario.get("custom_p_el", 188.0))
custom_c_el_val = float(cfg_usuario.get("custom_c_el", 210.0))
custom_g_el_val = float(cfg_usuario.get("custom_g_el", 60.0))
modo_pers_el_val = str(cfg_usuario.get("modo_pers_el", "Calorías Totales Directas (kcal)"))

if "Personalizado" in opcion_act_el:
    st.sidebar.markdown("""
    <div style="background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 8px; padding: 10px; margin-top: 6px; margin-bottom: 10px;">
        <strong style="color: #60a5fa; font-size: 0.9rem;">🛠️ Panel Personalizado (Él)</strong><br>
        <span style="font-size: 0.78rem; color: #cbd5e1;">Ajusta tus calorías o tus gramos de macros libremente:</span>
    </div>
    """, unsafe_allow_html=True)
    
    modo_pers_el_val = st.sidebar.radio(
        "Ajustar por (Él):",
        ["Gramos de Macronutrientes (P, C, G)", "Calorías Totales Directas (kcal)"],
        index=0 if modo_pers_el_val == "Gramos de Macronutrientes (P, C, G)" else 1,
        key="modo_pers_el"
    )
    
    if modo_pers_el_val == "Calorías Totales Directas (kcal)":
        custom_kcal_el_val = st.sidebar.number_input(
            "Calorías Diarias Asignadas (kcal)",
            min_value=1000.0, max_value=5000.0, value=custom_kcal_el_val, step=50.0,
            key="custom_kcal_el",
            help="Presupuesto calórico diario que te asignó tu plan o nutricionista."
        )
        meta_kcal_el = custom_kcal_el_val
        req_p_el = round((meta_kcal_el * 0.35) / 4.0)
        req_c_el = round((meta_kcal_el * 0.40) / 4.0)
        req_g_el = round((meta_kcal_el * 0.25) / 9.0)
        st.sidebar.caption(f"Distribución sugerida (35% P, 40% C, 25% G): **{req_p_el:.0f}g P | {req_c_el:.0f}g C | {req_g_el:.0f}g G**")
    else:
        st.sidebar.markdown("**Gramos Diarios (Él):**")
        c_p_el, c_c_el, c_g_el = st.sidebar.columns(3)
        with c_p_el:
            custom_p_el_val = st.number_input("Prot (g)", min_value=10.0, max_value=400.0, value=custom_p_el_val, step=1.0, key="custom_p_el")
        with c_c_el:
            custom_c_el_val = st.number_input("Carb (g)", min_value=10.0, max_value=600.0, value=custom_c_el_val, step=1.0, key="custom_c_el")
        with c_g_el:
            custom_g_el_val = st.number_input("Grasa (g)", min_value=10.0, max_value=250.0, value=custom_g_el_val, step=1.0, key="custom_g_el")
        req_p_el = custom_p_el_val
        req_c_el = custom_c_el_val
        req_g_el = custom_g_el_val
        meta_kcal_el = (req_p_el * 4.0) + (req_c_el * 4.0) + (req_g_el * 9.0)
        custom_kcal_el_val = meta_kcal_el

elif "2150" in opcion_act_el:
    meta_kcal_el = 2150.0
    req_p_el = 188.0
    req_c_el = 210.0
    req_g_el = 60.0
elif "2400" in opcion_act_el:
    meta_kcal_el = 2400.0
    req_p_el = 200.0
    req_c_el = 240.0
    req_g_el = 70.0
elif "Mantenimiento" in opcion_act_el:
    meta_kcal_el = float(round(tdee_prom_el))
    req_p_el = round((meta_kcal_el * 0.30) / 4.0)
    req_c_el = round((meta_kcal_el * 0.45) / 4.0)
    req_g_el = round((meta_kcal_el * 0.25) / 9.0)
else: # Superávit
    meta_kcal_el = float(round(tdee_prom_el + 300.0))
    req_p_el = round((meta_kcal_el * 0.30) / 4.0)
    req_c_el = round((meta_kcal_el * 0.45) / 4.0)
    req_g_el = round((meta_kcal_el * 0.25) / 9.0)

# Indicador de estado calórico (Él)
delta_el = meta_kcal_el - tdee_prom_el
if delta_el <= -15:
    badge_estado_el = f"<span style='color:#10b981; font-weight:700;'>📉 Déficit: {delta_el:.0f} kcal</span>"
elif delta_el >= 15:
    badge_estado_el = f"<span style='color:#60a5fa; font-weight:700;'>📈 Superávit: +{delta_el:.0f} kcal</span>"
else:
    badge_estado_el = "<span style='color:#94a3b8; font-weight:700;'>⚖️ Mantenimiento</span>"

st.sidebar.markdown(
    f"<span class='badge-kcal'>Meta: {meta_kcal_el:.0f} kcal</span> {badge_estado_el}<br>"
    f"<span class='badge-p'>{req_p_el:.0f}g P</span> "
    f"<span class='badge-c'>{req_c_el:.0f}g C</span> "
    f"<span class='badge-g'>{req_g_el:.0f}g G</span>",
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

# --- OBJETIVO & META CALÓRICA: ELLA ---
st.sidebar.markdown("### 🎯 Objetivo & Meta Calórica (Ella)")
lista_act_ella = [
    "📉 Déficit Moderado (Base 1300 kcal)",
    "📉 Déficit Ligero (Base 1500 kcal)",
    "⚖️ Mantenimiento Metabólico (TDEE)",
    "📈 Superávit (+250 kcal Ganancia / Volumen)",
    "🛠️ Personalizada (Ajustar a mano kcal o macros)"
]
idx_act_ella = lista_act_ella.index(cfg_usuario.get("opcion_act_ella")) if cfg_usuario.get("opcion_act_ella") in lista_act_ella else 0
opcion_act_ella = st.sidebar.selectbox("Meta Nutricional (Ella)", lista_act_ella, index=idx_act_ella, key="sel_act_ella")

# Variables personalizadas Ella para persistencia
custom_kcal_ella_val = float(cfg_usuario.get("custom_kcal_ella", 1300.0))
custom_p_ella_val = float(cfg_usuario.get("custom_p_ella", 115.0))
custom_c_ella_val = float(cfg_usuario.get("custom_c_ella", 120.0))
custom_g_ella_val = float(cfg_usuario.get("custom_g_ella", 38.0))
modo_pers_ella_val = str(cfg_usuario.get("modo_pers_ella", "Calorías Totales Directas (kcal)"))

if "Personalizada" in opcion_act_ella:
    st.sidebar.markdown("""
    <div style="background: rgba(236, 72, 153, 0.12); border: 1px solid rgba(236, 72, 153, 0.35); border-radius: 8px; padding: 10px; margin-top: 6px; margin-bottom: 10px;">
        <strong style="color: #f472b6; font-size: 0.9rem;">🛠️ Panel Personalizado (Ella)</strong><br>
        <span style="font-size: 0.78rem; color: #cbd5e1;">Ajusta tus calorías o tus gramos de macros libremente:</span>
    </div>
    """, unsafe_allow_html=True)
    
    modo_pers_ella_val = st.sidebar.radio(
        "Ajustar por (Ella):",
        ["Gramos de Macronutrientes (P, C, G)", "Calorías Totales Directas (kcal)"],
        index=0 if modo_pers_ella_val == "Gramos de Macronutrientes (P, C, G)" else 1,
        key="modo_pers_ella"
    )
    
    if modo_pers_ella_val == "Calorías Totales Directas (kcal)":
        custom_kcal_ella_val = st.sidebar.number_input(
            "Calorías Diarias Asignadas (Ella)",
            min_value=800.0, max_value=4000.0, value=custom_kcal_ella_val, step=25.0,
            key="custom_kcal_ella",
            help="Presupuesto calórico diario que te asignó tu plan o nutricionista."
        )
        meta_kcal_ella = custom_kcal_ella_val
        req_p_ella = round((meta_kcal_ella * 0.35) / 4.0)
        req_c_ella = round((meta_kcal_ella * 0.38) / 4.0)
        req_g_ella = round((meta_kcal_ella * 0.27) / 9.0)
        st.sidebar.caption(f"Distribución sugerida (35% P, 38% C, 27% G): **{req_p_ella:.0f}g P | {req_c_ella:.0f}g C | {req_g_ella:.0f}g G**")
    else:
        st.sidebar.markdown("**Gramos Diarios (Ella):**")
        c_p_ella, c_c_ella, c_g_ella = st.sidebar.columns(3)
        with c_p_ella:
            custom_p_ella_val = st.number_input("Prot (g)", min_value=10.0, max_value=300.0, value=custom_p_ella_val, step=1.0, key="custom_p_ella")
        with c_c_ella:
            custom_c_ella_val = st.number_input("Carb (g)", min_value=10.0, max_value=400.0, value=custom_c_ella_val, step=1.0, key="custom_c_ella")
        with c_g_ella:
            custom_g_ella_val = st.number_input("Grasa (g)", min_value=10.0, max_value=200.0, value=custom_g_ella_val, step=1.0, key="custom_g_ella")
        req_p_ella = custom_p_ella_val
        req_c_ella = custom_c_ella_val
        req_g_ella = custom_g_ella_val
        meta_kcal_ella = (req_p_ella * 4.0) + (req_c_ella * 4.0) + (req_g_ella * 9.0)
        custom_kcal_ella_val = meta_kcal_ella

elif "1300" in opcion_act_ella:
    meta_kcal_ella = 1300.0
    req_p_ella = 115.0
    req_c_ella = 120.0
    req_g_ella = 38.0
elif "1500" in opcion_act_ella:
    meta_kcal_ella = 1500.0
    req_p_ella = 125.0
    req_c_ella = 150.0
    req_g_ella = 45.0
elif "Mantenimiento" in opcion_act_ella:
    meta_kcal_ella = float(round(tdee_prom_ella))
    req_p_ella = round((meta_kcal_ella * 0.30) / 4.0)
    req_c_ella = round((meta_kcal_ella * 0.45) / 4.0)
    req_g_el_ella = round((meta_kcal_ella * 0.25) / 9.0)
    req_g_ella = req_g_el_ella
else: # Superávit
    meta_kcal_ella = float(round(tdee_prom_ella + 250.0))
    req_p_ella = round((meta_kcal_ella * 0.30) / 4.0)
    req_c_ella = round((meta_kcal_ella * 0.45) / 4.0)
    req_g_ella = round((meta_kcal_ella * 0.25) / 9.0)

# Indicador de estado calórico (Ella)
delta_ella = meta_kcal_ella - tdee_prom_ella
if delta_ella <= -15:
    badge_estado_ella = f"<span style='color:#10b981; font-weight:700;'>📉 Déficit: {delta_ella:.0f} kcal</span>"
elif delta_ella >= 15:
    badge_estado_ella = f"<span style='color:#ec4899; font-weight:700;'>📈 Superávit: +{delta_ella:.0f} kcal</span>"
else:
    badge_estado_ella = "<span style='color:#94a3b8; font-weight:700;'>⚖️ Mantenimiento</span>"

st.sidebar.markdown(
    f"<span class='badge-kcal'>Meta: {meta_kcal_ella:.0f} kcal</span> {badge_estado_ella}<br>"
    f"<span class='badge-p'>{req_p_ella:.0f}g P</span> "
    f"<span class='badge-c'>{req_c_ella:.0f}g C</span> "
    f"<span class='badge-g'>{req_g_ella:.0f}g G</span>",
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

# --- REPARTO DEL PLATO COMPARTIDO ---
lista_reparto = ["Dinámica según Metas Calóricas", "Fija Estándar (60% Él / 40% Ella)"]
idx_reparto = lista_reparto.index(cfg_usuario.get("tipo_reparto")) if cfg_usuario.get("tipo_reparto") in lista_reparto else 0
tipo_reparto = st.sidebar.radio("Proporción de Olla Compartida", lista_reparto, index=idx_reparto)

# Guardar automáticamente la configuración si cambió para que nunca se pierda al refrescar
cfg_actual = {
    "peso_el": float(peso_el),
    "altura_el": int(altura_el),
    "edad_el": int(edad_el),
    "opcion_act_el": str(opcion_act_el),
    "custom_kcal_el": float(custom_kcal_el_val),
    "custom_p_el": float(custom_p_el_val),
    "custom_c_el": float(custom_c_el_val),
    "custom_g_el": float(custom_g_el_val),
    "modo_pers_el": str(modo_pers_el_val),
    "peso_ella": float(peso_ella),
    "altura_ella": int(altura_ella),
    "edad_ella": int(edad_ella),
    "opcion_act_ella": str(opcion_act_ella),
    "custom_kcal_ella": float(custom_kcal_ella_val),
    "custom_p_ella": float(custom_p_ella_val),
    "custom_c_ella": float(custom_c_ella_val),
    "custom_g_ella": float(custom_g_ella_val),
    "modo_pers_ella": str(modo_pers_ella_val),
    "horas_sem": float(horas_sem),
    "opcion_mets": str(opcion_mets),
    "tipo_reparto": str(tipo_reparto)
}
if cfg_actual != cfg_usuario:
    guardar_config_usuario(cfg_actual)

# ==============================================================================
# BALANCE ENERGÉTICO & PROPORCIONES DE PLATO
# ==============================================================================
# Déficit Diario Neto (positivo = déficit/pérdida de grasa, negativo = superávit/ganancia)
deficit_el = tdee_prom_el - meta_kcal_el
deficit_ella = tdee_prom_ella - meta_kcal_ella

kg_sem_el = abs(deficit_el * 7.0) / 7700.0
kg_sem_ella = abs(deficit_ella * 7.0) / 7700.0

kg_mes_el = abs(deficit_el * 30.4) / 7700.0
kg_mes_ella = abs(deficit_ella * 30.4) / 7700.0

# Proporción del Plato Compartido
if tipo_reparto == "Fija Estándar (60% Él / 40% Ella)":
    prop_el = 0.60
    prop_ella = 0.40
else:
    suma_metas = meta_kcal_el + meta_kcal_ella
    prop_el = meta_kcal_el / suma_metas if suma_metas > 0 else 0.5
    prop_ella = meta_kcal_ella / suma_metas if suma_metas > 0 else 0.5

# Macros diarios asignados
macros_ref_el = {
    "p": round(req_p_el),
    "c": round(req_c_el),
    "g": round(req_g_el),
    "kcal": meta_kcal_el
}
macros_ref_ella = {
    "p": round(req_p_ella),
    "c": round(req_c_ella),
    "g": round(req_g_ella),
    "kcal": meta_kcal_ella
}

# ==============================================================================
# HEADER PRINCIPAL
# ==============================================================================
st.title("⚖️ Sistema Analítico de Nutrición & Auditoría Metabólica")
st.markdown(
    f"Plataforma de alta precisión para el balance energético en pareja. "
    f"Proporción de Olla Compartida activa: **Él {prop_el*100:.1f}%** | **Ella {prop_ella*100:.1f}%**."
)

# ==============================================================================
# TABS PRINCIPALES
# ==============================================================================
tab1, tab_sem, tab2, tab3 = st.tabs([
    "🧮 Calculadora de Alimentos & Armador de Platos",
    "📅 Registro & Balance Semanal (Lunes a Domingo)",
    "🔥 Auditoría Metabólica & Simulador de Caminatas",
    "📈 Registro de Peso y Avance Real"
])

# ==============================================================================
# PESTAÑA 1: CALCULADORA DE ALIMENTOS & ARMADOR DE PLATOS
# ==============================================================================
with tab1:
    st.markdown("### 1. Consulta Rápida e Intercambio de Equivalencias")
    
    col_c1, col_c2 = st.columns([1.1, 0.9])
    
    with col_c1:
        st.markdown("**Selecciona un alimento y cantidad en crudo / neto:**")
        nombres_alimentos = sorted(df_alimentos["nombre"].unique())
        
        col_sel, col_gr = st.columns([2, 1])
        with col_sel:
            alimento_sel_nombre = st.selectbox("Alimento", nombres_alimentos, index=nombres_alimentos.index("Pechuga de pollo sin piel") if "Pechuga de pollo sin piel" in nombres_alimentos else 0)
        with col_gr:
            gramos_sel = st.number_input("Gramos", min_value=1.0, max_value=2000.0, value=220.0, step=10.0)
            
        row_alimento = df_alimentos[df_alimentos["nombre"] == alimento_sel_nombre].iloc[0]
        factor = gramos_sel / 100.0
        
        calc_kcal = row_alimento["kcal"] * factor
        calc_p = row_alimento["p"] * factor
        calc_c = row_alimento["c"] * factor
        calc_g = row_alimento["g"] * factor
        
        # Tarjetas de visualización de macronutrientes
        st.markdown(f"""
        <div style="display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap;">
            <div class="metric-card" style="flex: 1; min-width: 110px; text-align: center;">
                <div class="metric-title">Calorías</div>
                <div class="metric-val" style="color: #f87171;">{calc_kcal:.1f}</div>
                <div class="metric-sub">kcal</div>
            </div>
            <div class="metric-card" style="flex: 1; min-width: 110px; text-align: center;">
                <div class="metric-title">Proteínas</div>
                <div class="metric-val" style="color: #60a5fa;">{calc_p:.1f}</div>
                <div class="metric-sub">gramos</div>
            </div>
            <div class="metric-card" style="flex: 1; min-width: 110px; text-align: center;">
                <div class="metric-title">Carbohidratos</div>
                <div class="metric-val" style="color: #34d399;">{calc_c:.1f}</div>
                <div class="metric-sub">gramos</div>
            </div>
            <div class="metric-card" style="flex: 1; min-width: 110px; text-align: center;">
                <div class="metric-title">Grasas</div>
                <div class="metric-val" style="color: #fbbf24;">{calc_g:.1f}</div>
                <div class="metric-sub">gramos</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_c2:
        # Gráfico de Dona: Distribución Calórica de este alimento
        kcal_p_total = calc_p * 4.0
        kcal_c_total = calc_c * 4.0
        kcal_g_total = calc_g * 9.0
        suma_cal_macros = kcal_p_total + kcal_c_total + kcal_g_total
        
        if suma_cal_macros > 0:
            fig_dona = go.Figure(data=[go.Pie(
                labels=['Proteínas (4 kcal/g)', 'Carbohidratos (4 kcal/g)', 'Grasas (9 kcal/g)'],
                values=[kcal_p_total, kcal_c_total, kcal_g_total],
                hole=0.58,
                marker=dict(colors=['#3b82f6', '#10b981', '#f59e0b']),
                textinfo='percent',
                hoverinfo='label+value',
                hovertemplate='%{label}: %{value:.1f} kcal (%{percent})<extra></extra>'
            )])
            fig_dona.update_layout(
                title=dict(text=f"Distribución Calórica: {gramos_sel:.0f}g {alimento_sel_nombre[:25]}", font=dict(size=13, color="#cbd5e1")),
                template="plotly_dark",
                height=240,
                margin=dict(l=10, r=10, t=35, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=10))
            )
            st.plotly_chart(fig_dona, use_container_width=True)
        else:
            st.info("Alimento con aporte calórico insignificante.")

    # Buscador de Equivalencias Automático
    with st.expander("🔄 Buscador Inteligente de Equivalencias por Nutriente"):
        col_eq1, col_eq2 = st.columns([1, 2])
        with col_eq1:
            criterio_eq = st.radio(
                "Igualar por:",
                ["Proteína (g)", "Carbohidratos (g)", "Calorías (kcal)"],
                index=0 if calc_p >= calc_c else 1
            )
            filtrar_misma_cat = st.checkbox("Solo misma categoría", value=True)
        
        with col_eq2:
            categoria_actual = row_alimento["categoria"]
            if filtrar_misma_cat:
                df_candidatos = df_alimentos[df_alimentos["categoria"] == categoria_actual].copy()
            else:
                df_candidatos = df_alimentos.copy()
            
            # Remover el alimento seleccionado para comparar
            df_candidatos = df_candidatos[df_candidatos["nombre"] != alimento_sel_nombre]
            
            equivalencias = []
            for _, cand in df_candidatos.iterrows():
                if criterio_eq == "Proteína (g)":
                    if cand["p"] > 1.0: # Evitar división por cero o alimentos sin proteína
                        gr_necesarios = (calc_p / cand["p"]) * 100.0
                        equivalencias.append({
                            "Alimento Equivalente": cand["nombre"],
                            "Categoría": cand["categoria"],
                            "Gramos para igualar": round(gr_necesarios, 1),
                            "Proteína aportada": round((cand["p"] * gr_necesarios) / 100.0, 1),
                            "Calorías resultantes": round((cand["kcal"] * gr_necesarios) / 100.0, 1),
                            "Carbos resultantes": round((cand["c"] * gr_necesarios) / 100.0, 1),
                            "Grasas resultantes": round((cand["g"] * gr_necesarios) / 100.0, 1)
                        })
                elif criterio_eq == "Carbohidratos (g)":
                    if cand["c"] > 1.0:
                        gr_necesarios = (calc_c / cand["c"]) * 100.0
                        equivalencias.append({
                            "Alimento Equivalente": cand["nombre"],
                            "Categoría": cand["categoria"],
                            "Gramos para igualar": round(gr_necesarios, 1),
                            "Carbos aportados": round((cand["c"] * gr_necesarios) / 100.0, 1),
                            "Calorías resultantes": round((cand["kcal"] * gr_necesarios) / 100.0, 1),
                            "Proteína resultante": round((cand["p"] * gr_necesarios) / 100.0, 1),
                            "Grasas resultantes": round((cand["g"] * gr_necesarios) / 100.0, 1)
                        })
                else: # Calorías
                    if cand["kcal"] > 5.0:
                        gr_necesarios = (calc_kcal / cand["kcal"]) * 100.0
                        equivalencias.append({
                            "Alimento Equivalente": cand["nombre"],
                            "Categoría": cand["categoria"],
                            "Gramos para igualar": round(gr_necesarios, 1),
                            "Calorías aportadas": round((cand["kcal"] * gr_necesarios) / 100.0, 1),
                            "Proteína resultante": round((cand["p"] * gr_necesarios) / 100.0, 1),
                            "Carbos resultantes": round((cand["c"] * gr_necesarios) / 100.0, 1),
                            "Grasas resultantes": round((cand["g"] * gr_necesarios) / 100.0, 1)
                        })
            
            if equivalencias:
                df_eq_res = pd.DataFrame(equivalencias)
                st.markdown(f"**Para igualar {gramos_sel:.0f}g de {alimento_sel_nombre} ({criterio_eq}):**")
                st.dataframe(
                    df_eq_res.sort_values(by="Gramos para igualar").reset_index(drop=True),
                    use_container_width=True,
                    height=220
                )
            else:
                st.warning("No hay suficientes alimentos en el catálogo con contenido significativo de este macronutriente.")

    st.markdown("---")

    # --- SECCIÓN 2: ARMADOR DE COMIDA / OLLA COMPARTIDA ---
    st.markdown("### 2. Armador de Comida / Olla Compartida")
    st.markdown("Construye una receta ingrediente por ingrediente o carga una receta guardada de tu recetario permanente.")

    # PANEL DE RECETAS FAVORITAS (GUARDAR Y CARGAR)
    with st.expander("📖 Recetario Permanente: Cargar o Guardar Recetas", expanded=True):
        col_rec_load, col_rec_save = st.columns([1.5, 1.5])
        
        # Cargar Receta Existente
        with col_rec_load:
            st.markdown("##### 📥 Cargar Receta a la Olla")
            nombres_recetas = sorted(list(st.session_state.recetas_guardadas.keys()))
            if nombres_recetas:
                rec_sel_nombre = st.selectbox("Tus Recetas Guardadas:", nombres_recetas, key="sel_rec_guardada")
                col_btn_c, col_btn_e = st.columns(2)
                with col_btn_c:
                    if st.button("📥 Cargar a la Olla", use_container_width=True):
                        st.session_state.receta = [dict(item) for item in st.session_state.recetas_guardadas[rec_sel_nombre]]
                        st.success(f"¡Receta '{rec_sel_nombre}' cargada con éxito en la Olla!")
                        st.rerun()
                with col_btn_e:
                    if st.button("🗑️ Eliminar Receta", use_container_width=True):
                        del st.session_state.recetas_guardadas[rec_sel_nombre]
                        guardar_recetas_guardadas(st.session_state.recetas_guardadas)
                        st.success(f"Receta '{rec_sel_nombre}' eliminada.")
                        st.rerun()
            else:
                st.info("Aún no tienes recetas guardadas. Agrega ingredientes a la olla y guárdala a la derecha.")

        # Guardar Olla Actual como Receta
        with col_rec_save:
            st.markdown("##### 💾 Guardar Olla Actual")
            nombre_nueva_receta = st.text_input("Nombre para esta receta:", placeholder="Ej: Pollo al horno con papas y calabaza", key="txt_nom_receta")
            if st.button("💾 Guardar Olla en Recetario", use_container_width=True):
                if not st.session_state.receta:
                    st.warning("Primero debes agregar al menos un ingrediente a la olla antes de guardar.")
                elif not nombre_nueva_receta.strip():
                    st.error("Por favor, escribe un nombre para la receta.")
                else:
                    nom_limpio = nombre_nueva_receta.strip()
                    st.session_state.recetas_guardadas[nom_limpio] = [dict(item) for item in st.session_state.receta]
                    guardar_recetas_guardadas(st.session_state.recetas_guardadas)
                    st.success(f"¡Receta '{nom_limpio}' guardada en tu recetario permanente!")
                    st.rerun()

    st.markdown("---")
    st.markdown("##### ➕ Agregar Ingrediente a la Olla Actual")
    col_add1, col_add2, col_add3, col_add4 = st.columns([2.5, 1.2, 1.8, 1.2])
    with col_add1:
        ing_nombre = st.selectbox("Ingrediente para la Olla", nombres_alimentos, key="add_ing_nombre")
    with col_add2:
        ing_gramos = st.number_input("Gramos Crudo", min_value=1.0, max_value=5000.0, value=250.0, step=10.0, key="add_ing_gr")
    with col_add3:
        ing_tipo = st.selectbox("Destino de la carga", ["Olla Compartida (Ambos)", "Solo para Él", "Solo para Ella"], key="add_ing_tipo")
    with col_add4:
        st.write("")
        st.write("")
        btn_agregar = st.button("➕ Agregar", use_container_width=True)
        
    if btn_agregar:
        info_ing = df_alimentos[df_alimentos["nombre"] == ing_nombre].iloc[0]
        fac = ing_gramos / 100.0
        st.session_state.receta.append({
            "id": len(st.session_state.receta) + 1,
            "alimento": ing_nombre,
            "gramos": ing_gramos,
            "tipo": ing_tipo,
            "kcal": info_ing["kcal"] * fac,
            "p": info_ing["p"] * fac,
            "c": info_ing["c"] * fac,
            "g": info_ing["g"] * fac
        })
        st.success(f"¡Agregado: {ing_gramos:.0f}g de {ing_nombre}!")
        st.rerun()

    # Formulario para crear alimento personalizado en la base de datos
    # Formulario para crear alimento personalizado en la base de datos
    with st.expander("✨ Agregar Alimento Personalizado al Catálogo (por 100g o por Porción de 10g, 30g, etc.)"):
        with st.form("form_custom_food", clear_on_submit=True):
            st.markdown("##### 📦 Datos del Alimento o Producto")
            col_modo1, col_modo2 = st.columns([1.6, 1.0])
            with col_modo1:
                modo_carga = st.selectbox(
                    "Modo de Carga:",
                    ["Por Porción / Unidad del Paquete (ej. 10g, 25g, 30g, 45g)", "Directo por cada 100 gramos"],
                    index=0,
                    help="Si la tabla nutricional de tu producto informa valores por porción (ej. 30g), selecciónalo aquí para no tener que calcular nada a mano."
                )
            with col_modo2:
                peso_porcion_input = st.number_input(
                    "Peso de la Porción (gramos)",
                    min_value=1.0, max_value=1000.0, value=30.0, step=1.0,
                    help="Indica cuántos gramos pesa 1 porción o unidad según el paquete."
                )

            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                c_nom = st.text_input("Nombre del Alimento / Marca", placeholder="Ej: Barra de proteína X o Galletita Y")
                c_cat = st.selectbox("Categoría", [
                    "Cereales, Legumbres y Tubérculos", "Carnes y Aves", "Pescados, Huevos y Fiambres", "Lácteos",
                    "Grasas, Frutas y Vegetales", "Snacks y Panificados", "Suplementos y Otros"
                ])
            with f_col2:
                c_kcal = st.number_input("Calorías (kcal)", min_value=0.0, max_value=2000.0, value=120.0, step=1.0,
                                         help="Kcal que figuran en el paquete para la porción o por 100g según el modo elegido.")
                c_p = st.number_input("Proteína (g)", min_value=0.0, max_value=200.0, value=5.0, step=0.1)
            with f_col3:
                c_c = st.number_input("Carbohidratos (g)", min_value=0.0, max_value=200.0, value=15.0, step=0.1)
                c_g = st.number_input("Grasas (g)", min_value=0.0, max_value=200.0, value=4.0, step=0.1)
            
            btn_guardar_custom = st.form_submit_button("💾 Guardar Alimento en Catálogo")
            if btn_guardar_custom:
                if c_nom.strip():
                    es_por_porcion = "Por Porción" in modo_carga
                    if es_por_porcion and peso_porcion_input > 0:
                        factor_100 = 100.0 / peso_porcion_input
                        kcal_final = round(c_kcal * factor_100, 1)
                        p_final = round(c_p * factor_100, 1)
                        c_final = round(c_c * factor_100, 1)
                        g_final = round(c_g * factor_100, 1)
                        # Agregar sufijo informativo si no lo tiene
                        nombre_final = c_nom.strip()
                        if f"{peso_porcion_input:.0f}g" not in nombre_final:
                            nombre_final = f"{nombre_final} (1 u = {peso_porcion_input:.0f}g)"
                    else:
                        kcal_final = round(c_kcal, 1)
                        p_final = round(c_p, 1)
                        c_final = round(c_c, 1)
                        g_final = round(c_g, 1)
                        nombre_final = c_nom.strip()

                    st.session_state.alimentos_custom.append({
                        "nombre": nombre_final,
                        "categoria": c_cat,
                        "kcal": kcal_final,
                        "p": p_final,
                        "c": c_final,
                        "g": g_final
                    })
                    guardar_alimentos_custom(st.session_state.alimentos_custom)
                    st.success(
                        f"¡Guardado con éxito! '{nombre_final}' ya está en tu catálogo permanente "
                        f"(Valores automáticos cada 100g: {kcal_final:.0f} kcal | {p_final:.1f}g P | {c_final:.1f}g C | {g_final:.1f}g G)."
                    )
                    st.rerun()
                else:
                    st.error("Por favor, ingresa un nombre para el alimento.")

    # Mostrar la tabla de la receta actual
    if st.session_state.receta:
        st.markdown("#### Ingredientes en la Comida Actual")
        df_rec = pd.DataFrame(st.session_state.receta)
        
        col_t1, col_t2 = st.columns([4, 1])
        with col_t1:
            st.dataframe(
                df_rec[["alimento", "gramos", "tipo", "kcal", "p", "c", "g"]].rename(columns={
                    "alimento": "Alimento", "gramos": "Gramos Crudo", "tipo": "Asignación",
                    "kcal": "Kcal", "p": "Prot (g)", "c": "Carb (g)", "g": "Grasa (g)"
                }),
                use_container_width=True
            )
        with col_t2:
            if st.button("🗑️ Vaciar Olla / Reiniciar", use_container_width=True):
                st.session_state.receta = []
                st.rerun()
            
            item_a_borrar = st.selectbox("Eliminar ítem:", [f"{r['id']}: {r['alimento']} ({r['gramos']}g)" for r in st.session_state.receta], key="del_sel")
            if st.button("Borrar Seleccionado", use_container_width=True):
                id_borrar = int(item_a_borrar.split(":")[0])
                st.session_state.receta = [r for r in st.session_state.receta if r["id"] != id_borrar]
                st.rerun()

        # Calcular totales agregados
        total_olla_kcal = sum(r["kcal"] for r in st.session_state.receta if r["tipo"] == "Olla Compartida (Ambos)")
        total_olla_p = sum(r["p"] for r in st.session_state.receta if r["tipo"] == "Olla Compartida (Ambos)")
        total_olla_c = sum(r["c"] for r in st.session_state.receta if r["tipo"] == "Olla Compartida (Ambos)")
        total_olla_g = sum(r["g"] for r in st.session_state.receta if r["tipo"] == "Olla Compartida (Ambos)")
        total_gr_crudo = sum(r["gramos"] for r in st.session_state.receta if r["tipo"] == "Olla Compartida (Ambos)")

        # Porciones individuales directas
        solo_el_kcal = sum(r["kcal"] for r in st.session_state.receta if r["tipo"] == "Solo para Él")
        solo_el_p = sum(r["p"] for r in st.session_state.receta if r["tipo"] == "Solo para Él")
        solo_el_c = sum(r["c"] for r in st.session_state.receta if r["tipo"] == "Solo para Él")
        solo_el_g = sum(r["g"] for r in st.session_state.receta if r["tipo"] == "Solo para Él")

        solo_ella_kcal = sum(r["kcal"] for r in st.session_state.receta if r["tipo"] == "Solo para Ella")
        solo_ella_p = sum(r["p"] for r in st.session_state.receta if r["tipo"] == "Solo para Ella")
        solo_ella_c = sum(r["c"] for r in st.session_state.receta if r["tipo"] == "Solo para Ella")
        solo_ella_g = sum(r["g"] for r in st.session_state.receta if r["tipo"] == "Solo para Ella")

        # Asignación final en el plato
        plato_el_kcal = (total_olla_kcal * prop_el) + solo_el_kcal
        plato_el_p = (total_olla_p * prop_el) + solo_el_p
        plato_el_c = (total_olla_c * prop_el) + solo_el_c
        plato_el_g = (total_olla_g * prop_el) + solo_el_g

        plato_ella_kcal = (total_olla_kcal * prop_ella) + solo_ella_kcal
        plato_ella_p = (total_olla_p * prop_ella) + solo_ella_p
        plato_ella_c = (total_olla_c * prop_ella) + solo_ella_c
        plato_ella_g = (total_olla_g * prop_ella) + solo_ella_g

        st.markdown("---")
        # DIVISOR DE PLATO COCIDO (60/40 O PROPORCIÓN METABÓLICA)
        st.markdown("### ⚖️ Divisor de Plato Cocido en Balanza")
        st.markdown(
            "Al cocinar, los alimentos pierden agua (carnes, vegetales) o la absorben (arroz, pasta). "
            "Pesa toda la preparación cocida junta y la balanza te dirá cuántos gramos servir exactamente en cada plato."
        )

        col_bal1, col_bal2, col_bal3 = st.columns([1.5, 1.5, 1.5])
        with col_bal1:
            peso_cocido_total = st.number_input(
                "Peso Final Cocido en Balanza (g)",
                min_value=0.0, max_value=8000.0,
                value=float(round(total_gr_crudo * 0.85, 0)) if total_gr_crudo > 0 else 500.0,
                step=10.0,
                help="Peso total de la olla compartida recién cocinada (tara descontada)."
            )
        
        gramos_servir_el = peso_cocido_total * prop_el
        gramos_servir_ella = peso_cocido_total * prop_ella

        with col_bal2:
            st.markdown(f"""
            <div class="profile-card-he">
                <strong style="color: #60a5fa; font-size: 1.1rem;">Plato de Él ({prop_el*100:.1f}%)</strong>
                <div style="font-size: 1.8rem; font-weight: 700; color: #f8fafc; margin: 4px 0;">{gramos_servir_el:.0f} g</div>
                <div style="font-size: 0.85rem; color: #94a3b8;">Servir en balanza de comida cocida</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_bal3:
            st.markdown(f"""
            <div class="profile-card-she">
                <strong style="color: #f472b6; font-size: 1.1rem;">Plato de Ella ({prop_ella*100:.1f}%)</strong>
                <div style="font-size: 1.8rem; font-weight: 700; color: #f8fafc; margin: 4px 0;">{gramos_servir_ella:.0f} g</div>
                <div style="font-size: 0.85rem; color: #94a3b8;">Servir en balanza de comida cocida</div>
            </div>
            """, unsafe_allow_html=True)

        # RESUMEN PARA WHATSAPP
        texto_whatsapp = (
            f"🍽️ *Olla Compartida Lista ({peso_cocido_total:.0f}g en balanza):*\n\n"
            f"👨 *Plato de Él ({prop_el*100:.1f}%):*\n"
            f"👉 Servir en balanza: *{gramos_servir_el:.0f} g*\n"
            f"📊 Macros: {plato_el_kcal:.0f} kcal | {plato_el_p:.1f}g P | {plato_el_c:.1f}g C | {plato_el_g:.1f}g G\n\n"
            f"👩 *Plato de Ella ({prop_ella*100:.1f}%):*\n"
            f"👉 Servir en balanza: *{gramos_servir_ella:.0f} g*\n"
            f"📊 Macros: {plato_ella_kcal:.0f} kcal | {plato_ella_p:.1f}g P | {plato_ella_c:.1f}g C | {plato_ella_g:.1f}g G"
        )
        
        with st.expander("📲 Compartir Resumen de Balanza para WhatsApp"):
            st.markdown("Copia este texto y pégalo directamente en WhatsApp:")
            st.text_area("Texto listo para copiar:", value=texto_whatsapp, height=145, key="txt_wa_resumen")

        # COMPARATIVA CON METAS DIARIAS
        st.markdown("#### Impacto Nutricional del Plato vs. Meta Diaria")
        
        comp_col1, comp_col2 = st.columns(2)
        
        with comp_col1:
            st.markdown(f"##### 👨 Plato de Él: {plato_el_kcal:.0f} kcal")
            st.markdown(
                f"<span class='badge-kcal'>{plato_el_kcal:.0f} kcal</span> "
                f"<span class='badge-p'>{plato_el_p:.1f}g P</span> "
                f"<span class='badge-c'>{plato_el_c:.1f}g C</span> "
                f"<span class='badge-g'>{plato_el_g:.1f}g G</span>",
                unsafe_allow_html=True
            )
            pct_kcal_el = min(1.0, plato_el_kcal / meta_kcal_el if meta_kcal_el > 0 else 0)
            pct_p_el = min(1.0, plato_el_p / macros_ref_el['p'] if macros_ref_el['p'] > 0 else 0)
            pct_c_el = min(1.0, plato_el_c / macros_ref_el['c'] if macros_ref_el['c'] > 0 else 0)
            pct_g_el = min(1.0, plato_el_g / macros_ref_el['g'] if macros_ref_el['g'] > 0 else 0)
            
            st.write(f"Calorías cubiertas: **{(pct_kcal_el*100):.1f}%** de {meta_kcal_el:.0f} kcal")
            st.progress(pct_kcal_el)
            st.write(f"Proteína cubierta: **{(pct_p_el*100):.1f}%** de {macros_ref_el['p']}g")
            st.progress(pct_p_el)
            st.write(f"Carbohidratos cubiertos: **{(pct_c_el*100):.1f}%** de {macros_ref_el['c']}g")
            st.progress(pct_c_el)
            st.write(f"Grasas cubiertas: **{(pct_g_el*100):.1f}%** de {macros_ref_el['g']}g")
            st.progress(pct_g_el)

        with comp_col2:
            st.markdown(f"##### 👩 Plato de Ella: {plato_ella_kcal:.0f} kcal")
            st.markdown(
                f"<span class='badge-kcal'>{plato_ella_kcal:.0f} kcal</span> "
                f"<span class='badge-p'>{plato_ella_p:.1f}g P</span> "
                f"<span class='badge-c'>{plato_ella_c:.1f}g C</span> "
                f"<span class='badge-g'>{plato_ella_g:.1f}g G</span>",
                unsafe_allow_html=True
            )
            pct_kcal_ella = min(1.0, plato_ella_kcal / meta_kcal_ella if meta_kcal_ella > 0 else 0)
            pct_p_ella = min(1.0, plato_ella_p / macros_ref_ella['p'] if macros_ref_ella['p'] > 0 else 0)
            pct_c_ella = min(1.0, plato_ella_c / macros_ref_ella['c'] if macros_ref_ella['c'] > 0 else 0)
            pct_g_ella = min(1.0, plato_ella_g / macros_ref_ella['g'] if macros_ref_ella['g'] > 0 else 0)
            
            st.write(f"Calorías cubiertas: **{(pct_kcal_ella*100):.1f}%** de {meta_kcal_ella:.0f} kcal")
            st.progress(pct_kcal_ella)
            st.write(f"Proteína cubierta: **{(pct_p_ella*100):.1f}%** de {macros_ref_ella['p']}g")
            st.progress(pct_p_ella)
            st.write(f"Carbohidratos cubiertos: **{(pct_c_ella*100):.1f}%** de {macros_ref_ella['c']}g")
            st.progress(pct_c_ella)
            st.write(f"Grasas cubiertas: **{(pct_g_ella*100):.1f}%** de {macros_ref_ella['g']}g")
            st.progress(pct_g_ella)

        # Gráfico Comparativo de Macronutrientes por Plato
        fig_macros_plato = go.Figure()
        fig_macros_plato.add_trace(go.Bar(
            name="Él (Plato)",
            x=["Proteína (g)", "Carbohidratos (g)", "Grasas (g)"],
            y=[plato_el_p, plato_el_c, plato_el_g],
            marker_color="#3b82f6"
        ))
        fig_macros_plato.add_trace(go.Bar(
            name="Ella (Plato)",
            x=["Proteína (g)", "Carbohidratos (g)", "Grasas (g)"],
            y=[plato_ella_p, plato_ella_c, plato_ella_g],
            marker_color="#ec4899"
        ))
        fig_macros_plato.update_layout(
            barmode='group',
            template="plotly_dark",
            title="Comparativa de Macronutrientes Servidos en Cada Plato",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_macros_plato, use_container_width=True)

        # GUARDAR ESTA COMIDA EN UN DÍA DE LA SEMANA
        st.markdown("---")
        st.markdown("##### 📅 Guardar esta Preparación en tu Registro Semanal")
        col_env1, col_env2, col_env3 = st.columns([1.5, 2.5, 1.2])
        with col_env1:
            dia_para_enviar = st.selectbox("Día de la semana a asignar:", DIAS_SEMANA, key="sel_dia_enviar_plato")
        with col_env2:
            desc_comida_env = st.text_input("Nombre / Descripción de la Comida:", value="Olla Compartida", key="desc_comida_env")
        with col_env3:
            st.write("")
            st.write("")
            if st.button("➕ Enviar a ese Día", use_container_width=True):
                st.session_state.semana_alimentos[dia_para_enviar].append({
                    "id": len(st.session_state.semana_alimentos[dia_para_enviar]) + 1,
                    "descripcion": desc_comida_env.strip() if desc_comida_env.strip() else "Olla Compartida",
                    "el_kcal": round(plato_el_kcal, 1),
                    "el_p": round(plato_el_p, 1),
                    "el_c": round(plato_el_c, 1),
                    "el_g": round(plato_el_g, 1),
                    "ella_kcal": round(plato_ella_kcal, 1),
                    "ella_p": round(plato_ella_p, 1),
                    "ella_c": round(plato_ella_c, 1),
                    "ella_g": round(plato_ella_g, 1)
                })
                guardar_semana_alimentos(st.session_state.semana_alimentos)
                st.success(f"¡Comida guardada exitosamente en el día {dia_para_enviar}!")
                st.rerun()

    else:
        st.info("💡 Aún no has agregado ingredientes a la Olla Compartida. Selecciona un alimento arriba y haz clic en '➕ Agregar'.")

# ==============================================================================
# PESTAÑA: REGISTRO & BALANCE SEMANAL (LUNES A DOMINGO)
# ==============================================================================
with tab_sem:
    st.markdown("### 📅 Planificador & Balance de la Semana Completa")
    st.markdown("Registra las comidas de cada día (Lunes a Domingo) para Él y para Ella. El sistema audita el consumo acumulado de los 7 días frente a tu gasto real semanal para darte el **déficit o superávit neto real de la semana**.")

    # Formulario rápido para cargar alimentos sueltos o snacks a cualquier día
    with st.expander("➕ Cargar Alimento o Snack Directo a un Día"):
        col_rap1, col_rap2, col_rap3, col_rap4, col_rap5 = st.columns([1.3, 2.2, 1.2, 1.6, 1.2])
        with col_rap1:
            rap_dia = st.selectbox("Día de la semana", DIAS_SEMANA, key="rap_dia")
        with col_rap2:
            rap_ali = st.selectbox("Alimento", sorted(df_alimentos["nombre"].unique()), key="rap_ali")
        with col_rap3:
            rap_gr = st.number_input("Gramos", min_value=1.0, max_value=2500.0, value=100.0, step=10.0, key="rap_gr")
        with col_rap4:
            rap_quien = st.selectbox("Asignar a:", ["Solo Él", "Solo Ella", "Ambos (Reparto Olla)"], key="rap_quien")
        with col_rap5:
            st.write("")
            st.write("")
            if st.button("➕ Cargar", key="btn_rap_cargar", use_container_width=True):
                row_a = df_alimentos[df_alimentos["nombre"] == rap_ali].iloc[0]
                f_rap = rap_gr / 100.0
                k_tot = row_a["kcal"] * f_rap
                p_tot = row_a["p"] * f_rap
                c_tot = row_a["c"] * f_rap
                g_tot = row_a["g"] * f_rap
                
                if rap_quien == "Solo Él":
                    el_k, el_p, el_c, el_g = k_tot, p_tot, c_tot, g_tot
                    ella_k, ella_p, ella_c, ella_g = 0.0, 0.0, 0.0, 0.0
                elif rap_quien == "Solo Ella":
                    el_k, el_p, el_c, el_g = 0.0, 0.0, 0.0, 0.0
                    ella_k, ella_p, ella_c, ella_g = k_tot, p_tot, c_tot, g_tot
                else: # Ambos
                    el_k, el_p, el_c, el_g = k_tot * prop_el, p_tot * prop_el, c_tot * prop_el, g_tot * prop_el
                    ella_k, ella_p, ella_c, ella_g = k_tot * prop_ella, p_tot * prop_ella, c_tot * prop_ella, g_tot * prop_ella
                    
                st.session_state.semana_alimentos[rap_dia].append({
                    "id": len(st.session_state.semana_alimentos[rap_dia]) + 1,
                    "descripcion": f"{rap_gr:.0f}g {rap_ali}",
                    "el_kcal": round(el_k, 1), "el_p": round(el_p, 1), "el_c": round(el_c, 1), "el_g": round(el_g, 1),
                    "ella_kcal": round(ella_k, 1), "ella_p": round(ella_p, 1), "ella_c": round(ella_c, 1), "ella_g": round(ella_g, 1)
                })
                guardar_semana_alimentos(st.session_state.semana_alimentos)
                st.success(f"¡Agregado {rap_gr:.0f}g de {rap_ali} a {rap_dia}!")
                st.rerun()

    # Visualización Día por Día
    st.markdown("#### 📋 Comidas Registradas Día por Día")
    tabs_dias = st.tabs(DIAS_SEMANA)
    for i_dia, dia_nom in enumerate(DIAS_SEMANA):
        with tabs_dias[i_dia]:
            comidas_dia = st.session_state.semana_alimentos.get(dia_nom, [])
            if comidas_dia:
                c_t1, c_t2 = st.columns([3.8, 1.2])
                with c_t1:
                    st.markdown(f"##### Comidas cargadas en {dia_nom}:")
                    for idx_c, c_item in enumerate(comidas_dia):
                        row_c1, row_c2, row_c3, row_c4 = st.columns([3.2, 2.5, 2.5, 0.8])
                        with row_c1:
                            st.markdown(f"🍽️ **{c_item.get('descripcion', 'Comida')}**")
                        with row_c2:
                            st.markdown(f"<span style='color:#60a5fa;'>👨 Él: <b>{c_item.get('el_kcal', 0):.0f} kcal</b> ({c_item.get('el_p', 0):.0f}P {c_item.get('el_c', 0):.0f}C {c_item.get('el_g', 0):.0f}G)</span>", unsafe_allow_html=True)
                        with row_c3:
                            st.markdown(f"<span style='color:#f472b6;'>👩 Ella: <b>{c_item.get('ella_kcal', 0):.0f} kcal</b> ({c_item.get('ella_p', 0):.0f}P {c_item.get('ella_c', 0):.0f}C {c_item.get('ella_g', 0):.0f}G)</span>", unsafe_allow_html=True)
                        with row_c4:
                            if st.button("❌", key=f"del_c_{dia_nom}_{idx_c}", help="Eliminar este alimento"):
                                st.session_state.semana_alimentos[dia_nom].pop(idx_c)
                                guardar_semana_alimentos(st.session_state.semana_alimentos)
                                st.rerun()
                with c_t2:
                    tot_dia_el_k = sum(c["el_kcal"] for c in comidas_dia)
                    tot_dia_ella_k = sum(c["ella_kcal"] for c in comidas_dia)
                    st.markdown(f"**Totales {dia_nom}:**")
                    dif_el_dia = meta_kcal_el - tot_dia_el_k
                    dif_ella_dia = meta_kcal_ella - tot_dia_ella_k
                    st.write(f"👨 Él: **{tot_dia_el_k:.0f} / {meta_kcal_el:.0f} kcal**")
                    st.caption(f"{'Restan ' + str(round(dif_el_dia)) if dif_el_dia >= 0 else 'Exceso +' + str(round(abs(dif_el_dia)))} kcal")
                    st.write(f"👩 Ella: **{tot_dia_ella_k:.0f} / {meta_kcal_ella:.0f} kcal**")
                    st.caption(f"{'Restan ' + str(round(dif_ella_dia)) if dif_ella_dia >= 0 else 'Exceso +' + str(round(abs(dif_ella_dia)))} kcal")
                    if st.button(f"🗑️ Vaciar {dia_nom}", key=f"btn_vaciar_{dia_nom}", use_container_width=True):
                        st.session_state.semana_alimentos[dia_nom] = []
                        guardar_semana_alimentos(st.session_state.semana_alimentos)
                        st.rerun()
            else:
                st.info(f"No hay comidas cargadas para el {dia_nom}. Puedes enviarlas desde el Armador de Olla o cargarlas arriba.")

    # Totales y Balance Semanal
    st.markdown("---")
    st.markdown("#### 📊 Balance Metabólico Semanal Acumulado (7 Días)")
    
    consumo_dias_el = [sum(c["el_kcal"] for c in st.session_state.semana_alimentos.get(d, [])) for d in DIAS_SEMANA]
    consumo_dias_ella = [sum(c["ella_kcal"] for c in st.session_state.semana_alimentos.get(d, [])) for d in DIAS_SEMANA]
    
    total_sem_el_k = sum(consumo_dias_el)
    total_sem_ella_k = sum(consumo_dias_ella)
    
    gasto_sem_el = tdee_prom_el * 7.0
    gasto_sem_ella = tdee_prom_ella * 7.0
    
    neto_sem_el = gasto_sem_el - total_sem_el_k  # positivo = deficit, negativo = superavit
    neto_sem_ella = gasto_sem_ella - total_sem_ella_k
    
    kg_sem_real_el = abs(neto_sem_el) / 7700.0
    kg_sem_real_ella = abs(neto_sem_ella) / 7700.0

    col_b_el, col_b_ella = st.columns(2)
    with col_b_el:
        st.markdown("""
        <div class="profile-card-he">
            <strong style="color: #60a5fa; font-size: 1.15rem;">👨 Balance Semanal de Él</strong>
        </div>
        """, unsafe_allow_html=True)
        cb_1, cb_2, cb_3 = st.columns(3)
        with cb_1:
            st.metric("Consumo 7 Días", f"{total_sem_el_k:.0f} kcal", f"Prom: {(total_sem_el_k/7):.0f} kcal/día")
        with cb_2:
            st.metric("Gasto Semanal TDEE", f"{gasto_sem_el:.0f} kcal", f"{tdee_prom_el:.0f} kcal/día")
        with cb_3:
            if neto_sem_el >= 50:
                st.metric("Déficit Semanal", f"-{neto_sem_el:.0f} kcal", f"-{kg_sem_real_el:.2f} kg grasa")
            elif neto_sem_el <= -50:
                st.metric("Superávit Semanal", f"+{abs(neto_sem_el):.0f} kcal", f"+{kg_sem_real_el:.2f} kg ganados", delta_color="inverse")
            else:
                st.metric("Balance Semanal", "0 kcal", "Mantenimiento")

    with col_b_ella:
        st.markdown("""
        <div class="profile-card-she">
            <strong style="color: #f472b6; font-size: 1.15rem;">👩 Balance Semanal de Ella</strong>
        </div>
        """, unsafe_allow_html=True)
        cb_4, cb_5, cb_6 = st.columns(3)
        with cb_4:
            st.metric("Consumo 7 Días", f"{total_sem_ella_k:.0f} kcal", f"Prom: {(total_sem_ella_k/7):.0f} kcal/día")
        with cb_5:
            st.metric("Gasto Semanal TDEE", f"{gasto_sem_ella:.0f} kcal", f"{tdee_prom_ella:.0f} kcal/día")
        with cb_3 if False else cb_6:
            if neto_sem_ella >= 50:
                st.metric("Déficit Semanal", f"-{neto_sem_ella:.0f} kcal", f"-{kg_sem_real_ella:.2f} kg grasa")
            elif neto_sem_ella <= -50:
                st.metric("Superávit Semanal", f"+{abs(neto_sem_ella):.0f} kcal", f"+{kg_sem_real_ella:.2f} kg ganados", delta_color="inverse")
            else:
                st.metric("Balance Semanal", "0 kcal", "Mantenimiento")

    # Gráfico de Consumo Diario vs Meta
    fig_sem = go.Figure()
    fig_sem.add_trace(go.Bar(
        name="Consumo Él (kcal)",
        x=DIAS_SEMANA,
        y=consumo_dias_el,
        marker_color="#3b82f6"
    ))
    fig_sem.add_trace(go.Bar(
        name="Consumo Ella (kcal)",
        x=DIAS_SEMANA,
        y=consumo_dias_ella,
        marker_color="#ec4899"
    ))
    fig_sem.add_trace(go.Scatter(
        name="Meta Diaria Él",
        x=DIAS_SEMANA,
        y=[meta_kcal_el] * 7,
        mode="lines",
        line=dict(color="#60a5fa", width=2, dash="dash")
    ))
    fig_sem.add_trace(go.Scatter(
        name="Meta Diaria Ella",
        x=DIAS_SEMANA,
        y=[meta_kcal_ella] * 7,
        mode="lines",
        line=dict(color="#f472b6", width=2, dash="dash")
    ))
    fig_sem.update_layout(
        barmode='group',
        template="plotly_dark",
        title="Consumo Calórico Diario por Día (Lunes a Domingo) vs. Metas",
        xaxis=dict(title="Día de la Semana"),
        yaxis=dict(title="Calorías (kcal)"),
        height=370,
        margin=dict(l=40, r=20, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_sem, use_container_width=True)

    col_btn_sem1, col_btn_sem2 = st.columns([1.5, 3.5])
    with col_btn_sem1:
        if st.button("🗑️ Reiniciar Semana Completa (Borrar 7 días)", key="btn_reset_semana", use_container_width=True):
            st.session_state.semana_alimentos = {d: [] for d in DIAS_SEMANA}
            guardar_semana_alimentos(st.session_state.semana_alimentos)
            st.success("¡Semana reiniciada exitosamente!")
            st.rerun()
with tab2:
    st.markdown("### 🔥 Auditoría Metabólica y Gasto Energético Comparado")
    st.markdown("Cálculos científicos basados en Mifflin-St Jeor y equivalentes metabólicos (METs) precisos.")

    col_aud_he, col_aud_she = st.columns(2)
    
    with col_aud_he:
        st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 12px; padding: 18px; margin-bottom: 20px;">
            <h3 style="color: #60a5fa; margin-top: 0;">👨 Auditoría Metabólica: Él</h3>
            <p style="color: #94a3b8; font-size: 0.88rem;">Estatura: 180 cm | Peso: %.1f kg | Edad: %d años</p>
        </div>
        """ % (peso_el, edad_el), unsafe_allow_html=True)
        
        m_c1, m_c2 = st.columns(2)
        with m_c1:
            st.metric("Piso Vital (TMB)", f"{tmb_el:.0f} kcal", help="Mifflin-St Jeor: Calorías mínimas para subsistir en reposo absoluto.")
            st.metric("Techo Sedentario", f"{sed_el:.0f} kcal", help="TMB * 1.2: Límite para no engordar sin hacer actividad física.")
            st.metric("TDEE Promedio Semanal", f"{tdee_prom_el:.0f} kcal", help="Gasto promedio diario incluyendo tus horas de caminata.")
        with m_c2:
            st.metric("Quema 1h Caminata", f"{quema_1h_el:.0f} kcal", f"{mets_val} METs x {peso_el:.0f}kg", help="Fórmula: METs * Peso * 1h")
            st.metric("Techo Día con Caminata", f"{techo_cam_el:.0f} kcal", help="Sedentario + 1 hora de caminata.")
            st.metric(
                "Meta Calórica Asignada",
                f"{meta_kcal_el:.0f} kcal",
                help="🎯 Meta Calórica Asignada: Es tu presupuesto diario de comida. Está por encima de tu Piso Vital (TMB) para cuidar tu tiroides y masa muscular, y por debajo de tu Gasto (TDEE) para forzar la quema de grasa."
            )
        if deficit_el >= 15:
            card_title_el = "📉 Déficit Calórico Neto Diario"
            card_val_el = f"-{deficit_el:.0f} kcal / día"
            card_sub_el = f"Pérdida estimada de grasa (a 7700 kcal/kg):<br><b>📉 -{kg_sem_el:.2f} kg / semana</b> &nbsp;|&nbsp; <b>📅 -{kg_mes_el:.2f} kg / mes</b>"
            border_color_el = "#10b981"
            badge_note_el = f"💡 <b>¿Qué significa?</b> Comes <b>-{deficit_el:.0f} kcal/día</b> por debajo de tu gasto ({tdee_prom_el:.0f} kcal). Generas déficit para quemar reservas de grasa corporal."
        elif deficit_el <= -15:
            card_title_el = "📈 Superávit Calórico Neto Diario"
            card_val_el = f"+{abs(deficit_el):.0f} kcal / día"
            card_sub_el = f"Ganancia estimada de masa / peso:<br><b>📈 +{kg_sem_el:.2f} kg / semana</b> &nbsp;|&nbsp; <b>📅 +{kg_mes_el:.2f} kg / mes</b>"
            border_color_el = "#3b82f6"
            badge_note_el = f"💡 <b>¿Qué significa?</b> Comes <b>+{abs(deficit_el):.0f} kcal/día</b> por encima de tu gasto ({tdee_prom_el:.0f} kcal). Estás en superávit para ganar peso / masa muscular."
        else:
            card_title_el = "⚖️ Mantenimiento Calórico Diario"
            card_val_el = "Equilibrado (0 kcal)"
            card_sub_el = "Consumo equilibrado con tu gasto diario. Tu peso se mantendrá estable."
            border_color_el = "#94a3b8"
            badge_note_el = f"💡 <b>¿Qué significa?</b> Comes exactamente lo que gastas ({tdee_prom_el:.0f} kcal). Tu peso se mantendrá sin variaciones."

        st.markdown(f"""
        <div style="font-size: 0.77rem; color: #cbd5e1; background: rgba(59, 130, 246, 0.12); border-left: 3px solid #3b82f6; padding: 4px 8px; border-radius: 4px; margin-top: -6px; margin-bottom: 8px;">
            {badge_note_el}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid {border_color_el}; margin-top: 15px;">
            <div class="metric-title" style="color: {border_color_el};">{card_title_el}</div>
            <div class="metric-val" style="color: {border_color_el};">{card_val_el}</div>
            <div class="metric-sub">
                {card_sub_el}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_aud_she:
        st.markdown("""
        <div style="background: rgba(236, 72, 153, 0.08); border: 1px solid rgba(236, 72, 153, 0.25); border-radius: 12px; padding: 18px; margin-bottom: 20px;">
            <h3 style="color: #f472b6; margin-top: 0;">👩 Auditoría Metabólica: Ella</h3>
            <p style="color: #94a3b8; font-size: 0.88rem;">Estatura: 150 cm | Peso: %.1f kg | Edad: %d años</p>
        </div>
        """ % (peso_ella, edad_ella), unsafe_allow_html=True)
        
        m_c3, m_c4 = st.columns(2)
        with m_c3:
            st.metric("Piso Vital (TMB)", f"{tmb_ella:.0f} kcal", help="Mifflin-St Jeor: Gasto mínimo para funciones vitales.")
            st.metric("Techo Sedentario", f"{sed_ella:.0f} kcal", help="TMB * 1.2: Límite para no engordar en reposo.")
            st.metric("TDEE Promedio Semanal", f"{tdee_prom_ella:.0f} kcal", help="Gasto promedio diario incluyendo tus horas de caminata.")
        with m_c4:
            st.metric("Quema 1h Caminata", f"{quema_1h_ella:.0f} kcal", f"{mets_val} METs x {peso_ella:.0f}kg", help="Fórmula: METs * Peso * 1h")
            st.metric("Techo Día con Caminata", f"{techo_cam_ella:.0f} kcal", help="Sedentario + 1 hora de caminata.")
            st.metric(
                "Meta Calórica Asignada",
                f"{meta_kcal_ella:.0f} kcal",
                help="🎯 Meta Calórica Asignada: Es tu presupuesto diario de comida. Puede ser déficit para bajar de peso o superávit para ganar masa muscular."
            )

        if deficit_ella >= 15:
            card_title_ella = "📉 Déficit Calórico Neto Diario"
            card_val_ella = f"-{deficit_ella:.0f} kcal / día"
            card_sub_ella = f"Pérdida estimada de grasa (a 7700 kcal/kg):<br><b>📉 -{kg_sem_ella:.2f} kg / semana</b> &nbsp;|&nbsp; <b>📅 -{kg_mes_ella:.2f} kg / mes</b>"
            border_color_ella = "#10b981"
            badge_note_ella = f"💡 <b>¿Qué significa?</b> Comes <b>-{deficit_ella:.0f} kcal/día</b> por debajo de tu gasto ({tdee_prom_ella:.0f} kcal). Generas déficit para quemar reservas de grasa corporal."
        elif deficit_ella <= -15:
            card_title_ella = "📈 Superávit Calórico Neto Diario"
            card_val_ella = f"+{abs(deficit_ella):.0f} kcal / día"
            card_sub_ella = f"Ganancia estimada de masa / peso:<br><b>📈 +{kg_sem_ella:.2f} kg / semana</b> &nbsp;|&nbsp; <b>📅 +{kg_mes_ella:.2f} kg / mes</b>"
            border_color_ella = "#ec4899"
            badge_note_ella = f"💡 <b>¿Qué significa?</b> Comes <b>+{abs(deficit_ella):.0f} kcal/día</b> por encima de tu gasto ({tdee_prom_ella:.0f} kcal). Estás en superávit para ganar peso / masa muscular."
        else:
            card_title_ella = "⚖️ Mantenimiento Calórico Diario"
            card_val_ella = "Equilibrado (0 kcal)"
            card_sub_ella = "Consumo equilibrado con tu gasto diario. Tu peso se mantendrá estable."
            border_color_ella = "#94a3b8"
            badge_note_ella = f"💡 <b>¿Qué significa?</b> Comes exactamente lo que gastas ({tdee_prom_ella:.0f} kcal). Tu peso se mantendrá sin variaciones."

        st.markdown(f"""
        <div style="font-size: 0.77rem; color: #cbd5e1; background: rgba(236, 72, 153, 0.12); border-left: 3px solid #ec4899; padding: 4px 8px; border-radius: 4px; margin-top: -6px; margin-bottom: 8px;">
            {badge_note_ella}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid {border_color_ella}; margin-top: 15px;">
            <div class="metric-title" style="color: {border_color_ella};">{card_title_ella}</div>
            <div class="metric-val" style="color: {border_color_ella};">{card_val_ella}</div>
            <div class="metric-sub">
                {card_sub_ella}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # GRÁFICO 1: UMBRALES CALÓRICOS COMPARATIVOS
    st.markdown("#### 1. Comparación de Umbrales Energéticos (Él vs. Ella)")
    
    categorias_umbrales = ["Piso Vital (TMB)", "Consumo del Plan", "Techo Sedentario", "Gasto Promedio (TDEE)", "Techo Día Caminata"]
    valores_el = [tmb_el, meta_kcal_el, sed_el, tdee_prom_el, techo_cam_el]
    valores_ella = [tmb_ella, meta_kcal_ella, sed_ella, tdee_prom_ella, techo_cam_ella]
    
    fig_umbrales = go.Figure()
    fig_umbrales.add_trace(go.Bar(
        name="Él",
        x=categorias_umbrales,
        y=valores_el,
        text=[f"{v:.0f} kcal" for v in valores_el],
        textposition="outside",
        marker_color="#3b82f6"
    ))
    fig_umbrales.add_trace(go.Bar(
        name="Ella",
        x=categorias_umbrales,
        y=valores_ella,
        text=[f"{v:.0f} kcal" for v in valores_ella],
        textposition="outside",
        marker_color="#ec4899"
    ))
    
    fig_umbrales.update_layout(
        barmode='group',
        template="plotly_dark",
        height=400,
        yaxis=dict(title="Kilocalorías (kcal/día)", range=[0, max(max(valores_el), max(valores_ella)) * 1.18]),
        xaxis=dict(title="Umbral Metabólico"),
        margin=dict(l=40, r=20, t=30, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_umbrales, use_container_width=True)

    st.markdown("---")

    # GRÁFICO 2: PROYECCIÓN DINÁMICA A 24 SEMANAS RECALCULANDO TMB
    st.markdown("#### 2. Curva de Proyección Dinámica a 24 Semanas (6 Meses)")
    st.markdown(
        "*Simulación adaptativa:* Modela semana a semana tanto el déficit (pérdida de peso) como el superávit (ganancia de masa/peso), "
        "recalculando el nuevo TMB y gasto físico con el peso actualizado."
    )
    
    semanas = list(range(0, 25))
    proy_peso_el = [peso_el]
    proy_peso_ella = [peso_ella]
    proy_deficit_el = [deficit_el]
    proy_deficit_ella = [deficit_ella]

    curr_p_el = peso_el
    curr_p_ella = peso_ella

    for s in range(1, 25):
        # Recalcular Él
        tmb_s_el = (10.0 * curr_p_el) + (6.25 * altura_el) - (5.0 * edad_el) + 5.0
        sed_s_el = tmb_s_el * 1.2
        q1h_s_el = mets_val * curr_p_el * 1.0
        tdee_s_el = sed_s_el + ((q1h_s_el * horas_sem) / 7.0)
        def_s_el = tdee_s_el - meta_kcal_el
        var_sem_el = (def_s_el * 7.0) / 7700.0
        curr_p_el = max(45.0, min(220.0, curr_p_el - var_sem_el))
        proy_peso_el.append(round(curr_p_el, 2))
        proy_deficit_el.append(round(def_s_el, 0))

        # Recalcular Ella
        tmb_s_ella = (10.0 * curr_p_ella) + (6.25 * altura_ella) - (5.0 * edad_ella) - 161.0
        sed_s_ella = tmb_s_ella * 1.2
        q1h_s_ella = mets_val * curr_p_ella * 1.0
        tdee_s_ella = sed_s_ella + ((q1h_s_ella * horas_sem) / 7.0)
        def_s_ella = tdee_s_ella - meta_kcal_ella
        var_sem_ella = (def_s_ella * 7.0) / 7700.0
        curr_p_ella = max(35.0, min(160.0, curr_p_ella - var_sem_ella))
        proy_peso_ella.append(round(curr_p_ella, 2))
        proy_deficit_ella.append(round(def_s_ella, 0))

    df_proy = pd.DataFrame({
        "Semana": semanas,
        "Peso_El": proy_peso_el,
        "Deficit_El": proy_deficit_el,
        "Peso_Ella": proy_peso_ella,
        "Deficit_Ella": proy_deficit_ella
    })

    fig_proy = go.Figure()

    fig_proy.add_trace(go.Scatter(
        x=df_proy["Semana"],
        y=df_proy["Peso_El"],
        mode="lines+markers",
        name=f"Él ({proy_peso_el[0]:.1f} kg → {proy_peso_el[-1]:.1f} kg)",
        line=dict(color="#3b82f6", width=3),
        marker=dict(size=6),
        hovertemplate="<b>Semana %{x}</b><br>Peso Él: %{y:.1f} kg<extra></extra>"
    ))

    fig_proy.add_trace(go.Scatter(
        x=df_proy["Semana"],
        y=df_proy["Peso_Ella"],
        mode="lines+markers",
        name=f"Ella ({proy_peso_ella[0]:.1f} kg → {proy_peso_ella[-1]:.1f} kg)",
        line=dict(color="#ec4899", width=3),
        marker=dict(size=6),
        hovertemplate="<b>Semana %{x}</b><br>Peso Ella: %{y:.1f} kg<extra></extra>"
    ))

    fig_proy.update_layout(
        template="plotly_dark",
        title="Trayectoria Proyectada de Peso a 24 Semanas con Ajuste Dinámico de TMB",
        xaxis=dict(title="Semana del Programa", tickmode="linear", tick0=0, dtick=2),
        yaxis=dict(title="Peso Corporal (kg)"),
        height=450,
        hovermode="x unified",
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig_proy, use_container_width=True)

    diff_8_el = proy_peso_el[8] - peso_el
    diff_24_el = proy_peso_el[24] - peso_el
    diff_8_ella = proy_peso_ella[8] - peso_ella
    diff_24_ella = proy_peso_ella[24] - peso_ella

    tipo_el_str = "Ganancia" if diff_24_el > 0 else "Pérdida" if diff_24_el < 0 else "Estable"
    tipo_ella_str = "Ganancia" if diff_24_ella > 0 else "Pérdida" if diff_24_ella < 0 else "Estable"

    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    with col_h1:
        st.metric("Él: Semana 8 (2 meses)", f"{proy_peso_el[8]:.1f} kg", f"{diff_8_el:+.1f} kg", delta_color="normal" if diff_8_el > 0 else "inverse")
    with col_h2:
        st.metric("Él: Semana 24 (6 meses)", f"{proy_peso_el[24]:.1f} kg", f"{diff_24_el:+.1f} kg ({tipo_el_str})", delta_color="normal" if diff_24_el > 0 else "inverse")
    with col_h3:
        st.metric("Ella: Semana 8 (2 meses)", f"{proy_peso_ella[8]:.1f} kg", f"{diff_8_ella:+.1f} kg", delta_color="normal" if diff_8_ella > 0 else "inverse")
    with col_h4:
        st.metric("Ella: Semana 24 (6 meses)", f"{proy_peso_ella[24]:.1f} kg", f"{diff_24_ella:+.1f} kg ({tipo_ella_str})", delta_color="normal" if diff_24_ella > 0 else "inverse")


# ==============================================================================
# PESTAÑA 3: REGISTRO DE PESO Y AVANCE REAL (TRACKER CON PERSISTENCIA)
# ==============================================================================
with tab3:
    st.markdown("### 📈 Registro de Peso y Avance Real")
    st.markdown("Guarda tus pesajes periódicos y compáralos contra la curva metabólica proyectada.")

    ARCHIVO_CSV = "registro_peso.csv"

    # Cargar o crear el DataFrame de persistencia local
    if os.path.exists(ARCHIVO_CSV):
        try:
            df_registro = pd.read_csv(ARCHIVO_CSV)
            df_registro["Fecha"] = pd.to_datetime(df_registro["Fecha"]).dt.date
        except Exception:
            df_registro = pd.DataFrame(columns=["Fecha", "Peso_El", "Peso_Ella", "Notas"])
    else:
        df_registro = pd.DataFrame(columns=["Fecha", "Peso_El", "Peso_Ella", "Notas"])

    # Formulario para registrar nuevo pesaje
    with st.expander("📝 Registrar Nuevo Pesaje", expanded=(len(df_registro) == 0)):
        with st.form("form_nuevo_pesaje", clear_on_submit=False):
            f_col_p1, f_col_p2, f_col_p3, f_col_p4 = st.columns(4)
            with f_col_p1:
                input_fecha = st.date_input("Fecha del Pesaje", value=date.today())
            with f_col_p2:
                input_p_el = st.number_input("Peso de Él (kg)", min_value=60.0, max_value=170.0, value=float(peso_el), step=0.1)
            with f_col_p3:
                input_p_ella = st.number_input("Peso de Ella (kg)", min_value=35.0, max_value=120.0, value=float(peso_ella), step=0.1)
            with f_col_p4:
                input_notas = st.text_input("Comentarios / Semana", placeholder="Ej: Semana 1 completada")

            btn_guardar_pesaje = st.form_submit_button("💾 Guardar Registro de Peso")
            
            if btn_guardar_pesaje:
                # Comprobar si ya existe un registro para esa fecha
                if not df_registro.empty and input_fecha in df_registro["Fecha"].values:
                    df_registro.loc[df_registro["Fecha"] == input_fecha, ["Peso_El", "Peso_Ella", "Notas"]] = [input_p_el, input_p_ella, input_notas]
                    st.success(f"Registro actualizado para la fecha {input_fecha}.")
                else:
                    nuevo_reg = pd.DataFrame([{
                        "Fecha": input_fecha,
                        "Peso_El": input_p_el,
                        "Peso_Ella": input_p_ella,
                        "Notas": input_notas
                    }])
                    df_registro = pd.concat([df_registro, nuevo_reg], ignore_index=True)
                    st.success(f"¡Pesaje guardado exitosamente para el {input_fecha}!")
                
                # Ordenar por fecha y persistir a CSV
                df_registro = df_registro.sort_values(by="Fecha").reset_index(drop=True)
                df_registro.to_csv(ARCHIVO_CSV, index=False)
                
                # Sincronizar automáticamente con la configuración del perfil para que persista
                cfg_actual = cargar_config_usuario()
                cfg_actual["peso_el"] = float(input_p_el)
                cfg_actual["peso_ella"] = float(input_p_ella)
                guardar_config_usuario(cfg_actual)
                
                st.rerun()

    # Visualización y Comparación Gráfica
    if not df_registro.empty:
        df_registro["Fecha"] = pd.to_datetime(df_registro["Fecha"]).dt.date
        df_registro = df_registro.sort_values(by="Fecha").reset_index(drop=True)
        
        # Superposición de curva teórica vs. registros reales
        st.markdown("#### Curva Teórica Proyectada vs. Pesos Reales Registrados")
        
        # Generar fechas proyectadas a partir de la primera fecha registrada
        fecha_inicio = df_registro["Fecha"].iloc[0]
        fechas_proy = [fecha_inicio + pd.Timedelta(weeks=w) for w in semanas]

        fig_tracker = go.Figure()

        # Curva Teórica Él
        fig_tracker.add_trace(go.Scatter(
            x=fechas_proy,
            y=proy_peso_el,
            mode="lines",
            name="Proyección Teórica (Él)",
            line=dict(color="rgba(59, 130, 246, 0.4)", width=2, dash="dash"),
            hoverinfo="skip"
        ))

        # Registros Reales Él
        fig_tracker.add_trace(go.Scatter(
            x=df_registro["Fecha"],
            y=df_registro["Peso_El"],
            mode="lines+markers",
            name="Real: Él",
            line=dict(color="#3b82f6", width=3),
            marker=dict(size=9, symbol="diamond"),
            hovertemplate="<b>Él (Real)</b><br>Fecha: %{x}<br>Peso: %{y:.1f} kg<extra></extra>"
        ))

        # Curva Teórica Ella
        fig_tracker.add_trace(go.Scatter(
            x=fechas_proy,
            y=proy_peso_ella,
            mode="lines",
            name="Proyección Teórica (Ella)",
            line=dict(color="rgba(236, 72, 153, 0.4)", width=2, dash="dash"),
            hoverinfo="skip"
        ))

        # Registros Reales Ella
        fig_tracker.add_trace(go.Scatter(
            x=df_registro["Fecha"],
            y=df_registro["Peso_Ella"],
            mode="lines+markers",
            name="Real: Ella",
            line=dict(color="#ec4899", width=3),
            marker=dict(size=9, symbol="circle"),
            hovertemplate="<b>Ella (Real)</b><br>Fecha: %{x}<br>Peso: %{y:.1f} kg<extra></extra>"
        ))

        fig_tracker.update_layout(
            template="plotly_dark",
            title="Evolución Real de Pesajes vs. Meta Metabólica",
            xaxis=dict(title="Fecha"),
            yaxis=dict(title="Peso (kg)"),
            height=460,
            hovermode="x unified",
            margin=dict(l=40, r=20, t=50, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_tracker, use_container_width=True)

        # Tabla histórica y métricas de avance
        st.markdown("#### Historial de Pesajes Registrados")
        
        c_hist1, c_hist2 = st.columns([3, 1])
        with c_hist1:
            st.dataframe(df_registro, use_container_width=True)
            
        with c_hist2:
            peso_ini_el = df_registro["Peso_El"].iloc[0]
            peso_act_el = df_registro["Peso_El"].iloc[-1]
            diff_el = peso_act_el - peso_ini_el

            peso_ini_ella = df_registro["Peso_Ella"].iloc[0]
            peso_act_ella = df_registro["Peso_Ella"].iloc[-1]
            diff_ella = peso_act_ella - peso_ini_ella

            st.metric("Avance Acumulado (Él)", f"{peso_act_el:.1f} kg", f"{diff_el:+.1f} kg", delta_color="inverse")
            st.metric("Avance Acumulado (Ella)", f"{peso_act_ella:.1f} kg", f"{diff_ella:+.1f} kg", delta_color="inverse")
            
            # Opción para eliminar el último registro
            if st.button("Eliminar Último Registro", use_container_width=True):
                df_registro = df_registro.iloc[:-1]
                df_registro.to_csv(ARCHIVO_CSV, index=False)
                st.rerun()

    else:
        st.info("No hay pesajes guardados todavía. Usa el formulario de arriba para cargar tu primer registro.")
