"""
Script para carregar dados do ENEM do CSV para MongoDB
"""

import sys
from pathlib import Path

import pandas as pd

src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from config.logs import logger  # noqa: E402
from infra.settings.database import get_sync_database  # noqa: E402
from models.escola import Escola  # noqa: E402
from models.municipio import Municipio  # noqa: E402
from models.participante import Participante  # noqa: E402
from models.questionario import QuestionarioSocioeconomico  # noqa: E402
from models.resultado import Resultado  # noqa: E402


def clean_and_convert_value(value, target_type=str):
    """Limpar e converter valores dos CSVs"""
    if pd.isna(value) or value == "" or value == "nan":
        return None

    try:
        if target_type is int:
            return int(float(value))
        elif target_type is float:
            return float(value)
        elif target_type is bool:
            return str(value).upper() in ["1", "TRUE", "SIM", "S"]
        else:
            return str(value).strip()
    except (ValueError, TypeError):
        return None


def create_areas_conhecimento(db):
    """Criar as áreas de conhecimento padrão do ENEM."""
    logger.info("Criando áreas de conhecimento...")

    areas = [
        {
            "codigo": "CN",
            "nome": "Ciências da Natureza e suas Tecnologias",
            "descricao": "Área que engloba Física, Química e Biologia",
            "sigla": "CN",
            "peso_default": 1.0,
            "ativa": True,
        },
        {
            "codigo": "CH",
            "nome": "Ciências Humanas e suas Tecnologias",
            "descricao": "Área que engloba História, Geografia, Filosofia e Sociologia",
            "sigla": "CH",
            "peso_default": 1.0,
            "ativa": True,
        },
        {
            "codigo": "LC",
            "nome": "Linguagens, Códigos e suas Tecnologias",
            "descricao": "Área que engloba Língua Portuguesa, Literatura, Língua Estrangeira, Artes e Educação Física",
            "sigla": "LC",
            "peso_default": 1.0,
            "ativa": True,
        },
        {
            "codigo": "MT",
            "nome": "Matemática e suas Tecnologias",
            "descricao": "Área que engloba Matemática",
            "sigla": "MT",
            "peso_default": 1.0,
            "ativa": True,
        },
        {
            "codigo": "RE",
            "nome": "Redação",
            "descricao": "Prova de produção textual",
            "sigla": "RE",
            "peso_default": 1.0,
            "ativa": True,
        },
    ]

    # Limpar áreas existentes
    db.areas_conhecimento.delete_many({})

    # Inserir as áreas
    db.areas_conhecimento.insert_many(areas)
    logger.info(f"Criadas {len(areas)} áreas de conhecimento")

    # Criar índices para áreas de conhecimento
    try:
        db.areas_conhecimento.create_index("codigo", unique=True)
        db.areas_conhecimento.create_index("sigla")
        db.areas_conhecimento.create_index("ativa")
        logger.info("Índices criados para areas_conhecimento")
    except Exception as e:
        logger.warning(f"Alguns índices já existem: {e}")


