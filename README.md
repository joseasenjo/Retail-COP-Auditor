--- RETAIL-COP-AUDITOR ---

Calculadora de Coste de Oportunidad en Retail

Versión: 3.2
Autor: José Luis Asenjo
Tecnología: Streamlit, Python, Plotly

PROPÓSITO

Retail-COP-Auditor es una herramienta analítica diseñada para cuantificar, en tiempo real, el coste de oportunidad (COP) que una tienda física incurre cada hora al no alcanzar los estándares de su sector. El modelo se apoya en tres pilares:

Infracobertura comercial (falta de personal en horas punta)

Bajo cross-selling (pocos artículos por ticket)

Bajo up-selling (ticket medio inferior al del benchmark)

La herramienta permite a responsables de tienda, district managers o equipos de operaciones identificar rápidamente dónde se está escapando el margen y tomar decisiones correctivas basadas en datos.

ARQUITECTURA Y FLUJO DE DATOS

La aplicación se ejecuta sobre Streamlit en el lado del cliente. Los datos de entrada se capturan mediante widgets interactivos en la barra lateral; el motor de cálculo procesa estos valores y genera:

Un indicador principal de COP (coste de oportunidad agregado)

Un gráfico de gauge (densidad de pista)

Un diagrama de cascada que descompone el margen potencial en sus componentes

Tres paneles desplegables con el detalle de cada ineficiencia

MODELO DE DATOS

3.1. Parámetros de entrada (sidebar)

Sector: Selector con 7 sectores predefinidos. Define los benchmarks de referencia (conversión, UPT, AOV, tráfico óptimo por vendedor).

Tráfico: Slider 10–200. Visitantes que han entrado en la tienda durante la última hora.

Vendedores: Slider 1–10. Número de empleados en planta durante esa hora.

Transacciones: Slider 0–100. Tickets cobrados en el período.

AOV real: Number input (>=5 €). Ticket medio real (ingreso total / transacciones).

UPT real: Number input (>=1.0). Unidades por ticket real (artículos vendidos / transacciones).

Margen bruto: Slider 10%–90%. Margen bruto sobre ventas (expresado en porcentaje).

3.2. Benchmarks sectoriales (internos)

La aplicación incluye una tabla de referencia con valores típicos para siete sectores. Cada sector define:

conv: tasa de conversión esperada (ventas / visitantes * 100)

upt: unidades por ticket objetivo

aov: ticket medio objetivo (en €)

traf_opt_empleado: número de clientes que un vendedor puede atender óptimamente por hora (ratio de capacidad)

Los valores han sido obtenidos de estudios de productividad en retail y pueden ser ajustados por el administrador de la aplicación.

LÓGICA DE CÁLCULO

4.1. Variables derivadas

A partir de los inputs se calculan:

Conversión real = transacciones / tráfico * 100

Ratio de densidad = tráfico / vendedores (clientes por vendedor)

4.2. Coste de oportunidad por tráfico perdido (infracobertura)

Objetivo: Estimar el margen que se deja de capturar cuando hay más clientes de los que el equipo puede atender adecuadamente.

Fórmula:

Si ratio_actual > traf_opt_empleado:

capacidad_optima = vendedores * traf_opt_empleado

trafico_exceso = tráfico - capacidad_optima

clientes_perdidos = trafico_exceso * (conv_benchmark / 100)

COP_tráfico = clientes_perdidos * aov_benchmark * margen

Interpretación: Se asume que los clientes que exceden la capacidad óptima no son atendidos y, por tanto, no compran. El número de compradores perdidos se estima aplicando la tasa de conversión del benchmark.

4.3. Coste de oportunidad por bajo cross-selling (UPT)

Objetivo: Medir la pérdida por no vender suficientes artículos por ticket.

Fórmula:

precio_medio_art_real = AOV_real / UPT_real (si UPT_real > 0)

gap_upt = max(0, UPT_benchmark - UPT_real)

