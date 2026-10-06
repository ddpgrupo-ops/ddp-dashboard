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
    header {visibility: hidden;}
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
    
    /* Ajuste rudo para forzar que los números y títulos nunca se corten con "..." */
    [data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
    }
    [data-testid="stMetricValue"] > div {
        overflow: visible !important;
        white-space: normal !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
    }
    [data-testid="stMetricLabel"] > div > div > p {
        overflow: visible !important;
        white-space: normal !important;
        line-height: 1.1 !important;
    }
</style>
""", unsafe_allow_html=True)


# --- 1. SISTEMA DE SEGURIDAD / LOGIN ---
USERS = {
    "jorge.delamora@ddp.mx": {"password": "DDP0025", "role": "viewer", "name": "Jorge de la Mora"},
    "leonardo.velazquez@ddp.mx": {"password": "DDP2505", "role": "admin", "name": "Leonardo Velázquez"}
}

def check_password():
    def password_entered():
        user = st.session_state["username"]
        pwd = st.session_state["password"]
        
        if user in USERS and USERS[user]["password"] == pwd:
            st.session_state["password_correct"] = True
            st.session_state["role"] = USERS[user]["role"]
            st.session_state["name"] = USERS[user]["name"]
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
                st.text_input("Correo Institucional", key="username", placeholder="ejemplo@ddp.mx")
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
                st.text_input("Correo Institucional", key="username")
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
        if "CSV_URL" in st.secrets:
            try:
                df = pd.read_csv(st.secrets["CSV_URL"])
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
    "HOSPITAL": 32371388.04,
    "ESTANCIA": 1490474.12,
    "PITAHAYA": 35912747.18
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
st.markdown(f"<p style='color: #64748b; font-size: 16px;'>{texto_periodo}{texto_mes} | Visualizando como: <strong>{user_name}</strong></p>", unsafe_allow_html=True)
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
        df_conc_egreso = df_conc_egreso.sort_values(by='COSTO S/IVA', ascending=False).head(8) # Top 8 para limpieza
        
        # Paleta corporativa (Azules, grises, verdes)
        colores = ['#1A365D', '#2b5c8f', '#4f83cc', '#6DB33F', '#8bc34a', '#cddc39', '#94a3b8', '#cbd5e1']
        
        fig2 = px.pie(df_conc_egreso, values='COSTO S/IVA', names='CONCEPTO', hole=0.6,
                      color_discrete_sequence=colores)
        fig2.update_layout(title="Estructura de Costos (Top 8)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        fig2.update_traces(textposition='outside', textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True)

# Pestaña deslizante (expander) con los datos duros mensuales
with st.expander("📊 Ver tabla numérica: Ingresos vs Egresos por Mes"):
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
            dict(selector="table", props=[('margin-left', 'auto'), ('margin-right', 'auto'), ('width', '60%'), ('border-collapse', 'collapse'), ('box-shadow', '0 4px 6px -1px rgba(0,0,0,0.1)')]),
            dict(selector="tr:nth-child(even)", props=[('background-color', '#f8fafc')]),
            dict(selector="tr:hover", props=[('background-color', '#e2e8f0')])
        ]
        
        html_table = (df_flujo_mensual.style
                      .format("${:,.2f}")
                      .set_table_styles(styles)
                      .to_html())
        
        st.markdown("<br>" + html_table + "<br>", unsafe_allow_html=True)
    else:
        st.info("No hay datos registrados en este periodo.")

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
    df_concepto_mes = df_egresos.groupby(['MES', 'CONCEPTO'])['COSTO S/IVA'].sum().reset_index()
    
    # Gráfica de Barras Apiladas (100% corporativo)
    fig3 = px.bar(df_concepto_mes, x='MES', y='COSTO S/IVA', color='CONCEPTO',
                  labels={'COSTO S/IVA': 'Gasto Acumulado ($)', 'MES': ''},
                  color_discrete_sequence=px.colors.qualitative.Safe)
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", barmode='stack', legend_title_text="Concepto de Gasto")
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
    
    # Mostrar la tabla con formato de moneda en toda la pantalla
    st.dataframe(
        pivot_df.style.format("${:,.2f}"), 
        use_container_width=True,
        height=400
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
        Dashboard diseñado e implementado por TI DDP (Leonardo Velázquez).<br>
        Derechos reservados &copy; 2026. Versión de Sistema v1.13.0
    </div>
    """,
    unsafe_allow_html=True
)