def create_participante_areas_from_resultados(db):
    """Criar relacionamentos N:N entre participantes e áreas baseado nos resultados."""
    logger.info("Criando relacionamentos participante-área...")

    # Limpar relacionamentos existentes
    db.participantes_areas_conhecimento.delete_many({})

    # Buscar todos os resultados
    resultados = list(db.resultados.find({}))
    logger.info(f"Processando {len(resultados)} resultados para criar relacionamentos")

    participante_areas = []

    for resultado in resultados:
        try:
            participante_inscricao = str(resultado.get("nu_sequencial"))
            ano = resultado.get("nu_ano", 2023)

            if not participante_inscricao:
                continue

            # Mapear áreas e notas
            areas_mapping = [
                {
                    "area_codigo": "CN",
                    "nota": resultado.get("nota_cn"),
                    "presenca": resultado.get("presenca_cn") == 1,
                },
                {
                    "area_codigo": "CH",
                    "nota": resultado.get("nota_ch"),
                    "presenca": resultado.get("presenca_ch") == 1,
                },
                {
                    "area_codigo": "LC",
                    "nota": resultado.get("nota_lc"),
                    "presenca": resultado.get("presenca_lc") == 1,
                },
                {
                    "area_codigo": "MT",
                    "nota": resultado.get("nota_mt"),
                    "presenca": resultado.get("presenca_mt") == 1,
                },
                {
                    "area_codigo": "RE",
                    "nota": resultado.get("nota_redacao"),
                    "presenca": resultado.get("status_redacao", 0) > 0,
                },
            ]

            for area_data in areas_mapping:
                if area_data["nota"] is None:
                    continue

                # Calcular acertos para áreas objetivas (estimativa)
                if area_data["area_codigo"] == "RE":
                    numero_acertos = None
                    total_questoes = None
                    percentual_acerto = None
                else:
                    total_questoes = 45
                    # Estimativa baseada na nota
                    if area_data["nota"] >= 800:
                        numero_acertos = int(total_questoes * 0.9)
                    elif area_data["nota"] >= 700:
                        numero_acertos = int(total_questoes * 0.8)
                    elif area_data["nota"] >= 600:
                        numero_acertos = int(total_questoes * 0.7)
                    elif area_data["nota"] >= 500:
                        numero_acertos = int(total_questoes * 0.6)
                    elif area_data["nota"] >= 400:
                        numero_acertos = int(total_questoes * 0.5)
                    elif area_data["nota"] >= 300:
                        numero_acertos = int(total_questoes * 0.4)
                    else:
                        numero_acertos = int(total_questoes * 0.3)

                    percentual_acerto = (numero_acertos / total_questoes) * 100

                participante_area_data = {
                    "participante_inscricao": participante_inscricao,
                    "area_codigo": area_data["area_codigo"],
                    "nota": float(area_data["nota"]),
                    "presenca": area_data["presenca"],
                    "numero_acertos": numero_acertos,
                    "total_questoes": total_questoes,
                    "percentual_acerto": percentual_acerto,
                    "situacao": "Presente" if area_data["presenca"] else "Ausente",
                    "ano_prova": ano,
                }

                participante_areas.append(participante_area_data)

        except Exception as e:
            logger.error(
                f"Erro ao processar resultado {resultado.get('nu_sequencial')}: {e}"
            )
            continue

    # Inserir em lotes para melhor performance
    if participante_areas:
        batch_size = 1000
        total_batches = (len(participante_areas) + batch_size - 1) // batch_size

        for i in range(0, len(participante_areas), batch_size):
            batch = participante_areas[i : i + batch_size]
            db.participantes_areas_conhecimento.insert_many(batch)
            logger.info(f"Lote {(i // batch_size) + 1}/{total_batches} inserido")

        logger.info(
            f"Criados {len(participante_areas)} relacionamentos participante-área"
        )

    # Criar índices para melhor performance
    try:
        db.participantes_areas_conhecimento.create_index("participante_inscricao")
        db.participantes_areas_conhecimento.create_index("area_codigo")
        db.participantes_areas_conhecimento.create_index(
            [("participante_inscricao", 1), ("area_codigo", 1)], unique=True
        )
        db.participantes_areas_conhecimento.create_index("nota")
        db.participantes_areas_conhecimento.create_index("ano_prova")
        logger.info("Índices criados para participantes_areas_conhecimento")
    except Exception as e:
        logger.warning(f"Alguns índices já existem: {e}")


