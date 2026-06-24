#core.py

import datetime

import pandas as pd
import streamlit as st
from geopy.distance import geodesic

from config import (
    C_OBRA, C_COD_CRM, C_REGIONAL, C_CIDADE, C_CLUSTER,
    C_DATA_FUND, C_DATA_TERRA, C_DATA_ENCERR,
    C_COMPLEXIDADE_BASE, C_SENIORIDADE, C_LINHA, C_RESP1,
    C_ID_EMP, C_NOME_EMP, C_CIDADE_EMP, C_CLUSTER_EMP,
    C_FUND_EMP, C_TERRA_EMP, C_ENCERR_EMP, C_COMPLEXIDADE_EMP, C_REGIONAL_EMP,
    C_PROX_OBRA, C_ID_PROX, C_TERRA_PROX, C_ENCERR_PROX,
    C_CIDADE_PROX, C_ORIGEM, C_LATENCIA, C_DISTANCIA, C_FONTE_PROX,
)
from utils import sigla_senioridade, complexidades_permitidas_para, _normalizar


def montar_linha(row) -> str:
    cluster = str(row[C_CLUSTER]).strip()       if pd.notna(row[C_CLUSTER])    else ""
    sigla   = sigla_senioridade(row[C_SENIORIDADE])
    resp1   = str(row[C_RESP1]).strip().upper() if pd.notna(row[C_RESP1])      else ""
    partes  = [p for p in [cluster, sigla, resp1] if p != ""]
    return " | ".join(partes)


def resolver_simultaneidade(df_base):
    ids_devolvidos  = set()
    info_devolvidas = []
    indices_manter  = []

    for linha_id, grupo in df_base.groupby(C_LINHA):
        if len(grupo) == 1:
            indices_manter.append(grupo.index[0])
            continue
        grupo_valido = grupo[grupo[C_DATA_ENCERR].notna()]
        if grupo_valido.empty:
            indices_manter.append(grupo.index[0])
            continue
        idx_max = grupo_valido[C_DATA_ENCERR].idxmax()
        indices_manter.append(idx_max)
        for idx, row in grupo.iterrows():
            if idx == idx_max:
                continue
            cod = str(row.get(C_COD_CRM, "")).strip()
            if cod:
                ids_devolvidos.add(cod)
            info_devolvidas.append({
                "_idx_original": idx,
                "_linha_id":     linha_id,
                "_cod_crm":      cod,
                "_row":          row,
            })

    df_representantes = df_base.loc[indices_manter].copy()
    return df_representantes, ids_devolvidos, info_devolvidas


def _aplicar_filtros_candidatas(cands, permitidas, coord_atual, coord_cache,
                                 fim_atual, latencia_maxima_dias):
    if permitidas:
        cands = cands[cands["_complexidade_norm"].isin(permitidas)].copy()
    if cands.empty:
        return cands

    cands["_dist"] = cands[C_CIDADE_EMP].apply(
        lambda cid_b: geodesic(coord_atual, coord_cache.get(cid_b)).kilometers
        if coord_atual and coord_cache.get(cid_b) else 9999.0
    )
    cands = cands[cands["_dist"] <= 200].copy()
    if cands.empty:
        return cands

    cands["_gap"] = (cands[C_TERRA_EMP] - fim_atual).dt.days
    cands = cands[cands["_gap"] <= latencia_maxima_dias].copy()

    return cands


