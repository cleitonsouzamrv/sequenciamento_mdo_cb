#config.py

COMPLEXIDADES_PERMITIDAS = {
    "JUNIOR": {"NAO COMPLEXO"},
    "PLENO":  {"NAO COMPLEXO", "MEDIO"},
    "SENIOR": {"NAO COMPLEXO", "MEDIO", "COMPLEXO"},
}

LEGENDA = {
    "✅ Obrigatório":     "A coluna deve estar presente e preenchida para o sequenciamento funcionar.",
    "❌ Gerado pelo app": "Coluna criada/preenchida automaticamente pelo sequenciador.",
}

COLUNAS_ESPERADAS = {
    "Base": {
        "descricao": "Planilha principal com os empreendimentos, engenheiros e informações de sequenciamento.",
        "colunas": [
            {"coluna": "OBRA",                          "tipo": "Texto", "obrigatorio": "✅", "descricao": "Nome do empreendimento/obra"},
            {"coluna": "Cód. CRM",                      "tipo": "Texto", "obrigatorio": "✅", "descricao": "Código identificador da obra no CRM"},
            {"coluna": "Regional",                      "tipo": "Texto", "obrigatorio": "✅", "descricao": "Regional responsável pela obra"},
            {"coluna": "Cidade",                        "tipo": "Texto", "obrigatorio": "✅", "descricao": "Cidade onde a obra está localizada"},
            {"coluna": "CLUSTER",                       "tipo": "Texto", "obrigatorio": "✅", "descricao": "Cluster ao qual a obra pertence"},
            {"coluna": "AMP (abr)",                     "tipo": "Texto", "obrigatorio": "❌", "descricao": "Abreviação do AMP da obra"},
            {"coluna": "Status",                        "tipo": "Texto", "obrigatorio": "✅", "descricao": "Status atual da obra"},
            {"coluna": "Data Fundação",                 "tipo": "Data",  "obrigatorio": "✅", "descricao": "Data de fundação/início da obra"},
            {"coluna": "Data Terraplenagem",            "tipo": "Data",  "obrigatorio": "✅", "descricao": "Marco de início para o sequenciamento"},
            {"coluna": "Data Encerramento Módulo",      "tipo": "Data",  "obrigatorio": "✅", "descricao": "Marco de término para o sequenciamento"},
            {"coluna": "COMPLEXIDADE",                  "tipo": "Texto", "obrigatorio": "❌", "descricao": "Nível de complexidade da obra (NÃO COMPLEXO / MÉDIO / COMPLEXO)"},
            {"coluna": "Engenheiro 1",                  "tipo": "Texto", "obrigatorio": "✅", "descricao": "Nome do primeiro engenheiro responsável"},
            {"coluna": "Engenheiro 2",                  "tipo": "Texto", "obrigatorio": "❌", "descricao": "Nome do segundo engenheiro responsável (quando houver)"},
            {"coluna": "Engenheiro CRM",                "tipo": "Texto", "obrigatorio": "❌", "descricao": "Engenheiro registrado no CRM"},
            {"coluna": "Gestor CRM",                    "tipo": "Texto", "obrigatorio": "❌", "descricao": "Gestor registrado no CRM"},
            {"coluna": "Responsável 1",                 "tipo": "Texto", "obrigatorio": "✅", "descricao": "Responsável principal pela obra"},
            {"coluna": "Responsável 2 (quando houver)", "tipo": "Texto", "obrigatorio": "❌", "descricao": "Segundo responsável pela obra (quando houver)"},
            {"coluna": "Senioridade ENG1",              "tipo": "Texto", "obrigatorio": "❌", "descricao": "Nível de senioridade do Engenheiro 1"},
            {"coluna": "Senioridade ENG2",              "tipo": "Texto", "obrigatorio": "❌", "descricao": "Nível de senioridade do Engenheiro 2"},
            {"coluna": "Gestor",                        "tipo": "Texto", "obrigatorio": "❌", "descricao": "Gestor responsável pela obra"},
            {"coluna": "Observação",                    "tipo": "Texto", "obrigatorio": "❌", "descricao": "Observações gerais sobre a obra"},
        ]
    },
    "Sheet1": {
        "descricao": "Planilha de catálogo com todos os empreendimentos disponíveis para sequenciamento.",
        "colunas": [
            {"coluna": "Regional",            "tipo": "Texto", "obrigatorio": "✅", "descricao": "Regional responsável pelo empreendimento"},
            {"coluna": "IDTRSICRM",           "tipo": "Texto", "obrigatorio": "✅", "descricao": "Identificador único do empreendimento no CRM"},
            {"coluna": "Empreendimento",      "tipo": "Texto", "obrigatorio": "✅", "descricao": "Nome do empreendimento"},
            {"coluna": "CLUSTER_CORRIGIDO",   "tipo": "Texto", "obrigatorio": "✅", "descricao": "Cluster corrigido do empreendimento"},
            {"coluna": "CIDADE",              "tipo": "Texto", "obrigatorio": "✅", "descricao": "Cidade onde o empreendimento está localizado"},
            {"coluna": "Fundação",            "tipo": "Data",  "obrigatorio": "✅", "descricao": "Data prevista de início da fundação"},
            {"coluna": "Terraplenagem",       "tipo": "Data",  "obrigatorio": "✅", "descricao": "Marco de início para o sequenciamento"},
            {"coluna": "Encerramento Módulo", "tipo": "Data",  "obrigatorio": "✅", "descricao": "Marco de término — data prevista de encerramento do módulo"},
            {"coluna": "Complexidade",        "tipo": "Texto", "obrigatorio": "❌", "descricao": "Nível de complexidade da obra candidata"},
            {"coluna": "Nome Ref Ajuste",     "tipo": "Texto", "obrigatorio": "❌", "descricao": "Nome de referência para ajuste — informativo"},
        ]
    }
}