def process_participantes_data(df_participantes):
    """Processar dados dos participantes"""
    logger.info("Processando dados dos participantes...")

    participantes = []
    municipios_set = set()

    for _, row in df_participantes.iterrows():
        try:
            # Processar questionário socioeconômico
            questionario_data = {}
            for i in range(1, 24):  # Q001 a Q023
                col_name = f"Q{i:03d}"
                if col_name in row:
                    questionario_data[col_name] = clean_and_convert_value(row[col_name])

            questionario = (
                QuestionarioSocioeconomico(**questionario_data)
                if questionario_data
                else None
            )

            # Criar participante
            participante_data = {
                "nu_inscricao": clean_and_convert_value(row["NU_INSCRICAO"]),
                "nu_ano": clean_and_convert_value(row["NU_ANO"], int),
                "faixa_etaria": clean_and_convert_value(row["TP_FAIXA_ETARIA"], int),
                "sexo": clean_and_convert_value(row["TP_SEXO"]),
                "estado_civil": clean_and_convert_value(row["TP_ESTADO_CIVIL"], int),
                "cor_raca": clean_and_convert_value(row["TP_COR_RACA"], int),
                "nacionalidade": clean_and_convert_value(row["TP_NACIONALIDADE"], int),
                "st_conclusao": clean_and_convert_value(row["TP_ST_CONCLUSAO"], int),
                "ano_concluiu": clean_and_convert_value(row["TP_ANO_CONCLUIU"], int),
                "ensino": clean_and_convert_value(row["TP_ENSINO"], int),
                "treineiro": clean_and_convert_value(row["IN_TREINEIRO"], bool),
                "municipio_prova_codigo": clean_and_convert_value(
                    row["CO_MUNICIPIO_PROVA"], int
                ),
                "uf_prova": clean_and_convert_value(row["SG_UF_PROVA"]),
                "questionario": questionario.model_dump() if questionario else None,
            }

            # Remover valores None
            participante_data = {
                k: v for k, v in participante_data.items() if v is not None
            }

            if participante_data.get("nu_inscricao"):
                # Calcular total de provas realizadas (estimativa baseada nos dados do questionário)
                total_provas = 0
                if not participante_data.get(
                    "treineiro"
                ):  # Se não é treineiro, provavelmente fez todas as provas
                    total_provas = 4  # CN, CH, LC, MT
                else:
                    total_provas = 2  # Treineiros geralmente fazem menos provas

                participante_data["total_provas_realizadas"] = total_provas

                participante = Participante(**participante_data)
                participantes.append(participante.model_dump(by_alias=True))

                # Coletar municípios únicos
                if participante_data.get("municipio_prova_codigo"):
                    municipios_set.add(
                        (
                            participante_data["municipio_prova_codigo"],
                            clean_and_convert_value(row.get("NO_MUNICIPIO_PROVA", "")),
                            clean_and_convert_value(row.get("CO_UF_PROVA"), int),
                            participante_data["uf_prova"],
                        )
                    )

        except Exception as e:
            logger.error(f"Erro ao processar participante: {e}")
            continue

    return participantes, municipios_set


