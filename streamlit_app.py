import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- Chargement des données DVF échantillon ---
@st.cache_data
def load_data():
    url = "https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20230418-141742/valeursfoncieres-2022.txt"
    df = pd.read_csv(url, sep="|", low_memory=False)
    df = df[['Commune', 'Code postal', 'Valeur fonciere', 'Surface reelle bati', 'Nombre de pieces principales', 'Latitude', 'Longitude']]
    df = df.dropna(subset=['Latitude', 'Longitude', 'Surface reelle bati'])
    df = df[df['Surface reelle bati'] > 0]
    return df

df = load_data()

# --- Interface Streamlit ---
st.title("🧭 Analyse des prix immobiliers DVF")
ville = st.text_input("Nom de la commune :", "Paris")

# --- Filtrage ---
df_ville = df[df['Commune'].str.contains(ville.upper(), na=False)]

if df_ville.empty:
    st.warning("Aucune donnée trouvée pour cette commune.")
else:
    prix_m2 = (df_ville['Valeur fonciere'] / df_ville['Surface reelle bati']).median()
    st.metric(f"Prix médian au m² à {ville.capitalize()}", f"{int(prix_m2):,} €/m²")

    # --- Carte interactive ---
    m = folium.Map(location=[df_ville['Latitude'].mean(), df_ville['Longitude'].mean()], zoom_start=13)
    for _, row in df_ville.sample(min(300, len(df_ville))).iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=3,
            popup=f"{int(row['Valeur fonciere'])}€ - {row['Surface reelle bati']} m²",
            color="blue",
            fill=True,
            fill_opacity=0.6
        ).add_to(m)

    st_folium(m, width=700)

