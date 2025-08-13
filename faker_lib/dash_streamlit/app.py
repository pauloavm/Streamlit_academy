import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas de Eletrônicos",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS para um tema claro
st.markdown(
    """
    <style>
    /* Estilo para a página inteira: fundo claro e texto escuro */
    body {
        background-color: #f0f2f6; /* Fundo cinza claro */
        color: #1a237e; /* Texto azul escuro */
    }
    
    /* Container principal */
    .main .block-container{
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }

    /* Títulos */
    h1, h2, h3, h4, h5, h6 {
        color: #1a237e;
    }
    
    /* Estilo da barra lateral para garantir fundo claro e texto escuro */
    .st-emotion-cache-18ni4h0 {
        background-color: #e3f2fd; /* Fundo azul claro para a sidebar */
        color: #1a237e; /* Texto azul escuro */
    }

    /* Estilo para os gráficos (destaque) */
    .plotly-graph-div {
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        transition: 0.3s;
        border-radius: 5px;
        background-color: white;
    }
    
    /* Estilo para a métrica de vendas */
    div[data-testid="metric-container"] {
        background-color: #e3f2fd;
        border: 1px solid #1a237e;
        padding: 5% 5% 5% 10%;
        border-radius: 5px;
        color: #1a237e;
        overflow-wrap: break-word;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Carregar o dataset
try:
    df = pd.read_csv("vendas_eletronicos.csv")
except FileNotFoundError:
    st.error(
        "Arquivo 'vendas_eletronicos.csv' não encontrado. Por favor, verifique se o arquivo está no mesmo diretório do script."
    )
    st.stop()


# Limpeza e Pré-processamento dos Dados
df["Data_Venda"] = pd.to_datetime(df["Data_Venda"])
df["Ano"] = df["Data_Venda"].dt.year
df["Mês"] = df["Data_Venda"].dt.month
df["Trimestre"] = df["Data_Venda"].dt.quarter


# Título principal do dashboard
st.title("Dashboard de Análise de Vendas")
st.markdown("Uma análise interativa dos dados de vendas de eletrônicos.")


# --- Barra lateral para filtros ---
st.sidebar.header("Filtros")


# Filtro por Ano
anos_disponiveis = sorted(df["Ano"].unique())
anos_selecionados = st.sidebar.multiselect(
    "Selecione o(s) Ano(s)",
    options=anos_disponiveis,
    default=anos_disponiveis,
)


# Filtro por Trimestre
trimestres_disponiveis = sorted(df["Trimestre"].unique())
trimestres_selecionados = st.sidebar.multiselect(
    "Selecione o(s) Trimestre(s)",
    options=trimestres_disponiveis,
    default=trimestres_disponiveis,
)


# Filtrar o DataFrame
df_filtrado = df[
    (df["Ano"].isin(anos_selecionados))
    & (df["Trimestre"].isin(trimestres_selecionados))
]


# Mensagem de alerta se nenhum dado for encontrado
if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    # --- Visualizações ---
    st.header("Análise de Vendas")

    # Criar colunas para colocar as métricas lado a lado
    col1_metric, col2_metric = st.columns(2)

    with col1_metric:
        # Exibir o valor total de vendas como um KPI
        total_vendas = df_filtrado["Total_Venda"].sum()
        st.metric(label="Total de Vendas", value=f"US$ {total_vendas:,.2f}")

    with col2_metric:
        # Calcular e exibir o ticket médio por venda
        if len(df_filtrado) > 0:
            ticket_medio = df_filtrado["Total_Venda"].mean()
            st.metric(label="Ticket Médio por Venda", value=f"US$ {ticket_medio:,.2f}")
        else:
            st.metric(label="Ticket Médio por Venda", value="US$ 0.00")

    # Criar colunas para colocar os gráficos lado a lado
    col1, col2 = st.columns(2)

    # Top 5 Produtos por Vendas (valor total)
    with col1:
        st.subheader("Top 5 Produtos por Vendas")
        top_produtos_valor = (
            df_filtrado.groupby("Produto")["Total_Venda"]
            .sum()
            .nlargest(5)
            .reset_index()
        )
        fig_prod_valor = px.bar(
            top_produtos_valor,
            x="Total_Venda",
            y="Produto",
            title="Top 5 Produtos por Vendas",
            orientation="h",
            color="Produto",
            labels={"Total_Venda": "Vendas Totais ($)", "Produto": "Produto"},
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )
        fig_prod_valor.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_prod_valor, use_container_width=True)

    # Top 5 Produtos por Quantidade Vendida
    with col2:
        st.subheader("Top 5 Produtos por Quantidade")
        top_produtos_qtd = (
            df_filtrado.groupby("Produto")["Quantidade"].sum().nlargest(5).reset_index()
        )
        fig_prod_qtd = px.bar(
            top_produtos_qtd,
            x="Quantidade",
            y="Produto",
            title="Top 5 Produtos por Quantidade Vendida",
            orientation="h",
            color="Produto",
            labels={"Quantidade": "Quantidade Vendida", "Produto": "Produto"},
            color_discrete_sequence=px.colors.qualitative.T10,
        )
        fig_prod_qtd.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_prod_qtd, use_container_width=True)

    # Vendas por País (agora um mapa interativo, logo abaixo dos dois primeiros)
    st.subheader("Vendas por País")
    vendas_por_pais = df_filtrado.groupby("País")["Total_Venda"].sum().reset_index()
    fig_mapa = px.choropleth(
        vendas_por_pais,
        locations="País",
        locationmode="country names",
        color="Total_Venda",
        hover_name="País",
        color_continuous_scale=px.colors.sequential.Plasma,
        title="Vendas Totais por País",
        labels={"Total_Venda": "Vendas Totais ($)"},
    )
    st.plotly_chart(fig_mapa, use_container_width=True)

    st.subheader("Vendas Totais por Mês")
    vendas_por_mes = (
        df_filtrado.groupby(["Ano", "Mês"])["Total_Venda"].sum().reset_index()
    )
    vendas_por_mes["Data"] = (
        vendas_por_mes["Ano"].astype(str) + "-" + vendas_por_mes["Mês"].astype(str)
    )
    fig_mes = px.bar(
        vendas_por_mes,
        x="Data",
        y="Total_Venda",
        title="Vendas Totais por Mês",
        # color='Ano',
        labels={"Data": "Ano-Mês", "Total_Venda": "Vendas Totais ($)"},
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )
    st.plotly_chart(fig_mes, use_container_width=True)

    st.subheader("Top 5 Clientes")
    top_clientes_vendas = (
        df_filtrado.groupby("Nome_Cliente")["Total_Venda"]
        .sum()
        .nlargest(5)
        .reset_index()
    )
    fig_clientes = px.bar(
        top_clientes_vendas,
        x="Total_Venda",
        y="Nome_Cliente",
        title="Top 5 Clientes por Vendas",
        orientation="h",
        color="Nome_Cliente",
        labels={"Total_Venda": "Vendas Totais ($)", "Nome_Cliente": "Nome do Cliente"},
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_clientes.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_clientes, use_container_width=True)