def process_resultados_data(df_resultados):
    """Processar dados dos resultados"""
    logger.info("Processando dados dos resultados...")

    resultados = []
    escolas_set = set()
    municipios_escola_set = set()

    for _, row in df_resultados.iterrows():
        try:
            # Calcular média das provas objetivas
            notas = []
            for area in ["CN", "CH", "LC", "MT"]:
                nota = clean_and_convert_value(row.get(f"NU_NOTA_{area}"), float)
                if nota is not None:
                    notas.append(nota)

            media_objetivas = sum(notas) / len(notas) if notas else None

            resultado_data = {
                "nu_sequencial": clean_and_convert_value(row["NU_SEQUENCIAL"]),
                "nu_ano": clean_and_convert_value(row["NU_ANO"], int),
                "participante_inscricao": clean_and_convert_value(
                    row["NU_SEQUENCIAL"]
                ),  # Usando sequencial como chave
                "escola_codigo": clean_and_convert_value(row["CO_ESCOLA"], int),
                "municipio_escola_codigo": clean_and_convert_value(
                    row["CO_MUNICIPIO_ESC"], int
                ),
                "municipio_escola_nome": clean_and_convert_value(
                    row["NO_MUNICIPIO_ESC"]
                ),
                "uf_escola_codigo": clean_and_convert_value(row["CO_UF_ESC"], int),
                "uf_escola_sigla": clean_and_convert_value(row["SG_UF_ESC"]),
                "dependencia_administrativa": clean_and_convert_value(
                    row["TP_DEPENDENCIA_ADM_ESC"], int
                ),
                "localizacao_escola": clean_and_convert_value(
                    row["TP_LOCALIZACAO_ESC"], int
                ),
                "situacao_funcionamento": clean_and_convert_value(
                    row["TP_SIT_FUNC_ESC"], int
                ),
                "municipio_prova_codigo": clean_and_convert_value(
                    row["CO_MUNICIPIO_PROVA"], int
                ),
                "municipio_prova_nome": clean_and_convert_value(
                    row["NO_MUNICIPIO_PROVA"]
                ),
                "uf_prova_codigo": clean_and_convert_value(row["CO_UF_PROVA"], int),
                "uf_prova_sigla": clean_and_convert_value(row["SG_UF_PROVA"]),
                # Presenças
                "presenca_cn": clean_and_convert_value(row["TP_PRESENCA_CN"], int),
                "presenca_ch": clean_and_convert_value(row["TP_PRESENCA_CH"], int),
                "presenca_lc": clean_and_convert_value(row["TP_PRESENCA_LC"], int),
                "presenca_mt": clean_and_convert_value(row["TP_PRESENCA_MT"], int),
                # Códigos das provas
                "codigo_prova_cn": clean_and_convert_value(row["CO_PROVA_CN"]),
                "codigo_prova_ch": clean_and_convert_value(row["CO_PROVA_CH"]),
                "codigo_prova_lc": clean_and_convert_value(row["CO_PROVA_LC"]),
                "codigo_prova_mt": clean_and_convert_value(row["CO_PROVA_MT"]),
                # Notas
                "nota_cn": clean_and_convert_value(row["NU_NOTA_CN"], float),
                "nota_ch": clean_and_convert_value(row["NU_NOTA_CH"], float),
                "nota_lc": clean_and_convert_value(row["NU_NOTA_LC"], float),
                "nota_mt": clean_and_convert_value(row["NU_NOTA_MT"], float),
                # Redação
                "status_redacao": clean_and_convert_value(
                    row["TP_STATUS_REDACAO"], int
                ),
                "nota_comp1": clean_and_convert_value(row["NU_NOTA_COMP1"], float),
                "nota_comp2": clean_and_convert_value(row["NU_NOTA_COMP2"], float),
                "nota_comp3": clean_and_convert_value(row["NU_NOTA_COMP3"], float),
                "nota_comp4": clean_and_convert_value(row["NU_NOTA_COMP4"], float),
                "nota_comp5": clean_and_convert_value(row["NU_NOTA_COMP5"], float),
                "nota_redacao": clean_and_convert_value(row["NU_NOTA_REDACAO"], float),
                # Campos calculados
                "media_provas_objetivas": media_objetivas,
                # Respostas e gabaritos
                "respostas_cn": clean_and_convert_value(row["TX_RESPOSTAS_CN"]),
                "respostas_ch": clean_and_convert_value(row["TX_RESPOSTAS_CH"]),
                "respostas_lc": clean_and_convert_value(row["TX_RESPOSTAS_LC"]),
                "respostas_mt": clean_and_convert_value(row["TX_RESPOSTAS_MT"]),
                "gabarito_cn": clean_and_convert_value(row["TX_GABARITO_CN"]),
                "gabarito_ch": clean_and_convert_value(row["TX_GABARITO_CH"]),
                "gabarito_lc": clean_and_convert_value(row["TX_GABARITO_LC"]),
                "gabarito_mt": clean_and_convert_value(row["TX_GABARITO_MT"]),
                "lingua_estrangeira": clean_and_convert_value(row["TP_LINGUA"], int),
            }

            # Remover valores None
            resultado_data = {k: v for k, v in resultado_data.items() if v is not None}

            if resultado_data.get("nu_sequencial"):
                resultado = Resultado(**resultado_data)
                resultados.append(resultado.model_dump(by_alias=True))

                # Coletar escolas únicas
                if resultado_data.get("escola_codigo"):
                    escolas_set.add(
                        (
                            resultado_data["escola_codigo"],
                            resultado_data.get("municipio_escola_codigo"),
                            resultado_data.get("uf_escola_codigo"),
                            resultado_data.get("uf_escola_sigla"),
                            resultado_data.get("dependencia_administrativa"),
                            resultado_data.get("localizacao_escola"),
                            resultado_data.get("situacao_funcionamento"),
                        )
                    )

                # Coletar municípios das escolas
                if resultado_data.get("municipio_escola_codigo"):
                    municipios_escola_set.add(
                        (
                            resultado_data["municipio_escola_codigo"],
                            resultado_data.get("municipio_escola_nome"),
                            resultado_data.get("uf_escola_codigo"),
                            resultado_data.get("uf_escola_sigla"),
                        )
                    )

        except Exception as e:
            logger.error(f"Erro ao processar resultado: {e}")
            continue

    return resultados, escolas_set, municipios_escola_set