COLUNAS_GERADAS = [
    {"coluna": "Linha",                    "tipo": "Texto",  "descricao": "Pivot principal: CLUSTER | Sigla Senioridade | Responsável 1"},
    {"coluna": "Tipo de Linha",            "tipo": "Texto",  "descricao": "'Existente' = linha veio da guia Base | 'Nova' = linha criada pelo app"},
    {"coluna": "Ordem",                    "tipo": "Número", "descricao": "Sequência da obra dentro da linha (1 = atual/primeira, 2 = próxima, ...)"},
    {"coluna": "OBRA",                     "tipo": "Texto",  "descricao": "Nome da obra"},
    {"coluna": "Cód. CRM",                 "tipo": "Texto",  "descricao": "Código CRM da obra"},
    {"coluna": "Regional",                 "tipo": "Texto",  "descricao": "Regional da obra"},
    {"coluna": "Cidade",                   "tipo": "Texto",  "descricao": "Cidade da obra"},
    {"coluna": "CLUSTER",                  "tipo": "Texto",  "descricao": "Cluster da obra"},
    {"coluna": "Complexidade Obra",        "tipo": "Texto",  "descricao": "Nível de complexidade da obra"},
    {"coluna": "Senioridade ENG1",         "tipo": "Texto",  "descricao": "Senioridade do Engenheiro 1 (apenas Ordem 1 de linhas existentes)"},
    {"coluna": "Data Fundação",            "tipo": "Data",   "descricao": "Data de fundação da obra"},
    {"coluna": "Data Terraplenagem",       "tipo": "Data",   "descricao": "Data de terraplenagem — marco de início"},
    {"coluna": "Data Encerramento Módulo", "tipo": "Data",   "descricao": "Data de encerramento — marco de término"},
    {"coluna": "Marco Início Obra A",      "tipo": "Data",   "descricao": "Data usada como marco de início da Obra A (Terraplenagem ou Fundação, conforme seleção do usuário)"},
    {"coluna": "Simultaneidade",           "tipo": "Texto",  "descricao": "'Sim' = obra estava simultânea na linha e foi devolvida ao pool | vazio = fluxo normal"},
    {"coluna": "Fonte da Próxima Obra",    "tipo": "Texto",  "descricao": "'DH' = veio da guia Base | 'Ferramenta' = sugerida pelo app. Vazio para Ordem 1."},
    {"coluna": "Origem Sequenciamento",    "tipo": "Texto",  "descricao": "'Sequenciamento DH' = sequência já existia na Base | 'Sequenciamento - ferramenta' = sugerida pelo app"},
    {"coluna": "Latência (Dias)",          "tipo": "Número", "descricao": "Gap em dias entre encerramento da obra anterior e terraplenagem desta"},
    {"coluna": "Distância (km)",           "tipo": "Número", "descricao": "Distância em km da obra anterior para esta"},
]

C_OBRA              = "OBRA"
C_COD_CRM           = "Cód. CRM"
C_REGIONAL          = "Regional"
C_CIDADE            = "Cidade"
C_CLUSTER           = "CLUSTER"
C_DATA_FUND         = "Data Fundação"
C_DATA_TERRA        = "Data Terraplenagem"
C_DATA_ENCERR       = "Data Encerramento Módulo"
C_COMPLEXIDADE_BASE = "COMPLEXIDADE"
C_RESP1             = "Responsável 1"
C_SENIORIDADE       = "Senioridade ENG1"
C_LINHA             = "Linha"

C_ID_EMP           = "IDTRSICRM"
C_NOME_EMP         = "Empreendimento"
C_CIDADE_EMP       = "CIDADE"
C_CLUSTER_EMP      = "CLUSTER_CORRIGIDO"
C_FUND_EMP         = "Fundação"
C_TERRA_EMP        = "Terraplenagem"
C_ENCERR_EMP       = "Encerramento Módulo"
C_COMPLEXIDADE_EMP = "Complexidade"
C_REGIONAL_EMP     = "Regional"

C_PROX_OBRA   = "Próxima Obra"
C_ID_PROX     = "ID CRM - Próxima Obra"
C_TERRA_PROX  = "Terraplenagem - Próxima Obra"
C_ENCERR_PROX = "Encerramento - Próxima Obra"
C_CIDADE_PROX = "Cidade - Próxima Obra"
C_ORIGEM      = "Origem Sequenciamento"
C_LATENCIA    = "Latência (Dias)"
C_DISTANCIA   = "Distância (km)"
C_FONTE_PROX  = "Fonte da Próxima Obra"
