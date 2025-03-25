
# percentil_por_pais_app.py

import pandas as pd
from scipy.stats import percentileofscore
import streamlit as st
import os
import matplotlib.pyplot as plt
import seaborn as sns

########
#HOPERMAS DATA
########

# Import Hopermas database: cut-off 12_24
calculadora_pbls_code.py
input_dir="https://github.com/rafaelabastidas/Calculadora-PBLs/raw/main/"
file_name =os.path.join(input_dir, "Hopermas_filtered.csv")
data= pd.read_csv(file_name)

# Filter rows where modality_cd is either "PBP" or "DDP"
data = data[data["lending_instrmnt_cd"].isin(["PBL"])].reset_index(drop=True)

#Filter INACTIVE
data = data[data["sts_cd"]!="INACTIVE"]

#Keep only COMPLETED (approval)
data=data[data["apprvl_dt_sts"]=="COMPLETED"]

#Check the different operation types: LON, GRF, GUA
data["oper_typ_cd"].value_counts()

#Keep from 2019 to have the period 2019-2024
#data=data[data["apprvl_dt_yr"]>=2019]

#To millions
data["orig_apprvd_useq_amnt_m"]=data["orig_apprvd_useq_amnt"]/1000000



################################
# Interfaz
################################


# 👉 Asegúrate de cargar tu DataFrame `data` antes de este punto.
# Por ejemplo: data = pd.read_csv("tus_datos.csv")

st.title("Calculadora de Percentiles para Programación de PBLs")

# Filtro por país con opción 'Todos'
paises_disponibles = ['Todos'] + sorted(data['cntry_benfit'].dropna().unique().tolist())
pais_seleccionado = st.selectbox("Selecciona un país (o 'Todos' para no filtrar)", paises_disponibles)

# Filtro por sector con opción 'Todos'
sectores_disponibles = ['Todos'] + sorted(data['sector_cd'].dropna().unique().tolist())
sector_seleccionado = st.selectbox("Selecciona un sector (o 'Todos' para no filtrar)", sectores_disponibles)

# Filtro por rango de año de aprobación
anio_min = int(data['apprvl_dt_yr'].min())
anio_max = int(data['apprvl_dt_yr'].max())
rango_anios = st.slider("Selecciona el rango de años de aprobación", min_value=anio_min, max_value=anio_max, value=(anio_min, anio_max))

# Filtrar base según país, sector y años
df_filtrado = data.copy()
if pais_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['cntry_benfit'] == pais_seleccionado]
if sector_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['sector_cd'] == sector_seleccionado]
df_filtrado = df_filtrado[(df_filtrado['apprvl_dt_yr'] >= rango_anios[0]) & (df_filtrado['apprvl_dt_yr'] <= rango_anios[1])]

# Input del usuario
valor_input = st.number_input("¿Cuál va a ser el monto esperado (en USD millones) del PBL programado?", value=300)

# Cálculo del percentil
if not df_filtrado.empty:
    percentil = percentileofscore(df_filtrado['orig_apprvd_useq_amnt_m'], valor_input, kind='rank')

    texto_pais = f"en {pais_seleccionado}" if pais_seleccionado != 'Todos' else "en todos los países"
    texto_sector = f"del sector {sector_seleccionado}" if sector_seleccionado != 'Todos' else "de todos los sectores"
    texto_anios = f"entre {rango_anios[0]} y {rango_anios[1]}"

    st.markdown(
        f"El monto del PBL programado (**{valor_input}** USD millones) está por encima del **{percentil:.2f}%** de los PBLs {texto_pais}, {texto_sector}, {texto_anios}.")

    # Histograma de distribución
    st.subheader("Visualización del valor frente a la distribución (Histograma)")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df_filtrado['orig_apprvd_useq_amnt_m'], bins=30, kde=False, color='skyblue')
    ax.axvline(valor_input, color='red', linestyle='--', linewidth=2, label=f'Monto esperado: {valor_input} (Percentil {percentil:.2f}%)')
    ax.text(valor_input, ax.get_ylim()[1]*0.9, f'{percentil:.2f}%', color='red', ha='center')
    ax.set_title('Distribución de Montos Aprobados de PBLs (USD millones)')
    ax.set_xlabel('Monto aprobado (millones USD)')
    ax.set_ylabel('Número de operaciones')
    ax.legend()
    st.pyplot(fig)

    # Mostrar tabla de operaciones relevantes
    st.subheader("PBLs relevantes")
    df_filtrado= df_filtrado[['apprvl_dt_yr', 'oper_num', 'orig_apprvd_useq_amnt_m']].sort_values(by='orig_apprvd_useq_amnt_m', ascending=False)

    # Renombrar columnas
    df_filtrado = df_filtrado.rename(columns={
        'apprvl_dt_yr': 'Año de aprobación',
        'oper_num': 'Número de operación',
        'orig_apprvd_useq_amnt_m': 'Monto aprobado (USD millones)'
    })

    st.dataframe(df_filtrado)

else:
    st.warning("⚠️ No hay datos disponibles para este filtro.")

#streamlit run "C:\Users\RAFAELAB\OneDrive - Inter-American Development Bank Group\Documents\PBLs\others\Code\Prueba PBLs.py"
