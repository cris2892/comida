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
ARCHIVO_CAMINATAS_SEMANA = "semana_caminatas.json"
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Catálogo completo de actividades físicas con valores METs estándar
CATALOGO_ACTIVIDADES = {
    "🚶 Caminata Paso Constante (4.0 METs)": {"mets": 4.0, "icono": "🚶", "nombre": "Caminata Paso Constante"},
    "🚶‍♂️ Caminata Rápida (4.8 METs)": {"mets": 4.8, "icono": "🚶‍♂️", "nombre": "Caminata Rápida"},
    "🚶‍♀️ Caminata Suave / Paseo (3.0 METs)": {"mets": 3.0, "icono": "🚶‍♀️", "nombre": "Caminata Suave"},
    "🏋️ Musculación / Gimnasio / Pesas (4.5 METs)": {"mets": 4.5, "icono": "🏋️", "nombre": "Musculación / Pesas"},
    "🚴 Ciclismo / Bicicleta (6.0 METs)": {"mets": 6.0, "icono": "🚴", "nombre": "Ciclismo / Bici"},
    "🎾 Pádel / Tenis (6.0 METs)": {"mets": 6.0, "icono": "🎾", "nombre": "Pádel / Tenis"},
    "🏃 Running / Trote (8.0 METs)": {"mets": 8.0, "icono": "🏃", "nombre": "Running / Trote"},
    "🧘 Yoga / Pilates / Estiramiento (3.0 METs)": {"mets": 3.0, "icono": "🧘", "nombre": "Yoga / Pilates"},
    "🏊 Natación Moderada (6.0 METs)": {"mets": 6.0, "icono": "🏊", "nombre": "Natación"},
    "🥊 Boxeo / HIIT / Funcional (7.5 METs)": {"mets": 7.5, "icono": "🥊", "nombre": "HIIT / Funcional"},
    "⌚ Actividad con Reloj Inteligente (kcal directas)": {"mets": 0.0, "icono": "⌚", "nombre": "Reloj Inteligente"},
    "⚡ Otra Actividad Personalizada": {"mets": 4.0, "icono": "⚡", "nombre": "Otra Actividad"}
}

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

def cargar_caminatas_semana():
    base = {
        d: {
            "actividades_el": [],
            "actividades_ella": [],
            "horas_el": 0.0,
            "kcal_el": 0.0,
            "horas_ella": 0.0,
            "kcal_ella": 0.0
        } for d in DIAS_SEMANA
    }
    if os.path.exists(ARCHIVO_CAMINATAS_SEMANA):
        try:
            with open(ARCHIVO_CAMINATAS_SEMANA, "r", encoding="utf-8") as f:
                data = json.load(f)
                for d in DIAS_SEMANA:
                    if d in data:
                        d_info = data[d]
                        acts_el = d_info.get("actividades_el")
                        acts_ella = d_info.get("actividades_ella")

                        # Migración retrocompatible si el archivo guardado tiene el formato viejo
                        if acts_el is None:
                            acts_el = []
                            h_old = float(d_info.get("horas_el", 0.0))
                            k_old = float(d_info.get("kcal_el", 0.0))
                            if k_old > 0:
                                acts_el.append({
                                    "id": f"el_init_{d}",
                                    "nombre": "Reloj Inteligente",
                                    "icono": "⌚",
                                    "minutos": int(round((k_old / (4.0 * 119.0)) * 60)),
                                    "kcal": round(k_old, 1),
                                    "modo": "Reloj"
                                })
                            elif h_old > 0:
                                acts_el.append({
                                    "id": f"el_init_{d}",
                                    "nombre": "Caminata",
                                    "icono": "🚶",
                                    "minutos": int(round(h_old * 60)),
                                    "kcal": round(h_old * 4.0 * 119.0, 1),
                                    "modo": "METs"
                                })

                        if acts_ella is None:
                            acts_ella = []
                            h_old_ella = float(d_info.get("horas_ella", 0.0))
                            k_old_ella = float(d_info.get("kcal_ella", 0.0))
                            if k_old_ella > 0:
                                acts_ella.append({
                                    "id": f"ella_init_{d}",
                                    "nombre": "Reloj Inteligente",
                                    "icono": "⌚",
                                    "minutos": int(round((k_old_ella / (4.0 * 69.0)) * 60)),
                                    "kcal": round(k_old_ella, 1),
                                    "modo": "Reloj"
                                })
                            elif h_old_ella > 0:
                                acts_ella.append({
                                    "id": f"ella_init_{d}",
                                    "nombre": "Caminata",
                                    "icono": "🚶",
                                    "minutos": int(round(h_old_ella * 60)),
                                    "kcal": round(h_old_ella * 4.0 * 69.0, 1),
                                    "modo": "METs"
                                })

                        base[d] = {
                            "actividades_el": acts_el,
                            "actividades_ella": acts_ella,
                            "horas_el": round(sum(a.get("minutos", 0) for a in acts_el) / 60.0, 2),
                            "kcal_el": round(sum(float(a.get("kcal", 0.0)) for a in acts_el), 1),
                            "horas_ella": round(sum(a.get("minutos", 0) for a in acts_ella) / 60.0, 2),
                            "kcal_ella": round(sum(float(a.get("kcal", 0.0)) for a in acts_ella), 1)
                        }
                return base
        except Exception:
            return base
    return base

