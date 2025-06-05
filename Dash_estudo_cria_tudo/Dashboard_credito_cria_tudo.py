import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from itertools import product

# Configuração da página
st.set_page_config(page_title="DASHBOARD DE ANÁLISE DE CRÉDITO", layout="wide")


# Função para criar o dataset
def create_dataset():
    np.random.seed(42)
    n = 10000  # Número de clientes
    data = {
        "ID_CLIENTE": range(1, n + 1),
        "IDADE": np.random.randint(18, 81, n),
        "RENDA_MENSAL": np.round(
            np.random.normal(2000, 20001, n).clip(min=1000, max=20000), 2
        ),
        "SCORE_CREDITO": np.random.randint(190, 999, n),
        "TEMPO_RESIDENCIA": np.random.randint(0, 41, n),
        "DIVIDA_ATUAL": np.round(np.random.exponential(1000, n).clip(max=50000), 2),
        "HISTORICO_INADIMPLENCIA": np.random.choice(["NÃO", "SIM"], n, p=[0.8, 0.2]),
        "EMPREGO": np.random.choice(
            ["CLT", "AUTÔNOMO", "DESEMPREGADO"], n, p=[0.7, 0.2, 0.1]
        ),
        "ESTADO_CIVIL": np.random.choice(
            ["SOLTEIRO", "CASADO", "DIVORCIADO"], n, p=[0.4, 0.5, 0.1]
        ),
        "TEMPO_EMPREGO": np.random.randint(0, 41, n),
        "VALOR_SOLICITADO": np.round(
            np.random.randint(5000, 300001, n).astype(float), 2
        ),
        "APROVADO": [
            "APROVADO" if s > 600 and r > 3000 else "REPROVADO"
            for s, r in zip(
                np.random.randint(300, 851, n), np.random.normal(5000, 2000, n)
            )
        ],
    }
    df = pd.DataFrame(data)
    df.to_csv("base_credito_ficticia.csv", index=False)
    return df


# Verificar se o arquivo já existe
if not os.path.exists("base_credito_ficticia.csv"):
    df = create_dataset()
else:
    df = pd.read_csv("base_credito_ficticia.csv")

# Transformar textos em caixa alta
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].str.upper()

# Criar coluna numérica para APROVADO
df["APROVADO_NUM"] = df["APROVADO"].map({"APROVADO": 1, "REPROVADO": 0})

# Criar faixas etárias
df["FAIXA_ETARIA"] = pd.cut(
    df["IDADE"],
    bins=[18, 30, 40, 50, 60, 80],
    labels=["18-30", "31-40", "41-50", "51-60", "61-80"],
)

# Criar faixas de score
df["FAIXA_SCORE"] = pd.cut(
    df["SCORE_CREDITO"],
    bins=[0, 300, 500, 700, 850, 1000],
    labels=[
        "Muito Baixo (300-499)",
        "Baixo (500-699)",
        "Médio (700-849)",
        "Bom (850-999)",
        "Excelente (1000)",
    ],
)

# Criar razão valor solicitado / renda anual
df["RAZAO_VALOR_RENDA"] = df["VALOR_SOLICITADO"] / (df["RENDA_MENSAL"] * 12)

# Título do Dashboard
st.title("📊 DASHBOARD DE ANÁLISE DE CRÉDITO")

# Filtros interativos
st.sidebar.header("🔍 FILTROS")
estado_civil = st.sidebar.multiselect(
    "ESTADO CIVIL",
    options=df["ESTADO_CIVIL"].unique(),
    default=df["ESTADO_CIVIL"].unique(),
    help="Selecione os estados civis para análise",
)
emprego = st.sidebar.multiselect(
    "TIPO DE EMPREGO",
    options=df["EMPREGO"].unique(),
    default=df["EMPREGO"].unique(),
    help="Selecione os tipos de vínculo empregatício",
)
idade_range = st.sidebar.slider(
    "FAIXA ETÁRIA",
    min_value=int(df["IDADE"].min()),
    max_value=int(df["IDADE"].max()),
    value=(int(df["IDADE"].min()), int(df["IDADE"].max())),
    help="Selecione a faixa etária desejada",
)
score_range = st.sidebar.slider(
    "SCORE DE CRÉDITO",
    min_value=int(df["SCORE_CREDITO"].min()),
    max_value=int(df["SCORE_CREDITO"].max()),
    value=(int(df["SCORE_CREDITO"].min()), int(df["SCORE_CREDITO"].max())),
    help="Selecione o range de score desejado",
)

