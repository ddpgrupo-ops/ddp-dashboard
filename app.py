import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# Configuración inicial de la página (Debe ser la primera línea de código de Streamlit)
st.set_page_config(page_title="Dashboard Ejecutivo DDP", page_icon="📊", layout="wide")

# --- INYECCIÓN DE CSS PARA DISEÑO CORPORATIVO (ESTILO "DASHBOARD") ---
st.markdown("""
<style>
    /* Ocultar elementos de Streamlit para que parezca una Web App propia */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Espaciado general más limpio */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Estilo de Tarjetas (Cards) para los KPIs */
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e2e8f0;
        padding: 20px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        text-align: center;
    }
    div[data-testid="stMetric"] label {
        font-size: 15px !important;
        color: #64748b !important;
        font-weight: 600 !important;
        justify-content: center;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 32px !important;
        color: #0f172a !important;
        font-weight: bold !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
        justify-content: center;
    }
    
    /* Títulos de secciones */
    .seccion-titulo {
        font-size: 20px;
        font-weight: 600;
        color: #1e293b;
        margin-top: 30px;
        margin-bottom: 15px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 5px;
    }
    
    /* Títulos de Expanders (Pestañas Deslizantes) */
    .streamlit-expanderHeader {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #1A365D !important;
    }
    
    /* Ajuste definitivo para el tamaño de las métricas */
    div[data-testid="stMetricValue"] > div {
        font-size: 1.2rem !important; /* Más chico para que quepa perfecto */
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
    }
</style>
""", unsafe_allow_html=True)


# --- 1. SISTEMA DE SEGURIDAD / LOGIN ---
USERS = {
    "jorge.delamora@ddp.mx": {"password": "DDP0025", "role": "viewer", "name": "Jorge de la Mora", "title": "Director General / Socio"},
    "maricarmen.plata@ddp.mx": {"password": "DDP0012", "role": "viewer", "name": "Maricarmen Plata Castro", "title": "Asistente de Dirección"},
    "raul.ramirez@ddp.mx": {"password": "DDP0149", "role": "viewer", "name": "Raúl Ramírez Domínguez", "title": "Gerente Administrativo"},
    "manuel.acosta@ddp.mx": {"password": "DDP1489", "role": "viewer", "name": "Manuel Acosta del Río", "title": "Director de Operaciones"},
    "leonardo.velazquez@ddp.mx": {"password": "DDP2505", "role": "admin", "name": "J. Leonardo Velázques Rocha", "title": "Gerente de TI & Telecom"}
}