def create_municipios_from_sets(municipios_set, municipios_escola_set):
    """Criar municípios únicos a partir dos conjuntos coletados"""
    all_municipios = {}

    # Dados básicos por região para enriquecer os municípios
    info_por_regiao = {
        "AC": {
            "regiao": "Norte",
            "populacao_media": 45000,
            "pib_per_capita": 15000,
            "idh": 0.663,
        },
        "AL": {
            "regiao": "Nordeste",
            "populacao_media": 95000,
            "pib_per_capita": 12000,
            "idh": 0.631,
        },
        "AP": {
            "regiao": "Norte",
            "populacao_media": 50000,
            "pib_per_capita": 16000,
            "idh": 0.708,
        },
        "AM": {
            "regiao": "Norte",
            "populacao_media": 65000,
            "pib_per_capita": 18000,
            "idh": 0.674,
        },
        "BA": {
            "regiao": "Nordeste",
            "populacao_media": 35000,
            "pib_per_capita": 13000,
            "idh": 0.660,
        },
        "CE": {
            "regiao": "Nordeste",
            "populacao_media": 50000,
            "pib_per_capita": 11000,
            "idh": 0.682,
        },
        "DF": {
            "regiao": "Centro-Oeste",
            "populacao_media": 120000,
            "pib_per_capita": 65000,
            "idh": 0.824,
        },
        "ES": {
            "regiao": "Sudeste",
            "populacao_media": 55000,
            "pib_per_capita": 28000,
            "idh": 0.740,
        },
        "GO": {
            "regiao": "Centro-Oeste",
            "populacao_media": 40000,
            "pib_per_capita": 22000,
            "idh": 0.735,
        },
        "MA": {
            "regiao": "Nordeste",
            "populacao_media": 35000,
            "pib_per_capita": 10000,
            "idh": 0.639,
        },
        "MT": {
            "regiao": "Centro-Oeste",
            "populacao_media": 35000,
            "pib_per_capita": 35000,
            "idh": 0.725,
        },
        "MS": {
            "regiao": "Centro-Oeste",
            "populacao_media": 35000,
            "pib_per_capita": 28000,
            "idh": 0.729,
        },
        "MG": {
            "regiao": "Sudeste",
            "populacao_media": 45000,
            "pib_per_capita": 18000,
            "idh": 0.731,
        },
        "PA": {
            "regiao": "Norte",
            "populacao_media": 55000,
            "pib_per_capita": 14000,
            "idh": 0.646,
        },
        "PB": {
            "regiao": "Nordeste",
            "populacao_media": 18000,
            "pib_per_capita": 11000,
            "idh": 0.658,
        },
        "PR": {
            "regiao": "Sul",
            "populacao_media": 30000,
            "pib_per_capita": 24000,
            "idh": 0.749,
        },
        "PE": {
            "regiao": "Nordeste",
            "populacao_media": 50000,
            "pib_per_capita": 14000,
            "idh": 0.673,
        },
        "PI": {
            "regiao": "Nordeste",
            "populacao_media": 15000,
            "pib_per_capita": 9000,
            "idh": 0.646,
        },
        "RJ": {
            "regiao": "Sudeste",
            "populacao_media": 100000,
            "pib_per_capita": 32000,
            "idh": 0.761,
        },
        "RN": {
            "regiao": "Nordeste",
            "populacao_media": 20000,
            "pib_per_capita": 12000,
            "idh": 0.684,
        },
        "RS": {
            "regiao": "Sul",
            "populacao_media": 25000,
            "pib_per_capita": 28000,
            "idh": 0.746,
        },
        "RO": {
            "regiao": "Norte",
            "populacao_media": 35000,
            "pib_per_capita": 16000,
            "idh": 0.690,
        },
        "RR": {
            "regiao": "Norte",
            "populacao_media": 45000,
            "pib_per_capita": 18000,
            "idh": 0.707,
        },
        "SC": {
            "regiao": "Sul",
            "populacao_media": 25000,
            "pib_per_capita": 30000,
            "idh": 0.774,
        },
        "SP": {
            "regiao": "Sudeste",
            "populacao_media": 70000,
            "pib_per_capita": 40000,
            "idh": 0.783,
        },
        "SE": {
            "regiao": "Nordeste",
            "populacao_media": 40000,
            "pib_per_capita": 15000,
            "idh": 0.665,
        },
        "TO": {
            "regiao": "Norte",
            "populacao_media": 20000,
            "pib_per_capita": 18000,
            "idh": 0.699,
        },
    }

    # Processar municípios das provas
    for codigo, nome, uf_codigo, uf_sigla in municipios_set:
        if codigo and codigo not in all_municipios:
            info_uf = info_por_regiao.get(
                uf_sigla,
                {
                    "regiao": "Não informado",
                    "populacao_media": 30000,
                    "pib_per_capita": 20000,
                    "idh": 0.700,
                },
            )

            municipio_data = {
                "codigo": codigo,
                "nome": nome or f"Município {codigo}",
                "uf_codigo": uf_codigo or 0,
                "uf_sigla": uf_sigla or "BR",
                "regiao": info_uf["regiao"],
                "populacao": int(
                    info_uf["populacao_media"] * (0.5 + (codigo % 100) / 100)
                ),  # Variação baseada no código
                "pib_per_capita": round(
                    info_uf["pib_per_capita"] * (0.7 + (codigo % 50) / 100), 2
                ),
                "idh": round(
                    info_uf["idh"] + ((codigo % 20) - 10) * 0.001, 3
                ),  # Pequena variação
            }
            municipio = Municipio(**municipio_data)
            all_municipios[codigo] = municipio.model_dump(by_alias=True)

    # Processar municípios das escolas
    for codigo, nome, uf_codigo, uf_sigla in municipios_escola_set:
        if codigo and codigo not in all_municipios:
            info_uf = info_por_regiao.get(
                uf_sigla,
                {
                    "regiao": "Não informado",
                    "populacao_media": 30000,
                    "pib_per_capita": 20000,
                    "idh": 0.700,
                },
            )

            municipio_data = {
                "codigo": codigo,
                "nome": nome or f"Município {codigo}",
                "uf_codigo": uf_codigo or 0,
                "uf_sigla": uf_sigla or "BR",
                "regiao": info_uf["regiao"],
                "populacao": int(
                    info_uf["populacao_media"] * (0.5 + (codigo % 100) / 100)
                ),
                "pib_per_capita": round(
                    info_uf["pib_per_capita"] * (0.7 + (codigo % 50) / 100), 2
                ),
                "idh": round(info_uf["idh"] + ((codigo % 20) - 10) * 0.001, 3),
            }
            municipio = Municipio(**municipio_data)
            all_municipios[codigo] = municipio.model_dump(by_alias=True)

    return list(all_municipios.values())