def sequenciar_linhas_existentes(df_base_repr, df_emp, coord_cache, info_devolvidas,
                                  latencia_maxima_dias=90,
                                  nomes_base_completo=None,
                                  ids_base_completo=None):

    df_candidatas = df_emp[
        df_emp[C_TERRA_EMP].notna() &
        df_emp[C_ENCERR_EMP].notna() &
        df_emp[C_CIDADE_EMP].notna() &
        (df_emp[C_TERRA_EMP] >= pd.Timestamp(datetime.date.today()))
    ].copy()

    df_candidatas["_complexidade_norm"] = df_candidatas[C_COMPLEXIDADE_EMP].apply(
        lambda x: _normalizar(str(x).strip()) if pd.notna(x) and str(x).strip() != "" else ""
    )

    for col in [C_PROX_OBRA, C_ID_PROX, C_TERRA_PROX, C_ENCERR_PROX,
                C_CIDADE_PROX, C_ORIGEM, C_LATENCIA, C_DISTANCIA, C_FONTE_PROX]:
        if col not in df_base_repr.columns:
            df_base_repr[col] = None

    ids_base = set(df_base_repr[C_COD_CRM].dropna().astype(str).str.strip().unique())
    if ids_base_completo:
        ids_base |= ids_base_completo

    mask_dh = df_base_repr[C_PROX_OBRA].notna() & (df_base_repr[C_PROX_OBRA].astype(str).str.strip() != "")
    df_base_repr.loc[mask_dh, C_FONTE_PROX] = "DH"
    df_base_repr.loc[mask_dh, C_ORIGEM]     = "Sequenciamento DH"

    obras_alocadas = set(df_base_repr[C_ID_PROX].dropna().astype(str).str.strip().unique())
    obras_alocadas |= ids_base

    nomes_dh = set(
        df_base_repr.loc[
            df_base_repr[C_PROX_OBRA].notna() &
            (df_base_repr[C_PROX_OBRA].astype(str).str.strip() != ""),
            C_PROX_OBRA
        ].astype(str).str.strip().unique()
    )
    ids_dh_por_nome = set(
        df_emp.loc[
            df_emp[C_NOME_EMP].astype(str).str.strip().isin(nomes_dh),
            C_ID_EMP
        ].astype(str).str.strip().unique()
    )
    obras_alocadas |= ids_dh_por_nome

    nomes_obra_a = set(df_base_repr[C_OBRA].dropna().astype(str).str.strip().unique())
    if nomes_base_completo:
        nomes_obra_a |= nomes_base_completo

    ids_obra_a_por_nome = set(
        df_emp.loc[
            df_emp[C_NOME_EMP].astype(str).str.strip().isin(nomes_obra_a),
            C_ID_EMP
        ].astype(str).str.strip().unique()
    )
    obras_alocadas |= ids_obra_a_por_nome

    df_candidatas = df_candidatas[
        ~df_candidatas[C_ID_EMP].astype(str).str.strip().isin(obras_alocadas)
    ].copy()

    barra      = st.progress(0)
    status_seq = st.empty()
    total      = len(df_base_repr)

    for idx, (i, row) in enumerate(df_base_repr.iterrows()):
        status_seq.text(f"🔄 Sequenciando linhas existentes: {row[C_OBRA]} ({idx+1}/{total})")
        barra.progress((idx + 1) / total)

        if pd.notna(row[C_PROX_OBRA]) and str(row[C_PROX_OBRA]).strip() != "":
            continue

        fim_atual  = row[C_DATA_ENCERR]
        cid_atual  = row[C_CIDADE]
        clu_atual  = row[C_CLUSTER]
        sen_atual  = row[C_SENIORIDADE]

        if pd.isna(fim_atual) or pd.isna(cid_atual) or pd.isna(clu_atual):
            continue

        permitidas  = complexidades_permitidas_para(sen_atual)
        coord_atual = coord_cache.get(cid_atual)

        cands = df_candidatas[
            (df_candidatas[C_TERRA_EMP] >= fim_atual) &
            (df_candidatas[C_CLUSTER_EMP] == clu_atual) &
            (~df_candidatas[C_ID_EMP].astype(str).str.strip().isin(obras_alocadas))
        ].copy()

        cands        = _aplicar_filtros_candidatas(cands, permitidas, coord_atual,
                                                   coord_cache, fim_atual, latencia_maxima_dias)
        cluster_diff = False

        if cands.empty:
            cands = df_candidatas[
                (df_candidatas[C_TERRA_EMP] >= fim_atual) &
                (df_candidatas[C_CLUSTER_EMP] != clu_atual) &
                (~df_candidatas[C_ID_EMP].astype(str).str.strip().isin(obras_alocadas))
            ].copy()
            cands        = _aplicar_filtros_candidatas(cands, permitidas, coord_atual,
                                                       coord_cache, fim_atual, latencia_maxima_dias)
            cluster_diff = True

        if cands.empty:
            continue

        res = cands.sort_values("_gap").iloc[0]

        origem_seq = (
            "Sequenciamento - ferramenta (cluster diferente)"
            if cluster_diff else
            "Sequenciamento - ferramenta"
        )

        df_base_repr.at[i, C_PROX_OBRA]   = res[C_NOME_EMP]
        df_base_repr.at[i, C_ID_PROX]     = res[C_ID_EMP]
        df_base_repr.at[i, C_TERRA_PROX]  = res[C_TERRA_EMP]
        df_base_repr.at[i, C_ENCERR_PROX] = res[C_ENCERR_EMP]
        df_base_repr.at[i, C_CIDADE_PROX] = res[C_CIDADE_EMP]
        df_base_repr.at[i, C_ORIGEM]      = origem_seq
        df_base_repr.at[i, C_LATENCIA]    = res["_gap"]
        df_base_repr.at[i, C_DISTANCIA]   = round(res["_dist"], 2)
        df_base_repr.at[i, C_FONTE_PROX]  = "Ferramenta"
        obras_alocadas.add(str(res[C_ID_EMP]).strip())

    status_seq.empty()
    barra.empty()

    nomes_dh_alocados = set(
        df_base_repr.loc[
            df_base_repr[C_FONTE_PROX] == "DH",
            C_PROX_OBRA
        ].dropna().astype(str).str.strip().unique()
    )
    nomes_dh_alocados |= nomes_obra_a

    return df_base_repr, obras_alocadas, nomes_dh_alocados


