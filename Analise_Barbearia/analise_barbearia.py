import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime


# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide")


# 2--------- CONFIGURAÇÕES INICIAIS ---
@st.cache_data
def carregar_dados():
    """
    Carrega e transforma os dados da planilha Excel.
    Mostra um erro e para o app se o arquivo não for encontrado.
    """
    try:
        df = pd.read_excel("AGENDAMENTOS.xlsx")
    except FileNotFoundError:
        st.error(
            "Arquivo 'AGENDAMENTOS.xlsx' não encontrado! Verifique se ele está na mesma pasta do script."
        )
        st.stop()  # Interrompe a execução do script de forma limpa

    # Aplica as transformações de forma encadeada para maior clareza
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

    # Remove linhas onde a data é inválida, pois são essenciais para as análises
    df.dropna(subset=["Data"], inplace=True)

    df["Ano"] = df["Data"].dt.year
    df["Mês"] = df["Data"].dt.to_period("M").astype(str)

    return df


# Uso da função
df_original = carregar_dados()


# --- 3. BARRA LATERAL (FILTROS) ---
st.sidebar.image("logo_DonMunhoz_semFundo.png", use_container_width=True)

st.sidebar.header("Filtros Interativos")

# Filtro por Ano
anos_disponiveis = sorted(df_original["Ano"].unique(), reverse=True)
anos_selecionados = st.sidebar.multiselect(
    "Selecione o(s) Ano(s)", options=anos_disponiveis, default=anos_disponiveis
)

# Filtro por Profissional
profissionais = sorted(df_original["Profissional"].unique())
profissionais_selecionados = st.sidebar.multiselect(
    "Selecione o Profissional", options=profissionais, default=profissionais
)

# NOVO: Filtro por Serviço
servicos = sorted(df_original["Serviço"].unique())
servicos_selecionados = st.sidebar.multiselect(
    "Selecione o(s) Serviço(s)", options=servicos, default=servicos
)

# Filtro por Status do Agendamento
status_lista = sorted(df_original["Status_descrito"].unique())
status_selecionados = st.sidebar.multiselect(
    "Selecione o Status", options=status_lista, default=status_lista
)

# Filtro por Período
min_data = df_original["Data"].min().to_pydatetime()
max_data = df_original["Data"].max().to_pydatetime()
data_selecionada = st.sidebar.date_input(
    "Selecione o Período Específico",
    value=(min_data, max_data),
    min_value=min_data,
    max_value=max_data,
)
# Garante que data_selecionada seja sempre uma tupla de dois elementos
if not isinstance(data_selecionada, (tuple, list)) or len(data_selecionada) != 2:
    data_selecionada = (min_data, max_data)

# filtro de serviço
df_filtrado = df_original[
    (df_original["Ano"].isin(anos_selecionados))
    & (df_original["Profissional"].isin(profissionais_selecionados))
    & (df_original["Serviço"].isin(servicos_selecionados))
    & (df_original["Status_descrito"].isin(status_selecionados))
    & (df_original["Data"] >= pd.to_datetime(data_selecionada[0]))
    & (df_original["Data"] <= pd.to_datetime(data_selecionada[1]))
]


# --- 4. TÍTULO PRINCIPAL DO DASHBOARD ---
st.title("📊 Análise de Situação da Barbearia")
st.markdown("---")

# --- 5. MÉTRICAS PRINCIPAIS (KPIs) ---
df_realizado = df_filtrado[df_filtrado["Status_descrito"] == "Realizado"]

total_faturamento = df_realizado["Valor"].sum()
total_agendamentos_realizados = df_realizado.shape[0]
ticket_medio = (
    total_faturamento / total_agendamentos_realizados
    if total_agendamentos_realizados > 0
    else 0
)

col1, col2, col3 = st.columns(3)
col1.metric("Faturamento Total", f"R$ {total_faturamento:,.2f}")
col2.metric("Agendamentos Realizados", f"{total_agendamentos_realizados}")
col3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
st.markdown("---")


# --- 6. GRÁFICOS E VISUALIZAÇÕES ---

# Pergunta 1: Qual o faturamento total por serviço e por profissional?
st.subheader("Faturamento por Profissional e Serviço")
if not df_realizado.empty:
    fig_faturamento_prof = px.bar(
        df_realizado,
        x="Profissional",
        y="Valor",
        color="Serviço",
        title="Faturamento por Profissional e Serviço",
        labels={"Valor": "Faturamento (R$)", "Profissional": "Profissional"},
        barmode="group",
    )
    fig_faturamento_prof.update_traces(
        hovertemplate=(
            "<b>Profissional:</b> %{x}<br>"
            "<b>Serviço:</b> %{data.name}<br>"
            "<b>Faturamento:</b> R$ %{y:,.2f}<extra></extra>"
        )
    )
    st.plotly_chart(fig_faturamento_prof, use_container_width=True)
else:
    st.info("Não há faturamento para exibir com os filtros atuais.")

st.markdown("---")


