#ui.py

import io

import pandas as pd
import streamlit as st

from config import COLUNAS_ESPERADAS, COLUNAS_GERADAS, LEGENDA


def render_guia_colunas():
    with st.expander("📋 Ver estrutura esperada das planilhas (clique para expandir)", expanded=False):
        st.markdown("### 📌 Legenda de Obrigatoriedade")
        cols_leg = st.columns(2)
        for idx, (icone, desc) in enumerate(LEGENDA.items()):
            cols_leg[idx].info(f"**{icone}**\n\n{desc}")
        st.divider()
        icones_aba = {"Base": "📄 Planilha 1 — Base", "Sheet1": "📄 Planilha 2 — Todos Empreendimentos"}
        for aba, info in COLUNAS_ESPERADAS.items():
            st.markdown(f"### 🗂️ {icones_aba[aba]} › Guia: `{aba}`")
            st.caption(info["descricao"])
            df_cols         = pd.DataFrame(info["colunas"])
            df_cols.columns = ["Coluna", "Tipo de Dado", "Obrigatório", "Descrição"]
            def colorir_linha(row):
                if row["Obrigatório"] == "✅":
                    return ["background-color: #e6f4ea"] * len(row)
                return ["background-color: #f1f3f4"] * len(row)
            st.dataframe(
                df_cols.style.apply(colorir_linha, axis=1),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Coluna":       st.column_config.TextColumn("Coluna",       width="medium"),
                    "Tipo de Dado": st.column_config.TextColumn("Tipo de Dado", width="small"),
                    "Obrigatório":  st.column_config.TextColumn("Obrigatório",  width="small"),
                    "Descrição":    st.column_config.TextColumn("Descrição",    width="large"),
                }
            )
            st.markdown("")
        st.divider()
        st.markdown("### ⚙️ Colunas geradas automaticamente pelo sequenciador")
        st.caption("Adicionadas na planilha de saída — não precisam existir nas planilhas originais.")
        df_geradas         = pd.DataFrame(COLUNAS_GERADAS)
        df_geradas.columns = ["Coluna", "Tipo de Dado", "Descrição"]
        st.dataframe(
            df_geradas.style.apply(lambda row: ["background-color: #fff8e1"] * len(row), axis=1),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Coluna":       st.column_config.TextColumn("Coluna",       width="medium"),
                "Tipo de Dado": st.column_config.TextColumn("Tipo de Dado", width="small"),
                "Descrição":    st.column_config.TextColumn("Descrição",    width="large"),
            }
        )
        st.markdown(
            "💡 **Regra de complexidade:** JUNIOR → apenas NÃO COMPLEXO | "
            "PLENO → NÃO COMPLEXO e MÉDIO | SENIOR → qualquer complexidade. "
            "**Simultaneidade:** quando uma linha possui N obras ao mesmo tempo, apenas a de maior encerramento "
            "é mantida ativa para sequenciamento; as demais são devolvidas ao pool de novas linhas."
        )


def render_upload():
    col_up1, col_up2 = st.columns(2)
    with col_up1:
        st.markdown("#### 📄 Planilha 1 — Base")
        st.caption("Deve conter a guia **Base** com os engenheiros e obras atuais.")
        arquivo_base = st.file_uploader("Suba a planilha Base aqui", type=["xlsx"], key="upload_base")
    with col_up2:
        st.markdown("#### 📄 Planilha 2 — Todos Empreendimentos")
        st.caption("Deve conter a guia **Sheet1** com o catálogo de obras candidatas.")
        arquivo_empreendimentos = st.file_uploader("Suba a planilha de Empreendimentos aqui", type=["xlsx"], key="upload_emp")

    if arquivo_base and not arquivo_empreendimentos:
        st.info("⏳ Aguardando o upload da **Planilha 2 — Todos Empreendimentos** para continuar.")
    if arquivo_empreendimentos and not arquivo_base:
        st.info("⏳ Aguardando o upload da **Planilha 1 — Base** para continuar.")

    return arquivo_base, arquivo_empreendimentos