def sequenciar_novas_linhas(df_emp, coord_cache, obras_alocadas, info_devolvidas,
                             latencia_maxima_dias=90, nomes_dh_alocados=None):

    if nomes_dh_alocados:
        ids_bloqueados_por_nome = set(
            df_emp.loc[
                df_emp[C_NOME_EMP].astype(str).str.strip().isin(nomes_dh_alocados),
                C_ID_EMP
            ].astype(str).str.strip().unique()
        )
        obras_alocadas |= ids_bloqueados_por_nome

    df_candidatas = df_emp[
        df_emp[C_TERRA_EMP].notna() &
        df_emp[C_ENCERR_EMP].notna() &
        df_emp[C_CIDADE_EMP].notna() &
        (df_emp[C_TERRA_EMP] >= pd.Timestamp(datetime.date.today()))
    ].copy()

    df_candidatas["_complexidade_norm"] = df_candidatas[C_COMPLEXIDADE_EMP].apply(
        lambda x: _normalizar(str(x).strip()) if pd.notna(x) and str(x).strip() != "" else ""
    )

    obras_nao_alocadas = df_candidatas[
        ~df_candidatas[C_ID_EMP].astype(str).str.strip().isin(obras_alocadas)
    ].copy()

    ids_devolvidos_validos = {
        d["_cod_crm"] for d in info_devolvidas
        if d["_cod_crm"]
        and d["_cod_crm"] not in obras_alocadas
        and str(d["_row"].get(C_OBRA, "")).strip() not in (nomes_dh_alocados or set())
    }

    if ids_devolvidos_validos:
        df_devolvidas_emp = df_emp[
            df_emp[C_ID_EMP].astype(str).str.strip().isin(ids_devolvidos_validos)
        ].copy()
        df_devolvidas_emp["_complexidade_norm"] = df_devolvidas_emp[C_COMPLEXIDADE_EMP].apply(
            lambda x: _normalizar(str(x).strip()) if pd.notna(x) and str(x).strip() != "" else ""
        )
        obras_nao_alocadas = pd.concat([df_devolvidas_emp, obras_nao_alocadas], ignore_index=True)
        obras_nao_alocadas = obras_nao_alocadas.drop_duplicates(subset=[C_ID_EMP])

    novas_linhas_rows     = []
    contador_novas_linhas = {}
    novas_linhas_dict     = {}

    if obras_nao_alocadas.empty:
        return pd.DataFrame(columns=[
            "Linha", "Ordem", "OBRA", "Cód. CRM", "Regional", "Cidade", "CLUSTER",
            "Complexidade Obra", "Data Fundação", "Data Terraplenagem",
            "Data Encerramento Módulo", "Fonte da Próxima Obra",
            "Origem Sequenciamento", "Latência (Dias)", "Distância (km)"
        ])

    st.info(f"🔁 {len(obras_nao_alocadas)} empreendimento(s) no pool — criando novas linhas por cluster...")

    obras_nao_alocadas_sorted = obras_nao_alocadas.sort_values(C_TERRA_EMP)
    barra2      = st.progress(0)
    status_seq2 = st.empty()
    total2      = len(obras_nao_alocadas_sorted)

    for idx2, (_, emp_row) in enumerate(obras_nao_alocadas_sorted.iterrows()):
        status_seq2.text(f"🆕 Criando novas linhas: {emp_row[C_NOME_EMP]} ({idx2+1}/{total2})")
        barra2.progress((idx2 + 1) / total2)

        cluster_emp = str(emp_row.get(C_CLUSTER_EMP, "")).strip()
        id_emp      = str(emp_row[C_ID_EMP]).strip()

        if id_emp in obras_alocadas:
            continue

        if nomes_dh_alocados and str(emp_row.get(C_NOME_EMP, "")).strip() in nomes_dh_alocados:
            continue

        linha_nova_key = None
        melhor_gap     = None

        for key, info in novas_linhas_dict.items():
            if info["cluster"] != cluster_emp:
                continue
            ultimo_encerr = info["ultimo_encerr"]
            if pd.isna(ultimo_encerr) or ultimo_encerr is None:
                continue
            if emp_row[C_TERRA_EMP] < ultimo_encerr:
                continue
            gap       = (emp_row[C_TERRA_EMP] - ultimo_encerr).days
            if gap > latencia_maxima_dias:
                continue
            coord_ult = coord_cache.get(info["ultima_cidade"])
            coord_emp = coord_cache.get(str(emp_row.get(C_CIDADE_EMP, "")))
            dist      = geodesic(coord_ult, coord_emp).kilometers if coord_ult and coord_emp else 9999.0
            if dist > 200:
                continue
            if melhor_gap is None or gap < melhor_gap:
                melhor_gap     = gap
                linha_nova_key = key

        if linha_nova_key is None:
            if cluster_emp not in contador_novas_linhas:
                contador_novas_linhas[cluster_emp] = 0
            contador_novas_linhas[cluster_emp] += 1
            num            = contador_novas_linhas[cluster_emp]
            linha_nova_key = f"{cluster_emp} | Linha nova {num}"
            novas_linhas_dict[linha_nova_key] = {
                "cluster":       cluster_emp,
                "ultimo_encerr": None,
                "ultima_cidade": None,
                "ordem":         0,
            }

        info          = novas_linhas_dict[linha_nova_key]
        ordem_emp     = info["ordem"] + 1
        ultimo_encerr = info["ultimo_encerr"]
        ultima_cidade = info["ultima_cidade"]

        if ultimo_encerr is not None and pd.notna(ultimo_encerr):
            gap_dias  = (emp_row[C_TERRA_EMP] - ultimo_encerr).days
            coord_ult = coord_cache.get(str(ultima_cidade))
            coord_emp = coord_cache.get(str(emp_row.get(C_CIDADE_EMP, "")))
            dist_km   = round(geodesic(coord_ult, coord_emp).kilometers, 2) if coord_ult and coord_emp else None
        else:
            gap_dias = None
            dist_km  = None

        novas_linhas_rows.append({
            "Linha":                    linha_nova_key,
            "Ordem":                    ordem_emp,
            "OBRA":                     emp_row.get(C_NOME_EMP),
            "Cód. CRM":                 emp_row.get(C_ID_EMP),
            "Regional":                 emp_row.get(C_REGIONAL_EMP),
            "Cidade":                   emp_row.get(C_CIDADE_EMP),
            "CLUSTER":                  cluster_emp,
            "Complexidade Obra":        emp_row.get(C_COMPLEXIDADE_EMP),
            "Data Fundação":            emp_row.get(C_FUND_EMP),
            "Data Terraplenagem":       emp_row.get(C_TERRA_EMP),
            "Data Encerramento Módulo": emp_row.get(C_ENCERR_EMP),
            "Fonte da Próxima Obra":    None,
            "Origem Sequenciamento":    "Sequenciamento - ferramenta",
            "Latência (Dias)":          gap_dias,
            "Distância (km)":           dist_km,
        })

        novas_linhas_dict[linha_nova_key]["ultimo_encerr"] = emp_row[C_ENCERR_EMP]
        novas_linhas_dict[linha_nova_key]["ultima_cidade"] = emp_row.get(C_CIDADE_EMP)
        novas_linhas_dict[linha_nova_key]["ordem"]         = ordem_emp
        obras_alocadas.add(id_emp)

    barra2.empty()
    status_seq2.empty()

    return pd.DataFrame(novas_linhas_rows)


