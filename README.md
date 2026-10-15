# ⚖️ Sistema Analítico de Nutrición & Auditoría Metabólica

Plataforma analítica e interactiva desarrollada con **Streamlit** y **Plotly**, diseñada para gestionar la nutrición de precisión, el balance energético y la división de preparaciones culinarias en pareja de forma científica, dinámica y personalizada.

---

## 🚀 Características Principales

### 1. 🧮 Calculadora de Alimentos & Armador de Olla Compartida
* **Base de Alimentos Completa:** Carnes magras, pescados, huevos, lácteos, cereales, harinas, legumbres, tubérculos, grasas y vegetales clasificados en crudo/neto.
* **Alimentos Personalizados con Autoconversión:** Agrega cualquier producto industrial o casero especificando los valores nutricionales por cada 100g o por porción/unidad (ej. galletas, alfajores, yogures, barras de proteína).
* **División Matemática de la Olla Compartida:**
  * Permite cocinar un plato común (guiso, estofado, salteado, etc.) ingresando los ingredientes en crudo y el peso final cocido.
  * Calcula el factor de hidratación o reducción por evaporación.
  * Divide las porciones para **Él** y **Ella** según:
    * **Proporción Dinámica:** Según las metas calóricas de cada uno.
    * **Proporción Fija Estándar:** Reparto 60% Él / 40% Ella.
  * Indica exactamente cuántos **gramos cocidos colocar en el plato en la balanza**.
* **Libro de Recetas Guardadas:** Guarda tus recetas favoritas en disco y cárgalas a la olla con un solo clic.
* **Exportación para WhatsApp:** Genera un resumen con formato y emojis listo para copiar y pegar por mensajería.

### 2. 📅 Registro & Balance Semanal (Lunes a Domingo)
* **🧭 Mini-Dashboard de Ritmo Semanal (7 Días):** Tira superior compacta que resume de un solo vistazo el estado de cada día (Lunes a Domingo) con chips de balance calórico neto (`🟢 Déficit` / `🔵 Superávit` / `⚪ Sin registro`).
* **📐 Layout Diario en Doble Columna Maestra:**
  * **Columna Izquierda (🍽️ Nutrición & Comidas):** Lista limpia de alimentos cargados con macros, desglose calórico y formulario rápido de carga.
  * **Columna Derecha (🏃 Actividades & Smartwatch):** Acceso rápido con **chips de 1 clic** (`[🚶 30m Paseo]`, `[🚶‍♂️ 1h Caminata]`, `[🏋️ 1h Gimnasio]`), panel para calorías de reloj inteligente y detalle de actividades.
* **🏃/⌚ Gestor de Múltiples Actividades Físicas por Día:**
  * **Múltiples sesiones diarias:** Permite registrar todas las actividades que realices en el día (ej: Caminata matutina + Sesión de Gimnasio/Pesas + Partido de Pádel o Bici).
  * **Catálogo de Ejercicios Integrado:** Incluye caminata paso constante/ligero/rápido, musculación/gimnasio, ciclismo, running, pádel/tenis, natación, yoga/pilates, funcional/HIIT y actividades personalizadas.
  * **Doble Modo de Registro:**
    * **⏱️ Por Minutos (Fórmulas METs):** Calcula la quema calórica exacta en tiempo real según el peso corporal del usuario ($METs \times peso \times \frac{min}{60}$).
    * **⌚ Por Calorías de Reloj Inteligente (kcal directas):** Ingreso manual del gasto calórico activo exacto reportado por tu smartwatch (Apple Watch, Garmin, Xiaomi, Fitbit, Galaxy Watch, etc.).
  * **Asignación Flexible:** Carga actividades para *Solo Él*, *Solo Ella* o para *Ambos (juntos)* con cálculo simultáneo adaptado al peso de cada uno.
  * **Gestión Visual:** Lista con badges, minutos, calorías quemadas y botón `❌` para eliminar actividades individuales.
