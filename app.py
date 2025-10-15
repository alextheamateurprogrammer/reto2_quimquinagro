# app.py  — Tablero contable QuimQuinAgro (versión simple estilo clase)

import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import altair as alt

st.title("📊 QuimQuinAgro – Tablero Contable")


# Conexión a la base de datos (ruta local)

conn = sqlite3.connect("contabilidad.db")


# Q1. Caja mensual (ingresos vs. egresos por mes)

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

st.markdown("**Conclusión (Q1):** Entre enero y abril de 2025 la caja muestra meses positivos: los ingresos superan a los egresos, con picos en enero y febrero. Marzo y mayo registran ingresos bajos y sin egresos, mientras que septiembre aparece como el único mes neto negativo (0 ingresos vs 90k de egresos). En conjunto, el flujo es sólido a inicios de año y se debilita hacia mediados, con un desbalance puntual en septiembre.")



# Q2. Top 10 egresos (por detalle)

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

st.markdown("**Conclusión (Q2):** Los mayores egresos corresponden a recibo de caja 169 y recibo de caja 164, ambos asociados a Yamile Vera, con un valor de 500.000 cada uno. Otros desembolsos importantes son los de Brigitte Caterine Herrera (300.000) y María Julieth Madrid (100.000). Los demás registros presentan montos menores a 100.000, lo que indica que un pequeño grupo de pagos concentra la mayor parte de las salidas totales, reflejando una fuerte concentración en determinados beneficiarios.")



# Q3. Ingresos por socio (CXC) 

st.header("Q3. Ingresos por socio (CXC)")

st.info("La tabla **cxc2020** no tiene columna de fecha, este análisis usa todos los registros.")

# Selectbox con socios (+ opción 'Todos')
socios = pd.read_sql_query("SELECT DISTINCT socio FROM cxc2020 ORDER BY socio;", conn)["socio"].tolist()
socios_opc = ["Todos"] + socios
socio_sel = st.selectbox("Socio", socios_opc)

# Consulta fija:
# Si “Todos”: ranking de ingresos por socio
# Si un socio específico: total de ese socio
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

st.markdown("**Conclusión (Q3):** Los resultados muestran que German Lopez (395.000) y Marcial Mutis (265.000) son los principales contribuyentes, seguidos por Omar Borja (210.000). Los demás socios presentan ingresos menores pero constantes, alrededor de 120.000, mientras que algunos como Amanda Murillas y Luis Ernesto Granada registran montos mínimos. Esto evidencia una alta concentración de ingresos en pocos miembros clave, donde los tres primeros representan la mayor parte del total.")



# Q4. Total de Ingresos y Egresos (Balance General)

st.header("Q4. Total de Ingresos y Egresos (Balance General)")

sql_q4 = """
SELECT
  SUM(abono) AS total_ingresos,
  SUM(prestamo) AS total_egresos
FROM caja2025;
"""

df_q4 = pd.read_sql_query(sql_q4, conn)

st.subheader("Resumen general de caja")
st.dataframe(df_q4, use_container_width=True)

# Gráfico de barras comparando ingresos y egresos totales
if not df_q4.empty:
    df_q4_melt = df_q4.melt(var_name="Tipo", value_name="Valor")
    chart_q4 = (
        alt.Chart(df_q4_melt)
          .mark_bar()
          .encode(
              x=alt.X("Valor:Q", title="Valor total"),
              y=alt.Y("Tipo:N", title="Categoría", sort="-x"),
              color=alt.Color("Tipo:N", title="")
          )
          .properties(height=200)
    )
    st.altair_chart(chart_q4, use_container_width=True)

st.markdown("**Conclusión (Q4):** Los ingresos acumulados superan los egresos totales, indicando un balance de caja positivo durante el periodo analizado.")


# Q4. Total de Ingresos, Egresos y Balance Neto

st.header("Q4. Total de Ingresos, Egresos y Balance Neto")

sql_q4 = """
SELECT
  SUM(abono) AS total_ingresos,
  SUM(prestamo) AS total_egresos,
  SUM(abono) - SUM(prestamo) AS balance_neto
FROM caja2025;
"""

df_q4 = pd.read_sql_query(sql_q4, conn)

st.subheader("Resumen general de caja")
st.dataframe(df_q4, use_container_width=True)

# Gráfico de barras
if not df_q4.empty:
    df_q4_melt = df_q4.melt(var_name="Categoría", value_name="Valor")
    chart_q4 = (
        alt.Chart(df_q4_melt)
        .mark_bar()
        .encode(
            x=alt.X("Valor:Q", title="Valor total"),
            y=alt.Y("Categoría:N", sort="-x", title=""),
            color=alt.Color("Categoría:N", title="")
        )
        .properties(height=250)
    )
    st.altair_chart(chart_q4, use_container_width=True)

# Conclusión en español
balance_neto = float(df_q4["balance_neto"].iloc[0]) if not df_q4.empty else 0
if balance_neto > 0:
    st.markdown(
        f"**Conclusión (Q4):** Los ingresos totales superan los egresos, con un **balance neto positivo de {balance_neto:,.0f}**. "
        "Esto refleja una gestión financiera eficiente y un flujo de caja saludable."
    )
else:
    st.markdown(
        f"**Conclusión (Q4):** Los egresos totales superan los ingresos, con un **balance neto negativo de {abs(balance_neto):,.0f}**. "
        "Esto sugiere la necesidad de revisar los gastos operativos durante el periodo analizado."
    )



# Cerrar conexión

conn.close()
