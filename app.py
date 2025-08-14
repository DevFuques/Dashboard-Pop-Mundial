import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da Página
st.set_page_config(
    page_title="Dashboard População Mundial",
    page_icon="🌍",
    layout="wide",
)

# Título e descrição
st.title("🌍 Dashboard de População Mundial")
st.markdown("Dados fornecidos pelo [DataHub](https://datahub.io/core/population) com base no Banco Mundial.")

# Carregamento dos dados
url = "https://datahub.io/core/population/r/population.csv"
df = pd.read_csv(url)

# Renomeação de colunas
renomear_colunas = {
    'Country Name': 'País',
    'Country Code': 'Código ISO',
    'Year': 'Ano',
    'Value': 'População Total'
}
df = df.rename(columns=renomear_colunas)

# A linha abaixo filtra países com códigos ISO de 3 caracteres
df_paises = df[df["Código ISO"].str.len() == 3]

# Dicionário de metadados
colunas_info = {
    "País": "Nome completo do país ou região.",
    "Código ISO": "Código ISO Alpha-3 que identifica o país.",
    "Ano": "Ano de referência dos dados.",
    "População Total": "Número estimado de habitantes no país nesse ano."
}

# Barra lateral com filtros
st.sidebar.header("🔍 Filtros")
anos = sorted(df_paises["Ano"].unique())
ano = st.sidebar.slider("Selecione o ano", min_value=min(anos), max_value=max(anos), value=2020)

paises = sorted(df_paises["País"].unique())
pais = st.sidebar.selectbox("Selecione um país para análise", paises)

# --- Informações principais ---
ano_mais_antigo = df_paises['Ano'].min()
ano_mais_recente = df_paises['Ano'].max()
pais_menos_populoso = df_paises[df_paises['Ano'] == ano_mais_recente] \
                        .sort_values('População Total', ascending=True).iloc[0]['País']
populacao_pais_selecionado = df_paises[
    (df_paises['País'] == pais) & (df_paises['Ano'] == ano_mais_recente)
]['População Total'].iloc[0]

col1, col2, col3 = st.columns(3)

col1.metric("Ano mais antigo", ano_mais_antigo)
col2.metric("Ano mais recente", ano_mais_recente)
col3.metric("País menos populoso", pais_menos_populoso)

st.markdown("---")

st.subheader("Gráficos")

st.metric(f"População do País Selecionado - {pais}", f"{populacao_pais_selecionado:,.0f}")

df_paises = df[df["País"] != "World"]

col_graf1, col_graf2 = st.columns(2)

# Gráfico 1: Evolução da população de um país
df_pais_selecionado = df_paises[df_paises["País"] == pais]

with col_graf1:
    if not df_pais_selecionado.empty:
        fig = px.line(
            df_pais_selecionado,
            x="Ano",
            y="População Total",
            title=f"Evolução da População - {pais}"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"Nenhum dado encontrado para {pais}.")

# Gráfico 2: Top 5 pregiões econômicas mais populosas
df_ano_top5 = df_paises[(df_paises["Ano"] == ano)].nlargest(5, "População Total")

with col_graf2:
    if not df_ano_top5.empty:
        fig2 = px.bar(
            df_ano_top5,
            x="População Total",  
            y="País",             
            orientation='h',      
            title=f"Top 5 regiões econômicas mais populosas - {ano}"
        )
        # Opcional: inverte a ordem para que o maior fique no topo
        fig2.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning(f"Nenhum dado encontrado para o ano de {ano}.")

# Gráfico 3: Mapa do mundo
df_ano_mapa = df_paises[df_paises["Ano"] == ano]

with st.container():
    if not df_ano_mapa.empty:
        fig3 = px.choropleth(
            df_ano_mapa,
            locations="Código ISO",
            color="População Total",
            hover_name="País",
            color_continuous_scale=px.colors.sequential.Plasma,
            title=f"População Mundial - {ano}"
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning(f"Nenhum dado para exibir no mapa do ano de {ano}.")

# Gráfico 4: Mapa animado
with st.container():
    if not df_paises.empty:
        fig4 = px.choropleth(
            df_paises,
            locations="Código ISO",
            color="População Total",
            hover_name="País",
            animation_frame="Ano",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Evolução da População Mundial"
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("Não há dados disponíveis para gerar o mapa animado.")

st.subheader("📊 Comparação de Crescimento Populacional")
st.markdown("Compare a população de cada país em dois anos.")

# Seletores para os anos de comparação
col_ano_comp1, col_ano_comp2 = st.columns(2)
ano_comp1 = col_ano_comp1.selectbox("Selecione o primeiro ano", anos, index=0)
ano_comp2 = col_ano_comp2.selectbox("Selecione o segundo ano", anos, index=len(anos)-1)

if ano_comp1 and ano_comp2 and ano_comp1 != ano_comp2:
    # Filtra os dados para os dois anos selecionados
    df_ano1 = df_paises[df_paises['Ano'] == ano_comp1][['País', 'População Total']].rename(columns={'População Total': 'População ' + str(ano_comp1)})
    df_ano2 = df_paises[df_paises['Ano'] == ano_comp2][['País', 'População Total']].rename(columns={'População Total': 'População ' + str(ano_comp2)})
    
    # Mescla os dataframes para ter os dois anos na mesma linha
    df_comparacao = pd.merge(df_ano1, df_ano2, on='País', how='inner')

    # Cria o gráfico de dispersão
    fig_scatter = px.scatter(
        df_comparacao,
        x='População ' + str(ano_comp1),
        y='População ' + str(ano_comp2),
        hover_name='País',
        title=f"População de {ano_comp2} vs. {ano_comp1}"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("Selecione dois anos diferentes para a comparação.")

# Descrição das colunas
st.subheader("ℹ️ Descrição das colunas")
st.dataframe(colunas_info)


# Dados brutos
with st.expander("📄 Ver dados brutos"):
    if not df_paises.empty:
        st.dataframe(df_paises)
    else:
        st.info("Nenhum dado disponível para exibir.")
