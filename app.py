import streamlit as st
import pandas as pd
import plotly.express as px
import kagglehub
import os

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard Spotify",
    page_icon="🎶",
    layout="wide",
)

# --- Carregamento dos dados ---
@st.cache_data
def load_data():
    # 1️⃣ Faz o download do dataset
    path_str = kagglehub.dataset_download("yamaerenay/spotify-dataset-1921-2020-160k-tracks")

    # 2️⃣ Localiza o CSV usando os.path.join
    file_csv = os.path.join(path_str, "data.csv")  # ajuste o nome se for diferente

    # 3️⃣ Lê o CSV
    df = pd.read_csv(file_csv)

    # 4️⃣ Limpeza e preparação
    df = df.dropna(subset=["year", "artists", "popularity"])
    df["year"] = df["year"].astype(int)
    df["decada"] = (df["year"] // 10) * 10

    return df

df = load_data()

# --- Descrição inicial ---
st.title("🎶 Dashboard Spotify")
st.markdown(
    """
    Este dashboard interativo permite explorar músicas do **Spotify** a partir do dataset.
    Você pode filtrar por ano, artista ou gênero (quando disponível), e visualizar métricas, gráficos e tabelas.
    """
)

# --- Filtros na barra lateral ---
st.sidebar.header("Filtros")

# Ano de lançamento (intervalo)
anos = sorted(df["year"].unique())
ano_min, ano_max = st.sidebar.select_slider(
    "Selecione o intervalo de anos",
    options=anos,
    value=(anos[0], anos[-1])
)

# Artista
artistas = df["artists"].unique()
artista_sel = st.sidebar.multiselect("Selecione Artistas", artistas)

# Aplicando filtros
df_filtrado = df[(df["year"] >= ano_min) & (df["year"] <= ano_max)]

if artista_sel:
    df_filtrado = df_filtrado[df_filtrado["artists"].isin(artista_sel)]

# --- KPIs ---
st.subheader("📊 Métricas principais")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total de músicas", df_filtrado.shape[0])

with col2:
    if not df_filtrado.empty:
        artista_top = df_filtrado["artists"].mode()[0]
        st.metric("Artista mais frequente", artista_top)
    else:
        st.metric("Artista mais frequente", "-")

with col3:
    st.metric(
        "Média Popularidade",
        round(df_filtrado["popularity"].mean(), 2) if not df_filtrado.empty else 0
    )

# --- Gráficos ---
st.subheader("📈 Gráficos Interativos")

# Gráfico de barras - Top 10 artistas
top_artistas = (
    df_filtrado["artists"]
    .value_counts()
    .head(10)
    .reset_index()
)
top_artistas.columns = ["Artista", "Quantidade"]

fig_bar = px.bar(
    top_artistas,
    x="Artista",
    y="Quantidade",
    title="Top 10 artistas com mais músicas",
    text="Quantidade",
)
st.plotly_chart(fig_bar, use_container_width=True)

# Gráfico de pizza - Distribuição por década
dist_decadas = df_filtrado["decada"].value_counts().reset_index()
dist_decadas.columns = ["Década", "Qtd"]

fig_pizza = px.pie(
    dist_decadas,
    values="Qtd",
    names="Década",
    title="Distribuição das músicas por década"
)
st.plotly_chart(fig_pizza, use_container_width=True)

# --- Tabela ---
st.subheader("📋 Tabela de Músicas Filtradas")
st.dataframe(df_filtrado)