def guardar_caminatas_semana(dict_caminatas):
    try:
        for d in DIAS_SEMANA:
            if d in dict_caminatas:
                acts_el = dict_caminatas[d].get("actividades_el", [])
                acts_ella = dict_caminatas[d].get("actividades_ella", [])
                dict_caminatas[d]["horas_el"] = round(sum(a.get("minutos", 0) for a in acts_el) / 60.0, 2)
                dict_caminatas[d]["kcal_el"] = round(sum(float(a.get("kcal", 0.0)) for a in acts_el), 1)
                dict_caminatas[d]["horas_ella"] = round(sum(a.get("minutos", 0) for a in acts_ella) / 60.0, 2)
                dict_caminatas[d]["kcal_ella"] = round(sum(float(a.get("kcal", 0.0)) for a in acts_ella), 1)
        with open(ARCHIVO_CAMINATAS_SEMANA, "w", encoding="utf-8") as f:
            json.dump(dict_caminatas, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error al guardar caminatas semanales: {e}")

# Inicialización en session_state con persistencia local
if "alimentos_custom" not in st.session_state:
    st.session_state.alimentos_custom = cargar_alimentos_custom()

if "recetas_guardadas" not in st.session_state:
    st.session_state.recetas_guardadas = cargar_recetas_guardadas()

if "semana_alimentos" not in st.session_state:
    st.session_state.semana_alimentos = cargar_semana_alimentos()

if "semana_caminatas" not in st.session_state:
    st.session_state.semana_caminatas = cargar_caminatas_semana()

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
st.sidebar.markdown("## ⚙️ Configuración Personal")

cfg_usuario = cargar_config_usuario()

tab_sb_el, tab_sb_ella = st.sidebar.tabs(["👨 Perfil: Él", "👩 Perfil: Ella"])

with tab_sb_el:
    col_el1, col_el2 = st.columns(2)
    with col_el1:
        peso_el = st.number_input("Peso (kg)", min_value=50.0, max_value=170.0, value=float(cfg_usuario.get("peso_el", 119.0)), step=0.5, key="peso_el")
    with col_el2:
        altura_el = st.number_input("Altura (cm)", min_value=130, max_value=220, value=int(cfg_usuario.get("altura_el", 180)), step=1, key="altura_el")
    edad_el = st.number_input("Edad (años)", min_value=18, max_value=99, value=int(cfg_usuario.get("edad_el", 34)), step=1, key="edad_el")

with tab_sb_ella:
    col_ella1, col_ella2 = st.columns(2)
    with col_ella1:
        peso_ella = st.number_input("Peso (kg)", min_value=35.0, max_value=140.0, value=float(cfg_usuario.get("peso_ella", 69.0)), step=0.5, key="peso_ella")
    with col_ella2:
        altura_ella = st.number_input("Altura (cm)", min_value=120, max_value=200, value=int(cfg_usuario.get("altura_ella", 150)), step=1, key="altura_ella")
    edad_ella = st.number_input("Edad (años)", min_value=18, max_value=99, value=int(cfg_usuario.get("edad_ella", 33)), step=1, key="edad_ella")

# Configuración de Actividad Semanal e Intensidad
intensidad_mets_dict = {
    "4.0 METs - Caminata paso constante/ligero (4.8 - 5.0 km/h)": 4.0,
    "3.0 METs - Caminata suave (4.0 km/h)": 3.0,
    "4.8 METs - Caminata rápida (5.5 - 6.0 km/h)": 4.8
}
opcion_mets = st.session_state.get("sim_opcion_mets", cfg_usuario.get("opcion_mets", "4.0 METs - Caminata paso constante/ligero (4.8 - 5.0 km/h)"))
if opcion_mets not in intensidad_mets_dict:
    opcion_mets = "4.0 METs - Caminata paso constante/ligero (4.8 - 5.0 km/h)"
mets_val = intensidad_mets_dict[opcion_mets]
horas_sem = float(st.session_state.get("sim_horas_sem", cfg_usuario.get("horas_sem", 3.0)))

# Criterio de reparto de la Olla Compartida
tipo_reparto = st.session_state.get("tipo_reparto_val", cfg_usuario.get("tipo_reparto", "Dinámica según Metas Calóricas"))

# CÁLCULOS METABÓLICOS BASE (MIFFLIN-ST JEOR & TDEE)
tmb_el = (10.0 * peso_el) + (6.25 * altura_el) - (5.0 * edad_el) + 5.0
sed_el = tmb_el * 1.2
quema_1h_el = mets_val * peso_el * 1.0
techo_cam_el = sed_el + quema_1h_el
tdee_prom_el = sed_el + ((quema_1h_el * horas_sem) / 7.0)

tmb_ella = (10.0 * peso_ella) + (6.25 * altura_ella) - (5.0 * edad_ella) - 161.0
sed_ella = tmb_ella * 1.2
quema_1h_ella = mets_val * peso_ella * 1.0
techo_cam_ella = sed_ella + quema_1h_ella
tdee_prom_ella = sed_ella + ((quema_1h_ella * horas_sem) / 7.0)

with tab_sb_el:
    st.markdown("---")
    st.markdown("### 🎯 Objetivo & Meta Calórica (Él)")
    lista_act_el = [
        "📉 Déficit Moderado (Base 2150 kcal)",
        "📉 Déficit Ligero (Base 2400 kcal)",
        "⚖️ Mantenimiento Metabólico (TDEE)",
        "📈 Superávit (+300 kcal Ganancia / Volumen)",
        "🛠️ Personalizado (Ajustar a mano kcal o macros)"
    ]
    idx_act_el = lista_act_el.index(cfg_usuario.get("opcion_act_el")) if cfg_usuario.get("opcion_act_el") in lista_act_el else 0
    opcion_act_el = st.selectbox("Meta Nutricional (Él)", lista_act_el, index=idx_act_el, key="sel_act_el")

    custom_kcal_el_val = float(cfg_usuario.get("custom_kcal_el", 2150.0))
    custom_p_el_val = float(cfg_usuario.get("custom_p_el", 188.0))
    custom_c_el_val = float(cfg_usuario.get("custom_c_el", 210.0))
    custom_g_el_val = float(cfg_usuario.get("custom_g_el", 60.0))
    modo_pers_el_val = str(cfg_usuario.get("modo_pers_el", "Calorías Totales Directas (kcal)"))

    if "Personalizado" in opcion_act_el:
        st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 8px; padding: 10px; margin-top: 6px; margin-bottom: 10px;">
            <strong style="color: #60a5fa; font-size: 0.9rem;">🛠️ Panel Personalizado (Él)</strong><br>
            <span style="font-size: 0.78rem; color: #cbd5e1;">Ajusta tus calorías o tus gramos de macros libremente:</span>
        </div>
        """, unsafe_allow_html=True)
        
        modo_pers_el_val = st.radio(
            "Ajustar por (Él):",
            ["Gramos de Macronutrientes (P, C, G)", "Calorías Totales Directas (kcal)"],
            index=0 if modo_pers_el_val == "Gramos de Macronutrientes (P, C, G)" else 1,
            key="modo_pers_el"
        )
        
        if modo_pers_el_val == "Calorías Totales Directas (kcal)":
            custom_kcal_el_val = st.number_input(
                "Calorías Diarias Asignadas (kcal)",
                min_value=1000.0, max_value=5000.0, value=custom_kcal_el_val, step=50.0,
                key="custom_kcal_el",
                help="Presupuesto calórico diario que te asignó tu plan o nutricionista."
            )
            meta_kcal_el = custom_kcal_el_val
            req_p_el = round((meta_kcal_el * 0.35) / 4.0)
            req_c_el = round((meta_kcal_el * 0.40) / 4.0)
            req_g_el = round((meta_kcal_el * 0.25) / 9.0)
            st.caption(f"Distribución sugerida (35% P, 40% C, 25% G): **{req_p_el:.0f}g P | {req_c_el:.0f}g C | {req_g_el:.0f}g G**")
        else:
            st.markdown("**Gramos Diarios (Él):**")
            c_p_el, c_c_el, c_g_el = st.columns(3)
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

    st.markdown(
        f"<span class='badge-kcal'>Meta: {meta_kcal_el:.0f} kcal</span> {badge_estado_el}<br>"
        f"<span class='badge-p'>{req_p_el:.0f}g P</span> "
        f"<span class='badge-c'>{req_c_el:.0f}g C</span> "
        f"<span class='badge-g'>{req_g_el:.0f}g G</span>",
        unsafe_allow_html=True
    )

with tab_sb_ella:
    st.markdown("---")
    st.markdown("### 🎯 Objetivo & Meta Calórica (Ella)")
    lista_act_ella = [
        "📉 Déficit Moderado (Base 1300 kcal)",
        "📉 Déficit Ligero (Base 1500 kcal)",
        "⚖️ Mantenimiento Metabólico (TDEE)",
        "📈 Superávit (+250 kcal Ganancia / Volumen)",
        "🛠️ Personalizada (Ajustar a mano kcal o macros)"
    ]
    idx_act_ella = lista_act_ella.index(cfg_usuario.get("opcion_act_ella")) if cfg_usuario.get("opcion_act_ella") in lista_act_ella else 0
    opcion_act_ella = st.selectbox("Meta Nutricional (Ella)", lista_act_ella, index=idx_act_ella, key="sel_act_ella")

    custom_kcal_ella_val = float(cfg_usuario.get("custom_kcal_ella", 1300.0))
    custom_p_ella_val = float(cfg_usuario.get("custom_p_ella", 115.0))
    custom_c_ella_val = float(cfg_usuario.get("custom_c_ella", 120.0))
    custom_g_ella_val = float(cfg_usuario.get("custom_g_ella", 38.0))
    modo_pers_ella_val = str(cfg_usuario.get("modo_pers_ella", "Calorías Totales Directas (kcal)"))

    if "Personalizada" in opcion_act_ella:
        st.markdown("""
        <div style="background: rgba(236, 72, 153, 0.12); border: 1px solid rgba(236, 72, 153, 0.35); border-radius: 8px; padding: 10px; margin-top: 6px; margin-bottom: 10px;">
            <strong style="color: #f472b6; font-size: 0.9rem;">🛠️ Panel Personalizado (Ella)</strong><br>
            <span style="font-size: 0.78rem; color: #cbd5e1;">Ajusta tus calorías o tus gramos de macros libremente:</span>
        </div>
        """, unsafe_allow_html=True)
        
        modo_pers_ella_val = st.radio(
            "Ajustar por (Ella):",
            ["Gramos de Macronutrientes (P, C, G)", "Calorías Totales Directas (kcal)"],
            index=0 if modo_pers_ella_val == "Gramos de Macronutrientes (P, C, G)" else 1,
            key="modo_pers_ella"
        )
        
        if modo_pers_ella_val == "Calorías Totales Directas (kcal)":
            custom_kcal_ella_val = st.number_input(
                "Calorías Diarias Asignadas (Ella)",
                min_value=800.0, max_value=4000.0, value=custom_kcal_ella_val, step=25.0,
                key="custom_kcal_ella",
                help="Presupuesto calórico diario que te asignó tu plan o nutricionista."
            )
            meta_kcal_ella = custom_kcal_ella_val
            req_p_ella = round((meta_kcal_ella * 0.35) / 4.0)
            req_c_ella = round((meta_kcal_ella * 0.38) / 4.0)
            req_g_ella = round((meta_kcal_ella * 0.27) / 9.0)
            st.caption(f"Distribución sugerida (35% P, 38% C, 27% G): **{req_p_ella:.0f}g P | {req_c_ella:.0f}g C | {req_g_ella:.0f}g G**")
        else:
            st.markdown("**Gramos Diarios (Ella):**")
            c_p_ella, c_c_ella, c_g_ella = st.columns(3)
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

    st.markdown(
        f"<span class='badge-kcal'>Meta: {meta_kcal_ella:.0f} kcal</span> {badge_estado_ella}<br>"
        f"<span class='badge-p'>{req_p_ella:.0f}g P</span> "
        f"<span class='badge-c'>{req_c_ella:.0f}g C</span> "
        f"<span class='badge-g'>{req_g_ella:.0f}g G</span>",
        unsafe_allow_html=True
    )

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
tab1, tab_sem, tab2, tab3, tab4 = st.tabs([
    "🧮 Calculadora de Alimentos & Armador de Platos",
    "📅 Registro & Balance Semanal (Lunes a Domingo)",
    "🔥 Auditoría Metabólica & Simulador de Caminatas",
    "📈 Registro de Peso y Avance Real",
    "📚 Guía Metabólica & Glosario Nutricional"
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

    # Criterio de Reparto de la Olla Compartida
    with st.container():
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.55); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px 16px; margin-bottom: 12px;">
            <span style="font-weight: 700; color: #38bdf8; font-size: 0.92rem;">⚖️ CRITERIO DE REPARTO DE LA OLLA:</span>
            <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 2px;">
                Elige cómo dividir las porciones cocidas de la olla entre ambos:
            </div>
        </div>
        """, unsafe_allow_html=True)
        lista_reparto_tab1 = ["Dinámica según Metas Calóricas", "Fija Estándar (60% Él / 40% Ella)"]
        idx_reparto_tab1 = lista_reparto_tab1.index(tipo_reparto) if tipo_reparto in lista_reparto_tab1 else 0
        tipo_reparto_sel = st.radio(
            "Criterio de Reparto:",
            lista_reparto_tab1,
            index=idx_reparto_tab1,
            horizontal=True,
            key="tipo_reparto_val",
            help="Dinámica: Reparte según las calorías objetivo de cada uno. Fija: Siempre 60% para Él y 40% para Ella."
        )
        c_inf_r1, c_inf_r2 = st.columns(2)
        with c_inf_r1:
            st.markdown(f"<span style='color: #60a5fa; font-weight: 600; font-size: 0.88rem;'>👨 Porción Él: <b>{prop_el*100:.1f}%</b> del total cocido</span>", unsafe_allow_html=True)
        with c_inf_r2:
            st.markdown(f"<span style='color: #f472b6; font-weight: 600; font-size: 0.88rem;'>👩 Porción Ella: <b>{prop_ella*100:.1f}%</b> del total cocido</span>", unsafe_allow_html=True)


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
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(30,41,59,0.5); padding:10px 18px; border-radius:10px; border:1px solid rgba(255,255,255,0.08); margin-bottom:14px; flex-wrap:wrap; gap:8px;">
        <div style="font-size:0.85rem; font-weight:700; color:#38bdf8;">PASO 1: 🥩 Ingredientes en Crudo</div>
        <div style="color:#64748b;">➜</div>
        <div style="font-size:0.85rem; font-weight:700; color:#cbd5e1;">PASO 2: ⚖️ Pesar Olla Cocida</div>
        <div style="color:#64748b;">➜</div>
        <div style="font-size:0.85rem; font-weight:700; color:#10b981;">PASO 3: 🍽️ Servir en Balanza</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("##### ➕ PASO 1: Agregar Ingrediente a la Olla Actual (en crudo)")
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
        st.markdown("### ⚖️ PASO 2 & 3: Pesar Olla Cocida y Servir en Balanza")
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

    # Mini-Dashboard Tira Semanal de 7 Días (Visión general instantánea)
    st.markdown("#### 🧭 Ritmo Metabólico Semanal (7 Días)")
    tira_cols = st.columns(7)
    for idx_td, d_nom in enumerate(DIAS_SEMANA):
        com_d = st.session_state.semana_alimentos.get(d_nom, [])
        act_d = st.session_state.semana_caminatas.get(d_nom, {})
        cons_el_d = sum(c.get("el_kcal", 0.0) for c in com_d)
        quem_el_d = sum(float(a.get("kcal", 0.0)) for a in act_d.get("actividades_el", []))
        gasto_d_el = sed_el + quem_el_d
        net_el_d = gasto_d_el - cons_el_d  # positivo = deficit

        cons_ella_d = sum(c.get("ella_kcal", 0.0) for c in com_d)
        quem_ella_d = sum(float(a.get("kcal", 0.0)) for a in act_d.get("actividades_ella", []))
        gasto_d_ella = sed_ella + quem_ella_d
        net_ella_d = gasto_d_ella - cons_ella_d

        with tira_cols[idx_td]:
            if cons_el_d == 0 and quem_el_d == 0:
                bg_chip = "rgba(100, 116, 139, 0.15)"
                border_chip = "rgba(100, 116, 139, 0.3)"
                txt_el = "<span style='color:#94a3b8;'>⚪ 0 kcal</span>"
                txt_ella = "<span style='color:#94a3b8;'>⚪ 0 kcal</span>"
            else:
                if net_el_d >= 50:
                    txt_el = f"<span style='color:#10b981; font-weight:700;'>📉 -{net_el_d:.0f}</span>"
                elif net_el_d <= -50:
                    txt_el = f"<span style='color:#60a5fa; font-weight:700;'>📈 +{abs(net_el_d):.0f}</span>"
                else:
                    txt_el = "<span style='color:#94a3b8;'>⚖️ 0</span>"

                if net_ella_d >= 50:
                    txt_ella = f"<span style='color:#10b981; font-weight:700;'>📉 -{net_ella_d:.0f}</span>"
                elif net_ella_d <= -50:
                    txt_ella = f"<span style='color:#f472b6; font-weight:700;'>📈 +{abs(net_ella_d):.0f}</span>"
                else:
                    txt_ella = "<span style='color:#94a3b8;'>⚖️ 0</span>"

                bg_chip = "rgba(30, 41, 59, 0.6)"
                border_chip = "rgba(255, 255, 255, 0.12)"

            st.markdown(f"""
            <div style="background: {bg_chip}; border: 1px solid {border_chip}; border-radius: 8px; padding: 6px 2px; text-align: center; margin-bottom: 12px;">
                <div style="font-weight: 700; font-size: 0.82rem; color: #f8fafc; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 2px; margin-bottom: 4px;">{d_nom[:3]}</div>
                <div style="font-size: 0.73rem;">👨 {txt_el}</div>
                <div style="font-size: 0.73rem;">👩 {txt_ella}</div>
            </div>
            """, unsafe_allow_html=True)

    # Visualización Día por Día
    st.markdown("#### 📋 Registro Diario (Comidas & Actividades)")
    tabs_dias = st.tabs(DIAS_SEMANA)
    for i_dia, dia_nom in enumerate(DIAS_SEMANA):
        with tabs_dias[i_dia]:
            cam_data_dia = st.session_state.semana_caminatas.get(dia_nom, {})
            acts_el = cam_data_dia.get("actividades_el", [])
            acts_ella = cam_data_dia.get("actividades_ella", [])

            quema_dia_el = sum(float(a.get("kcal", 0.0)) for a in acts_el)
            minutos_dia_el = sum(int(a.get("minutos", 0)) for a in acts_el)
            gasto_real_dia_el = sed_el + quema_dia_el

            quema_dia_ella = sum(float(a.get("kcal", 0.0)) for a in acts_ella)
            minutos_dia_ella = sum(int(a.get("minutos", 0)) for a in acts_ella)
            gasto_real_dia_ella = sed_ella + quema_dia_ella

            comidas_dia = st.session_state.semana_alimentos.get(dia_nom, [])
            tot_dia_el_k = sum(c.get("el_kcal", 0.0) for c in comidas_dia)
            tot_dia_ella_k = sum(c.get("ella_kcal", 0.0) for c in comidas_dia)

            bal_hoy_el = gasto_real_dia_el - tot_dia_el_k
            bal_hoy_ella = gasto_real_dia_ella - tot_dia_ella_k

            # Header del Día con Balance en Vivo
            if bal_hoy_el >= 50:
                badge_bal_el = f"<span style='color:#10b981; font-weight:700;'>📉 Déficit: -{bal_hoy_el:.0f} kcal</span>"
            elif bal_hoy_el <= -50:
                badge_bal_el = f"<span style='color:#60a5fa; font-weight:700;'>📈 Superávit: +{abs(bal_hoy_el):.0f} kcal</span>"
            else:
                badge_bal_el = "<span style='color:#94a3b8; font-weight:700;'>⚖️ Equilibrio</span>"

            if bal_hoy_ella >= 50:
                badge_bal_ella = f"<span style='color:#10b981; font-weight:700;'>📉 Déficit: -{bal_hoy_ella:.0f} kcal</span>"
            elif bal_hoy_ella <= -50:
                badge_bal_ella = f"<span style='color:#ec4899; font-weight:700;'>📈 Superávit: +{abs(bal_hoy_ella):.0f} kcal</span>"
            else:
                badge_bal_ella = "<span style='color:#94a3b8; font-weight:700;'>⚖️ Equilibrio</span>"

            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.55); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px 16px; margin-bottom: 14px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <strong style="color: #60a5fa; font-size: 0.95rem;">👨 Él:</strong> 
                        <span style="font-size: 0.88rem; color: #cbd5e1;">Consumo: <b>{tot_dia_el_k:.0f} kcal</b> | Gasto: <b>{gasto_real_dia_el:.0f} kcal</b></span> 
                        &nbsp;→&nbsp; {badge_bal_el}
                    </div>
                    <div>
                        <strong style="color: #f472b6; font-size: 0.95rem;">👩 Ella:</strong> 
                        <span style="font-size: 0.88rem; color: #cbd5e1;">Consumo: <b>{tot_dia_ella_k:.0f} kcal</b> | Gasto: <b>{gasto_real_dia_ella:.0f} kcal</b></span> 
                        &nbsp;→&nbsp; {badge_bal_ella}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Master 2-Column Layout
            col_dia_izq, col_dia_der = st.columns([1.1, 0.9])

            # ==============================================================
            # COLUMNA IZQUIERDA: COMIDAS Y NUTRICIÓN
            # ==============================================================
            with col_dia_izq:
                st.markdown(f"##### 🍽️ Comidas de {dia_nom} ({len(comidas_dia)})")

                with st.expander(f"➕ Cargar Alimento / Snack a {dia_nom}", expanded=(len(comidas_dia) == 0)):
                    cd_a1, cd_a2 = st.columns([2.5, 1.2])
                    with cd_a1:
                        ali_rap_dia = st.selectbox("Alimento", sorted(df_alimentos["nombre"].unique()), key=f"ali_rap_{dia_nom}")
                    with cd_a2:
                        gr_rap_dia = st.number_input("Gramos", min_value=1.0, max_value=2500.0, value=100.0, step=10.0, key=f"gr_rap_{dia_nom}")

                    cd_a3, cd_a4 = st.columns([2, 1.2])
                    with cd_a3:
                        qui_rap_dia = st.selectbox("Asignar a:", ["Solo Él", "Solo Ella", "Ambos (Olla)"], key=f"qui_rap_{dia_nom}")
                    with cd_a4:
                        st.write("")
                        st.write("")
                        btn_c_rap = st.button("➕ Cargar", key=f"btn_add_rap_{dia_nom}", use_container_width=True)

                    if btn_c_rap:
                        row_rd = df_alimentos[df_alimentos["nombre"] == ali_rap_dia].iloc[0]
                        f_rd = gr_rap_dia / 100.0
                        k_rd = row_rd["kcal"] * f_rd
                        p_rd = row_rd["p"] * f_rd
                        c_rd = row_rd["c"] * f_rd
                        g_rd = row_rd["g"] * f_rd
                        if qui_rap_dia == "Solo Él":
                            el_k, el_p, el_c, el_g = k_rd, p_rd, c_rd, g_rd
                            ella_k, ella_p, ella_c, ella_g = 0.0, 0.0, 0.0, 0.0
                        elif qui_rap_dia == "Solo Ella":
                            el_k, el_p, el_c, el_g = 0.0, 0.0, 0.0, 0.0
                            ella_k, ella_p, ella_c, ella_g = k_rd, p_rd, c_rd, g_rd
                        else:
                            el_k, el_p, el_c, el_g = k_rd * prop_el, p_rd * prop_el, c_rd * prop_el, g_rd * prop_el
                            ella_k, ella_p, ella_c, ella_g = k_rd * prop_ella, p_rd * prop_ella, c_rd * prop_ella, g_rd * prop_ella
                        st.session_state.semana_alimentos[dia_nom].append({
                            "id": len(st.session_state.semana_alimentos[dia_nom]) + 1,
                            "descripcion": f"{gr_rap_dia:.0f}g {ali_rap_dia}",
                            "el_kcal": round(el_k, 1), "el_p": round(el_p, 1), "el_c": round(el_c, 1), "el_g": round(el_g, 1),
                            "ella_kcal": round(ella_k, 1), "ella_p": round(ella_p, 1), "ella_c": round(ella_c, 1), "ella_g": round(ella_g, 1)
                        })
                        guardar_semana_alimentos(st.session_state.semana_alimentos)
                        st.rerun()

                # Lista de comidas cargadas hoy
                if comidas_dia:
                    for idx_c, c_item in enumerate(comidas_dia):
                        row_c1, row_c2, row_c3 = st.columns([4.2, 4.0, 0.8])
                        with row_c1:
                            st.markdown(f"🍽️ **{c_item.get('descripcion', 'Comida')}**")
                        with row_c2:
                            txt_el_p = f"<span style='color:#60a5fa; font-size:0.82rem;'>👨 <b>{c_item.get('el_kcal', 0):.0f}k</b></span>" if c_item.get('el_kcal', 0) > 0 else ""
                            txt_ella_p = f"<span style='color:#f472b6; font-size:0.82rem;'>👩 <b>{c_item.get('ella_kcal', 0):.0f}k</b></span>" if c_item.get('ella_kcal', 0) > 0 else ""
                            sep = " | " if (txt_el_p and txt_ella_p) else ""
                            st.markdown(f"{txt_el_p}{sep}{txt_ella_p}", unsafe_allow_html=True)
                        with row_c3:
                            if st.button("❌", key=f"del_c_{dia_nom}_{idx_c}", help="Eliminar comida"):
                                st.session_state.semana_alimentos[dia_nom].pop(idx_c)
                                guardar_semana_alimentos(st.session_state.semana_alimentos)
                                st.rerun()

                    if st.button(f"🗑️ Vaciar comidas de {dia_nom}", key=f"btn_vaciar_{dia_nom}"):
                        st.session_state.semana_alimentos[dia_nom] = []
                        guardar_semana_alimentos(st.session_state.semana_alimentos)
                        st.rerun()
                else:
                    st.caption("No hay comidas registradas para este día aún.")

                # ==============================================================
                # MONITOR DE MACRONUTRIENTES DIARIOS (P, C, G): DÉFICIT / EXCESO
                # ==============================================================
                tot_dia_el_p = sum(c.get("el_p", 0.0) for c in comidas_dia)
                tot_dia_el_c = sum(c.get("el_c", 0.0) for c in comidas_dia)
                tot_dia_el_g = sum(c.get("el_g", 0.0) for c in comidas_dia)

                tot_dia_ella_p = sum(c.get("ella_p", 0.0) for c in comidas_dia)
                tot_dia_ella_c = sum(c.get("ella_c", 0.0) for c in comidas_dia)
                tot_dia_ella_g = sum(c.get("ella_g", 0.0) for c in comidas_dia)

                st.markdown("---")
                st.markdown(f"###### 🎯 Cumplimiento de Macros ({dia_nom})")
                st.caption("Compara lo consumido hoy contra la meta diaria asignada. Indica si faltan gramos (déficit) o si se superó la meta (exceso).")

                tab_m_el, tab_m_ella = st.tabs(["👨 Macros Él", "👩 Macros Ella"])

                def render_card_macro(nom_macro, val_consumido, val_meta, color_val, class_badge):
                    diff_m = val_consumido - val_meta
                    pct_m = min(1.0, max(0.0, val_consumido / val_meta)) if val_meta > 0 else 0.0
                    if diff_m < -4.0:
                        badge_txt = f"<span style='background:rgba(59,130,246,0.18); color:#60a5fa; border:1px solid rgba(59,130,246,0.35); padding:2px 8px; border-radius:6px; font-size:0.78rem; font-weight:700;'>⏳ Faltan {abs(diff_m):.1f}g (Déficit)</span>"
                    elif diff_m > 4.0:
                        badge_txt = f"<span style='background:rgba(239,68,68,0.18); color:#f87171; border:1px solid rgba(239,68,68,0.35); padding:2px 8px; border-radius:6px; font-size:0.78rem; font-weight:700;'>⚠️ Pasado +{diff_m:.1f}g (Exceso)</span>"
                    else:
                        badge_txt = "<span style='background:rgba(16,185,129,0.18); color:#34d399; border:1px solid rgba(16,185,129,0.35); padding:2px 8px; border-radius:6px; font-size:0.78rem; font-weight:700;'>✅ En la meta exacto</span>"

                    st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 8px 12px; margin-bottom: 6px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span class="{class_badge}"><b>{nom_macro}</b></span>
                            <div>{badge_txt}</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: #cbd5e1;">
                            <span>Consumido: <b style="color:{color_val};">{val_consumido:.1f}g</b></span>
                            <span>Meta: <b>{val_meta:.0f}g</b> ({pct_m*100:.0f}%)</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(pct_m)

                with tab_m_el:
                    render_card_macro("Proteína", tot_dia_el_p, req_p_el, "#60a5fa", "badge-p")
                    render_card_macro("Carbohidratos", tot_dia_el_c, req_c_el, "#34d399", "badge-c")
                    render_card_macro("Grasas", tot_dia_el_g, req_g_el, "#fbbf24", "badge-g")

                with tab_m_ella:
                    render_card_macro("Proteína", tot_dia_ella_p, req_p_ella, "#f472b6", "badge-p")
                    render_card_macro("Carbohidratos", tot_dia_ella_c, req_c_ella, "#34d399", "badge-c")
                    render_card_macro("Grasas", tot_dia_ella_g, req_g_ella, "#fbbf24", "badge-g")

            # ==============================================================
            # COLUMNA DERECHA: ACTIVIDADES & RELOJ INTELIGENTE
            # ==============================================================
            with col_dia_der:
                st.markdown(f"##### 🏃 Ejercicio & Reloj ({len(acts_el) + len(acts_ella)} activ.)")

                # Botonera de Chips de Acceso Rápido (1 Clic)
                with st.container():
                    st.markdown("<span style='font-size:0.75rem; color:#38bdf8; font-weight:700;'>⚡ REGISTRO RÁPIDO (1 CLIC):</span>", unsafe_allow_html=True)
                    chip_dest = st.selectbox("Para:", ["👨 Solo Él", "👩 Solo Ella", "👫 Ambos (Juntos)"], key=f"chip_dest_{dia_nom}", label_visibility="collapsed")
                    ch1, ch2, ch3 = st.columns(3)

                    def registrar_quick_act(nom, ico, min_val, mets_v):
                        ts = datetime.now().strftime("%H%M%S%f")
                        if chip_dest in ["👨 Solo Él", "👫 Ambos (Juntos)"]:
                            k_el = round((mets_v * peso_el * min_val) / 60.0, 1)
                            st.session_state.semana_caminatas[dia_nom]["actividades_el"].append({
                                "id": f"el_{ts}", "nombre": nom, "icono": ico, "minutos": min_val, "kcal": k_el, "modo": "METs"
                            })
                        if chip_dest in ["👩 Solo Ella", "👫 Ambos (Juntos)"]:
                            k_ella = round((mets_v * peso_ella * min_val) / 60.0, 1)
                            st.session_state.semana_caminatas[dia_nom]["actividades_ella"].append({
                                "id": f"ella_{ts}", "nombre": nom, "icono": ico, "minutos": min_val, "kcal": k_ella, "modo": "METs"
                            })
                        guardar_caminatas_semana(st.session_state.semana_caminatas)
                        st.rerun()

                    with ch1:
                        if st.button("🚶 30m Paseo", key=f"chip_p30_{dia_nom}", help="Caminata constante 30 min (4.0 METs)", use_container_width=True):
                            registrar_quick_act("Caminata Paseo", "🚶", 30, 4.0)
                    with ch2:
                        if st.button("🚶‍♂️ 1h Caminata", key=f"chip_c60_{dia_nom}", help="Caminata rápida 60 min (4.8 METs)", use_container_width=True):
                            registrar_quick_act("Caminata Rápida", "🚶‍♂️", 60, 4.8)
                    with ch3:
                        if st.button("🏋️ 1h Gimnasio", key=f"chip_g60_{dia_nom}", help="Musculación / Pesas 60 min (4.5 METs)", use_container_width=True):
                            registrar_quick_act("Musculación / Pesas", "🏋️", 60, 4.5)

                # Formulario Detallado o Reloj Inteligente
                with st.expander(f"➕ Registro detallado o calorías de Reloj", expanded=False):
                    cf1, cf2 = st.columns([1.5, 2.0])
                    with cf1:
                        dest_act = st.selectbox("¿Quién?", ["👨 Solo Él", "👩 Solo Ella", "👫 Ambos (Juntos)"], key=f"dest_act_{dia_nom}")
                    with cf2:
                        modo_calc = st.radio("Método:", ["⏱️ Minutos (METs)", "⌚ Reloj (kcal)"], key=f"modo_calc_{dia_nom}", horizontal=True)

                    tipo_act_sel = st.selectbox("Actividad", list(CATALOGO_ACTIVIDADES.keys()), key=f"tipo_act_{dia_nom}")
                    act_info = CATALOGO_ACTIVIDADES[tipo_act_sel]
                    nombre_final = act_info["nombre"]
                    icono_final = act_info["icono"]
                    mets_act = act_info["mets"]

                    if "Otra Actividad" in nombre_final:
                        nombre_final = st.text_input("Nombre de la Actividad", value="Entrenamiento", key=f"nom_custom_act_{dia_nom}")
                        mets_act = st.number_input("Intensidad (METs)", min_value=1.0, max_value=16.0, value=4.5, step=0.5, key=f"mets_custom_{dia_nom}")

                    if "Minutos" in modo_calc:
                        dur_min = st.number_input("Duración (minutos)", min_value=5, max_value=360, value=45, step=5, key=f"min_act_{dia_nom}")
                        quema_prev_el = (mets_act * peso_el * dur_min) / 60.0
                        quema_prev_ella = (mets_act * peso_ella * dur_min) / 60.0
                        prev_txt = []
                        if dest_act in ["👨 Solo Él", "👫 Ambos (Juntos)"]:
                            prev_txt.append(f"👨 Él: +{quema_prev_el:.0f} kcal")
                        if dest_act in ["👩 Solo Ella", "👫 Ambos (Juntos)"]:
                            prev_txt.append(f"👩 Ella: +{quema_prev_ella:.0f} kcal")
                        st.caption(f"🔥 Quema: {' | '.join(prev_txt)}")
                    else:
                        dur_min = st.number_input("Duración aprox. (min)", min_value=0, max_value=360, value=45, step=5, key=f"min_reloj_{dia_nom}")
                        if dest_act == "👨 Solo Él":
                            kcal_in_el = st.number_input("Calorías Reloj (Él)", min_value=1.0, max_value=4000.0, value=300.0, step=10.0, key=f"kcal_in_el_{dia_nom}")
                        elif dest_act == "👩 Solo Ella":
                            kcal_in_ella = st.number_input("Calorías Reloj (Ella)", min_value=1.0, max_value=3000.0, value=200.0, step=10.0, key=f"kcal_in_ella_{dia_nom}")
                        else:
                            cr1, cr2 = st.columns(2)
                            with cr1:
                                kcal_in_el = st.number_input("Kcal Él", min_value=1.0, max_value=4000.0, value=300.0, step=10.0, key=f"kcal_in_el_ambos_{dia_nom}")
                            with cr2:
                                kcal_in_ella = st.number_input("Kcal Ella", min_value=1.0, max_value=3000.0, value=200.0, step=10.0, key=f"kcal_in_ella_ambos_{dia_nom}")

                    if st.button(f"➕ Guardar Actividad", key=f"btn_add_act_{dia_nom}", use_container_width=True):
                        ts_id = datetime.now().strftime("%H%M%S%f")
                        if dest_act in ["👨 Solo Él", "👫 Ambos (Juntos)"]:
                            k_calc_el = (mets_act * peso_el * dur_min / 60.0) if "Minutos" in modo_calc else float(kcal_in_el)
                            st.session_state.semana_caminatas[dia_nom]["actividades_el"].append({
                                "id": f"el_{ts_id}",
                                "nombre": nombre_final,
                                "icono": icono_final,
                                "minutos": int(dur_min),
                                "kcal": round(k_calc_el, 1),
                                "modo": "METs" if "Minutos" in modo_calc else "Reloj"
                            })
                        if dest_act in ["👩 Solo Ella", "👫 Ambos (Juntos)"]:
                            k_calc_ella = (mets_act * peso_ella * dur_min / 60.0) if "Minutos" in modo_calc else float(kcal_in_ella)
                            st.session_state.semana_caminatas[dia_nom]["actividades_ella"].append({
                                "id": f"ella_{ts_id}",
                                "nombre": nombre_final,
                                "icono": icono_final,
                                "minutos": int(dur_min),
                                "kcal": round(k_calc_ella, 1),
                                "modo": "METs" if "Minutos" in modo_calc else "Reloj"
                            })
                        guardar_caminatas_semana(st.session_state.semana_caminatas)
                        st.success("¡Actividad registrada correctamente!")
                        st.rerun()

                # Lista de Actividades registradas hoy
                st.markdown("<strong style='color: #60a5fa; font-size: 0.88rem;'>👨 Actividades de Él:</strong>", unsafe_allow_html=True)
                if acts_el:
                    for idx_a, act in enumerate(acts_el):
                        ca1, ca2, ca3 = st.columns([4.0, 4.0, 0.8])
                        with ca1:
                            st.markdown(f"{act.get('icono', '⚡')} <span style='font-size:0.85rem;'>{act.get('nombre', 'Actividad')}</span>", unsafe_allow_html=True)
                        with ca2:
                            st.markdown(f"<span style='color:#38bdf8; font-size:0.82rem;'>⏱️{act.get('minutos', 0)}m | 🔥<b>{act.get('kcal', 0):.0f}k</b></span>", unsafe_allow_html=True)
                        with ca3:
                            if st.button("❌", key=f"del_act_el_{dia_nom}_{idx_a}", help="Eliminar"):
                                st.session_state.semana_caminatas[dia_nom]["actividades_el"].pop(idx_a)
                                guardar_caminatas_semana(st.session_state.semana_caminatas)
                                st.rerun()
                else:
                    st.caption("Sin actividades registradas (Día de descanso)")

                st.markdown("<strong style='color: #f472b6; font-size: 0.88rem;'>👩 Actividades de Ella:</strong>", unsafe_allow_html=True)
                if acts_ella:
                    for idx_a, act in enumerate(acts_ella):
                        ca1, ca2, ca3 = st.columns([4.0, 4.0, 0.8])
                        with ca1:
                            st.markdown(f"{act.get('icono', '⚡')} <span style='font-size:0.85rem;'>{act.get('nombre', 'Actividad')}</span>", unsafe_allow_html=True)
                        with ca2:
                            st.markdown(f"<span style='color:#f472b6; font-size:0.82rem;'>⏱️{act.get('minutos', 0)}m | 🔥<b>{act.get('kcal', 0):.0f}k</b></span>", unsafe_allow_html=True)
                        with ca3:
                            if st.button("❌", key=f"del_act_ella_{dia_nom}_{idx_a}", help="Eliminar"):
                                st.session_state.semana_caminatas[dia_nom]["actividades_ella"].pop(idx_a)
                                guardar_caminatas_semana(st.session_state.semana_caminatas)
                                st.rerun()
                else:
                    st.caption("Sin actividades registradas (Día de descanso)")

    # Totales y Balance Semanal Acumulado
    st.markdown("---")
    st.markdown("#### 📊 Balance Metabólico Semanal Acumulado (7 Días)")
    st.caption("Cálculo exacto: Suma el gasto real de cada día (según horas de caminata o calorías de reloj inteligente) frente al consumo real acumulado.")

    # Totales de ejercicio y gasto en la semana
    quema_dias_el = []
    quema_dias_ella = []
    minutos_dias_el = []
    minutos_dias_ella = []

    for d in DIAS_SEMANA:
        c_dat = st.session_state.semana_caminatas.get(d, {})
        acts_el_d = c_dat.get("actividades_el", [])
        acts_ella_d = c_dat.get("actividades_ella", [])

        q_el = sum(float(a.get("kcal", 0.0)) for a in acts_el_d)
        m_el = sum(int(a.get("minutos", 0)) for a in acts_el_d)
        quema_dias_el.append(q_el)
        minutos_dias_el.append(m_el)

        q_ella = sum(float(a.get("kcal", 0.0)) for a in acts_ella_d)
        m_ella = sum(int(a.get("minutos", 0)) for a in acts_ella_d)
        quema_dias_ella.append(q_ella)
        minutos_dias_ella.append(m_ella)

    total_quema_sem_el = sum(quema_dias_el)
    total_quema_sem_ella = sum(quema_dias_ella)
    total_h_cam_el = sum(minutos_dias_el) / 60.0
    total_h_cam_ella = sum(minutos_dias_ella) / 60.0

    gastos_reales_el = [sed_el + q for q in quema_dias_el]
    gastos_reales_ella = [sed_ella + q for q in quema_dias_ella]

    gasto_sem_real_el = sum(gastos_reales_el)
    gasto_sem_real_ella = sum(gastos_reales_ella)

    consumo_dias_el = [sum(c["el_kcal"] for c in st.session_state.semana_alimentos.get(d, [])) for d in DIAS_SEMANA]
    consumo_dias_ella = [sum(c["ella_kcal"] for c in st.session_state.semana_alimentos.get(d, [])) for d in DIAS_SEMANA]

    total_sem_el_k = sum(consumo_dias_el)
    total_sem_ella_k = sum(consumo_dias_ella)

    neto_sem_el = gasto_sem_real_el - total_sem_el_k  # positivo = deficit, negativo = superavit
    neto_sem_ella = gasto_sem_real_ella - total_sem_ella_k

    kg_sem_real_el = abs(neto_sem_el) / 7700.0
    kg_sem_real_ella = abs(neto_sem_ella) / 7700.0

    col_b_el, col_b_ella = st.columns(2)
    with col_b_el:
        st.markdown("""
        <div class="profile-card-he">
            <strong style="color: #60a5fa; font-size: 1.15rem;">👨 Balance Semanal Real de Él</strong>
        </div>
        """, unsafe_allow_html=True)
        cb_1, cb_2, cb_3 = st.columns(3)
        with cb_1:
            st.metric("Consumo 7 Días", f"{total_sem_el_k:.0f} kcal", f"Prom: {(total_sem_el_k/7):.0f} kcal/día")
        with cb_2:
            st.metric("Gasto Real 7 Días", f"{gasto_sem_real_el:.0f} kcal", f"🔥 +{total_quema_sem_el:.0f} kcal ({total_h_cam_el:.1f}h)")
        with cb_3:
            if neto_sem_el >= 50:
                st.metric("Déficit Semanal Real", f"-{neto_sem_el:.0f} kcal", f"-{kg_sem_real_el:.2f} kg grasa")
            elif neto_sem_el <= -50:
                st.metric("Superávit Semanal Real", f"+{abs(neto_sem_el):.0f} kcal", f"+{kg_sem_real_el:.2f} kg ganados", delta_color="inverse")
            else:
                st.metric("Balance Semanal Real", "0 kcal", "Mantenimiento")

    with col_b_ella:
        st.markdown("""
        <div class="profile-card-she">
            <strong style="color: #f472b6; font-size: 1.15rem;">👩 Balance Semanal Real de Ella</strong>
        </div>
        """, unsafe_allow_html=True)
        cb_4, cb_5, cb_6 = st.columns(3)
        with cb_4:
            st.metric("Consumo 7 Días", f"{total_sem_ella_k:.0f} kcal", f"Prom: {(total_sem_ella_k/7):.0f} kcal/día")
        with cb_5:
            st.metric("Gasto Real 7 Días", f"{gasto_sem_real_ella:.0f} kcal", f"🔥 +{total_quema_sem_ella:.0f} kcal ({total_h_cam_ella:.1f}h)")
        with cb_6:
            if neto_sem_ella >= 50:
                st.metric("Déficit Semanal Real", f"-{neto_sem_ella:.0f} kcal", f"-{kg_sem_real_ella:.2f} kg grasa")
            elif neto_sem_ella <= -50:
                st.metric("Superávit Semanal Real", f"+{abs(neto_sem_ella):.0f} kcal", f"+{kg_sem_real_ella:.2f} kg ganados", delta_color="inverse")
            else:
                st.metric("Balance Semanal Real", "0 kcal", "Mantenimiento")

    # Gráfico Comparativo de Consumo vs Gasto Real Diario
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
        name="Gasto Real Día Él",
        x=DIAS_SEMANA,
        y=gastos_reales_el,
        mode="lines+markers",
        line=dict(color="#60a5fa", width=2.5),
        marker=dict(size=7, symbol="diamond")
    ))
    fig_sem.add_trace(go.Scatter(
        name="Gasto Real Día Ella",
        x=DIAS_SEMANA,
        y=gastos_reales_ella,
        mode="lines+markers",
        line=dict(color="#f472b6", width=2.5),
        marker=dict(size=7, symbol="circle")
    ))
    fig_sem.add_trace(go.Scatter(
        name="Meta Diaria Él",
        x=DIAS_SEMANA,
        y=[meta_kcal_el] * 7,
        mode="lines",
        line=dict(color="#93c5fd", width=1.5, dash="dash")
    ))
    fig_sem.add_trace(go.Scatter(
        name="Meta Diaria Ella",
        x=DIAS_SEMANA,
        y=[meta_kcal_ella] * 7,
        mode="lines",
        line=dict(color="#fbcfe8", width=1.5, dash="dash")
    ))
    fig_sem.update_layout(
        barmode='group',
        template="plotly_dark",
        title="Consumo Diario vs. Gasto Energético Real de Cada Día (según actividad o reloj)",
        xaxis=dict(title="Día de la Semana"),
        yaxis=dict(title="Calorías (kcal)"),
        height=390,
        margin=dict(l=40, r=20, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_sem, use_container_width=True)

    col_btn_sem1, col_btn_sem2 = st.columns([2, 3])
    with col_btn_sem1:
        if st.button("🗑️ Reiniciar Semana Completa (Comidas y Actividad)", key="btn_reset_semana", use_container_width=True):
            st.session_state.semana_alimentos = {d: [] for d in DIAS_SEMANA}
            st.session_state.semana_caminatas = {
                d: {
                    "actividades_el": [],
                    "actividades_ella": [],
                    "horas_el": 0.0,
                    "kcal_el": 0.0,
                    "horas_ella": 0.0,
                    "kcal_ella": 0.0
                } for d in DIAS_SEMANA
            }
            guardar_semana_alimentos(st.session_state.semana_alimentos)
            guardar_caminatas_semana(st.session_state.semana_caminatas)
            st.success("¡Semana reiniciada exitosamente!")
            st.rerun()
with tab2:
    st.markdown("### 🔥 Auditoría Metabólica y Gasto Energético Comparado")
    st.markdown("Cálculos científicos basados en Mifflin-St Jeor y equivalentes metabólicos (METs) precisos.")

    # ==============================================================
    # SELECTOR DE MODO DE AUDITORÍA & SIMULADOR "¿QUÉ PASARÍA SI...?"
    # ==============================================================
    col_mod_info, col_mod_ctrl = st.columns([1.2, 1.8])
    with col_mod_info:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 12px 16px;">
            <strong style="color: #38bdf8; font-size: 0.95rem;">🧭 Modo de Auditoría & Proyección:</strong>
            <p style="color: #94a3b8; font-size: 0.8rem; margin: 4px 0 0 0;">
                Elige si proyectar según tu <b>actividad real registrada</b> en la semana o si deseas usar el <b>simulador teórico</b> interactivo con slider.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_mod_ctrl:
        modo_auditoria = st.radio(
            "Modelo de Cálculo:",
            [
                "🏃‍♂️ Usar Actividad Real Registrada en la Semana",
                "🔮 Simulador Teórico ('¿Qué pasaría si...?')"
            ],
            index=0 if st.session_state.get("modo_aud_state", "Real") == "Real" else 1,
            key="sel_modo_auditoria",
            horizontal=False
        )

    # Cálculo de horas y METs según el modo elegido
    if "Simulador" in modo_auditoria:
        st.session_state.modo_aud_state = "Simulador"
        with st.container():
            st.markdown("""
            <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 10px; padding: 12px 16px; margin-bottom: 14px;">
                <strong style="color: #60a5fa; font-size: 0.9rem;">🔮 Simulador Teórico Activo</strong>
                <span style="color: #cbd5e1; font-size: 0.8rem; display: block; margin-top: 2px;">
                    Mueve el slider para explorar: "¿Cuántos kilos bajo en 6 meses si camino X horas por semana?":
                </span>
            </div>
            """, unsafe_allow_html=True)
            col_sim_h, col_sim_m = st.columns([1.5, 1.5])
            with col_sim_h:
                sim_h = st.slider(
                    "Horas de caminata semanales a simular:",
                    min_value=0.0, max_value=14.0,
                    value=float(st.session_state.get("sim_horas_sem", cfg_usuario.get("horas_sem", 3.0))),
                    step=0.5,
                    key="slider_sim_h_tab2"
                )
                st.session_state.sim_horas_sem = sim_h
            with col_sim_m:
                idx_m_sim = list(intensidad_mets_dict.keys()).index(opcion_mets) if opcion_mets in intensidad_mets_dict else 0
                sim_m_opc = st.selectbox(
                    "Intensidad de la caminata (METs):",
                    list(intensidad_mets_dict.keys()),
                    index=idx_m_sim,
                    key="sel_sim_mets_tab2"
                )
                st.session_state.sim_opcion_mets = sim_m_opc
                sim_mets_val = intensidad_mets_dict[sim_m_opc]

            h_aud_el = sim_h
            h_aud_ella = sim_h
            mets_aud = sim_mets_val
    else:
        st.session_state.modo_aud_state = "Real"
        # Usar la suma de horas reales registradas en la semana actual
        min_tot_el = sum(sum(int(a.get("minutos", 0)) for a in st.session_state.semana_caminatas.get(d, {}).get("actividades_el", [])) for d in DIAS_SEMANA)
        min_tot_ella = sum(sum(int(a.get("minutos", 0)) for a in st.session_state.semana_caminatas.get(d, {}).get("actividades_ella", [])) for d in DIAS_SEMANA)
        h_aud_el = round(min_tot_el / 60.0, 2)
        h_aud_ella = round(min_tot_ella / 60.0, 2)
        mets_aud = mets_val

        st.info(
            f"📊 **Actividad Real Detectada esta semana:** "
            f"👨 Él: **{h_aud_el:.1f} horas** registradas | 👩 Ella: **{h_aud_ella:.1f} horas** registradas. "
            f"(Para proyectar otros escenarios con slider manual, activa '🔮 Simulador Teórico' arriba)."
        )

    # Recálculo de Auditoría
    quema_1h_aud_el = mets_aud * peso_el * 1.0
    techo_cam_aud_el = sed_el + quema_1h_aud_el
    tdee_prom_aud_el = sed_el + ((quema_1h_aud_el * h_aud_el) / 7.0)
    deficit_aud_el = tdee_prom_aud_el - meta_kcal_el
    kg_sem_aud_el = abs(deficit_aud_el * 7.0) / 7700.0
    kg_mes_aud_el = abs(deficit_aud_el * 30.4) / 7700.0

    quema_1h_aud_ella = mets_aud * peso_ella * 1.0
    techo_cam_aud_ella = sed_ella + quema_1h_aud_ella
    tdee_prom_aud_ella = sed_ella + ((quema_1h_aud_ella * h_aud_ella) / 7.0)
    deficit_aud_ella = tdee_prom_aud_ella - meta_kcal_ella
    kg_sem_aud_ella = abs(deficit_aud_ella * 7.0) / 7700.0
    kg_mes_aud_ella = abs(deficit_aud_ella * 30.4) / 7700.0

    col_aud_he, col_aud_she = st.columns(2)
    
    with col_aud_he:
        st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 12px; padding: 18px; margin-bottom: 20px;">
            <h3 style="color: #60a5fa; margin-top: 0;">👨 Auditoría Metabólica: Él</h3>
            <p style="color: #94a3b8; font-size: 0.88rem;">Estatura: 180 cm | Peso: %.1f kg | Edad: %d años | Actividad: %.1fh/sem</p>
        </div>
        """ % (peso_el, edad_el, h_aud_el), unsafe_allow_html=True)
        
        m_c1, m_c2 = st.columns(2)
        with m_c1:
            st.metric("Piso Vital (TMB)", f"{tmb_el:.0f} kcal", help="Mifflin-St Jeor: Calorías mínimas para subsistir en reposo absoluto.")
            st.metric("Gasto Base (Día Descanso)", f"{sed_el:.0f} kcal", help="TMB * 1.2: Calorías que quemas un día que te quedas en casa y no sales a caminar.")
            st.metric("TDEE Promedio Semanal", f"{tdee_prom_aud_el:.0f} kcal", help=f"Gasto promedio diario considerando {h_aud_el:.1f}h de ejercicio semanal.")
        with m_c2:
            st.metric("Quema 1h Caminata", f"{quema_1h_aud_el:.0f} kcal", f"{mets_aud} METs x {peso_el:.0f}kg", help="Fórmula: METs * Peso * 1h")
            st.metric("Gasto Día con Caminata (1h)", f"{techo_cam_aud_el:.0f} kcal", help="Gasto Base + 1 hora de caminata.")
            st.metric(
                "Meta Calórica Asignada",
                f"{meta_kcal_el:.0f} kcal",
                help="🎯 Meta Calórica Asignada: Es tu presupuesto diario de comida. Está por encima de tu Piso Vital (TMB) para cuidar tu tiroides y masa muscular, y por debajo de tu Gasto (TDEE) para forzar la quema de grasa."
            )
        if deficit_aud_el >= 15:
            card_title_el = "📉 Déficit Calórico Neto Diario"
            card_val_el = f"-{deficit_aud_el:.0f} kcal / día"
            card_sub_el = f"Pérdida estimada de grasa (a 7700 kcal/kg):<br><b>📉 -{kg_sem_aud_el:.2f} kg / semana</b> &nbsp;|&nbsp; <b>📅 -{kg_mes_aud_el:.2f} kg / mes</b>"
            border_color_el = "#10b981"
            badge_note_el = f"💡 <b>¿Qué significa?</b> Comes <b>-{deficit_aud_el:.0f} kcal/día</b> por debajo de tu gasto ({tdee_prom_aud_el:.0f} kcal). Generas déficit para quemar reservas de grasa corporal."
        elif deficit_aud_el <= -15:
            card_title_el = "📈 Superávit Calórico Neto Diario"
            card_val_el = f"+{abs(deficit_aud_el):.0f} kcal / día"
            card_sub_el = f"Ganancia estimada de masa / peso:<br><b>📈 +{kg_sem_aud_el:.2f} kg / semana</b> &nbsp;|&nbsp; <b>📅 +{kg_mes_aud_el:.2f} kg / mes</b>"
            border_color_el = "#3b82f6"
            badge_note_el = f"💡 <b>¿Qué significa?</b> Comes <b>+{abs(deficit_aud_el):.0f} kcal/día</b> por encima de tu gasto ({tdee_prom_aud_el:.0f} kcal). Estás en superávit para ganar peso / masa muscular."
        else:
            card_title_el = "⚖️ Mantenimiento Calórico Diario"
            card_val_el = "Equilibrado (0 kcal)"
            card_sub_el = "Consumo equilibrado con tu gasto diario. Tu peso se mantendrá estable."
            border_color_el = "#94a3b8"
            badge_note_el = f"💡 <b>¿Qué significa?</b> Comes exactamente lo que gastas ({tdee_prom_aud_el:.0f} kcal). Tu peso se mantendrá sin variaciones."

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
            <p style="color: #94a3b8; font-size: 0.88rem;">Estatura: 150 cm | Peso: %.1f kg | Edad: %d años | Actividad: %.1fh/sem</p>
        </div>
        """ % (peso_ella, edad_ella, h_aud_ella), unsafe_allow_html=True)
        
        m_c3, m_c4 = st.columns(2)
        with m_c3:
            st.metric("Piso Vital (TMB)", f"{tmb_ella:.0f} kcal", help="Mifflin-St Jeor: Gasto mínimo para funciones vitales.")
            st.metric("Gasto Base (Día Descanso)", f"{sed_ella:.0f} kcal", help="TMB * 1.2: Calorías que quemas un día que te quedas en casa y no sales a caminar.")
            st.metric("TDEE Promedio Semanal", f"{tdee_prom_aud_ella:.0f} kcal", help=f"Gasto promedio diario considerando {h_aud_ella:.1f}h de ejercicio semanal.")
        with m_c4:
            st.metric("Quema 1h Caminata", f"{quema_1h_aud_ella:.0f} kcal", f"{mets_aud} METs x {peso_ella:.0f}kg", help="Fórmula: METs * Peso * 1h")
            st.metric("Gasto Día con Caminata (1h)", f"{techo_cam_aud_ella:.0f} kcal", help="Gasto Base + 1 hora de caminata.")
            st.metric(
                "Meta Calórica Asignada",
                f"{meta_kcal_ella:.0f} kcal",
                help="🎯 Meta Calórica Asignada: Es tu presupuesto diario de comida. Puede ser déficit para bajar de peso o superávit para ganar masa muscular."
            )

        if deficit_aud_ella >= 15:
            card_title_ella = "📉 Déficit Calórico Neto Diario"
            card_val_ella = f"-{deficit_aud_ella:.0f} kcal / día"
            card_sub_ella = f"Pérdida estimada de grasa (a 7700 kcal/kg):<br><b>📉 -{kg_sem_aud_ella:.2f} kg / semana</b> &nbsp;|&nbsp; <b>📅 -{kg_mes_aud_ella:.2f} kg / mes</b>"
            border_color_ella = "#10b981"
            badge_note_ella = f"💡 <b>¿Qué significa?</b> Comes <b>-{deficit_aud_ella:.0f} kcal/día</b> por debajo de tu gasto ({tdee_prom_aud_ella:.0f} kcal). Generas déficit para quemar reservas de grasa corporal."
        elif deficit_aud_ella <= -15:
            card_title_ella = "📈 Superávit Calórico Neto Diario"
            card_val_ella = f"+{abs(deficit_aud_ella):.0f} kcal / día"
            card_sub_ella = f"Ganancia estimada de masa / peso:<br><b>📈 +{kg_sem_aud_ella:.2f} kg / semana</b> &nbsp;|&nbsp; <b>📅 +{kg_mes_aud_ella:.2f} kg / mes</b>"
            border_color_ella = "#ec4899"
            badge_note_ella = f"💡 <b>¿Qué significa?</b> Comes <b>+{abs(deficit_aud_ella):.0f} kcal/día</b> por encima de tu gasto ({tdee_prom_aud_ella:.0f} kcal). Estás en superávit para ganar peso / masa muscular."
        else:
            card_title_ella = "⚖️ Mantenimiento Calórico Diario"
            card_val_ella = "Equilibrado (0 kcal)"
            card_sub_ella = "Consumo equilibrado con tu gasto diario. Tu peso se mantendrá estable."
            border_color_ella = "#94a3b8"
            badge_note_ella = f"💡 <b>¿Qué significa?</b> Comes exactamente lo que gastas ({tdee_prom_aud_ella:.0f} kcal). Tu peso se mantendrá sin variaciones."

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
    valores_el = [tmb_el, meta_kcal_el, sed_el, tdee_prom_aud_el, techo_cam_aud_el]
    valores_ella = [tmb_ella, meta_kcal_ella, sed_ella, tdee_prom_aud_ella, techo_cam_aud_ella]
    
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
        f"*Simulación adaptativa ({'Modo Simulador Teórico' if 'Simulador' in modo_auditoria else 'Modo Actividad Real'}):* "
        f"Modela semana a semana la evolución corporal recalculando TMB y gasto físico dinámicamente con el peso actualizado."
    )
    
    semanas = list(range(0, 25))
    proy_peso_el = [peso_el]
    proy_peso_ella = [peso_ella]
    proy_deficit_el = [deficit_aud_el]
    proy_deficit_ella = [deficit_aud_ella]

    curr_p_el = peso_el
    curr_p_ella = peso_ella

    for s in range(1, 25):
        # Recalcular Él
        tmb_s_el = (10.0 * curr_p_el) + (6.25 * altura_el) - (5.0 * edad_el) + 5.0
        sed_s_el = tmb_s_el * 1.2
        q1h_s_el = mets_aud * curr_p_el * 1.0
        tdee_s_el = sed_s_el + ((q1h_s_el * h_aud_el) / 7.0)
        def_s_el = tdee_s_el - meta_kcal_el
        var_sem_el = (def_s_el * 7.0) / 7700.0
        curr_p_el = max(45.0, min(220.0, curr_p_el - var_sem_el))
        proy_peso_el.append(round(curr_p_el, 2))
        proy_deficit_el.append(round(def_s_el, 0))

        # Recalcular Ella
        tmb_s_ella = (10.0 * curr_p_ella) + (6.25 * altura_ella) - (5.0 * edad_ella) - 161.0
        sed_s_ella = tmb_s_ella * 1.2
        q1h_s_ella = mets_aud * curr_p_ella * 1.0
        tdee_s_ella = sed_s_ella + ((q1h_s_ella * h_aud_ella) / 7.0)
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
        title=f"Trayectoria Proyectada de Peso a 24 Semanas ({'Simulador' if 'Simulador' in modo_auditoria else 'Actividad Real'})",
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