def check_password():
    def password_entered():
        user = st.session_state["username"]
        pwd = st.session_state["password"]
        
        if user in USERS and USERS[user]["password"] == pwd:
            st.session_state["password_correct"] = True
            st.session_state["role"] = USERS[user]["role"]
            st.session_state["name"] = USERS[user]["name"]
            st.session_state["title"] = USERS[user]["title"]
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        with col2:
            st.image("logo.png", use_container_width=True)
            st.markdown("<h2 style='text-align: center; color: #1e293b;'>Plataforma Ejecutiva</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b;'>Análisis y Control Financiero de Proyectos</p><br>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                st.text_input("Correo Institucional", key="username", placeholder="ejemplo@ddp.mx", autocomplete="username")
                st.text_input("Contraseña", type="password", key="password", placeholder="••••••••")
                st.checkbox("Mantener sesión iniciada", key="remember_me", help="El navegador recordará tu acceso.")
                st.form_submit_button("Acceder de forma segura", on_click=password_entered, use_container_width=True)
            
            st.info("💡 **Acceso Biométrico:** Para entrar con Face ID o Touch ID, presiona 'Mantener sesión iniciada' y acepta cuando tu equipo pregunte si deseas guardar la contraseña.")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        with col2:
            st.image("logo.png", use_container_width=True)
            st.markdown("<h2 style='text-align: center; color: #1e293b;'>Plataforma Ejecutiva</h2>", unsafe_allow_html=True)
            with st.form("login_form"):
                st.text_input("Correo Institucional", key="username", placeholder="ejemplo@ddp.mx", autocomplete="username")
                st.text_input("Contraseña", type="password", key="password")
                st.form_submit_button("Acceder de forma segura", on_click=password_entered, use_container_width=True)
            st.error("🚨 Credenciales incorrectas. Verifique e intente de nuevo.")
        return False
    else:
        return True

if not check_password():
    st.stop() 

# --- 2. CARGA Y PROCESAMIENTO DE DATOS ---
role = st.session_state.get("role", "viewer")
user_name = st.session_state.get("name", "Ejecutivo")
user_title = st.session_state.get("title", "")

uploaded_file = None
if role == "admin":
    st.sidebar.markdown("### ⚙️ Panel de Administración")
    uploaded_file = st.sidebar.file_uploader("Actualizar Base de Datos (Excel/CSV):", type=["csv", "xlsx"])
    if st.sidebar.button("Forzar recarga (Limpiar Caché)", use_container_width=True):
        st.cache_data.clear()
        st.sidebar.success("✅ Caché limpiada.")
    st.sidebar.markdown("---")

@st.cache_data
def load_data(file):
    if file is not None:
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file, encoding='utf-8')
            else:
                df = pd.read_excel(file)
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
            return pd.DataFrame()
    else:
        # Fallback 1: Buscar URL segura en los secretos de Streamlit (Google Sheets)
        csv_url = None
        try:
            csv_url = st.secrets.get("CSV_URL")
        except Exception:
            pass # Si corre local y no hay archivo de secretos, ignorar

        if csv_url:
            try:
                df = pd.read_csv(csv_url)
            except Exception as e:
                st.error(f"Error al conectar con la base de datos segura: {e}")
                return pd.DataFrame()
        # Fallback 2: Archivo local (si existe)
        else:
            local_path = "datos_chetumal.csv"
            if os.path.exists(local_path):
                df = pd.read_csv(local_path, encoding='utf-8')
            else:
                if role == "admin":
                    st.warning("⚠️ Sube la base de datos en el panel izquierdo o configura el Google Sheet.")
                else:
                    st.warning("⚠️ El departamento de TI no ha publicado los datos de este periodo.")
                return pd.DataFrame()
            
    if 'df' in locals() and not df.empty:
        # --- AUTO-MAPEO DE COLUMNAS (Soporte para múltiples formatos) ---
        # Si el Excel trae 'OBRA' en lugar de 'TT', o 'COSTO' en lugar de 'COSTO S/IVA'
        column_mapping = {
            'OBRA': 'TT',          # Proyecto Pitahaya
            'COSTO': 'COSTO S/IVA', # Monto
            'TIPO': 'TIPO 2'       # INGRESO/EGRESO
        }
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns and new_col not in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)
                
        if 'COSTO S/IVA' in df.columns:
            # Extraer solo números, puntos y signos negativos, ignorando todo lo demás
            df['COSTO S/IVA'] = df['COSTO S/IVA'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
            df['COSTO S/IVA'] = pd.to_numeric(df['COSTO S/IVA'], errors='coerce').fillna(0)
    
    # Limpiar espacios en blanco de columnas de texto clave para evitar fallos en filtros
    for col in ['TIPO 2', 'TT', 'MES', 'AÑO', 'CONCEPTO']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
            # Auto-renombrar proyectos si vienen con el nombre antiguo
            if col == 'TT':
                mapeo = {
                    "HOSPITAL": "HOSPITAL CHET",
                    "ESTANCIA": "ESTANCIA CHET",
                    "PITAHAYA": "PITAHAYA SLP"
                }
                df['TT'] = df['TT'].replace(mapeo)
            
    # Traductor inteligente para la columna MES (Convierte "10 2025" o "102025" a "2025-10 (Octubre)")
    if 'MES' in df.columns:
        def limpiar_mes(val):
            val_str = str(val).strip().replace(" ", "")
            val_str = val_str.split('.')[0] # Quitar decimales si Pandas lo leyó como float
            
            if len(val_str) == 6 and val_str.isdigit():
                mes = val_str[:2]
                ano = val_str[2:]
            elif len(val_str) == 5 and val_str.isdigit():
                mes = f"0{val_str[0]}"
                ano = val_str[1:]
            else:
                return val # Dejarlo intacto si no cumple el formato
                
            meses_nombres = {
                "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
                "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
                "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
            }
            nombre = meses_nombres.get(mes, mes)
            return f"{ano}-{mes} ({nombre})"
            
        df['MES'] = df['MES'].apply(limpiar_mes)

    if 'AÑO' in df.columns:
        df['AÑO'] = df['AÑO'].str.replace('.0', '', regex=False)
        
    return df

df = load_data(uploaded_file)

if df.empty:
    st.stop()

# --- 3. BARRA LATERAL EJECUTIVA ---
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("### 🎯 Parámetros del Reporte")

# Filtro: Año
opciones_ano = sorted(df['AÑO'].dropna().unique().tolist())
ano_seleccionado = st.sidebar.selectbox("Periodo Fiscal (Año):", options=["Histórico Total"] + opciones_ano)

if ano_seleccionado != "Histórico Total":
    df = df[df['AÑO'] == ano_seleccionado]

# Copia para graficar tendencias históricas (sin filtrar por el mes seleccionado)
df_para_tendencia = df.copy()

# Filtro: Mes
opciones_mes = df['MES'].dropna().unique().tolist()
# Para ordenar los meses correctamente si vienen como '01 2026', '02 2026'
opciones_mes.sort() 
mes_seleccionado = st.sidebar.selectbox("Mes de Análisis:", options=["Acumulado de todos los meses"] + opciones_mes)

if mes_seleccionado != "Acumulado de todos los meses":
    df = df[df['MES'] == mes_seleccionado]

# Filtro: Proyecto
opciones_proyecto = df['TT'].dropna().unique().tolist()
proyecto_seleccionado = st.sidebar.radio("Centro de Costos / Proyecto:", options=["Consolidado General"] + opciones_proyecto)

if proyecto_seleccionado != "Consolidado General":
    df_filtrado = df[df['TT'] == proyecto_seleccionado]
    df_para_tendencia = df_para_tendencia[df_para_tendencia['TT'] == proyecto_seleccionado]
else:
    df_filtrado = df.copy()

st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
if st.sidebar.button("Cerrar Sesión Segura", type="primary", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# --- CÁLCULOS FINANCIEROS ---
df_ingresos = df_filtrado[df_filtrado['TIPO 2'].str.upper() == 'INGRESO']
df_egresos = df_filtrado[df_filtrado['TIPO 2'].str.upper() == 'EGRESO']

total_ingresos = df_ingresos['COSTO S/IVA'].sum()
total_egresos = df_egresos['COSTO S/IVA'].sum()
utilidad = total_ingresos - total_egresos
margen = (utilidad / total_ingresos * 100) if total_ingresos > 0 else 0

# --- CÁLCULOS DE AVANCE (PRESUPUESTO) ---
PRESUPUESTOS = {
    "HOSPITAL CHET": 32371388.04,
    "ESTANCIA CHET": 1490474.12,
    "PITAHAYA SLP": 35912747.18
}

if proyecto_seleccionado == "Consolidado General":
    presupuesto_total = sum(PRESUPUESTOS.values())
else:
    # Aseguramos coincidencia de texto
    clave_proy = proyecto_seleccionado.strip().upper()
    presupuesto_total = PRESUPUESTOS.get(clave_proy, 0)

por_cobrar = presupuesto_total - total_ingresos
avance_cobranza = (total_ingresos / presupuesto_total * 100) if presupuesto_total > 0 else 0

# --- 4. CUERPO PRINCIPAL DEL DASHBOARD ---

# Título y Saludo
st.markdown(f"<h1 style='color: #0f172a; margin-bottom: 0px;'>Dashboard Financiero: {proyecto_seleccionado}</h1>", unsafe_allow_html=True)
texto_periodo = f"Año: {ano_seleccionado}" if ano_seleccionado != "Histórico Total" else "Histórico Completo"
texto_mes = f" | Mes: {mes_seleccionado}" if mes_seleccionado != "Acumulado de todos los meses" else " | Acumulado total"
if user_title:
    st.markdown(f"<p style='color: #64748b; font-size: 16px; margin-top: -10px;'>{texto_periodo}{texto_mes} | Visualizando como: <strong>{user_name}</strong> <span style='font-size: 14px;'>({user_title})</span></p>", unsafe_allow_html=True)
else:
    st.markdown(f"<p style='color: #64748b; font-size: 16px; margin-top: -10px;'>{texto_periodo}{texto_mes} | Visualizando como: <strong>{user_name}</strong></p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- KPIs (Tarjetas Superiores) ---
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.metric(label="Valor del Contrato (S/IVA)", value=f"${presupuesto_total:,.0f}")
with kpi2:
    st.metric(label="Ingresos Facturados (S/IVA)", value=f"${total_ingresos:,.0f}")
with kpi3:
    st.metric(label="Egresos Totales (S/IVA)", value=f"${total_egresos:,.0f}")
with kpi4:
    st.metric(label="Utilidad Bruta (S/IVA)", value=f"${utilidad:,.0f}", delta=f"${utilidad:,.0f}" if utilidad > 0 else f"${utilidad:,.0f}")
with kpi5:
    st.metric(label="Margen de Utilidad", value=f"{margen:.1f}%", delta=f"{margen:.1f}%" if margen > 0 else f"{margen:.1f}%")

# Barra de progreso visual
progreso_seguro = min(avance_cobranza / 100, 1.0)
st.progress(progreso_seguro)
st.markdown(
    f"""
    <div style='text-align: right; margin-top: 5px;'>
        <span style='font-size: 18px; color: #475569;'>Avance de Facturación / Cobranza:</span> 
        <strong style='font-size: 24px; color: #1A365D;'>{avance_cobranza:.1f}%</strong> 
        <span style='font-size: 18px; color: #cbd5e1;'>&nbsp;&nbsp;|&nbsp;&nbsp;</span> 
        <span style='font-size: 18px; color: #475569;'>Falta por cobrar:</span> 
        <strong style='font-size: 24px; color: #d62728;'>${por_cobrar:,.0f}</strong>
    </div>
    """, 
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)


# --- NUEVO: CÁLCULOS DE TENDENCIA Y BURN RATE ---
df_trend_ingresos = df_para_tendencia[df_para_tendencia['TIPO 2'].str.upper() == 'INGRESO'].groupby('MES')['COSTO S/IVA'].sum().reset_index()
df_trend_egresos = df_para_tendencia[df_para_tendencia['TIPO 2'].str.upper() == 'EGRESO'].groupby('MES')['COSTO S/IVA'].sum().reset_index()
df_trend = pd.merge(df_trend_ingresos, df_trend_egresos, on='MES', how='outer', suffixes=('_ING', '_EGR')).fillna(0)
df_trend = df_trend.sort_values(by='MES')
df_trend['Utilidad'] = df_trend['COSTO S/IVA_ING'] - df_trend['COSTO S/IVA_EGR']

# Burn Rate (Velocidad de gasto)
meses_con_gasto = df_trend[df_trend['COSTO S/IVA_EGR'] > 0]['MES'].nunique()
burn_rate = df_trend['COSTO S/IVA_EGR'].sum() / meses_con_gasto if meses_con_gasto > 0 else 0
meses_restantes = (presupuesto_total - df_trend['COSTO S/IVA_EGR'].sum()) / burn_rate if burn_rate > 0 else 0

st.markdown("<hr>", unsafe_allow_html=True)
col_trend, col_burn = st.columns([2.5, 1.5])

with col_trend:
    st.markdown("<div class='seccion-titulo'>Tendencia de Utilidad (Línea de Tiempo)</div>", unsafe_allow_html=True)
    if not df_trend.empty:
        import plotly.graph_objects as go
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=df_trend['MES'], y=df_trend['Utilidad'], mode='lines+markers', name='Utilidad Neta ($)',
                                       line=dict(color='#1A365D', width=4), marker=dict(size=8, color='#d62728')))
        fig_trend.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20, b=20, l=20, r=20),
                                yaxis=dict(title='Utilidad Neta ($)'), xaxis=dict(type='category', title='Mes'))
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Sin datos de tendencia.")