def render_preview(df_base, df_emp):
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.success(f"✅ Base carregada — {len(df_base)} registros")
        with st.expander("🔍 Pré-visualização — Base", expanded=False):
            st.dataframe(df_base, use_container_width=True)
    with col_info2:
        st.success(f"✅ Empreendimentos carregados — {len(df_emp)} registros")
        with st.expander("🔍 Pré-visualização — Sheet1", expanded=False):
            st.dataframe(df_emp, use_container_width=True)


def render_configuracao_marco() -> str:
    st.markdown("#### ⚙️ Configuração do Marco de Início da Obra A")
    st.caption(
        "Selecione qual data será usada como **marco de início** da Obra A (linhas existentes, Ordem 1). "
        "Essa data será exibida na coluna **'Marco Início Obra A'** no resultado."
    )
    marco = st.radio(
        label="Marco de início da Obra A:",
        options=["Terraplenagem", "Fundação"],
        index=1,
        horizontal=True,
        help=(
            "**Terraplenagem** → usa a coluna 'Data Terraplenagem' da guia Base.\n\n"
            "**Fundação** → usa a coluna 'Data Fundação' da guia Base."
        ),
        key="marco_inicio_obra_a"
    )
    if marco == "Terraplenagem":
        st.info("📌 Marco selecionado: **Terraplenagem** — coluna `Data Terraplenagem` (guia Base)")
    else:
        st.info("📌 Marco selecionado: **Fundação** — coluna `Data Fundação` (guia Base)")
    return marco


def render_filtro_latencia() -> int:
    st.markdown("#### ⏱️ Tempo máximo de prateleira (latência)")
    st.caption(
        "Define o intervalo máximo (em meses) entre o **término da Obra A** "
        "e o **início da Obra B**. Obras com gap maior serão ignoradas no sequenciamento."
    )
    meses = st.selectbox(
        label="Latência máxima permitida:",
        options=[3, 4, 5, 6, 7],
        index=0,
        format_func=lambda x: f"{x} mês" if x == 1 else f"{x} meses",
        key="filtro_latencia"
    )
    st.info(f"📌 Latência máxima: **{meses} meses** ({meses * 30} dias)")
    return meses


def render_filtro_senioridade() -> bool:
    st.markdown("#### 🎓 Filtro de Senioridade e Complexidade")
    st.caption(
        "Quando ativado, o sequenciador respeita a regra de complexidade por senioridade: "
        "JUNIOR → apenas NÃO COMPLEXO | PLENO → NÃO COMPLEXO e MÉDIO | SENIOR → qualquer complexidade. "
        "Quando desativado, esse critério é ignorado e apenas distância, cluster e latência são considerados."
    )
    usar = st.checkbox(
        label="Considerar senioridade e complexidade no sequenciamento",
        value=True,
        key="filtro_senioridade",
        help=(
            "✅ **Marcado** → aplica o filtro de complexidade conforme a senioridade do ENG1.\n\n"
            "☐ **Desmarcado** → ignora complexidade; sequencia usando apenas cluster, "
            "distância (≤ 200 km) e latência."
        ),
    )
    if usar:
        st.info("📌 Senioridade/complexidade: **ativada** — regras de complexidade serão aplicadas.")
    else:
        st.warning("📌 Senioridade/complexidade: **desativada** — obras serão sequenciadas sem restrição de complexidade.")
    return usar


