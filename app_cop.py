import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Configuración inicial de la página
st.set_page_config(
    page_title="Retail COP Calculator | Hemorragia de Margen",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para darle un toque premium y oscuro
st.markdown("""
<style>
    .big-font { font-size: 24px !important; font-weight: bold; color: #f8fafc; }
    .alert-red { color: #ef4444; font-size: 42px; font-weight: 900; line-height: 1.1; }
    .metric-box { background-color: #1e293b; padding: 20px; border-radius: 10px; border: 1px solid #334155; }
    .cta-box { background: linear-gradient(135deg, #0f1423 0%, #1e1b4b 100%); padding: 30px; border-radius: 15px; border: 1px solid #4f46e5; text-align: center; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

BENCHMARK_SECTORES = {
    "textil":        {"nombre": "Moda, Calzado & Complementos",    "conv": 22.0, "upt": 1.85, "aov": 38.00,  "traf_opt_empleado": 15},
    "gran_consumo":  {"nombre": "Supermercados & Gran Consumo",    "conv": 88.0, "upt": 4.50, "aov": 19.50,  "traf_opt_empleado": 25},
    "salud_belleza": {"nombre": "Salud, Belleza & Parafarmacia",   "conv": 35.0, "upt": 2.40, "aov": 24.00,  "traf_opt_empleado": 18},
    "tecnologia":    {"nombre": "Tecnología & Telecomunicaciones", "conv": 14.0, "upt": 1.30, "aov": 145.00, "traf_opt_empleado": 8},
    "hogar_brico":   {"nombre": "Bricolaje, Mueble & Hogar",       "conv": 48.0, "upt": 2.10, "aov": 65.00,  "traf_opt_empleado": 12},
    "lujo_joyas":    {"nombre": "Lujo, Joyería & Premium",         "conv": 4.5,  "upt": 1.10, "aov": 450.00, "traf_opt_empleado": 4},
    "deportes":      {"nombre": "Deporte & Outdoor",               "conv": 26.0, "upt": 2.10, "aov": 42.00,  "traf_opt_empleado": 16},
}

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3593/3593463.png", width=60)
st.sidebar.title("Simulador de Pista")
st.sidebar.markdown("Ajusta los parámetros para simular **1 HORA** de actividad en tu tienda.")

# Selector de Sector
sector_keys = list(BENCHMARK_SECTORES.keys())
sector_names = [BENCHMARK_SECTORES[k]["nombre"] for k in sector_keys]
selected_name = st.sidebar.selectbox("1. Elige tu sector comercial:", sector_names)
sector_key = sector_keys[sector_names.index(selected_name)]
bm = BENCHMARK_SECTORES[sector_key]

st.sidebar.markdown("---")

# Inputs Interactivos
trafico = st.sidebar.slider("2. Tráfico (visitantes esta hora):", min_value=10, max_value=200, value=45, step=5)
personal = st.sidebar.slider("3. Vendedores en tienda:", min_value=1, max_value=10, value=2, step=1)
transacciones = st.sidebar.slider("4. Transacciones (tickets cobrados):", min_value=0, max_value=100, value=8, step=1)
aov_real = st.sidebar.number_input("5. Ticket Medio actual (AOV) en €:", min_value=5.0, max_value=1000.0, value=bm["aov"]*0.85, step=1.0)
upt_real = st.sidebar.number_input("6. Venta cruzada actual (UPT):", min_value=1.0, max_value=10.0, value=max(1.0, bm["upt"]-0.5), step=0.1)
margen_pct = st.sidebar.slider("7. Margen Bruto de tu producto (%):", min_value=10, max_value=90, value=55, step=5)

margen = margen_pct / 100.0

# Variables de la hora
conv_real = (transacciones / trafico * 100) if trafico > 0 else 0
ratio_actual = trafico / personal if personal > 0 else trafico

# 1. COP de Tráfico (Infracobertura)
clientes_perdidos = 0
if ratio_actual > bm["traf_opt_empleado"]:
    # Exceso de tráfico que los vendedores no pudieron atender
    capacidad_optima = personal * bm["traf_opt_empleado"]
    trafico_exceso = trafico - capacidad_optima
    # Asumimos que de ese exceso habríamos convertido según el benchmark
    clientes_perdidos = trafico_exceso * (bm["conv"] / 100)

cop_trafico = max(0, clientes_perdidos * bm["aov"] * margen)

# 2. COP de Cross-Selling (UPT)
precio_medio_art_real = aov_real / upt_real if upt_real > 0 else 0
gap_upt = max(0, bm["upt"] - upt_real)
cop_cross = transacciones * gap_upt * precio_medio_art_real * margen

# 3. COP de Up-Selling (AOV)
precio_medio_art_bm = bm["aov"] / bm["upt"] if bm["upt"] > 0 else 0
gap_precio = max(0, precio_medio_art_bm - precio_medio_art_real)
unidades_totales = transacciones * upt_real
cop_up = unidades_totales * gap_precio * margen

# Totales
cop_total = cop_trafico + cop_cross + cop_up

# Ingreso y Margen Real
ingreso_real = transacciones * aov_real
margen_real_rescatado = ingreso_real * margen
margen_potencial_ideal = margen_real_rescatado + cop_total

st.title("🚨 Calculadora de Hemorragia de Margen (COP)")
st.markdown(f"**Análisis de Ineficiencia en Tiempo Real** | Sector: `{bm['nombre']}`")

st.markdown("""
Esta herramienta te muestra el dinero que tu tienda **pierde cada hora** al no alcanzar los estándares de tu sector por falta de personal en horas punta, o carencias en técnicas de cierre y venta cruzada.
""")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; font-size:14px; font-weight:bold; margin-bottom:0px;'>COSTE DE OPORTUNIDAD (1 HORA)</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='alert-red'>-{cop_total:,.2f} €</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#cbd5e1; font-size:13px;'>Margen neto esfumado en solo 60 minutos.</p>", unsafe_allow_html=True)
    
    impacto_pct = (cop_total / margen_potencial_ideal * 100) if margen_potencial_ideal > 0 else 0
    st.progress(min(1.0, impacto_pct/100))
    st.markdown(f"<p style='color:#f59e0b; font-size:12px; font-weight:bold;'>El {impacto_pct:.1f}% de tu beneficio potencial se ha perdido.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("")
    
    # Gráfico de Gauge (Termómetro de Saturación)
    estado_saturacion = "Óptimo" if ratio_actual <= bm["traf_opt_empleado"] else "Colapsado"
    color_gauge = "green" if ratio_actual <= bm["traf_opt_empleado"] else "red"
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = ratio_actual,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Densidad de Pista (Clientes / Vendedor)", 'font': {'size': 14, 'color': '#cbd5e1'}},
        gauge = {
            'axis': {'range': [0, bm["traf_opt_empleado"] * 2], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color_gauge},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, bm["traf_opt_empleado"]], 'color': "rgba(16, 185, 129, 0.2)"},
                {'range': [bm["traf_opt_empleado"], bm["traf_opt_empleado"]*2], 'color': "rgba(239, 68, 68, 0.2)"}],
            'threshold': {'line': {'color': "white", 'width': 3}, 'thickness': 0.75, 'value': bm["traf_opt_empleado"]}
        }
    ))
    fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#f8fafc"})
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    st.markdown("### 💸 El viaje de tu Margen Bruto")
    st.markdown("Observa cómo las ineficiencias erosionan tu beneficio ideal paso a paso.")
    
    fig_waterfall = go.Figure(go.Waterfall(
        name = "Margen", orientation = "v",
        measure = ["relative", "relative", "relative", "relative", "total"],
        x = ["Margen Ideal", "Infracobertura<br>(Falta Personal)", "Cross-Selling<br>(Pocos Artículos)", "Up-Selling<br>(Ticket Bajo)", "Margen Real<br>Capturado"],
        textposition = "outside",
        text = [f"{margen_potencial_ideal:,.0f}€", f"-{cop_trafico:,.0f}€", f"-{cop_cross:,.0f}€", f"-{cop_up:,.0f}€", f"{margen_real_rescatado:,.0f}€"],
        y = [margen_potencial_ideal, -cop_trafico, -cop_cross, -cop_up, margen_real_rescatado],
        connector = {"line":{"color":"#334155"}},
        decreasing = {"marker":{"color":"#ef4444"}},
        increasing = {"marker":{"color":"#10b981"}},
        totals = {"marker":{"color":"#3b82f6"}}
    ))
    fig_waterfall.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        showlegend=False
    )
    st.plotly_chart(fig_waterfall, use_container_width=True)

st.markdown("---")
st.markdown("### 🔬 Desglose del Diagnóstico")
c1, c2, c3 = st.columns(3)

with c1:
    with st.expander("🏃 Tráfico Perdido", expanded=True):
        st.write(f"**COP: -{cop_trafico:,.2f} €**")
        if cop_trafico > 0:
            st.write(f"El ratio actual es de **{ratio_actual:.1f}** clientes por empleado, superando el límite del sector ({bm['traf_opt_empleado']}). Se estima que **{clientes_perdidos:.1f} clientes** se fueron sin comprar por falta de atención.")
        else:
            st.write("✅ La tienda está bien dimensionada para el tráfico actual.")

with c2:
    with st.expander("🧩 Cross-Selling", expanded=True):
        st.write(f"**COP: -{cop_cross:,.2f} €**")
        if gap_upt > 0:
            st.write(f"Tu equipo está vendiendo **{upt_real:.2f}** artículos por ticket, cuando el estándar del sector es **{bm['upt']}**. Faltó ofrecer artículos complementarios en el mostrador.")
        else:
            st.write("✅ Excelente ratio de artículos por ticket.")

with c3:
    with st.expander("⬆️ Up-Selling", expanded=True):
        st.write(f"**COP: -{cop_up:,.2f} €**")
        if gap_precio > 0:
            st.write(f"El valor medio de tus artículos vendidos es más bajo de lo esperado. Tu AOV actual es de **{aov_real:.2f}€** vs **{bm['aov']:.2f}€** (benchmark). Se están vendiendo artículos baratos en lugar de gama premium.")
        else:
            st.write("✅ Cierre de ventas de alto valor en línea con el sector.")

# CALL TO ACTION (Lead Magnet para LinkedIn)
st.markdown(
    """
    <div class="cta-box">
        <h2 style="color:white; margin-bottom:10px;">¿Esto es solo una hora. ¿Cuánto estás perdiendo al mes?</h2>
        <p style="color:#94a3b8; font-size:16px;">
            El <strong>Retail Shift Auditor v3.2</strong> es un motor analítico avanzado que audita tu TPV de forma masiva, cruza datos con inteligencia de sector e identifica carencias (Skill/Will) empleado a empleado.
        </p>
        <a href="https://www.linkedin.com/in/joseluisasenjo" target="_blank" style="display:inline-block; background-color:#3b82f6; color:white; padding:12px 25px; border-radius:8px; text-decoration:none; font-weight:bold; margin-top:15px; border:1px solid #60a5fa;">
            Conectar en LinkedIn para solicitar Auditoría
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