df_filtered = df[
    df["ESTADO_CIVIL"].isin(estado_civil)
    & df["EMPREGO"].isin(emprego)
    & (df["IDADE"].between(idade_range[0], idade_range[1]))
    & (df["SCORE_CREDITO"].between(score_range[0], score_range[1]))
]

# Verificação de dados filtrados
if df_filtered.empty:
    st.warning(
        "⚠️ Nenhum dado encontrado com os filtros atuais. Ajuste os filtros e tente novamente."
    )
    st.stop()

# Seção de KPIs
st.header("📈 VISÃO GERAL")
col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Total de Clientes", f"{len(df_filtered):,}".replace(",", "."))
col2.metric(
    "✅ Taxa de Aprovação",
    f"{df_filtered['APROVADO_NUM'].mean():.1%}",
    help="Percentual de clientes aprovados no crédito",
)
col3.metric(
    "⚠️ Inadimplência",
    f"{df_filtered['HISTORICO_INADIMPLENCIA'].eq('SIM').mean():.1%}",
    help="Percentual de clientes com histórico de inadimplência",
)
col4.metric(
    "🏆 Score Médio",
    f"{df_filtered['SCORE_CREDITO'].mean():.0f}",
    help="Média do score de crédito dos clientes filtrados",
)

# Abas para diferentes análises
tab1, tab2, tab3 = st.tabs(
    ["👥 Análise Demográfica", "💰 Análise Financeira", "📉 Risco de Crédito"]
)