COP_cross = transacciones * gap_upt * precio_medio_art_real * margen

Interpretación: Cada ticket que lleva menos artículos del estándar del sector deja de ingresar el precio medio de un artículo adicional. Se multiplica por el margen para obtener el impacto en beneficio.

4.4. Coste de oportunidad por bajo up-selling (ticket medio)

Objetivo: Cuantificar la pérdida cuando el precio medio de los artículos vendidos es inferior al del benchmark.

Fórmula:

precio_medio_art_bm = AOV_benchmark / UPT_benchmark

gap_precio = max(0, precio_medio_art_bm - precio_medio_art_real)

unidades_totales = transacciones * UPT_real

COP_up = unidades_totales * gap_precio * margen

Interpretación: Se compara el precio medio por artículo real con el del sector. La diferencia, multiplicada por el número total de artículos vendidos, representa el margen perdido por vender artículos de menor valor.

4.5. Agregación y métricas finales

COP total = COP_tráfico + COP_cross + COP_up

Margen real capturado = (transacciones * AOV_real) * margen

Margen potencial ideal = Margen real capturado + COP_total

El porcentaje de beneficio perdido se calcula como:
(COP_total / Margen_potencial_ideal) * 100

VISUALIZACIONES

5.1. Gauge (densidad de pista)
Un velocímetro que muestra el ratio actual de clientes por vendedor frente al valor óptimo del sector. El color cambia a rojo cuando se supera el umbral, indicando colapso de atención.

5.2. Diagrama de cascada (Waterfall)
Descompone el margen ideal en los tres conceptos de pérdida, mostrando de forma gráfica cómo se erosiona el beneficio hasta llegar al margen real capturado. Las barras rojas indican pérdidas; la barra azul final representa el margen real.

5.3. Paneles de diagnóstico
Tres secciones expandibles que detallan cada componente del COP con mensajes interpretativos adaptados al contexto.

INTERPRETACIÓN DE RESULTADOS

Un COP elevado indica que la tienda está dejando de ganar una cantidad significativa de margen bruto cada hora. Las causas pueden ser:

Falta de personal en horas de alta afluencia (infracobertura).

Falta de técnicas de venta cruzada (no se ofrecen complementos).

Falta de up-selling (se venden artículos de gama baja cuando el cliente podría comprar productos de mayor valor).

El desglose permite priorizar acciones correctivas:

Si el principal componente es el tráfico perdido -> reforzar plantilla en los turnos críticos.

Si domina el cross-selling -> formación en venta adicional y disposición de productos en mostrador.

Si el up-selling es el problema -> revisar surtido y técnicas de recomendación.

LIMITACIONES Y CONSIDERACIONES

Los benchmarks son orientativos y deben ser calibrados para cada cadena con datos históricos propios.

El modelo asume que el comportamiento de conversión de los clientes no atendidos es igual al promedio del sector.

El coste de oportunidad se calcula sobre el margen bruto, no sobre el margen neto (no incluye costes fijos ni operativos).

La herramienta está diseñada para análisis por hora; para extrapolar a día, mes o año se debe multiplicar por el número de horas operativas.

TECNOLOGÍA Y DEPENDENCIAS

Python 3.9+

Streamlit – interfaz web interactiva

Plotly – gráficos de gauge y cascada

Pandas – manipulación de datos (no crítica)

Para instalar dependencias:
pip install streamlit plotly pandas

Para ejecutar la aplicación:
streamlit run app.py

MEJORAS FUTURAS

Conexión a API de TPV para ingesta automática de datos.

Histórico de sesiones y almacenamiento de resultados.

Generación de informes PDF descargables.

Ajuste dinámico de benchmarks mediante machine learning.

Soporte para múltiples tiendas y comparativas.

CRÉDITOS

Desarrollado por José Luis Asenjo
 https://www.linkedin.com/in/joseluisasenjo