# GRÁFICO DE FATURAMENTO POR SERVIÇO
st.subheader("Faturamento por Serviço no Período")
if not df_realizado.empty:
    faturamento_por_servico = (
        df_realizado.groupby("Serviço")["Valor"].sum().sort_values(ascending=True)
    )
    fig_faturamento_servico = px.bar(
        faturamento_por_servico,
        x=faturamento_por_servico.values,
        y=faturamento_por_servico.index,
        orientation="h",
        title="Faturamento por Serviço no Período",
        text_auto=True,
        labels={"x": "Faturamento Total (R$)", "y": "Serviço"},
    )
    fig_faturamento_servico.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_faturamento_servico, use_container_width=True)
else:
    st.info("Não há faturamento para exibir com os filtros atuais.")

st.markdown("---")


# Pergunta 2: Qual a taxa de cancelamento e ausência?
st.subheader("Cancelamentos e Ausências")
if not df_filtrado.empty:
    col_taxa1, col_taxa2 = st.columns(2)
    with col_taxa1:
        status_counts = df_filtrado["Status_descrito"].value_counts()
        fig_status_pizza = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Distribuição Geral de Status dos Agendamentos",
            hole=0.3,
        )
        st.plotly_chart(fig_status_pizza, use_container_width=True)

    with col_taxa2:
        df_cancelados = df_filtrado[df_filtrado["Status_descrito"] == "Cancelado"]
        if not df_cancelados.empty:
            cancel_por_prof = df_cancelados["Profissional"].value_counts().reset_index()
            cancel_por_prof.columns = ["Profissional", "Cancelamentos"]
            fig_cancel_prof = px.bar(
                cancel_por_prof,
                x="Profissional",
                y="Cancelamentos",
                title="Total de Cancelamentos por Profissional",
                text_auto=True,
            )
            st.plotly_chart(fig_cancel_prof, use_container_width=True)
        else:
            st.info("Nenhum cancelamento registrado para os filtros selecionados.")
else:
    st.warning("Nenhum dado de status encontrado para os filtros selecionados.")

st.markdown("---")


# Pergunta 3: Quais são os dias da semana e horários de maior movimento?
st.subheader("Fluxo de Clientes")
if df_filtrado.empty:
    st.warning(
        "Nenhum dado de fluxo de clientes encontrado para os filtros selecionados."
    )
else:
    col_fluxo1, col_fluxo2 = st.columns(2)
    with col_fluxo1:
        try:
            df_filtrado_dia = df_filtrado.copy()
            df_filtrado_dia["Dia da Semana"] = df_filtrado_dia["Data"].dt.day_name(
                locale="pt_BR.utf8"
            )
        except Exception:
            df_filtrado_dia["Dia da Semana"] = df_filtrado_dia["Data"].dt.day_name()

        agend_por_dia = df_filtrado_dia["Dia da Semana"].value_counts()
        if not agend_por_dia.empty:
            fig_fluxo_dia = px.bar(
                agend_por_dia,
                title="Agendamentos por Dia da Semana",
                labels={
                    "value": "Quantidade de Agendamentos",
                    "index": "Dia da Semana",
                },
                text_auto=True,
            )
            fig_fluxo_dia.update_layout(xaxis={"categoryorder": "total descending"})
            st.plotly_chart(fig_fluxo_dia, use_container_width=True)
        else:
            st.info(
                "Não há dados de agendamento por dia para exibir com os filtros atuais."
            )

    with col_fluxo2:
        horarios_validos = [
            "09:00:00",
            "09:40:00",
            "10:20:00",
            "11:00:00",
            "13:00:00",
            "13:40:00",
            "14:20:00",
            "15:00:00",
            "15:40:00",
            "16:20:00",
            "17:00:00",
            "17:40:00",
            "18:20:00",
            "19:00:00",
        ]
        df_filtrado_horas = df_filtrado.copy()
        df_filtrado_horas["Horário"] = df_filtrado_horas["Horário"].astype(str)
        df_horarios_filtrados = df_filtrado_horas[
            df_filtrado_horas["Horário"].isin(horarios_validos)
        ]
        agend_por_hora = df_horarios_filtrados["Horário"].value_counts().sort_index()

        if not agend_por_hora.empty:
            fig_fluxo_hora = px.bar(
                agend_por_hora,
                title="Agendamentos por Horário (Horas Selecionadas)",
                labels={"value": "Quantidade de Agendamentos", "index": "Horário"},
                text_auto=True,
            )
            st.plotly_chart(fig_fluxo_hora, use_container_width=True)
        else:
            st.info("Sem dados de agendamento para os horários selecionados.")

st.markdown("---")

# Pergunta 5: Quem são os clientes mais frequentes?
st.subheader("Top Clientes por Período")
if not df_realizado.empty:
    df_clientes_reais = df_realizado[df_realizado["Cliente"] != "Sem Cadastro"]
    if not df_clientes_reais.empty:
        top_clientes = (
            df_clientes_reais["Cliente"].value_counts().nlargest(10).reset_index()
        )
        top_clientes.columns = ["Cliente", "Nº de Visitas"]
        st.dataframe(top_clientes, use_container_width=True, hide_index=True)
    else:
        st.info(
            "Nenhum cliente (exceto 'Sem Cadastro') encontrado com os filtros atuais."
        )
else:
    st.info("Não há agendamentos realizados para exibir a lista de clientes.")