with tab1:
    st.header("👥 Análise Demográfica")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribuição por Faixa Etária")
        fig = px.pie(
            df_filtered,
            names="FAIXA_ETARIA",
            hole=0.3,
            color_discrete_sequence=px.colors.sequential.RdBu,
            labels={"FAIXA_ETARIA": "Faixa Etária"},
            title="Distribuição Percentual por Faixa Etária",
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Taxa de Aprovação por Estado Civil e Emprego")
        try:
            pivot = df_filtered.pivot_table(
                index="ESTADO_CIVIL",
                columns="EMPREGO",
                values="APROVADO_NUM",
                aggfunc="mean",
            )
            fig = px.imshow(
                pivot,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="Blues",
                labels=dict(
                    x="Tipo de Emprego", y="Estado Civil", color="Taxa de Aprovação"
                ),
                title="Taxa de Aprovação (%) por Estado Civil e Tipo de Emprego",
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(
                "Não foi possível gerar o gráfico de calor com os dados filtrados."
            )

    st.subheader("Distribuição de Scores por Faixa Etária")
    fig = px.box(
        df_filtered,
        x="FAIXA_ETARIA",
        y="SCORE_CREDITO",
        color="APROVADO",
        color_discrete_map={"APROVADO": "green", "REPROVADO": "red"},
        labels={"FAIXA_ETARIA": "Faixa Etária", "SCORE_CREDITO": "Score de Crédito"},
        title="Distribuição de Scores de Crédito por Faixa Etária e Status de Aprovação",
    )
    fig.update_layout(boxmode="group")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("💰 Análise Financeira")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Renda vs. Valor Solicitado")
        fig = px.scatter(
            df_filtered,
            x="RENDA_MENSAL",
            y="VALOR_SOLICITADO",
            color="APROVADO",
            color_discrete_map={"APROVADO": "green", "REPROVADO": "red"},
            trendline="lowess",
            opacity=0.7,
            hover_data=["SCORE_CREDITO", "IDADE", "EMPREGO"],
            labels={
                "RENDA_MENSAL": "Renda Mensal (R$)",
                "VALOR_SOLICITADO": "Valor Solicitado (R$)",
                "APROVADO": "Status",
            },
            title="Relação entre Renda Mensal e Valor Solicitado",
        )
        fig.update_layout(legend_title_text="Status de Aprovação")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Razão Valor Solicitado/Renda Anual")
        fig = px.histogram(
            df_filtered,
            x="RAZAO_VALOR_RENDA",
            color="APROVADO",
            color_discrete_map={"APROVADO": "green", "REPROVADO": "red"},
            nbins=30,
            barmode="overlay",
            opacity=0.6,
            labels={
                "RAZAO_VALOR_RENDA": "Razão (Valor Solicitado / Renda Anual)",
                "count": "Número de Clientes",
            },
            title="Distribuição da Razão entre Valor Solicitado e Renda Anual",
        )
        fig.add_vline(
            x=5,
            line_dash="dash",
            line_color="red",
            annotation_text="Limite Recomendado (5x)",
            annotation_position="top",
        )
        fig.update_layout(legend_title_text="Status de Aprovação")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Dívida Atual vs. Score de Crédito")
    fig = px.scatter(
        df_filtered,
        x="DIVIDA_ATUAL",
        y="SCORE_CREDITO",
        color="APROVADO",
        color_discrete_map={"APROVADO": "green", "REPROVADO": "red"},
        size="VALOR_SOLICITADO",
        hover_name="EMPREGO",
        opacity=0.7,
        labels={
            "DIVIDA_ATUAL": "Dívida Atual (R$)",
            "SCORE_CREDITO": "Score de Crédito",
            "VALOR_SOLICITADO": "Valor Solicitado (R$)",
            "APROVADO": "Status",
        },
        title="Relação entre Dívida Atual e Score de Crédito",
    )
    fig.update_layout(legend_title_text="Status de Aprovação")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("📉 Análise de Risco")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Inadimplência por Segmento")

        # Cria DataFrame agregado para garantir combinações válidas
        sunburst_df = (
            df_filtered.groupby(["FAIXA_ETARIA", "EMPREGO", "HISTORICO_INADIMPLENCIA"])
            .size()
            .reset_index(name="COUNT")
        )

        # Cria todas combinações possíveis para preencher missing paths
        all_combinations = list(
            product(
                df_filtered["FAIXA_ETARIA"].unique(),
                df_filtered["EMPREGO"].unique(),
                df_filtered["HISTORICO_INADIMPLENCIA"].unique(),
            )
        )

        complete_df = pd.DataFrame(
            all_combinations,
            columns=["FAIXA_ETARIA", "EMPREGO", "HISTORICO_INADIMPLENCIA"],
        )
        complete_df = complete_df.merge(sunburst_df, how="left").fillna(0)

        if len(complete_df) > 0:
            fig = px.sunburst(
                complete_df,
                path=["FAIXA_ETARIA", "EMPREGO", "HISTORICO_INADIMPLENCIA"],
                values="COUNT",
                color="HISTORICO_INADIMPLENCIA",
                color_discrete_map={"SIM": "#FF7F0E", "NÃO": "#1F77B4"},
                branchvalues="total",
                title="Distribuição Hierárquica da Inadimplência",
                labels={"COUNT": "Número de Clientes"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Dados insuficientes para o gráfico sunburst.")

    with col2:
        st.subheader("Score de Crédito por Categoria")
        if not df_filtered.empty:
            fig = px.violin(
                df_filtered,
                x="FAIXA_SCORE",
                y="SCORE_CREDITO",
                color="APROVADO",
                color_discrete_map={"APROVADO": "green", "REPROVADO": "red"},
                box=True,
                points="all",
                labels={
                    "FAIXA_SCORE": "Categoria de Score",
                    "SCORE_CREDITO": "Score de Crédito",
                    "APROVADO": "Status",
                },
                title="Distribuição de Scores por Categoria e Status de Aprovação",
            )
            fig.update_layout(legend_title_text="Status de Aprovação")
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Matriz de Correlação entre Variáveis")
    numeric_cols = df_filtered.select_dtypes(include=["int64", "float64"]).columns
    if len(numeric_cols) > 0:
        corr = df_filtered[numeric_cols].corr()
        fig = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu",
            range_color=[-1, 1],
            title="Correlação entre Variáveis Numéricas",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhuma coluna numérica para calcular correlação.")

# Rodapé
st.sidebar.markdown("---")
st.sidebar.markdown("**Dashboard de Análise de Crédito**")
st.sidebar.markdown("Versão 3.0 - Julho 2024")
st.sidebar.markdown(
    "Desenvolvido por [Paulo Munhoz](https://www.linkedin.com/in/paulomunhoz/)"
)
st.sidebar.markdown(
    "*Este dashboard foi criado para fins educacionais e de demonstração.*\n "
    "*Os dados são fictícios e não refletem informações reais.*"
)
