# app.py  — Tablero contable QuimQuinAgro (versión simple estilo clase)

import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import altair as alt

st.title("📊 QuimQuinAgro – Tablero contable (SQL fijas)")

# ------------------------------------------------------------
# Conexión a la base de datos (ruta local)
# ------------------------------------------------------------
conn = sqlite3.connect("contabilidad.db")

# ======================================================================
# Q1. Caja mensual (ingresos vs. egresos por mes)  ← SQL PREDEFINIDA
# ======================================================================
st.header("Q1. Caja mensual (Ingresos vs. Egresos por mes)")

# Formulario sencillo: fechas de inicio y fin
c1, c2 = st.columns(2)
with c1:
    f_ini_q1 = st.date_input("Fecha inicio", value=date(2025, 1, 1))
with c2:
    f_fin_q1 = st.date_input("Fecha fin", value=date.today())

# Consulta fija (solo a caja2025)
# Nota: strftime('%Y-%m', fecha) agrupa por mes (AAAA-MM)
sql_q1 = """
SELECT
  strftime('%Y-%m', fecha) AS mes,
  SUM(abono)    AS ingresos,
  SUM(prestamo) AS egresos
FROM caja2025
WHERE date(fecha) BETWEEN date(?) AND date(?)
GROUP BY mes
ORDER BY mes;
"""

df_q1 = pd.read_sql_query(sql_q1, conn, params=[f_ini_q1.isoformat(), f_fin_q1.isoformat()])

st.subheader("Resultado por mes")
st.dataframe(df_q1, use_container_width=True)

# Gráfico de barras agrupadas (ingresos vs egresos)
if not df_q1.empty:
    chart_q1 = (
        alt.Chart(df_q1)
          .transform_fold(["ingresos", "egresos"], as_=["Tipo", "Valor"])
          .mark_bar()
          .encode(
              x=alt.X("mes:N", title="Mes"),
              y=alt.Y("Valor:Q", title="Valor"),
              color=alt.Color("Tipo:N", title=""),
              column=alt.Column("Tipo:N", title="")
          )
          .properties(height=320)
          .resolve_scale(y="independent")
    )
    st.altair_chart(chart_q1, use_container_width=True)

st.markdown("**Conclusión (Q1):** escribe aquí 2–3 líneas con la lectura del flujo de caja mensual.")


# ======================================================================
# Q2. Top 10 egresos (por detalle)  ← SQL PREDEFINIDA
# ======================================================================
st.header("Q2. Top 10 egresos (Caja)")

# Formulario: fechas de inicio y fin
c1, c2 = st.columns(2)
with c1:
    f_ini_q2 = st.date_input("Fecha inicio (Q2)", value=date(2025, 1, 1), key="q2_ini")
with c2:
    f_fin_q2 = st.date_input("Fecha fin (Q2)", value=date.today(), key="q2_fin")

# Consulta fija (top 10 por detalle) sobre caja2025
sql_q2 = """
SELECT
  detalle AS item,
  SUM(prestamo) AS egresos
FROM caja2025
WHERE date(fecha) BETWEEN date(?) AND date(?)
GROUP BY detalle
ORDER BY egresos DESC
LIMIT 10;
"""

df_q2 = pd.read_sql_query(sql_q2, conn, params=[f_ini_q2.isoformat(), f_fin_q2.isoformat()])

st.subheader("Top 10 egresos por detalle")
st.dataframe(df_q2, use_container_width=True)

# Barras horizontales descendentes
if not df_q2.empty:
    chart_q2 = (
        alt.Chart(df_q2)
          .mark_bar()
          .encode(
              x=alt.X("egresos:Q", title="Egresos"),
              y=alt.Y("item:N", sort="-x", title="Detalle")
          )
          .properties(height=360)
    )
    st.altair_chart(chart_q2, use_container_width=True)

st.markdown("**Conclusión (Q2):** comenta brevemente en qué conceptos se concentran los egresos.")


# ======================================================================
# Q3. Ingresos por socio (CXC)  ← SQL PREDEFINIDA
# ======================================================================
st.header("Q3. Ingresos por socio (CXC)")

# NOTA: la tabla cxc2020 no tiene fecha; el filtro de fechas no aplica.
st.info("La tabla **cxc2020** no tiene columna de fecha; este análisis usa todos los registros.")

# Selectbox con socios (+ opción 'Todos')
socios = pd.read_sql_query("SELECT DISTINCT socio FROM cxc2020 ORDER BY socio;", conn)["socio"].tolist()
socios_opc = ["Todos"] + socios
socio_sel = st.selectbox("Socio", socios_opc)

# Consulta fija:
# - Si “Todos”: ranking de ingresos por socio
# - Si un socio específico: total de ese socio
if socio_sel == "Todos":
    sql_q3 = """
    SELECT socio, SUM(valor) AS ingresos
    FROM cxc2020
    GROUP BY socio
    ORDER BY ingresos DESC;
    """
    df_q3 = pd.read_sql_query(sql_q3, conn)
    st.subheader("Top ingresos por socio (Todos)")
    st.dataframe(df_q3, use_container_width=True)

    if not df_q3.empty:
        chart_q3 = (
            alt.Chart(df_q3.head(12))  # mostrar top 12 para que quepa cómodo
              .mark_bar()
              .encode(
                  x=alt.X("ingresos:Q", title="Ingresos"),
                  y=alt.Y("socio:N", sort="-x", title="Socio")
              )
              .properties(height=360)
        )
        st.altair_chart(chart_q3, use_container_width=True)

else:
    sql_q3_socio = """
    SELECT socio, SUM(valor) AS ingresos
    FROM cxc2020
    WHERE socio = ?
    GROUP BY socio;
    """
    df_q3 = pd.read_sql_query(sql_q3_socio, conn, params=[socio_sel])
    st.subheader(f"Ingresos del socio: {socio_sel}")
    st.dataframe(df_q3, use_container_width=True)

    if not df_q3.empty:
        chart_q3s = (
            alt.Chart(df_q3)
              .mark_bar()
              .encode(
                  x=alt.X("ingresos:Q", title="Ingresos"),
                  y=alt.Y("socio:N", title="Socio")
              )
              .properties(height=160)
        )
        st.altair_chart(chart_q3s, use_container_width=True)

st.markdown("**Conclusión (Q3):** describe la concentración de ingresos por socio y posibles dependencias.")

# ------------------------------------------------------------
# Cerrar conexión
# ------------------------------------------------------------
conn.close()
