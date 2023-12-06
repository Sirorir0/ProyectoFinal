import pandas as pd
import numpy as pn
import plotly.express as px
import re
import streamlit as st

crops = pd.read_excel("Datos/Crops_STV.xlsx")

#Funcion para preparar las temporadas
def split_seasons(original):
  temp = original
  if "and" in original:
    temp = re.split('and|,', original)
    newList = []
    for t in temp:
      newList.append(t.strip())
    return newList
  else:
    return original

crops["season"] = crops["season"].apply(lambda x: split_seasons(x))
crops = crops.assign(season=crops['season']).explode('season').reset_index(drop=True)

#Calcular el precio de crop procesado
def preserves_crops(crops):
  if crops["type"] == "flower":
    processed_value = crops["basic_price"] * 2 + 100
  elif crops["type"] == "coffee":
    processed_value = 50
  else:
    processed_value = crops['basic_price'] * 2 + 50
  return processed_value

def keg_crops(crops):
  if crops["type"] == "vegetable":
    processed_value = crops["basic_price"] * 2.25
  elif crops["type"] == "flower" or crops["type"] == "coffee":
    processed_value = crops["basic_price"] * 0
  else:
    processed_value = crops["basic_price"] * 3
  return processed_value

#Selector de la temporada
with st.sidebar:
  temporada = list(set(crops["season"]))
  tempSelec = st.multiselect("Selecciona las temporadas", temporada)

# Filtrar los datos basados en la selección del usuario
crops_filtered = crops[crops['season'].isin(tempSelec)]

#Inputs del streamlit
with st.sidebar:
  dia = st.number_input("Dia actual", min_value=1, max_value=28)
  seedmoney = st.number_input("Dinero máximo para semillas")
  artisan = st.checkbox("Profesión de artesano")
  seedsource = st.selectbox("Comprando en:", ["Pierre's", "Joja Mart","Oasis", "Egg festival","Carrito ambulante"])
  processed = st.selectbox("Procesado", ["Ninguno","Barril","Tarro de preservas"])

if processed == "Barril":
  crops_filtered["finalvalue"] = crops_filtered.apply(keg_crops, axis=1)
elif processed == "Tarro de preservas":
  crops_filtered["finalvalue"] = crops_filtered.apply(preserves_crops, axis=1)
else:
  crops_filtered["finalvalue"] = crops_filtered["basic_price"]

#Opciones para la source de las semillas
if seedsource == "Pierre's":
  seedsrc = crops_filtered["general_store"]
elif seedsource == "Joja Mart":
  seedsrc = crops_filtered["joja_mart"]
elif seedsource == "Oasis":
  seedsrc = crops_filtered["oasis"]
elif seedsource == "Carrito ambulante":
  seedsrc = crops_filtered["traveling_cart"]
else:
  seedsrc = crops_filtered["egg_festival"]

crops_filtered["seedsourc"] = seedsrc
if artisan == True and processed == "Barril" or processed == "Tarro de preservas":
  crops_filtered["finalvalue"] = crops_filtered["finalvalue"].apply(lambda x: x * 1.40)

crops_filtered["store"] = seedsource
crops_filtered["last_day"] = 28 - crops_filtered["harvest_initial"]

crops_filtered["finalvalue"] = crops_filtered["finalvalue"] - crops_filtered["seedsourc"]

crops_filtered = crops_filtered[(crops_filtered["seedsourc"] > 0) & (crops_filtered["store"] == seedsource) &  (crops_filtered["seedsourc"] <= seedmoney) & (crops_filtered["last_day"] >= dia) & (crops_filtered["finalvalue"] > 0)]
crops_filtered.sort_values(["finalvalue"], inplace = True)

fig1 = px.bar(crops_filtered, x="name", y="finalvalue", labels={'name': 'Cultivo', 'finalvalue': 'Ganancia total'}, title="Ganancia por cultivo", color="season")
st.plotly_chart(fig1, use_container_width=True)