with col_burn:
    st.markdown("<div class='seccion-titulo'>Velocidad de Gasto (Burn Rate)</div>", unsafe_allow_html=True)
    if burn_rate > 0:
        st.markdown(f'''
        <div style="background-color: #f8fafc; padding: 25px; border-radius: 12px; text-align: center; border-left: 6px solid #d62728; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            <p style="color: #64748b; font-size: 14px; margin-bottom: 5px; font-weight: 600; text-transform: uppercase;">Promedio Mensual de Gasto</p>
            <h2 style="color: #0f172a; margin-top: 0px; font-size: 32px; font-weight: 800;">${burn_rate:,.0f}</h2>
            <hr style="border-color: #e2e8f0; margin: 15px 0;">
            <p style="color: #64748b; font-size: 14px; margin-bottom: 5px; font-weight: 600;">El presupuesto restante se agotaría en:</p>
            <h2 style="color: #d62728; margin-top: 0px; font-size: 28px; font-weight: 800;">{meses_restantes:.1f} meses</h2>
        </div>
        
        <div style="margin-top: 15px; font-size: 12px; color: #64748b; text-align: left; background-color: #f1f5f9; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
            <strong>ℹ️ ¿Qué es este dato?</strong><br>
            El <em>Burn Rate</em> mide la velocidad a la que el proyecto "quema" o consume su presupuesto.<br><br>
            <strong>Fórmula utilizada:</strong><br>
            <code style="color: #1A365D; background: transparent; padding: 0;">Egresos Totales ÷ Meses Transcurridos</code><br><br>
            <i>Sirve como alerta temprana para saber si el dinero se acabará antes de terminar la obra.</i>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.info("No hay suficientes egresos registrados para calcular el Burn Rate.")

st.markdown("<hr>", unsafe_allow_html=True)

# --- SECCIÓN GRÁFICAS PRINCIPALES ---
st.markdown("<div class='seccion-titulo'>Rendimiento y Flujo de Efectivo</div>", unsafe_allow_html=True)

col_chart1, col_chart2 = st.columns([6, 4])

with col_chart1:
    if not df_filtrado.empty:
        df_mes = df_filtrado.groupby(['MES', 'TIPO 2'])['COSTO S/IVA'].sum().reset_index()
        fig1 = px.line(df_mes, x='MES', y='COSTO S/IVA', color='TIPO 2', markers=True,
                       color_discrete_map={'INGRESO': '#6DB33F', 'EGRESO': '#1A365D'},
                       labels={'COSTO S/IVA': 'Monto ($)', 'MES': ''})
        fig1.update_layout(title="Ingresos vs Egresos por Mes", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title_text="")
        fig1.update_traces(fill='tozeroy')
        st.plotly_chart(fig1, use_container_width=True)

with col_chart2:
    # Dona de gastos
    if not df_egresos.empty:
        df_conc_egreso = df_egresos.groupby('CONCEPTO')['COSTO S/IVA'].sum().reset_index()
        df_conc_egreso = df_conc_egreso.sort_values(by='COSTO S/IVA', ascending=False)
        
        # Filtro Inteligente: Agrupar en "Otros Gastos" si son más de 8 conceptos
        if len(df_conc_egreso) > 8:
            top7 = df_conc_egreso.iloc[:7]
            otros_monto = df_conc_egreso.iloc[7:]['COSTO S/IVA'].sum()
            otros_df = pd.DataFrame([{'CONCEPTO': 'OTROS GASTOS', 'COSTO S/IVA': otros_monto}])
            df_conc_egreso = pd.concat([top7, otros_df], ignore_index=True)
        
        # Paleta corporativa (Azules, grises, verdes)
        colores = ['#1A365D', '#2b5c8f', '#4f83cc', '#6DB33F', '#8bc34a', '#cddc39', '#94a3b8', '#cbd5e1']
        
        fig2 = px.pie(df_conc_egreso, values='COSTO S/IVA', names='CONCEPTO', hole=0.6,
                      color_discrete_sequence=colores)
        fig2.update_layout(title="Estructura de Costos (Top 8)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        fig2.update_traces(textposition='outside', textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True)

# Pestañas de Análisis Estratégico
st.markdown("<div class='seccion-titulo'>Centro de Inteligencia y Análisis Estratégico</div>", unsafe_allow_html=True)
tab_tabla, tab_pareto, tab_treemap, tab_forecast = st.tabs([
    "📊 Histórico Numérico", 
    "📈 Ley de Pareto (80/20)", 
    "🟩 Mapa de Árbol (Treemap)", 
    "🔮 Forecast a Cierre de Año"
])

with tab_tabla:
    if not df_filtrado.empty:
        df_flujo_mensual = df_filtrado.groupby(['MES', 'TIPO 2'])['COSTO S/IVA'].sum().unstack(fill_value=0)
        
        if 'INGRESO' not in df_flujo_mensual.columns:
            df_flujo_mensual['INGRESO'] = 0
        if 'EGRESO' not in df_flujo_mensual.columns:
            df_flujo_mensual['EGRESO'] = 0
            
        df_flujo_mensual['Utilidad Mensual'] = df_flujo_mensual['INGRESO'] - df_flujo_mensual['EGRESO']
        df_flujo_mensual = df_flujo_mensual[['INGRESO', 'EGRESO', 'Utilidad Mensual']]
        
        # Diseño de la tabla en HTML puro para máximo control
        th_props = [
            ('background-color', '#1A365D'),
            ('color', 'white'),
            ('text-align', 'center'),
            ('font-size', '15px'),
            ('font-weight', 'bold'),
            ('padding', '12px')
        ]
        td_props = [
            ('text-align', 'center'),
            ('font-size', '14px'),
            ('padding', '10px'),
            ('border-bottom', '1px solid #e2e8f0')
        ]
        styles = [
            dict(selector="th", props=th_props),
            dict(selector="th.row_heading", props=[('background-color', '#2b5c8f')]), # Color para la columna de Meses
            dict(selector="td", props=td_props),
            dict(selector="table", props=[('margin-left', 'auto'), ('margin-right', 'auto'), ('width', '100%'), ('border-collapse', 'collapse'), ('box-shadow', '0 4px 6px -1px rgba(0,0,0,0.1)')]),
            dict(selector="tr:nth-child(even)", props=[('background-color', '#f8fafc')]),
            dict(selector="tr:hover", props=[('background-color', '#e2e8f0')])
        ]
        
        html_table = (df_flujo_mensual.style
                      .format("${:,.2f}")
                      .set_table_styles(styles)
                      .to_html())
        
        col_tab, col_insights = st.columns([6, 4])
        
        with col_tab:
            st.markdown("<br>" + html_table + "<br>", unsafe_allow_html=True)
            
        with col_insights:
            st.markdown("<br>", unsafe_allow_html=True)
            # Encontrar mejores meses
            mes_mayor_ingreso = df_flujo_mensual['INGRESO'].idxmax() if df_flujo_mensual['INGRESO'].sum() > 0 else 'N/A'
            val_mayor_ingreso = df_flujo_mensual['INGRESO'].max()
            
            mes_mayor_egreso = df_flujo_mensual['EGRESO'].idxmax() if df_flujo_mensual['EGRESO'].sum() > 0 else 'N/A'
            val_mayor_egreso = df_flujo_mensual['EGRESO'].max()
            
            mes_mayor_utilidad = df_flujo_mensual['Utilidad Mensual'].idxmax() if df_flujo_mensual['Utilidad Mensual'].sum() != 0 else 'N/A'
            val_mayor_utilidad = df_flujo_mensual['Utilidad Mensual'].max()
            
            # Segundos lugares
            ingresos_sorted = df_flujo_mensual['INGRESO'].sort_values(ascending=False)
            mes_2do_ingreso = ingresos_sorted.index[1] if len(ingresos_sorted) > 1 and ingresos_sorted.iloc[1] > 0 else 'N/A'
            val_2do_ingreso = ingresos_sorted.iloc[1] if len(ingresos_sorted) > 1 and ingresos_sorted.iloc[1] > 0 else 0
            
            egresos_sorted = df_flujo_mensual['EGRESO'].sort_values(ascending=False)
            mes_2do_egreso = egresos_sorted.index[1] if len(egresos_sorted) > 1 and egresos_sorted.iloc[1] > 0 else 'N/A'
            val_2do_egreso = egresos_sorted.iloc[1] if len(egresos_sorted) > 1 and egresos_sorted.iloc[1] > 0 else 0
            
            utilidad_sorted = df_flujo_mensual['Utilidad Mensual'].sort_values(ascending=False)
            mes_2do_utilidad = utilidad_sorted.index[1] if len(utilidad_sorted) > 1 and utilidad_sorted.iloc[1] != 0 else 'N/A'
            val_2do_utilidad = utilidad_sorted.iloc[1] if len(utilidad_sorted) > 1 and utilidad_sorted.iloc[1] != 0 else 0

            st.markdown(f'''
            <div style="background-color: #f8fafc; padding: 25px; border-radius: 12px; border-left: 5px solid #1A365D; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h4 style="color: #0f172a; margin-top: 0px; font-weight: 800;">🏆 1ros Lugares del Periodo</h4>
                <hr style="border-color: #e2e8f0; margin: 15px 0;">
                <p style="color: #64748b; font-size: 13px; margin-bottom: 2px; text-transform: uppercase;">Mayor Facturación</p>
                <p style="color: #2b5c8f; font-size: 18px; font-weight: bold;">{mes_mayor_ingreso} <span style="font-size: 14px; color: #64748b; font-weight: normal;">(${val_mayor_ingreso:,.0f})</span></p>
                <p style="color: #64748b; font-size: 13px; margin-bottom: 2px; margin-top: 15px; text-transform: uppercase;">Mayor Gasto</p>
                <p style="color: #d62728; font-size: 18px; font-weight: bold;">{mes_mayor_egreso} <span style="font-size: 14px; color: #64748b; font-weight: normal;">(${val_mayor_egreso:,.0f})</span></p>
                <p style="color: #64748b; font-size: 13px; margin-bottom: 2px; margin-top: 15px; text-transform: uppercase;">Más Rentable</p>
                <p style="color: #6DB33F; font-size: 18px; font-weight: bold;">{mes_mayor_utilidad} <span style="font-size: 14px; color: #64748b; font-weight: normal;">(${val_mayor_utilidad:,.0f})</span></p>
            </div>
            
            <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 5px solid #94a3b8; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                <h4 style="color: #475569; margin-top: 0px; font-weight: 800;">🥈 2dos Lugares</h4>
                <hr style="border-color: #f1f5f9; margin: 15px 0;">
                <p style="color: #94a3b8; font-size: 13px; margin-bottom: 2px; text-transform: uppercase;">2da Mayor Facturación</p>
                <p style="color: #4f83cc; font-size: 16px; font-weight: bold;">{mes_2do_ingreso} <span style="font-size: 13px; color: #94a3b8; font-weight: normal;">(${val_2do_ingreso:,.0f})</span></p>
                <p style="color: #94a3b8; font-size: 13px; margin-bottom: 2px; margin-top: 15px; text-transform: uppercase;">2do Mayor Gasto</p>
                <p style="color: #ef4444; font-size: 16px; font-weight: bold;">{mes_2do_egreso} <span style="font-size: 13px; color: #94a3b8; font-weight: normal;">(${val_2do_egreso:,.0f})</span></p>
                <p style="color: #94a3b8; font-size: 13px; margin-bottom: 2px; margin-top: 15px; text-transform: uppercase;">2do Más Rentable</p>
                <p style="color: #8bc34a; font-size: 16px; font-weight: bold;">{mes_2do_utilidad} <span style="font-size: 13px; color: #94a3b8; font-weight: normal;">(${val_2do_utilidad:,.0f})</span></p>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("No hay datos registrados en este periodo.")


with tab_pareto:
    st.markdown("<br><h4 style='color: #1A365D; margin-top: 0px;'>Análisis de Pareto (Regla del 80/20)</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>Identifica rápidamente cuáles son los conceptos que consumen el 80% del presupuesto para priorizar auditorías y recortes.</p>", unsafe_allow_html=True)
    
    if not df_egresos.empty:
        # Calcular Pareto
        df_pareto = df_egresos.groupby('CONCEPTO')['COSTO S/IVA'].sum().reset_index()
        df_pareto = df_pareto.sort_values(by='COSTO S/IVA', ascending=False)
        df_pareto['Porcentaje'] = (df_pareto['COSTO S/IVA'] / df_pareto['COSTO S/IVA'].sum()) * 100
        df_pareto['Acumulado'] = df_pareto['Porcentaje'].cumsum()
        
        # Plotly Pareto
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_pareto.add_trace(
            go.Bar(x=df_pareto['CONCEPTO'], y=df_pareto['COSTO S/IVA'], name="Gasto ($)", marker_color='#2b5c8f'),
            secondary_y=False,
        )
        
        fig_pareto.add_trace(
            go.Scatter(x=df_pareto['CONCEPTO'], y=df_pareto['Acumulado'], name="% Acumulado", mode='lines+markers', line=dict(color='#d62728', width=3)),
            secondary_y=True,
        )
        
        fig_pareto.update_layout(
            hovermode="x unified",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        # Add 80% line
        fig_pareto.add_hline(y=80, line_dash="dot", line_color="#8bc34a", annotation_text="Línea 80%", secondary_y=True)
        
        fig_pareto.update_yaxes(title_text="Gasto Acumulado ($)", secondary_y=False)
        fig_pareto.update_yaxes(title_text="Porcentaje Acumulado (%)", range=[0, 105], secondary_y=True)
        
        st.plotly_chart(fig_pareto, use_container_width=True)

        st.markdown('''
        <div style="margin-top: 25px; font-size: 13px; color: #64748b; text-align: left; background-color: #f1f5f9; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
            <strong style="color: #1A365D; font-size: 14px;">ℹ️ ¿Qué significa este gráfico?</strong><br>
            El <em>Principio de Pareto (Regla del 80/20)</em> establece que, en la mayoría de los proyectos, aproximadamente el 80% del gasto total proviene de apenas un pequeño porcentaje de conceptos.<br><br>
            <strong style="color: #1A365D;">¿Cómo leerlo?</strong><br>
            Busca el punto donde la línea roja cruza la línea punteada verde. Los conceptos (barras azules) que están a la izquierda de ese cruce son tus verdaderos focos de atención financiero. Si el proyecto necesita recortes o auditorías urgentes, es en esos conceptos donde se debe actuar, ya que el resto a la derecha representa gastos menores ("pedacería").
        </div>
        ''', unsafe_allow_html=True)

    else:
        st.info("No hay datos de egresos para generar el Pareto.")

with tab_treemap:
    st.markdown("<br><h4 style='color: #1A365D; margin-top: 0px;'>Mapa de Árbol de Costos (Treemap)</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>Visualización de impacto: El tamaño del bloque representa el peso económico de cada concepto. Útil para ubicar 'fugas' visualmente.</p>", unsafe_allow_html=True)
    
    if not df_egresos.empty:
        import plotly.express as px
        df_tree = df_egresos.groupby('CONCEPTO')['COSTO S/IVA'].sum().reset_index()
        # Add a root node column to group them all
        df_tree['Proyecto'] = "Total Egresos"
        
        fig_tree = px.treemap(df_tree, path=['Proyecto', 'CONCEPTO'], values='COSTO S/IVA',
                              color='COSTO S/IVA', color_continuous_scale='Blues')
        fig_tree.update_layout(margin=dict(t=20, l=20, r=20, b=20))
        st.plotly_chart(fig_tree, use_container_width=True)

        st.markdown('''
        <div style="margin-top: 25px; font-size: 13px; color: #64748b; text-align: left; background-color: #f1f5f9; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
            <strong style="color: #1A365D; font-size: 14px;">ℹ️ ¿Qué significa este gráfico?</strong><br>
            El <em>Mapa de Árbol (Treemap)</em> es una visualización corporativa avanzada que muestra los datos agrupados en forma de rectángulos proporcionales.<br><br>
            <strong style="color: #1A365D;">¿Cómo leerlo?</strong><br>
            El tamaño del bloque y la intensidad del color azul son directamente proporcionales a la cantidad de dinero gastada. Es la herramienta perfecta para la mente directiva porque permite, en literalmente un segundo de vista, dimensionar los volúmenes económicos relativos de cada área sin tener que leer números ni tablas complejas.
        </div>
        ''', unsafe_allow_html=True)

    else:
        st.info("No hay datos de egresos para generar el mapa.")

with tab_forecast:
    st.markdown("<br><h4 style='color: #1A365D; margin-top: 0px;'>Proyección a Cierre de Año (Forecast)</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>Estimación matemática del cierre fiscal basándose en la velocidad histórica (Burn Rate).</p>", unsafe_allow_html=True)
    
    if burn_rate > 0 and not df_trend.empty:
        # Obtener el último mes registrado cronológicamente para saber cuántos faltan en el año
        ultimo_mes_str = str(df_trend['MES'].max())
        try:
            ultimo_mes_num = int(ultimo_mes_str.split('-')[1].split(' ')[0])
        except Exception:
            ultimo_mes_num = len(df_trend)
            
        meses_faltantes = max(0, 12 - ultimo_mes_num)
        gasto_proyectado = total_egresos + (burn_rate * meses_faltantes)
        
        # Proyectar Ingresos también (Run rate de ingresos)
        ingreso_promedio = df_trend['COSTO S/IVA_ING'].mean() if len(df_trend) > 0 else 0
        ingreso_proyectado = total_ingresos + (ingreso_promedio * meses_faltantes)
        
        utilidad_proyectada = ingreso_proyectado - gasto_proyectado
        margen_proyectado = (utilidad_proyectada / ingreso_proyectado * 100) if ingreso_proyectado > 0 else 0
        
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.metric("Gasto Estimado al Cierre", f"${gasto_proyectado:,.0f}", f"${gasto_proyectado - total_egresos:,.0f} faltantes", delta_color="inverse")
        with col_p2:
            st.metric("Ingreso Estimado al Cierre", f"${ingreso_proyectado:,.0f}", f"${ingreso_proyectado - total_ingresos:,.0f} por facturar")
        with col_p3:
            st.metric("Utilidad Estimada al Cierre", f"${utilidad_proyectada:,.0f}", f"{margen_proyectado:.1f}% Margen Global")
            
        st.markdown(f'''
        <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border-left: 5px solid #2b5c8f; margin-top: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <p style="color: #475569; font-size: 15px; margin: 0;"><strong>⚠️ Nota Predictiva:</strong> Faltan {meses_faltantes} meses para el cierre del año. Si la operación mantiene su ritmo actual (Gasto promedio de ${burn_rate:,.0f}/mes), terminarán el año con un margen neto aproximado del <strong>{margen_proyectado:.1f}%</strong>.</p>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.info("No hay suficientes datos históricos para calcular una proyección matemática fiable.")


# --- SECCIÓN CASCADA DE UTILIDAD Y AVANCE ---
st.markdown("<div class='seccion-titulo'>Rentabilidad y Avance del Proyecto</div>", unsafe_allow_html=True)

col_water, col_gauge = st.columns([7, 3])

with col_water:
    names = ["Ingresos"]
    measures = ["relative"]
    values = [total_ingresos]

    if not df_egresos.empty:
        df_conc = df_egresos.groupby('CONCEPTO')['COSTO S/IVA'].sum().sort_values(ascending=False)
        top_5 = df_conc.head(6) 
        otros = df_conc.iloc[6:].sum()
        
        for concepto, monto in top_5.items():
            nombre_corto = concepto[:15] + "..." if len(concepto) > 15 else concepto
            names.append(nombre_corto)
            measures.append("relative")
            values.append(-monto) 
            
        if otros > 0:
            names.append("Otros Gastos")
            measures.append("relative")
            values.append(-otros)
            
    names.append("Utilidad")
    measures.append("total")
    values.append(0)

    fig_waterfall = go.Figure(go.Waterfall(
        orientation = "v",
        measure = measures,
        x = names,
        textposition = "outside",
        text = [f"${v:,.0f}" if m == "relative" else f"${utilidad:,.0f}" for m, v in zip(measures, values)],
        y = values,
        connector = {"line":{"color":"#cbd5e1"}},
        decreasing = {"marker":{"color":"#e2e8f0", "line":{"color":"#475569", "width":2}}}, 
        increasing = {"marker":{"color":"#1A365D"}}, 
        totals = {"marker":{"color":"#6DB33F"}} 
    ))

    fig_waterfall.update_layout(
        title="Construcción de la Utilidad Bruta",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(t=40, b=40),
        height=380
    )
    st.plotly_chart(fig_waterfall, use_container_width=True)

with col_gauge:
    # Gráfica de Medidor (Gauge) para el Avance del Contrato
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = total_ingresos,
        title = {'text': "Cobranza vs Contrato", 'font': {'size': 18, 'color': '#1e293b'}},
        number = {'prefix': "$", 'valueformat': ",.0f", 'font': {'size': 26, 'color': '#0f172a'}},
        gauge = {
            'axis': {'range': [None, presupuesto_total], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
            'bar': {'color': "#1A365D"}, # Azul DDP para el progreso
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [0, presupuesto_total * 0.5], 'color': "#f8fafc"},
                {'range': [presupuesto_total * 0.5, presupuesto_total * 0.8], 'color': "#f1f5f9"},
                {'range': [presupuesto_total * 0.8, presupuesto_total], 'color': "#e2e8f0"}
            ],
            'threshold': {
                'line': {'color': "#6DB33F", 'width': 4}, # Verde DDP para la meta
                'thickness': 0.75,
                'value': presupuesto_total
            }
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=60, b=20, l=20, r=20),
        height=380
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

# --- SECCIÓN DETALLE DE CONCEPTOS ---
st.markdown("<div class='seccion-titulo'>Análisis Detallado de Egresos por Concepto</div>", unsafe_allow_html=True)

if not df_egresos.empty:
    # Obtener los 7 conceptos más caros del periodo para dejarlos, el resto será "OTROS GASTOS"
    top_conceptos = df_egresos.groupby('CONCEPTO')['COSTO S/IVA'].sum().nlargest(7).index.tolist()
    
    df_egresos_agrupado = df_egresos.copy()
    df_egresos_agrupado.loc[~df_egresos_agrupado['CONCEPTO'].isin(top_conceptos), 'CONCEPTO'] = 'OTROS GASTOS'
    
    df_concepto_mes = df_egresos_agrupado.groupby(['MES', 'CONCEPTO'])['COSTO S/IVA'].sum().reset_index()
    
    # Gráfica de Barras Apiladas (100% corporativo)
    # Forzamos que MES sea tratado como texto (categoría) para evitar que Plotly lo intente graficar como números continuos
    df_concepto_mes['MES'] = df_concepto_mes['MES'].astype(str)
    
    fig3 = px.bar(df_concepto_mes, x='MES', y='COSTO S/IVA', color='CONCEPTO',
                  labels={'COSTO S/IVA': 'Gasto Acumulado ($)', 'MES': ''},
                  color_discrete_sequence=px.colors.qualitative.Safe)
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", barmode='stack', legend_title_text="Concepto de Gasto")
    fig3.update_xaxes(type='category')
    st.plotly_chart(fig3, use_container_width=True)
    
# --- SECCIÓN MATRIZ FINANCIERA (TABLA DINÁMICA) ---
st.markdown("<div class='seccion-titulo'>Matriz Financiera (Tabla Dinámica de Datos Duros)</div>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748b;'>Esta tabla consolida los montos exactos por Concepto y Mes, replicando el formato de reporte ejecutivo.</p>", unsafe_allow_html=True)

if not df_egresos.empty:
    # Crear la tabla dinámica
    pivot_df = pd.pivot_table(df_egresos, 
        values='COSTO S/IVA', 
        index='CONCEPTO', 
        columns='MES', 
        aggfunc='sum', 
        fill_value=0
    )
    
    # Agregar columna de 'Total general' (Suma horizontal)
    pivot_df['Total general'] = pivot_df.sum(axis=1)
    
    # Agregar fila de 'Total general' (Suma vertical)
    pivot_df.loc['Total general'] = pivot_df.sum(axis=0)
    
    # Función para dar formato visual corporativo a los Totales
    def estilo_totales(row):
        estilos = []
        es_fila_total = (row.name == 'Total general')
        for col in row.index:
            es_col_total = (col == 'Total general')
            if es_fila_total and es_col_total:
                # Esquina inferior derecha (Gran Total)
                estilos.append('background-color: #1A365D; color: white; font-weight: bold;')
            elif es_fila_total:
                # Fila de Totales (Abajo)
                estilos.append('background-color: #e2e8f0; font-weight: bold; color: #0f172a;')
            elif es_col_total:
                # Columna de Totales (Derecha)
                estilos.append('background-color: #f1f5f9; font-weight: bold; color: #1e293b;')
            else:
                # Celdas normales
                estilos.append('')
        return estilos

    # Aplicar el estilo y formato de moneda
    tabla_estilizada = pivot_df.style.format("${:,.2f}").apply(estilo_totales, axis=1)
    
    # Mostrar la tabla en toda la pantalla
    st.dataframe(
        tabla_estilizada, 
        use_container_width=True,
        height=450
    )
else:
    st.info("No hay datos para generar la tabla dinámica.")

# --- AUDITORÍA SOLO PARA ADMIN ---
if role == "admin":
    st.markdown("<div class='seccion-titulo'>🗄️ Auditoría de Base de Datos (Solo TI)</div>", unsafe_allow_html=True)
    st.dataframe(df_filtrado, use_container_width=True)
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Descargar Reporte Generado (CSV)", data=csv, file_name='reporte_ddp.csv', mime='text/csv')

# --- FOOTER INSTITUCIONAL ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #94a3b8; font-size: 13px;'>
        <strong>Dirección Desarrollo Proyectos</strong><br>
        Dashboard diseñado e implementado por TI DDP (J. Leonardo Velázques Rocha).<br>
        Derechos reservados &copy; 2026. Versión de Sistema v1.34.0
    </div>
    """,
    unsafe_allow_html=True
)