def create_escolas_from_set(escolas_set):
    """Criar escolas únicas a partir do conjunto coletado"""
    escolas = []

    for (
        codigo,
        municipio_codigo,
        uf_codigo,
        uf_sigla,
        dep_adm,
        localizacao,
        sit_func,
    ) in escolas_set:
        if codigo:
            try:
                escola_data = {
                    "codigo": codigo,
                    "nome": f"Escola {codigo}",
                    "municipio_codigo": municipio_codigo or 0,
                    "uf_codigo": uf_codigo or 0,
                    "uf_sigla": uf_sigla or "BR",
                    "dependencia_administrativa": dep_adm or 0,
                    "localizacao": localizacao or 0,
                    "situacao_funcionamento": sit_func or 0,
                }
                escola = Escola(**escola_data)
                escolas.append(escola.model_dump(by_alias=True))
            except Exception as e:
                logger.error(f"Erro ao criar escola {codigo}: {e}")
                continue

    return escolas


def verificar_dados_carregados(db):
    """Verificar se todos os dados foram carregados corretamente."""
    logger.info("=== VERIFICAÇÃO DOS DADOS CARREGADOS ===")

    # Contar registros por coleção
    collections = [
        "municipios",
        "escolas",
        "participantes",
        "resultados",
        "areas_conhecimento",
        "participantes_areas_conhecimento",
    ]

    for collection_name in collections:
        count = db[collection_name].count_documents({})
        logger.info(f"{collection_name}: {count} documentos")

    # Verificar estatísticas das áreas
    logger.info("\n=== ESTATÍSTICAS POR ÁREA DE CONHECIMENTO ===")
    for area_codigo in ["CN", "CH", "LC", "MT", "RE"]:
        count = db.participantes_areas_conhecimento.count_documents(
            {"area_codigo": area_codigo}
        )
        if count > 0:
            # Calcular média da área
            pipeline = [
                {"$match": {"area_codigo": area_codigo, "nota": {"$ne": None}}},
                {
                    "$group": {
                        "_id": None,
                        "media": {"$avg": "$nota"},
                        "total": {"$sum": 1},
                    }
                },
            ]
            result = list(db.participantes_areas_conhecimento.aggregate(pipeline))
            if result:
                media = result[0]["media"]
                logger.info(
                    f"Área {area_codigo}: {count} participantes, média: {media:.2f}"
                )
            else:
                logger.info(f"Área {area_codigo}: {count} participantes (sem notas)")
        else:
            logger.warning(f"Área {area_codigo}: NENHUM participante encontrado!")

    logger.info("=== VERIFICAÇÃO CONCLUÍDA ===")


