import streamlit as st
import pandas as pd
import altair as alt

# Título do aplicativo
st.set_page_config(layout="wide")
st.title("Análise de Vendas de Eletrônicos")
st.write(
    "Este painel interativo responde a 5 perguntas de negócio com base nos dados de vendas fornecidos."
)

# 1. Carregar os dados
try:
    df = pd.read_csv("vendas_eletronicos.csv")
    # Convertendo a coluna de data para o formato datetime
    df["Data_Venda"] = pd.to_datetime(df["Data_Venda"])
    st.success("Arquivo 'vendas_eletronicos.csv' carregado com sucesso!")
except FileNotFoundError:
    st.error(
        "Erro: Arquivo 'vendas_eletronicos.csv' não encontrado. Por favor, verifique se o arquivo está no mesmo diretório."
    )
    st.stop()


# 2. Resumo dos dados
st.header("Resumo dos Dados")
st.write(f"**Total de Registros:** {len(df)}")
col1, col2 = st.columns(2)
with col1:
    st.write("**Primeiras 5 Linhas:**")
    st.dataframe(df.head())
with col2:
    st.write("**Informações do DataFrame:**")
    st.dataframe(df.info(buf=None))


# --- Análise das 5 Perguntas de Negócio ---
st.header("Análise das Perguntas de Negócio")

# Pergunta 1: Qual a receita total por categoria de produto?
st.subheader("1. Receita Total por Categoria de Produto")
receita_por_categoria = (
    df.groupby("Categoria_Produto")["Total_Venda"].sum().reset_index()
)
chart_receita_categoria = (
    alt.Chart(receita_por_categoria)
    .mark_bar()
    .encode(
        x=alt.X("Categoria_Produto", title="Categoria de Produto"),
        y=alt.Y("Total_Venda", title="Receita Total ($)"),
    )
    .properties(title="Receita Total por Categoria")
)
st.altair_chart(chart_receita_categoria, use_container_width=True)
st.write(
    "**Insight:** O gráfico de barras mostra a contribuição de cada categoria para a receita total. Esta visualização é útil para identificar qual categoria é a mais lucrativa."
)


# Pergunta 2: Quais são os 5 produtos mais vendidos em termos de quantidade e receita?
st.subheader("2. Top 5 Produtos Mais Vendidos")
st.write("**Top 5 por Receita:**")
top_receita = df.groupby("Produto")["Total_Venda"].sum().nlargest(5).reset_index()
chart_top_receita = (
    alt.Chart(top_receita)
    .mark_bar()
    .encode(
        x=alt.X("Produto", sort="-y", title="Produto"),
        y=alt.Y("Total_Venda", title="Receita Total ($)"),
    )
    .properties(title="Top 5 Produtos por Receita")
)
st.altair_chart(chart_top_receita, use_container_width=True)

st.write("**Top 5 por Quantidade:**")
top_quantidade = df.groupby("Produto")["Quantidade"].sum().nlargest(5).reset_index()
chart_top_quantidade = (
    alt.Chart(top_quantidade)
    .mark_bar()
    .encode(
        x=alt.X("Produto", sort="-y", title="Produto"),
        y=alt.Y("Quantidade", title="Quantidade Total"),
    )
    .properties(title="Top 5 Produtos por Quantidade Vendida")
)
st.altair_chart(chart_top_quantidade, use_container_width=True)
st.write(
    "**Insight:** A análise dos produtos mais vendidos por receita e quantidade ajuda a identificar os itens mais populares e valiosos, auxiliando na gestão de estoque e nas estratégias de marketing."
)


# Pergunta 3: Qual a distribuição das vendas por país?
st.subheader("3. Receita Total por País")
vendas_por_pais = df.groupby("País")["Total_Venda"].sum().reset_index()
chart_vendas_pais = (
    alt.Chart(vendas_por_pais)
    .mark_bar()
    .encode(
        x=alt.X("País", sort="-y", title="País"),
        y=alt.Y("Total_Venda", title="Receita Total ($)"),
    )
    .properties(title="Receita Total por País")
)
st.altair_chart(chart_vendas_pais, use_container_width=True)
st.write(
    "**Insight:** Este gráfico mostra de onde vêm a maior parte das vendas. Isso é crucial para entender o mercado-alvo e para planejar expansões ou campanhas de marketing focadas em regiões específicas."
)


# Pergunta 4: Qual a tendência de vendas ao longo do tempo?
st.subheader("4. Tendência de Vendas Mensais")
# Agrupar por mês
df["Mês"] = df["Data_Venda"].dt.to_period("M").astype(str)
vendas_mensais = df.groupby("Mês")["Total_Venda"].sum().reset_index()
chart_vendas_mensais = (
    alt.Chart(vendas_mensais)
    .mark_line(point=True)
    .encode(
        x=alt.X("Mês", title="Mês"), y=alt.Y("Total_Venda", title="Receita Total ($)")
    )
    .properties(title="Tendência de Receita ao Longo do Tempo")
)
st.altair_chart(chart_vendas_mensais, use_container_width=True)
st.write(
    "**Insight:** O gráfico de linha revela a tendência de receita ao longo do tempo, ajudando a identificar sazonalidade, picos de vendas ou períodos de queda que podem requerer ações estratégicas."
)


# Pergunta 5: Qual o ticket médio por categoria de produto?
st.subheader("5. Ticket Médio por Categoria")
ticket_medio = df.groupby("Categoria_Produto")["Total_Venda"].mean().reset_index()
chart_ticket_medio = (
    alt.Chart(ticket_medio)
    .mark_bar()
    .encode(
        x=alt.X("Categoria_Produto", title="Categoria de Produto"),
        y=alt.Y("Total_Venda", title="Ticket Médio ($)"),
    )
    .properties(title="Ticket Médio por Categoria de Produto")
)
st.altair_chart(chart_ticket_medio, use_container_width=True)
st.write(
    "**Insight:** Comparar o ticket médio por categoria pode fornecer insights sobre quais tipos de produtos geram vendas de maior valor, o que é útil para a estratégia de precificação e de promoções."
)