def montar_output_empilhado(df_base_repr, df_simultaneas, df_novas_linhas, mapa_emp, marco_inicio_obra_a):
    colunas_saida = [
        "Linha", "Tipo de Linha", "Ordem", "OBRA", "Cód. CRM", "Regional", "Cidade", "CLUSTER",
        "Complexidade Obra", "Senioridade ENG1",
        "Data Fundação", "Data Terraplenagem", "Data Encerramento Módulo",
        "Marco Início Obra A", "Simultaneidade",
        "Fonte da Próxima Obra", "Origem Sequenciamento",
        "Latência (Dias)", "Distância (km)",
    ]

    c_marco_base = C_DATA_TERRA if marco_inicio_obra_a == "Terraplenagem" else C_DATA_FUND
    linhas = []

    for _, row in df_base_repr.iterrows():
        linha_id    = row[C_LINHA]
        marco_valor = row.get(c_marco_base) if c_marco_base in df_base_repr.columns else None

        linhas.append({
            "Linha":                    linha_id,
            "Tipo de Linha":            "Existente",
            "Ordem":                    1,
            "OBRA":                     row.get(C_OBRA),
            "Cód. CRM":                 row.get(C_COD_CRM),
            "Regional":                 row.get(C_REGIONAL),
            "Cidade":                   row.get(C_CIDADE),
            "CLUSTER":                  row.get(C_CLUSTER),
            "Complexidade Obra":        row.get(C_COMPLEXIDADE_BASE),
            "Senioridade ENG1":         row.get(C_SENIORIDADE),
            "Data Fundação":            row.get(C_DATA_FUND),
            "Data Terraplenagem":       row.get(C_DATA_TERRA),
            "Data Encerramento Módulo": row.get(C_DATA_ENCERR),
            "Marco Início Obra A":      marco_valor,
            "Simultaneidade":           None,
            "Fonte da Próxima Obra":    None,
            "Origem Sequenciamento":    None,
            "Latência (Dias)":          None,
            "Distância (km)":           None,
        })

        tem_prox = pd.notna(row.get(C_PROX_OBRA)) and str(row.get(C_PROX_OBRA, "")).strip() != ""
        if not tem_prox:
            continue

        id_prox    = row.get(C_ID_PROX)
        emp_match  = mapa_emp.get(id_prox, {})
        fonte_prox = row.get(C_FONTE_PROX)

        linhas.append({
            "Linha":                    linha_id,
            "Tipo de Linha":            "Existente",
            "Ordem":                    2,
            "OBRA":                     row.get(C_PROX_OBRA),
            "Cód. CRM":                 id_prox,
            "Regional":                 emp_match.get(C_REGIONAL),
            "Cidade":                   row.get(C_CIDADE_PROX),
            "CLUSTER":                  emp_match.get(C_CLUSTER_EMP),
            "Complexidade Obra":        emp_match.get(C_COMPLEXIDADE_EMP),
            "Senioridade ENG1":         None,
            "Data Fundação":            emp_match.get(C_FUND_EMP),
            "Data Terraplenagem":       row.get(C_TERRA_PROX),
            "Data Encerramento Módulo": row.get(C_ENCERR_PROX),
            "Marco Início Obra A":      None,
            "Simultaneidade":           None,
            "Fonte da Próxima Obra":    fonte_prox,
            "Origem Sequenciamento":    row.get(C_ORIGEM),
            "Latência (Dias)":          row.get(C_LATENCIA),
            "Distância (km)":           row.get(C_DISTANCIA),
        })

    for item in df_simultaneas:
        row             = item["_row"]
        marco_valor_sim = row.get(c_marco_base) if c_marco_base in row.index else None
        linhas.append({
            "Linha":                    item["_linha_id"],
            "Tipo de Linha":            "Existente",
            "Ordem":                    1,
            "OBRA":                     row.get(C_OBRA),
            "Cód. CRM":                 row.get(C_COD_CRM),
            "Regional":                 row.get(C_REGIONAL),
            "Cidade":                   row.get(C_CIDADE),
            "CLUSTER":                  row.get(C_CLUSTER),
            "Complexidade Obra":        row.get(C_COMPLEXIDADE_BASE),
            "Senioridade ENG1":         row.get(C_SENIORIDADE),
            "Data Fundação":            row.get(C_DATA_FUND),
            "Data Terraplenagem":       row.get(C_DATA_TERRA),
            "Data Encerramento Módulo": row.get(C_DATA_ENCERR),
            "Marco Início Obra A":      marco_valor_sim,
            "Simultaneidade":           "Sim — devolvida ao pool",
            "Fonte da Próxima Obra":    None,
            "Origem Sequenciamento":    None,
            "Latência (Dias)":          None,
            "Distância (km)":           None,
        })

    for _, row in df_novas_linhas.iterrows():
        linhas.append({
            "Linha":                    row["Linha"],
            "Tipo de Linha":            "Nova",
            "Ordem":                    row["Ordem"],
            "OBRA":                     row["OBRA"],
            "Cód. CRM":                 row["Cód. CRM"],
            "Regional":                 row["Regional"],
            "Cidade":                   row["Cidade"],
            "CLUSTER":                  row["CLUSTER"],
            "Complexidade Obra":        row["Complexidade Obra"],
            "Senioridade ENG1":         None,
            "Data Fundação":            row["Data Fundação"],
            "Data Terraplenagem":       row["Data Terraplenagem"],
            "Data Encerramento Módulo": row["Data Encerramento Módulo"],
            "Marco Início Obra A":      None,
            "Simultaneidade":           None,
            "Fonte da Próxima Obra":    row["Fonte da Próxima Obra"],
            "Origem Sequenciamento":    row["Origem Sequenciamento"],
            "Latência (Dias)":          row["Latência (Dias)"],
            "Distância (km)":           row["Distância (km)"],
        })

    return pd.DataFrame(linhas, columns=colunas_saida)