* **🎯 Monitor de Cumplimiento Diario de Macros (P, C, G):** En cada día de la semana, compara los gramos consumidos contra la meta diaria asignada (Proteína, Carbohidratos y Grasas) para Él y para Ella, mostrando barras de progreso y badges dinámicos con alerta de gramos faltantes (`⏳ Déficit`) o superados (`⚠️ Exceso`).
* **Balance Diario y Semanal Real:** Suma el gasto base en reposo más todas las actividades registradas del día, calculando el balance neto diario y acumulado de 7 días.
* **Gráfica Comparativa Dinámica:** Barras de ingesta calórica vs. líneas de gasto real diario (que se elevan en función de la cantidad e intensidad de actividades registradas) y líneas de meta diaria.

### 3. 🔥 Auditoría Metabólica & Simulador de Caminatas
* **🔬 Modo Dual de Auditoría & Proyección:**
  * **🏃‍♂️ Actividad Real Semanal:** Audita y proyecta a partir de los datos reales registrados día a día en el Registro Semanal.
  * **🔮 Simulador Teórico ("¿Qué pasaría si...?"):** Slider interactivo manual (0 a 14 h/semana) e intensidad METs para modelar escenarios hipotéticos de pérdida de peso en el tiempo.
* **Fórmulas Científicas:**
  * **TMB (Mifflin-St Jeor):** Gasto basal vital según peso, altura y edad.
  * **Gasto Base (Día de Descanso):** Factor $1.2 \times TMB$ (gasto en días sin caminata).
  * **Gasto por Caminata (METs):** Quema calórica exacta en función del peso y ritmo de caminata (3.0, 4.0 o 4.8 METs).
  * **Gasto Energético Total Diario (TDEE Real):** Promedio diario incluyendo las horas de actividad física semanal.
* **Objetivos Metabólicos Configurables:**
  * 📉 **Déficit Moderado:** Enfoque en pérdida de grasa corporal.
  * 📉 **Déficit Ligero:** Definición suave y sostenible.
  * ⚖️ **Mantenimiento Metabólico:** Consumo igualado al gasto TDEE.
  * 📈 **Superávit (+250 / +300 kcal):** Aumento de masa muscular y peso.
  * 🛠️ **Personalizado:** Configuración libre de calorías totales o macronutrientes en gramos (P, C, G).
* **Curva Proyectada a 24 Semanas (6 Meses):** Simulación adaptativa que recalcula semana a semana el nuevo TMB y gasto físico a medida que el peso corporal varía, graficando trayectorias tanto de descenso como de ascenso.

### 4. 📈 Registro de Peso y Avance Real (Tracker Local)
* Registro histórico de pesajes periódicos en tabla persistente (`registro_peso.csv`).
* Gráfica comparativa superponiendo la **curva teórica proyectada** contra los **pesos reales registrados**.
* Métricas de avance acumulado desde el inicio del programa.

---

## 💾 Persistencia de Datos 100% Local y Offline

No requiere bases de datos externas ni conexión a internet para funcionar. Toda la información se almacena localmente en el directorio de la aplicación:

| Archivo | Contenido |
| :--- | :--- |
| `config_usuario.json` | Parámetros biométricos, objetivos y metas calóricas persistentes. |
| `alimentos_custom.json` | Catálogo de alimentos personalizados cargados por el usuario. |
| `recetas_guardadas.json` | Recetario de platos preparados guardados. |
| `semana_alimentos.json` | Registro de comidas del lunes al domingo. |
| `semana_caminatas.json` | Registro de actividad física diaria (horas o calorías de reloj) del lunes al domingo. |
| `registro_peso.csv` | Historial de pesajes y notas periódicas. |

---

## 🛠️ Instalación y Puesta en Marcha

### Prerrequisitos
* Python 3.10 o superior instalado.

### 1. Clonar el repositorio
```bash
git clone https://github.com/cris2892/comida.git
cd comida
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación
```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador web en `http://localhost:8501`.

---

## 📦 Dependencias Principales

* [Streamlit](https://streamlit.io/) - Framework de interfaz de usuario.
* [Pandas](https://pandas.pydata.org/) - Procesamiento y análisis de datos.
* [Plotly](https://plotly.com/python/) - Visualización gráfica interactiva en tema oscuro.
* [NumPy](https://numpy.org/) - Cálculos matemáticos vectorizados.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
