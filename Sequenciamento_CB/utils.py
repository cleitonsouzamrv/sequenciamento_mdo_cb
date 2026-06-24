import datetime
import json
import os
import time
import unicodedata

import pandas as pd
import streamlit as st
from geopy.geocoders import Nominatim

from config import COMPLEXIDADES_PERMITIDAS, COLUNAS_ESPERADAS

CACHE_FILE = "cache_coordenadas.json"


def _normalizar(texto: str) -> str:
    nfkd = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
    return sem_acento.upper()


def sigla_senioridade(valor) -> str:
    if pd.isna(valor) or str(valor).strip() == "":
        return ""
    v = _normalizar(str(valor).strip())
    if "ENGENHEIRO" in v or "ENGENHEIRA" in v:
        return "EN"
    if "ANALISTA" in v:
        return "AN"
    return ""


def nivel_senioridade(valor) -> str:
    if pd.isna(valor) or str(valor).strip() == "":
        return ""
    v = _normalizar(str(valor).strip())
    if v.endswith("JUNIOR"):
        return "JUNIOR"
    if v.endswith("PLENO"):
        return "PLENO"
    if v.endswith("SENIOR"):
        return "SENIOR"
    return ""


def complexidades_permitidas_para(valor_senioridade) -> set:
    nivel = nivel_senioridade(valor_senioridade)
    return COMPLEXIDADES_PERMITIDAS.get(nivel, set())


def converter_data_mrv(data_str):
    if isinstance(data_str, datetime.time):
        return None
    if pd.isna(data_str) or str(data_str).strip() == "":
        return None
    if isinstance(data_str, (datetime.datetime, pd.Timestamp)):
        return data_str
    meses_map = {
        'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04',
        'mai': '05', 'jun': '06', 'jul': '07', 'ago': '08',
        'set': '09', 'out': '10', 'nov': '11', 'dez': '12'
    }
    try:
        s = str(data_str).lower().replace('/', ' ').split()
        if len(s) == 3:
            dia = s[0].zfill(2)
            mes = meses_map.get(s[1], "01")
            ano = s[2]
            if len(ano) == 2:
                ano = "20" + ano
            return pd.to_datetime(f"{ano}-{mes}-{dia}")
    except:
        return pd.to_datetime(data_str, errors='coerce')
    return pd.to_datetime(data_str, errors='coerce')


def carregar_tabela_blindada(file, sheet_name, coluna_referencia):
    df_cru = pd.read_excel(file, sheet_name=sheet_name, header=None)
    linha_cabecalho = None
    for i, row in df_cru.iterrows():
        if coluna_referencia in [str(val).strip() for val in row.values]:
            linha_cabecalho = i
            break
    if linha_cabecalho is not None:
        df = pd.read_excel(file, sheet_name=sheet_name, skiprows=linha_cabecalho)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    return pd.read_excel(file, sheet_name=sheet_name)


def validar_colunas(df, aba) -> list:
    obrigatorias = [c["coluna"] for c in COLUNAS_ESPERADAS[aba]["colunas"] if c["obrigatorio"] == "✅"]
    return [c for c in obrigatorias if c not in df.columns]


def _carregar_cache_disco() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _salvar_cache_disco(cache: dict):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


@st.cache_data
def obter_dicionario_coordenadas(lista_cidades) -> dict:
    cache_disco   = _carregar_cache_disco()
    geolocator    = Nominatim(user_agent="mrv_sequenciador_v12")
    mapa_coords   = dict(cache_disco)
    cidades_novas = [c for c in lista_cidades if c not in cache_disco]

    if not cidades_novas:
        return mapa_coords

    prog   = st.progress(0)
    status = st.empty()

    for i, cidade in enumerate(cidades_novas):
        status.text(f"🌍 Obtendo coordenadas: {cidade} ({i+1}/{len(cidades_novas)})")
        try:
            location = geolocator.geocode(f"{cidade}, Brasil", timeout=10)
            mapa_coords[cidade] = (
                [location.latitude, location.longitude] if location else None
            )
            time.sleep(1.1)
        except:
            mapa_coords[cidade] = None
        prog.progress((i + 1) / len(cidades_novas))

    _salvar_cache_disco(mapa_coords)
    status.empty()
    prog.empty()
    return mapa_coords