# ── NOVO ──────────────────────────────────────────────────────────────────────
def render_filtro_distancia_cluster() -> tuple[int, bool]:
    st.markdown("#### 📍 Distância máxima e cluster")
    st.caption(
        "Define o raio máximo (em km) entre a obra atual e a próxima obra candidata, "
        "e se o sequenciador pode sugerir obras de **cluster diferente** como fallback "
        "quando não houver candidatas no mesmo cluster."
    )

    col_dist, col_cluster = st.columns(2)

    with col_dist:
        distancia_km = st.number_input(
            label="Distância máxima entre obras (km):",
            min_value=25,
            max_value=1000,
            value=50,
            step=25,
            key="filtro_distancia_km",
            help="Obras em cidades com distância superior a esse valor serão ignoradas no sequenciamento.",
        )
        st.info(f"📌 Distância máxima: **{distancia_km} km**")

    with col_cluster:
        permitir_cluster_diferente = st.checkbox(
            label="Permitir obras de cluster diferente",
            value=True,
            key="filtro_cluster_diferente",
            help=(
                "✅ **Marcado** → se não houver candidatas no mesmo cluster, "
                "o sequenciador tenta obras de outros clusters (dentro do raio e latência).\n\n"
                "☐ **Desmarcado** → apenas obras do mesmo cluster são consideradas."
            ),
        )
        if permitir_cluster_diferente:
            st.info("📌 Cluster diferente: **permitido** — usado como fallback quando necessário.")
        else:
            st.warning("📌 Cluster diferente: **bloqueado** — apenas obras do mesmo cluster serão sugeridas.")

    return distancia_km, permitir_cluster_diferente
# ──────────────────────────────────────────────────────────────────────────────


def render_botao_iniciar() -> bool:
    col_btn, col_status = st.columns([1, 3])
    with col_btn:
        clicou = st.button(
            label="▶️ Iniciar Sequenciamento",
            type="primary",
            key="btn_iniciar"
        )
    if clicou:
        st.session_state["sequenciamento_rodando"] = True
    if not st.session_state.get("sequenciamento_rodando", False):
        with col_status:
            st.info("⏳ Configure o marco de início acima e clique em **▶️ Iniciar Sequenciamento** para começar.")
        return False
    return True


def render_diagnostico(df_base):
    from utils import sigla_senioridade, nivel_senioridade, complexidades_permitidas_para
    with st.expander("🔬 Diagnóstico: valores únicos de Senioridade ENG1", expanded=False):
        if "Senioridade ENG1" in df_base.columns:
            vals = df_base["Senioridade ENG1"].dropna().unique().tolist()
            st.write("Valores encontrados na coluna:", vals)
            for v in vals:
                st.write(
                    f"  `{v}` → sigla: **'{sigla_senioridade(v)}'** | "
                    f"nível: **'{nivel_senioridade(v)}'** | "
                    f"complexidades permitidas: **{complexidades_permitidas_para(v)}**"
                )
        else:
            st.warning("Coluna 'Senioridade ENG1' não encontrada na Base.")


def render_resultado(df_output):
    with st.expander("📊 Ver resultado — Output Empilhado por Linha", expanded=True):
        st.caption(
            "🔑 **Linha** é o pivot. "
            "**Tipo de Linha**: `Existente` = veio da guia Base | `Nova` = criada pelo app. "
            "**Marco Início Obra A**: data usada como início da Obra A conforme seleção do usuário. "
            "**Simultaneidade**: `Sim — devolvida ao pool` = obra estava simultânea e foi redistribuída. "
            "**Fonte da Próxima Obra**: `DH` = veio da guia Base | `Ferramenta` = sugerida pelo app. "
            "**Origem Sequenciamento**: `Sequenciamento DH` = já existia na Base | `Sequenciamento - ferramenta` = app sequenciou."
        )
        st.dataframe(
            df_output.sort_values(["Linha", "Ordem"], na_position="last"),
            use_container_width=True,
            hide_index=True,
        )

def render_download(df_output, df_emp):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_output.sort_values(["Linha", "Ordem"], na_position="last").to_excel(
            writer, sheet_name="Sequenciamento", index=False
        )
        df_emp.to_excel(writer, sheet_name="Todos Empreendimentos", index=False)
    st.download_button(
        label     = "📥 Baixar Planilha Sequenciada",
        data      = buffer.getvalue(),
        file_name = "Sequenciamento_MRV.xlsx",
        mime      = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