def load_data_to_mongodb():
    """Carregar todos os dados para MongoDB incluindo áreas de conhecimento"""
    try:
        db = get_sync_database()
        logger.info("Conectado ao MongoDB")

        data_path = Path("data")

        logger.info("Carregando arquivos CSV...")
        df_participantes = pd.read_csv(data_path / "amostra_participantes.csv")
        df_resultados = pd.read_csv(data_path / "amostra_resultados.csv")

        logger.info(f"Participantes carregados: {len(df_participantes)}")
        logger.info(f"Resultados carregados: {len(df_resultados)}")

        # Processar dados
        participantes, municipios_prova_set = process_participantes_data(
            df_participantes
        )
        resultados, escolas_set, municipios_escola_set = process_resultados_data(
            df_resultados
        )

        # Criar municípios únicos
        municipios = create_municipios_from_sets(
            municipios_prova_set, municipios_escola_set
        )

        # Criar escolas únicas
        escolas = create_escolas_from_set(escolas_set)

        # Limpar coleções existentes
        logger.info("Limpando coleções existentes...")
        collections_to_clear = [
            "municipios",
            "escolas",
            "participantes",
            "resultados",
            "areas_conhecimento",
            "participantes_areas_conhecimento",
        ]
        for collection_name in collections_to_clear:
            db[collection_name].delete_many({})

        # 1. Criar áreas de conhecimento primeiro
        create_areas_conhecimento(db)

        # 2. Inserir municípios
        municipio_id_map = {}
        if municipios:
            logger.info(f"Inserindo {len(municipios)} municípios...")
            municipios_result = db.municipios.insert_many(municipios)

            # Criar mapeamento código -> ObjectId
            for i, inserted_id in enumerate(municipios_result.inserted_ids):
                codigo = municipios[i]["codigo"]
                municipio_id_map[codigo] = inserted_id

        # 3. Inserir escolas e fazer referência aos municípios
        escola_id_map = {}
        if escolas:
            logger.info(f"Inserindo {len(escolas)} escolas...")
            # Atualizar referências aos municípios nas escolas
            for escola in escolas:
                municipio_codigo = escola["municipio_codigo"]
                if municipio_codigo in municipio_id_map:
                    escola["municipio_id"] = municipio_id_map[municipio_codigo]

            escolas_result = db.escolas.insert_many(escolas)

            # Criar mapeamento código -> ObjectId
            for i, inserted_id in enumerate(escolas_result.inserted_ids):
                codigo = escolas[i]["codigo"]
                escola_id_map[codigo] = inserted_id

        # 4. Inserir participantes
        participante_sequencial_map = {}
        if participantes:
            logger.info(f"Inserindo {len(participantes)} participantes...")
            # Atualizar referências aos municípios nos participantes
            for participante in participantes:
                municipio_codigo = participante.get("municipio_prova_codigo")
                if municipio_codigo and municipio_codigo in municipio_id_map:
                    participante["municipio_prova_id"] = municipio_id_map[
                        municipio_codigo
                    ]

            participantes_result = db.participantes.insert_many(participantes)

            # Criar mapeamento nu_inscricao -> ObjectId
            for i, inserted_id in enumerate(participantes_result.inserted_ids):
                nu_inscricao = participantes[i]["nu_inscricao"]
                participante_sequencial_map[nu_inscricao] = inserted_id

        # 5. Inserir resultados com todas as referências
        if resultados:
            logger.info(f"Inserindo {len(resultados)} resultados...")
            # Atualizar referências nos resultados
            for resultado in resultados:
                # Referência à escola
                escola_codigo = resultado.get("escola_codigo")
                if escola_codigo and escola_codigo in escola_id_map:
                    resultado["escola_id"] = escola_id_map[escola_codigo]

                # Calcular total de acertos
                acertos = 0
                for area in ["CN", "CH", "LC", "MT"]:
                    respostas = resultado.get(f"respostas_{area.lower()}", "")
                    gabarito = resultado.get(f"gabarito_{area.lower()}", "")
                    if respostas and gabarito:
                        min_len = min(len(respostas), len(gabarito))
                        for j in range(min_len):
                            if respostas[j] == gabarito[j] and respostas[j] not in [
                                ".",
                                "*",
                                " ",
                                "",
                            ]:
                                acertos += 1
                resultado["total_acertos"] = acertos

            db.resultados.insert_many(resultados)

        # 6. Criar relacionamentos participante-área baseado nos resultados
        create_participante_areas_from_resultados(db)

        # 7. Criar índices para melhor performance
        logger.info("Criando índices adicionais...")
        db.municipios.create_index("codigo")
        db.escolas.create_index("codigo")
        db.escolas.create_index("municipio_codigo")
        db.participantes.create_index("nu_inscricao")
        db.participantes.create_index("municipio_prova_codigo")
        db.resultados.create_index("participante_inscricao")
        db.resultados.create_index("escola_codigo")
        db.resultados.create_index("nu_ano")

        # 8. Verificar se tudo foi carregado corretamente
        verificar_dados_carregados(db)

        logger.info("=== CARREGAMENTO COMPLETO CONCLUÍDO COM SUCESSO! ===")

    except Exception as e:
        logger.error(f"Erro durante o carregamento: {e}")
        raise


if __name__ == "__main__":
    load_data_to_mongodb()