# ==============================================================================
# PESTAÑA 5: GUÍA METABÓLICA, GLOSARIO Y CHULETA NUTRICIONAL
# ==============================================================================
with tab4:
    st.markdown("### 📚 Guía Metabólica, Glosario & Manual de Bolsillo")
    st.markdown(
        "Tu manual de cabecera: el rol de cada macro, cómo calcular lo que comes (crudo vs. cocido), "
        "estrategias para comer juntos con metas distintas, la regla de la mano para comer afuera, trampas ocultas y fórmulas metabólicas."
    )

    tab_g1, tab_g2, tab_g3, tab_g4, tab_g5, tab_g6 = st.tabs([
        "🧬 1. Rol de Macros & Calculadora g/kg",
        "🧮 2. Cálculo de Macros & Crudo vs. Cocido",
        "👫 3. Comer en Pareja con Metas Distintas",
        "📋 4. La Chuleta & Regla de la Mano",
        "🚨 5. Trampas Ocultas, Agua & Sal",
        "🔬 6. Fórmulas Metabólicas & Dudas Frecuentes"
    ])

    # --------------------------------------------------------------------------
    # SUB-PESTAÑA 1: EL ROL REAL DE CADA MACRONUTRIENTE & CALCULADORA G/KG
    # --------------------------------------------------------------------------
    with tab_g1:
        st.markdown("#### 🧬 ¿Para qué sirve realmente cada macro y qué pasa si falta o sobra?")
        
        c_m_p, c_m_c, c_m_g = st.columns(3)
        
        with c_m_p:
            st.markdown("""
            <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 16px; height: 100%;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span class="badge-p"><b>🍗 PROTEÍNAS</b></span>
                    <span style="color: #60a5fa; font-weight: 700; font-size: 0.9rem;">4 kcal / gramo</span>
                </div>
                <h5 style="color: #60a5fa; margin-top: 0;">El Blindaje Muscular y la Saciedad</h5>
                <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
                    <b>¿Qué hace en tu cuerpo?</b><br>
                    Son los "ladrillos" de la masa muscular, órganos, hormonas péptidas, anticuerpos y enzimas.
                </p>
                <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
                    <b>🔥 Efecto Térmico (TEF): 20% a 30%</b><br>
                    Es el macronutriente más "costoso" de digerir. De cada 100 kcal de proteína que ingieres, tu cuerpo quema hasta 30 kcal solo en procesarla.
                </p>
                <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
                    <b>🛡️ En Déficit Calórico:</b><br>
                    Cuando comes menos calorías de las que gastas, tu cuerpo busca energía en cualquier parte. Si tu proteína es alta (1.6 a 2.0g/kg), <b>blindas el músculo y obligas a tu organismo a quemar grasa corporal</b>.
                </p>
                <p style="font-size: 0.82rem; color: #94a3b8; line-height: 1.5;">
                    <b style="color: #f87171;">⚠️ Si te falta:</b> Pierdes masa muscular, se ralentiza el metabolismo basal, sientes hambre constante y fatiga.<br>
                    <b style="color: #34d399;">✅ Si te pasas un poco:</b> Muy difícilmente se acumula como grasa debido a su alto costo metabólico; simplemente aporta saciedad extra.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with c_m_c:
            st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 16px; height: 100%;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span class="badge-c"><b>🍞 CARBOHIDRATOS</b></span>
                    <span style="color: #34d399; font-weight: 700; font-size: 0.9rem;">4 kcal / gramo</span>
                </div>
                <h5 style="color: #34d399; margin-top: 0;">El Combustible y la Salud Tiroidea</h5>
                <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
                    <b>¿Qué hace en tu cuerpo?</b><br>
                    Es la fuente primaria de glucosa para el cerebro, el sistema nervioso central y los depósitos de glucógeno en músculos e hígado.
                </p>
                <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
                    <b>🦋 Tiroides y Leptina (Evitar estancarse):</b><br>
                    Eliminar los carbos a cero durante mucho tiempo reduce la conversión de hormona tiroidea T4 a T3 activa y deprime la leptina (hormona de saciedad y ritmo metabólico). Mantener carbohidratos adecuados le dice al cerebro: <i>"No hay hambruna, puedes seguir quemando grasa"</i>.
                </p>
                <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
                    <b>💧 El Mito del Peso Rápido:</b><br>
                    Cada 1g de glucógeno almacenado retiene 3 a 4g de agua intracelular. Si comes más carbos hoy, mañana la balanza puede subir 500g-1kg: <b>es agua muscular, no grasa</b>.
                </p>
                <p style="font-size: 0.82rem; color: #94a3b8; line-height: 1.5;">
                    <b style="color: #f87171;">⚠️ Si te faltan:</b> Entrenamientos débiles, cansancio en las caminatas, mal humor, niebla mental y atracones nocturnos.<br>
                    <b style="color: #34d399;">✅ Si te pasas:</b> Se llenan los depósitos de glucógeno; solo se almacena en grasa si superas tus calorías totales del día.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with c_m_g:
            st.markdown("""
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px; padding: 16px; height: 100%;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span class="badge-g"><b>🥑 GRASAS</b></span>
                    <span style="color: #fbbf24; font-weight: 700; font-size: 0.9rem;">9 kcal / gramo</span>
                </div>
                <h5 style="color: #fbbf24; margin-top: 0;">El Eje Hormonal y Celular Vital</h5>
                <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
                    <b>¿Qué hace en tu cuerpo?</b><br>
                    Son indispensables para sintetizar hormonas esteroideas (testosterona en él; estrógenos y progesterona en ella), mantener las membranas de cada célula y absorber vitaminas liposolubles (A, D, E, K).
                </p>
                <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
                    <b>🚨 Piso Mínimo de Seguridad:</b><br>
                    <b>Nunca bajar de 0.6g a 0.7g por kg de peso.</b> Cortar las grasas para "ahorrar calorías" desregula el ciclo menstrual en mujeres, reduce la testosterona y libido en hombres y arruina la calidad del sueño.
                </p>
                <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
                    <b>⚖️ Alta Densidad Calórica:</b><br>
                    Tienen 9 kcal/g (más del doble que proteínas y carbos). Una cucharada sopera de aceite (14g) suma 126 kcal casi invisibles. Medirlas con balanza marca la diferencia.
                </p>
                <p style="font-size: 0.82rem; color: #94a3b8; line-height: 1.5;">
                    <b style="color: #f87171;">⚠️ Si te faltan:</b> Desbalances hormonales, piel seca, caída de cabello, dificultad para dormir y desánimo.<br>
                    <b style="color: #34d399;">✅ Si te pasas:</b> Es el macronutriente que el cuerpo almacena con mayor eficiencia energética si estás en superávit calórico.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 🎯 ¿Cuánto de cada cosa debería tener mi dieta diaria?")
        st.markdown(
            "En nutrición deportiva moderna, tu plato diario no se diseña al azar ni con porcentajes mágicos; "
            "se construye siguiendo un **orden estricto de 3 pasos por prioridad biológica** basado en **Gramos por Kilo (g/kg)**:"
        )

        st.markdown("""
        <div style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px; background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 10px; padding: 12px;">
                <div style="font-weight: 700; color: #60a5fa; font-size: 0.95rem;">PASO 1: 🍗 Fijar la Proteína</div>
                <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 4px;">
                    Es lo <b>no negociable</b>. Protege tu masa muscular del catabolismo en déficit y da saciedad.
                </div>
            </div>
            <div style="flex: 1; min-width: 200px; background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 10px; padding: 12px;">
                <div style="font-weight: 700; color: #fbbf24; font-size: 0.95rem;">PASO 2: 🥑 Fijar la Grasa Mínima</div>
                <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 4px;">
                    Es el <b>piso hormonal vital</b>. Nunca bajar de 0.6g/kg para cuidar tiroides, testosterona y estrógenos.
                </div>
            </div>
            <div style="flex: 1; min-width: 200px; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 10px; padding: 12px;">
                <div style="font-weight: 700; color: #34d399; font-size: 0.95rem;">PASO 3: 🍞 Carbohidratos (El Resto)</div>
                <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 4px;">
                    Son el <b>combustible flexible</b>. Todas las calorías que sobren de tu presupuesto van a los carbos para rendir.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_gkg1, col_gkg2 = st.columns([1.1, 0.9])
        with col_gkg1:
            st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.65); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 16px;">
                <h5 style="color: #38bdf8; margin-top: 0;">⚖️ ¿Qué significa exactamente "Gramos por Kilo" (g/kg)?</h5>
                <p style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.5;">
                    Significa: <i>"Por cada 1 kilogramo que pesa tu cuerpo, necesitas ingerir X cantidad de gramos de ese nutriente en el día"</i>.
                </p>
                <div style="background: rgba(15, 23, 42, 0.85); border-left: 3px solid #38bdf8; padding: 8px 12px; font-family: monospace; font-size: 0.9rem; color: #f8fafc; margin: 8px 0;">
                    Gramos Diarios = Kilos de Peso × Multiplicador (g/kg)
                </div>
                <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
                    <b>¿Por qué es superior a los porcentajes fijos?</b><br>
                    Si alguien recorta calorías a 1.200 kcal y come "30% proteína", comería solo 90g de proteína (¡insuficiente para un adulto!).
                    El método de <b>gramos por kilo asegura la masa biológica que tus órganos y músculos necesitan sí o sí</b>, sin importar cuánto bajes las calorías totales.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_gkg2:
            st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.65); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 16px;">
                <h5 style="color: #ec4899; margin-top: 0;">💡 El "Secreto" del Peso Magro / Peso Objetivo</h5>
                <p style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.5;">
                    <b>La grasa acumulada no demanda proteína</b>; quienes la necesitan son tus músculos, órganos, huesos y sangre.
                </p>
                <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
                    Por eso, cuando se busca perder peso, la ciencia multiplica sobre el <b>Peso Objetivo o Peso Magro</b> para no inflar números innecesariamente:
                </p>
                <ul style="font-size: 0.8rem; color: #cbd5e1; line-height: 1.5;">
                    <li>👨 <b>En tu caso (Él):</b> Peso actual ~119 kg. Peso objetivo magro ~94 kg.<br>
                    👉 <code>94 kg × 2.0 g/kg = 188g de Proteína</code> (¡La meta de la app!).</li>
                    <li>👩 <b>En el caso de Ella:</b> Peso actual ~69 kg. Peso objetivo magro ~58-60 kg.<br>
                    👉 <code>59 kg × 2.0 g/kg = 118g de Proteína</code> (¡Sus 115g-125g en la app!).</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # CALCULADORA INTERACTIVA DE GRAMOS POR KILO EN VIVO
        with st.expander("🧮 Calculadora Interactiva de Gramos por Kilo en Vivo (Prueba tus propios números)", expanded=True):
            st.markdown("Simula cualquier peso y multiplicadores para ver cómo se distribuyen tus calorías exactas:")
            
            col_calc_sel, col_calc_p = st.columns([1.5, 1.5])
            with col_calc_sel:
                per_calc_sel = st.radio("Cargar valores predeterminados de:", ["👨 Perfil Él (Base 94 kg magro)", "👩 Perfil Ella (Base 59 kg magro)", "🛠️ Personalizado"], horizontal=True, key="rad_calc_gkg")
            
            if "Él" in per_calc_sel:
                peso_init_calc = 94.0
                kcal_init_calc = 2150.0
                p_mult_init = 2.0
                g_mult_init = 0.65
            elif "Ella" in per_calc_sel:
                peso_init_calc = 59.0
                kcal_init_calc = 1350.0
                p_mult_init = 2.0
                g_mult_init = 0.65
            else:
                peso_init_calc = 75.0
                kcal_init_calc = 1800.0
                p_mult_init = 1.8
                g_mult_init = 0.8

            with col_calc_p:
                peso_sim_gkg = st.number_input("Peso de Referencia (kg):", min_value=30.0, max_value=160.0, value=peso_init_calc, step=1.0, key="num_peso_sim_gkg")

            c_sl1, c_sl2, c_sl3 = st.columns(3)
            with c_sl1:
                mult_p = st.slider("Proteína (g/kg):", min_value=1.2, max_value=2.4, value=p_mult_init, step=0.1, key="sl_mult_p")
            with c_sl2:
                mult_g = st.slider("Grasa (g/kg):", min_value=0.5, max_value=1.2, value=g_mult_init, step=0.05, key="sl_mult_g")
            with c_sl3:
                kcal_presupuesto = st.number_input("Presupuesto Diario (kcal):", min_value=1000.0, max_value=4500.0, value=kcal_init_calc, step=50.0, key="num_kcal_presupuesto")

            # Cálculo en vivo
            gr_prot_calc = peso_sim_gkg * mult_p
            kcal_prot_calc = gr_prot_calc * 4.0

            gr_grasa_calc = peso_sim_gkg * mult_g
            kcal_grasa_calc = gr_grasa_calc * 9.0

            kcal_restantes = max(0.0, kcal_presupuesto - (kcal_prot_calc + kcal_grasa_calc))
            gr_carbo_calc = kcal_restantes / 4.0

            pct_p = (kcal_prot_calc / kcal_presupuesto) * 100.0 if kcal_presupuesto > 0 else 0
            pct_g = (kcal_grasa_calc / kcal_presupuesto) * 100.0 if kcal_presupuesto > 0 else 0
            pct_c = (kcal_restantes / kcal_presupuesto) * 100.0 if kcal_presupuesto > 0 else 0

            st.markdown(f"""
            <div style="display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap;">
                <div class="metric-card" style="flex: 1; min-width: 130px; text-align: center; border-left: 3px solid #3b82f6;">
                    <div class="metric-title" style="color: #60a5fa;">🍗 Proteína</div>
                    <div class="metric-val" style="color: #60a5fa;">{gr_prot_calc:.0f} g</div>
                    <div class="metric-sub">{kcal_prot_calc:.0f} kcal ({pct_p:.0f}%)</div>
                </div>
                <div class="metric-card" style="flex: 1; min-width: 130px; text-align: center; border-left: 3px solid #f59e0b;">
                    <div class="metric-title" style="color: #fbbf24;">🥑 Grasas</div>
                    <div class="metric-val" style="color: #fbbf24;">{gr_grasa_calc:.0f} g</div>
                    <div class="metric-sub">{kcal_grasa_calc:.0f} kcal ({pct_g:.0f}%)</div>
                </div>
                <div class="metric-card" style="flex: 1; min-width: 130px; text-align: center; border-left: 3px solid #10b981;">
                    <div class="metric-title" style="color: #34d399;">🍞 Carbohidratos</div>
                    <div class="metric-val" style="color: #34d399;">{gr_carbo_calc:.0f} g</div>
                    <div class="metric-sub">{kcal_restantes:.0f} kcal ({pct_c:.0f}%)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("##### 📋 Tabla de Escala Oficial: ¿Cuánto comer de cada cosa según tu meta?")
        datos_escala = [
            {"Macronutriente": "🍗 Proteína", "Rango en Déficit (Pérdida de Grasa)": "1.6 a 2.0 g/kg (o ~2.0 g/kg de peso objetivo)", "Rango Mantenimiento / Normal": "1.2 a 1.6 g/kg", "% Calórico Típico": "30% a 35%", "Motivo Biológico": "En déficit sube para frenar la pérdida de músculo y apagar el hambre."},
            {"Macronutriente": "🥑 Grasas", "Rango en Déficit (Pérdida de Grasa)": "0.6 a 0.8 g/kg (Piso mínimo)", "Rango Mantenimiento / Normal": "0.8 a 1.2 g/kg", "% Calórico Típico": "20% a 28%", "Motivo Biológico": "Se reduce para ahorrar calorías pero nunca por debajo del 20% para no frenar hormonas."},
            {"Macronutriente": "🍞 Carbohidratos", "Rango en Déficit (Pérdida de Grasa)": "2.0 a 3.0 g/kg (El resto de calorías)", "Rango Mantenimiento / Normal": "3.5 a 5.0 g/kg", "% Calórico Típico": "40% a 48%", "Motivo Biológico": "Es la variable de ajuste: se reducen para generar el déficit pero se mantienen para tener energía."}
        ]
        st.dataframe(pd.DataFrame(datos_escala), use_container_width=True, hide_index=True)

    # --------------------------------------------------------------------------
    # SUB-PESTAÑA 2: CÓMO CALCULAR LOS MACROS DE UN ALIMENTO
    # --------------------------------------------------------------------------
    with tab_g2:
        st.markdown("#### 🧮 Cómo Calcular los Macros de Cualquier Alimento")
        st.markdown(
            "El error más común es confundir el **peso del alimento en la balanza** con la **cantidad de nutriente puro**. "
            "Aprende a calcularlo en segundos con la fórmula universal y entiende la diferencia clave entre pesado en crudo vs. cocido."
        )

        col_calc_teo, col_calc_int = st.columns([1.2, 1.0])

        with col_calc_teo:
            st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 16px; margin-bottom: 14px;">
                <h5 style="color: #38bdf8; margin-top: 0;">📐 La Fórmula Universal (Regla de Tres)</h5>
                <p style="font-size: 0.85rem; color: #cbd5e1;">
                    Todas las tablas nutricionales de los paquetes informan los valores <b>por cada 100 gramos</b>. Para calcular tu porción real pesada:
                </p>
                <div style="background: rgba(15, 23, 42, 0.8); border-left: 3px solid #38bdf8; padding: 10px 14px; border-radius: 6px; font-family: monospace; font-size: 0.95rem; color: #f8fafc; margin: 10px 0;">
                    Macro Real (g) = (Gramos Pesados ÷ 100) × Valor en la Tabla
                </div>
                <p style="font-size: 0.82rem; color: #94a3b8;">
                    <b>Ejemplo Práctico con Arroz Crudo:</b><br>
                    • La etiqueta dice que cada 100g de arroz tiene <b>78g de carbohidratos</b>.<br>
                    • Si pones en tu balanza <b>65 gramos de arroz</b>:<br>
                    👉 <code>(65 ÷ 100) × 78 = 50.7g de Carbohidratos</code>
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_calc_int:
            st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 16px; margin-bottom: 14px;">
                <h5 style="color: #38bdf8; margin-top: 0;">🧪 Simulador Rápido de Etiqueta</h5>
                <span style="font-size: 0.8rem; color: #94a3b8;">Prueba con cualquier alimento de tu alacena:</span>
            </div>
            """, unsafe_allow_html=True)
            gr_test = st.number_input("Gramos que pesas en tu plato (g):", min_value=1.0, max_value=2000.0, value=75.0, step=5.0, key="calc_gr_test")
            v100_test = st.number_input("Valor en la etiqueta cada 100g:", min_value=0.0, max_value=100.0, value=78.0, step=1.0, key="calc_v100_test", help="Ej: 78g de carbohidratos en arroz o 22g de proteína en pollo")
            
            res_macro = (gr_test / 100.0) * v100_test
            st.markdown(f"""
            <div style="background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 8px; padding: 12px; text-align: center; margin-top: 10px;">
                <span style="font-size: 0.8rem; color: #94a3b8;">Aporte real a tu cuerpo:</span>
                <div style="font-size: 1.6rem; font-weight: 700; color: #60a5fa;">{res_macro:.1f} gramos</div>
                <span style="font-size: 0.78rem; color: #cbd5e1;">({gr_test:.0f}g pesados ÷ 100) × {v100_test:.1f}g = {res_macro:.1f}g</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### ⚠️ El Gran Cambio: Alimento Crudo vs. Alimento Cocido")
        st.markdown(
            "El agua no tiene calorías ni macronutrientes, pero altera drásticamente el peso de la balanza. "
            "Existen dos grandes familias de alimentos según cómo se comportan al cocinarse:"
        )

        col_fam1, col_fam2 = st.columns(2)
        with col_fam1:
            st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 10px; padding: 16px;">
                <h5 style="color: #34d399; margin-top: 0;">1. Los que ABSORBEN agua (Arroz, Fideos, Legumbres, Avena)</h5>
                <p style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.5;">
                    Al hervirse, absorben entre <b>2.5 a 3 veces su peso en agua</b>. El contenido de carbohidratos no cambia, pero se diluye en más peso:
                </p>
                <ul style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.6;">
                    <li><b>100g de Arroz Crudo:</b> Tiene <b>78g de Carbos</b> y 350 kcal.</li>
                    <li>Al cocinarlo, esos 100g absorben agua y se convierten en <b>~260g de Arroz Cocido</b>.</li>
                    <li>¡Esos 260g siguen teniendo los mismos 78g de carbos!</li>
                    <li>Por lo tanto, <b>100g de Arroz ya Cocido solo tienen ~28g a 30g de Carbos</b> (~130 kcal).</li>
                </ul>
                <div style="background: rgba(16, 185, 129, 0.15); padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; color: #a7f3d0;">
                    💡 <b>Regla de Oro:</b> Si pesas arroz o fideos ya cocidos en tu plato, calcula aproximadamente <b>28g a 30g de carbos por cada 100g de balanza</b>.
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_fam2:
            st.markdown("""
            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 10px; padding: 16px;">
                <h5 style="color: #f87171; margin-top: 0;">2. Los que PIERDEN agua (Carnes, Pollo, Pescados)</h5>
                <p style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.5;">
                    Al cocinarse a la plancha, horno o sartén, la carne evapora agua y <b>se encoge entre un 20% y 30%</b>. La proteína no se destruye, se concentra:
                </p>
                <ul style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.6;">
                    <li><b>200g de Pechuga Cruda:</b> Tienen unos <b>44g de Proteína</b> (~220 kcal).</li>
                    <li>Al cocinarse pierde agua y pesa en balanza solo <b>~150g</b>.</li>
                    <li>¡Esos 150g cocidos siguen teniendo los mismos 44g de proteína!</li>
                    <li>Por lo tanto, <b>100g de Pechuga ya Cocida tienen ~30g de Proteína</b> (~150 kcal).</li>
                </ul>
                <div style="background: rgba(239, 68, 68, 0.15); padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; color: #fca5a5;">
                    💡 <b>Regla de Oro:</b> Si pesas carne o pollo cocido, calcula aproximadamente <b>30g de proteína por cada 100g de balanza</b> (frente a 22g en crudo).
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SUB-PESTAÑA 3: COMER EN PAREJA CON METAS DISTINTAS
    # --------------------------------------------------------------------------
    with tab_g3:
        st.markdown("#### 👫 Comer en Pareja con Metas Distintas")
        st.markdown(
            "Cocinar para dos personas con diferentes requerimientos calóricos (~2.150 kcal vs. ~1.300-1.500 kcal) "
            "no significa cocinar dos menús separados. Aplica estas estrategias de oro para comer lo mismo disfrutando de la mesa:"
        )

        col_par1, col_par2 = st.columns(2)
        with col_par1:
            st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.65); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 18px; height: 100%;">
                <h5 style="color: #38bdf8; margin-top: 0;">🥘 La Técnica de la "Base Común + Ajuste en Plato"</h5>
                <p style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.5;">
                    La forma más inteligente y cómoda de cocinar juntos:
                </p>
                <ol style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.6;">
                    <li><b>Paso 1 (La Olla Base):</b> Preparen juntos una preparación compartida rica en proteína magra y vegetales (ej: pollo salteado con verduras, salsa boloñesa con carne picada magra, estofado o cazuela).</li>
                    <li><b>Paso 2 (Servir en Balanza):</b> Usen la Olla Compartida de la app (Pestaña 1) y pesen en balanza para servir la proporción exacta de cada uno (ej. 60% Él / 40% Ella).</li>
                    <li><b>Paso 3 (El Ajuste Calórico):</b><br>
                        • 👨 <b>Él (necesita más calorías/carbos):</b> Suma a su plato una porción extra de arroz, fideos o papa hervida.<br>
                        • 👩 <b>Ella (necesita volumen con pocas calorías):</b> Suma a su plato una ensalada de hojas verdes fresca o vegetales al vapor.
                    </li>
                </ol>
                <div style="background: rgba(56, 189, 248, 0.12); padding: 8px 12px; border-radius: 6px; font-size: 0.78rem; color: #bae6fd;">
                    ✨ <b>Resultado:</b> Comen el mismo plato caliente, cocinan una sola vez y cada uno cumple al gramo su déficit.
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_par2:
            st.markdown("""
            <div style="background: rgba(236, 72, 153, 0.08); border: 1px solid rgba(236, 72, 153, 0.3); border-radius: 12px; padding: 18px; height: 100%;">
                <h5 style="color: #f472b6; margin-top: 0;">🥗 El Secreto del "Volumen de Saciedad" para Ella (~1.300 kcal)</h5>
                <p style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.5;">
                    Comer 1.300 a 1.500 kcal no debe significar pasar hambre. La clave biológica es la <b>baja densidad calórica</b> (mucho volumen en el estómago por pocas calorías):
                </p>
                <ul style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.6;">
                    <li><b>Comparativa de Carbohidratos:</b><br>
                        • 100g de arroz cocido = 130 kcal (ocupa un puñito pequeño).<br>
                        • 100g de papa hervida = <b>80 kcal</b> (¡el doble de volumen y triple de saciedad!).<br>
                        • 250g de zapallitos o calabaza = <b>solo 65 kcal</b> (¡llena un plato hondo entero!).
                    </li>
                    <li><b>Trucos de Saciedad Inmediata:</b><br>
                        • Rallar zucchini, zanahoria o champiñones dentro de la carne molida.<br>
                        • Acompañar siempre con ensalada de hojas verdes o repollo crocante.<br>
                        • Tomar 1 vaso de agua fría o con gas antes de cada comida principal.
                    </li>
                </ul>
                <div style="background: rgba(236, 72, 153, 0.15); padding: 8px 12px; border-radius: 6px; font-size: 0.78rem; color: #fbcfe8;">
                    🍽️ <b>Sensación:</b> Terminas la comida con el estómago lleno y satisfecho, sin ansiedad posterior.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SUB-PESTAÑA 4: LA CHULETA & REGLA DE LA MANO
    # --------------------------------------------------------------------------
    with tab_g4:
        st.markdown("#### 📋 La Chuleta Rápida & Estimación con la Mano")
        st.markdown("Referencia inmediata de alimentos cotidianos y la guía visual de porciones cuando comes afuera o no tienes balanza.")

        # GUÍA VISUAL DE LA MANO
        with st.expander("🖐️ La Guía Visual de la Mano (Para comer afuera, restaurantes o viajes)", expanded=True):
            st.markdown("Cuando estés en un restaurante o evento social y no puedas usar balanza, usa tu propia mano como referencia estándar:")
            
            c_h1, c_h2, c_h3, c_h4 = st.columns(4)
            with c_h1:
                st.markdown("""
                <div style="background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 10px; padding: 14px; text-align: center; height: 100%;">
                    <div style="font-size: 2rem;">✋</div>
                    <strong style="color: #60a5fa; font-size: 0.95rem;">Palma de la Mano</strong>
                    <div style="font-size: 0.78rem; color: #94a3b8; margin: 4px 0;">(Grosor y tamaño sin dedos)</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #f8fafc;">~100g - 120g</div>
                    <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 4px;">🍗 <b>25g a 30g Proteína</b><br>(Carne, pollo o pescado cocido)</div>
                </div>
                """, unsafe_allow_html=True)
            with c_h2:
                st.markdown("""
                <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 10px; padding: 14px; text-align: center; height: 100%;">
                    <div style="font-size: 2rem;">✊</div>
                    <strong style="color: #34d399; font-size: 0.95rem;">Puño Cerrado</strong>
                    <div style="font-size: 0.78rem; color: #94a3b8; margin: 4px 0;">(Volumen aproximado 1 taza)</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #f8fafc;">~100g - 120g</div>
                    <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 4px;">🍞 <b>25g a 30g Carbos</b><br>(Arroz, fideos cocidos o 1 papa)</div>
                </div>
                """, unsafe_allow_html=True)
            with c_h3:
                st.markdown("""
                <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 10px; padding: 14px; text-align: center; height: 100%;">
                    <div style="font-size: 2rem;">👍</div>
                    <strong style="color: #fbbf24; font-size: 0.95rem;">Dedo Pulgar Entero</strong>
                    <div style="font-size: 0.78rem; color: #94a3b8; margin: 4px 0;">(De la base a la punta)</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #f8fafc;">~12g - 15g</div>
                    <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 4px;">🥑 <b>12g a 14g Grasa</b><br>(1 cda sopera de aceite o manteca)</div>
                </div>
                """, unsafe_allow_html=True)
            with c_h4:
                st.markdown("""
                <div style="background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 10px; padding: 14px; text-align: center; height: 100%;">
                    <div style="font-size: 2rem;">👐</div>
                    <strong style="color: #38bdf8; font-size: 0.95rem;">Dos Manos en Cuenco</strong>
                    <div style="font-size: 0.78rem; color: #94a3b8; margin: 4px 0;">(Juntas abiertas)</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #f8fafc;">~150g - 200g</div>
                    <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 4px;">🥗 <b>Vegetales Libres</b><br>(Ensalada verde, tomate, espinaca)</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### 🥗 Tabla de Consulta Rápida de Alimentos")
        lista_chuleta = [
            {"Alimento": "Arroz Blanco (en crudo)", "Tipo": "Carbohidrato", "Porción": "100g", "Carbos (g)": 78.0, "Prot (g)": 7.0, "Grasa (g)": 0.5, "Kcal": 350.0, "Nota Práctica": "Pesar antes de cocinar en agua."},
            {"Alimento": "Arroz Blanco (ya cocido)", "Tipo": "Carbohidrato", "Porción": "100g", "Carbos (g)": 28.0, "Prot (g)": 2.5, "Grasa (g)": 0.3, "Kcal": 130.0, "Nota Práctica": "Pesar servido en el plato. Rinde x2.6."},
            {"Alimento": "Fideos / Pasta (en seco)", "Tipo": "Carbohidrato", "Porción": "100g", "Carbos (g)": 72.0, "Prot (g)": 12.0, "Grasa (g)": 1.5, "Kcal": 355.0, "Nota Práctica": "Pesar en seco crudo."},
            {"Alimento": "Fideos / Pasta (cocida)", "Tipo": "Carbohidrato", "Porción": "100g", "Carbos (g)": 30.0, "Prot (g)": 5.0, "Grasa (g)": 0.8, "Kcal": 150.0, "Nota Práctica": "Pesar escurrido sin salsa."},
            {"Alimento": "Papa / Patata hervida", "Tipo": "Carbohidrato", "Porción": "100g", "Carbos (g)": 17.0, "Prot (g)": 2.0, "Grasa (g)": 0.1, "Kcal": 80.0, "Nota Práctica": "Altísimo índice de saciedad por pocas kcal."},
            {"Alimento": "Batata / Boniato al horno", "Tipo": "Carbohidrato", "Porción": "100g", "Carbos (g)": 21.0, "Prot (g)": 1.6, "Grasa (g)": 0.2, "Kcal": 95.0, "Nota Práctica": "Rica en fibra y carbohidrato complejo."},
            {"Alimento": "Avena en copos (seca)", "Tipo": "Carbohidrato", "Porción": "100g", "Carbos (g)": 60.0, "Prot (g)": 13.5, "Grasa (g)": 7.0, "Kcal": 370.0, "Nota Práctica": "Aporta beta-glucanos y saciedad prolongada."},
            {"Alimento": "Pan Integral de molde (2 rodajas)", "Tipo": "Carbohidrato", "Porción": "50g", "Carbos (g)": 24.0, "Prot (g)": 4.5, "Grasa (g)": 1.5, "Kcal": 130.0, "Nota Práctica": "2 rebanadas estándar de sandwich."},
            {"Alimento": "Pechuga de Pollo (cruda)", "Tipo": "Proteína", "Porción": "100g", "Carbos (g)": 0.0, "Prot (g)": 22.5, "Grasa (g)": 2.0, "Kcal": 110.0, "Nota Práctica": "La reina de la proteína magra limpia."},
            {"Alimento": "Pechuga de Pollo (cocida/grill)", "Tipo": "Proteína", "Porción": "100g", "Carbos (g)": 0.0, "Prot (g)": 31.0, "Grasa (g)": 3.0, "Kcal": 155.0, "Nota Práctica": "Al perder agua la proteína se concentra."},
            {"Alimento": "Carne Vacuna Magra (Nalga/Lomo)", "Tipo": "Proteína", "Porción": "100g", "Carbos (g)": 0.0, "Prot (g)": 21.5, "Grasa (g)": 4.5, "Kcal": 130.0, "Nota Práctica": "Cortes desgrasados, excelente hierro y zinc."},
            {"Alimento": "Huevos enteros (2 unidades)", "Tipo": "Proteína + Grasa", "Porción": "100g", "Carbos (g)": 1.0, "Prot (g)": 13.0, "Grasa (g)": 10.0, "Kcal": 150.0, "Nota Práctica": "2 huevos medianos. Excelente colina y vitaminas."},
            {"Alimento": "Claras de Huevo (3 unidades)", "Tipo": "Proteína", "Porción": "100g", "Carbos (g)": 0.7, "Prot (g)": 11.0, "Grasa (g)": 0.2, "Kcal": 50.0, "Nota Práctica": "Proteína pura sin grasa ni colesterol."},
            {"Alimento": "Atún al natural en lata (escurrido)", "Tipo": "Proteína", "Porción": "120g", "Carbos (g)": 0.0, "Prot (g)": 28.0, "Grasa (g)": 1.0, "Kcal": 125.0, "Nota Práctica": "1 lata estándar escurrida al natural."},
            {"Alimento": "Queso Port Salut / Magro", "Tipo": "Proteína + Grasa", "Porción": "50g", "Carbos (g)": 1.0, "Prot (g)": 11.0, "Grasa (g)": 7.0, "Kcal": 115.0, "Nota Práctica": "Aporta calcio y caseína de digestión lenta."},
            {"Alimento": "Aceite de Oliva (1 cucharada sopera)", "Tipo": "Grasa", "Porción": "14g", "Carbos (g)": 0.0, "Prot (g)": 0.0, "Grasa (g)": 14.0, "Kcal": 126.0, "Nota Práctica": "100% grasa pura monoinsaturada cardiosaludable."},
            {"Alimento": "Palta / Aguacate", "Tipo": "Grasa", "Porción": "100g", "Carbos (g)": 2.0, "Prot (g)": 2.0, "Grasa (g)": 15.0, "Kcal": 160.0, "Nota Práctica": "Grasas buenas con 7g de fibra saciante."},
            {"Alimento": "Frutos Secos (Nueces / Almendras)", "Tipo": "Grasa + Prot", "Porción": "30g", "Carbos (g)": 4.0, "Prot (g)": 6.0, "Grasa (g)": 16.0, "Kcal": 185.0, "Nota Práctica": "1 puñado cerrado (fácil de sobrepasar)."},
            {"Alimento": "Pasta / Manteca de Maní pura", "Tipo": "Grasa + Prot", "Porción": "20g", "Carbos (g)": 3.0, "Prot (g)": 5.5, "Grasa (g)": 10.0, "Kcal": 125.0, "Nota Práctica": "1 cucharada colmada. Sin azúcar agregada."}
        ]

        df_ch = pd.DataFrame(lista_chuleta)
        filtro_tipo = st.selectbox("Filtrar por grupo de macronutriente:", ["Todos los alimentos", "Carbohidrato", "Proteína", "Grasa"], key="filtro_chuleta_v2")
        if filtro_tipo != "Todos los alimentos":
            df_mostrar_ch = df_ch[df_ch["Tipo"].str.contains(filtro_tipo)]
        else:
            df_mostrar_ch = df_ch

        st.dataframe(df_mostrar_ch, use_container_width=True, height=400)

    # --------------------------------------------------------------------------
    # SUB-PESTAÑA 5: TRAMPAS OCULTAS, AGUA & SAL EN CAMINANTES
    # --------------------------------------------------------------------------
    with tab_g5:
        st.markdown("#### 🚨 Las Trampas Ocultas de la Cocina & Manejo de Agua y Sal")
        
        st.markdown("##### ⚠️ Las 4 Trampas que Arruinan un Déficit sin Darse Cuenta")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("""
            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 10px; padding: 14px; margin-bottom: 12px;">
                <strong style="color: #f87171; font-size: 0.95rem;">1. 🫒 El chorrito de aceite de oliva "a ojo"</strong>
                <p style="font-size: 0.82rem; color: #cbd5e1; margin-top: 4px;">
                    Un "chorrito generoso" en la sartén o ensaladera suele pesar <b>20g a 25g de aceite</b> (¡más de 200 kcal!). Dos veces al día son <b>400 kcal invisibles</b> que borran por completo el esfuerzo de una caminata de 1 hora.
                    <br>👉 <i>Solución:</i> Usar un pulverizador en spray o verter sobre la cuchara pesando en balanza.
                </p>
            </div>
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 10px; padding: 14px;">
                <strong style="color: #fbbf24; font-size: 0.95rem;">2. 🧀 Picar mientras se cocina</strong>
                <p style="font-size: 0.82rem; color: #cbd5e1; margin-top: 4px;">
                    Probar un cubo de queso, 4 aceitunas, mojar dos pedazos de pan en la salsa y comer 5 nueces mientras preparas la cena suma <b>250 a 350 kcal</b> que el cerebro no registra como comida.
                    <br>👉 <i>Solución:</i> Tener a mano tomates cherry o agua con gas mientras cocinas.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_t2:
            st.markdown("""
            <div style="background: rgba(168, 85, 247, 0.08); border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 10px; padding: 14px; margin-bottom: 12px;">
                <strong style="color: #c084fc; font-size: 0.95rem;">3. 🥫 Salsas y aderezos ultraprocesados</strong>
                <p style="font-size: 0.82rem; color: #cbd5e1; margin-top: 4px;">
                    Mayonesas comunes (70% aceite vegetal refinado), salsas césar, barbacoa con jarabe de maíz o kétchup azucarado añaden 150 kcal por porción.
                    <br>👉 <i>Solución:</i> Mostaza dijon, vinagre de manzana, jugo de limón, aceto balsámico, especias y queso untable descremado.
                </p>
            </div>
            <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 10px; padding: 14px;">
                <strong style="color: #60a5fa; font-size: 0.95rem;">4. 🥤 Calorías líquidas</strong>
                <p style="font-size: 0.82rem; color: #cbd5e1; margin-top: 4px;">
                    Un vaso de jugo de naranja exprimido requiere 3 naranjas (35g de azúcar rápida sin la fibra de la fruta) que no produce saciedad. Los cafés con leche entera y azúcar aportan 150 kcal cada taza.
                    <br>👉 <i>Solución:</i> Comer la fruta entera mordida, agua, infusiones, té, mate o café solo.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### 💧 Hidratación, Sal y Electrolitos en Quienes Caminan Regularmente")
        
        c_h_a1, c_h_a2 = st.columns(2)
        with c_h_a1:
            agua_base_el = peso_el * 0.035
            agua_cam_el = agua_base_el + 0.50
            vasos_el = int(round(agua_base_el / 0.25))

            agua_base_ella = peso_ella * 0.035
            agua_cam_ella = agua_base_ella + 0.50
            vasos_ella = int(round(agua_base_ella / 0.25))

            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.65); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 16px;">
                <h5 style="color: #38bdf8; margin-top: 0;">💧 Requerimiento de Agua Personalizado en Vivo</h5>
                <p style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.5;">
                    La regla médica para personas activas: <b>35 ml por cada kilo de peso corporal</b> (+ 500 ml por hora de caminata).
                </p>
                <div style="background: rgba(15, 23, 42, 0.85); border-left: 3px solid #38bdf8; padding: 8px 12px; font-family: monospace; font-size: 0.88rem; color: #f8fafc; margin: 8px 0;">
                    Agua Diaria (L) = (Peso Actual en kg × 0.035 L) + (Horas Caminata × 0.5 L)
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_w_el, col_w_ella = st.columns(2)
            with col_w_el:
                st.markdown(f"""
                <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 12px; margin-top: 8px;">
                    <strong style="color: #60a5fa; font-size: 0.9rem;">👨 Para Él ({peso_el:.1f} kg actual):</strong>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #f8fafc; margin: 4px 0;">{agua_base_el:.2f} Litros / día</div>
                    <div style="font-size: 0.78rem; color: #cbd5e1;">• 🛋️ Día descanso: <b>~{vasos_el} vasos</b> (de 250ml)<br>• 🚶 Con 1h caminata: <b>{agua_cam_el:.2f} L</b></div>
                </div>
                """, unsafe_allow_html=True)

            with col_w_ella:
                st.markdown(f"""
                <div style="background: rgba(236, 72, 153, 0.1); border: 1px solid rgba(236, 72, 153, 0.3); border-radius: 8px; padding: 12px; margin-top: 8px;">
                    <strong style="color: #f472b6; font-size: 0.9rem;">👩 Para Ella ({peso_ella:.1f} kg actual):</strong>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #f8fafc; margin: 4px 0;">{agua_base_ella:.2f} Litros / día</div>
                    <div style="font-size: 0.78rem; color: #cbd5e1;">• 🛋️ Día descanso: <b>~{vasos_ella} vasos</b> (de 250ml)<br>• 🚶 Con 1h caminata: <b>{agua_cam_ella:.2f} L</b></div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background: rgba(56, 189, 248, 0.08); border: 1px dashed rgba(56, 189, 248, 0.3); border-radius: 8px; padding: 10px; margin-top: 10px; font-size: 0.8rem; color: #cbd5e1;">
                💡 <b>¿Por qué cambia tu necesidad al bajar de peso?</b><br>
                Con tu peso actual de <b>{peso_el:.1f} kg</b>, tienes más masa celular y volumen sanguíneo que hidratar (~<b>{agua_base_el:.2f} L</b>).<br>
                Cuando alcances los <b>90 kg</b>, tu necesidad biológica bajará naturalmente a ~<b>{(90.0 * 0.035):.2f} L</b> (¡más de 1 litro menos al día!).
            </div>
            """, unsafe_allow_html=True)

        with c_h_a2:
            st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.65); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 16px;">
                <h5 style="color: #f59e0b; margin-top: 0;">🧂 El Gran Mito de la Sal (Sodio)</h5>
                <p style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.5;">
                    <b>La sal tiene 0 calorías. No engorda ni crea grasa corporal.</b>
                </p>
                <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
                    Cuando dejas los alimentos ultraprocesados y cocinas comida real en casa, la ingesta de sodio baja bruscamente.
                    Si sales a caminar 1 hora y sudas, <b>tu cuerpo pierde agua y sodio</b>.
                </p>
                <ul style="font-size: 0.8rem; color: #cbd5e1; line-height: 1.5;">
                    <li><b>Si te falta sal:</b> Sentirás pesadez en las piernas, calambres nocturnos, presión baja y dolor de cabeza.</li>
                    <li><b>Si un día comes con más sal:</b> La balanza subirá 500g de agua durante 24h a 48h, pero esa agua se orina sola al regularse los electrolitos.</li>
                </ul>
                <div style="background: rgba(245, 158, 11, 0.15); padding: 6px 10px; border-radius: 4px; font-size: 0.78rem; color: #fde68a;">
                    💡 Sala tu comida al gusto razonable sin miedo; es un electrolito vital para el rendimiento físico.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SUB-PESTAÑA 6: FÓRMULAS METABÓLICAS & DUDAS FRECUENTES
    # --------------------------------------------------------------------------
    with tab_g6:
        st.markdown("#### 🔬 Explicación de las Fórmulas Científicas de la App")
        
        with st.expander("1. ¿Qué es la Tasa Metabólica Basal (TMB - Mifflin-St Jeor)?", expanded=True):
            st.markdown("""
            La **TMB** son las calorías mínimas que tu organismo quema en 24 horas simplemente para mantenerte con vida (latidos del corazón, respiración, función hepática, temperatura corporal) en reposo total acostado en cama.
            
            **Fórmula de Mifflin-St Jeor:**
            * 👨 **Hombres:** `(10 × Peso en kg) + (6.25 × Altura en cm) - (5 × Edad) + 5`
            * 👩 **Mujeres:** `(10 × Peso en kg) + (6.25 × Altura en cm) - (5 × Edad) - 161`
            
            *Por qué es vital:* **Nunca debes comer por debajo de tu TMB de forma crónica**, ya que tu cuerpo lo interpreta como inanición, bajando la tiroides y quemando músculo en lugar de grasa.
            """)

        with st.expander("2. ¿Qué es el Techo Sedentario / Gasto Base (TMB × 1.2)?"):
            st.markdown("""
            Es el gasto de un día en el que **no sales a hacer caminata ni ejercicio programado**, pero te levantas de la cama, te bañas, cocinas, trabajas sentado o te mueves por la casa.
            
            Ese movimiento diario espontáneo se llama **NEAT** (*Non-Exercise Activity Thermogenesis*) y en personas sedentarias representa aproximadamente un **20% extra sobre el piso vital** (`TMB × 1.2`).
            """)

        with st.expander("3. ¿Cómo se calcula la Quema de las Caminatas y Ejercicios (METs)?"):
            st.markdown("""
            El **MET** (*Metabolic Equivalent of Task*) es la unidad científica estándar de intensidad de ejercicio (1 MET = reposo sentado).
            
            **Fórmula exacta aplicada en la app:**
            $$\\text{Kcal Quemadas} = \\text{METs} \\times \\text{Peso Corporal (kg)} \\times \\text{Horas}$$
            
            * **Caminata suave (4.0 km/h):** 3.0 METs
            * **Caminata constante/ligera (5.0 km/h):** 4.0 METs
            * **Caminata rápida (5.8 km/h):** 4.8 METs
            * **Musculación / Gimnasio:** 4.5 METs
            
            *Por qué el peso importa tanto:* Una persona de 119 kg quema **476 kcal** en 1 hora de caminata a 4.0 METs ($4.0 \\times 119$), mientras que una de 69 kg quema **276 kcal** ($4.0 \\times 69$) al mismo ritmo exacto. Mover más masa requiere más energía mecánica.
            """)

        with st.expander("4. La Regla de Oro de las 7.700 kcal (¿Cómo se pierde 1 kg de grasa?)"):
            st.markdown("""
            1 kilogramo de tejido adiposo humano almacena aproximadamente **7.700 kilocalorías de energía química**.
            
            * Para perder **1 kg de grasa pura**, necesitas acumular un **déficit calórico neto de 7.700 kcal**.
            * Si mantienes un déficit diario de **500 kcal**:
              * En 7 días habrás acumulado un déficit de **3.500 kcal** $\\rightarrow$ **~0.45 kg de grasa perdida por semana**.
              * En 1 mes habrás acumulado un déficit de **15.000 kcal** $\\rightarrow$ **~2.0 kg de grasa pura perdida al mes**.
            """)

        with st.expander("5. ¿Por qué la balanza sube 1 kg de un día para otro si no rompí la dieta?"):
            st.markdown("""
            **Es fisiológicamente imposible ganar 1 kg de grasa en 24 horas** (requeriría comer 7.700 kcal de golpe *por encima* de tu gasto, es decir, ¡más de 10.000 kcal en un solo día!).
            
            Las fluctuaciones diarias de 0.5 kg a 1.5 kg en la balanza se deben a:
            1. **Agua de Carbohidratos (Glucógeno):** Cada gramo de carbohidrato que entra a los músculos retiene de 3 a 4 gramos de agua. Si cenaste más arroz o pasta, te pesas más pesado porque tus músculos están hidratados, no con grasa.
            2. **Sodio y Sal:** Una comida con más sal retiene agua extracelular durante 24-48 horas.
            3. **Tránsito Intestinal:** El volumen y peso de la comida aún en digestión antes de evacuar.
            4. **Cortisol (Estrés o poco sueño):** El estrés eleva el cortisol, que actúa sobre los receptores de aldosterona provocando retención hídrica temporal.
            
            *Consejo:* Mira siempre el promedio semanal o la curva a 24 semanas de la app, nunca el número aislado de un solo día.
            """)

