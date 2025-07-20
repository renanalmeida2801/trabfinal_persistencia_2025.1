"""
Script para carregar dados do ENEM do CSV para MongoDB
"""

import logging
from pathlib import Path

import pandas as pd
from pymongo import MongoClient

from src.config.settings import settings
from src.models import (
    Escola,
    Municipio,
    Participante,
    QuestionarioSocioeconomico,
    Resultado,
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_sync_database():
    """Conexão síncrona com MongoDB"""
    client = MongoClient(settings.MONGO_URL)
    return client[settings.DATABASE_NAME]


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
                "questionario": questionario.dict() if questionario else None,
            }

            # Remover valores None
            participante_data = {
                k: v for k, v in participante_data.items() if v is not None
            }

            if participante_data.get("nu_inscricao"):
                participante = Participante(**participante_data)
                participantes.append(participante.dict(by_alias=True))

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
                resultados.append(resultado.dict(by_alias=True))

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

    # Processar municípios das provas
    for codigo, nome, uf_codigo, uf_sigla in municipios_set:
        if codigo and codigo not in all_municipios:
            municipio_data = {
                "codigo": codigo,
                "nome": nome or f"Município {codigo}",
                "uf_codigo": uf_codigo or 0,
                "uf_sigla": uf_sigla or "BR",
            }
            municipio = Municipio(**municipio_data)
            all_municipios[codigo] = municipio.dict(by_alias=True)

    # Processar municípios das escolas
    for codigo, nome, uf_codigo, uf_sigla in municipios_escola_set:
        if codigo and codigo not in all_municipios:
            municipio_data = {
                "codigo": codigo,
                "nome": nome or f"Município {codigo}",
                "uf_codigo": uf_codigo or 0,
                "uf_sigla": uf_sigla or "BR",
            }
            municipio = Municipio(**municipio_data)
            all_municipios[codigo] = municipio.dict(by_alias=True)

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
                escolas.append(escola.dict(by_alias=True))
            except Exception as e:
                logger.error(f"Erro ao criar escola {codigo}: {e}")
                continue

    return escolas


def load_data_to_mongodb():
    """Carregar todos os dados para MongoDB"""
    try:
        # Conectar ao banco
        db = get_sync_database()
        logger.info("Conectado ao MongoDB")

        # Carregar CSVs
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
        db.municipios.delete_many({})
        db.escolas.delete_many({})
        db.participantes.delete_many({})
        db.resultados.delete_many({})

        # Inserir dados
        if municipios:
            logger.info(f"Inserindo {len(municipios)} municípios...")
            db.municipios.insert_many(municipios)

        if escolas:
            logger.info(f"Inserindo {len(escolas)} escolas...")
            db.escolas.insert_many(escolas)

        if participantes:
            logger.info(f"Inserindo {len(participantes)} participantes...")
            db.participantes.insert_many(participantes)

        if resultados:
            logger.info(f"Inserindo {len(resultados)} resultados...")
            db.resultados.insert_many(resultados)

        # Criar índices para melhor performance
        logger.info("Criando índices...")
        db.municipios.create_index("codigo")
        db.escolas.create_index("codigo")
        db.participantes.create_index("nu_inscricao")
        db.resultados.create_index("participante_inscricao")
        db.resultados.create_index("nu_ano")

        logger.info("Carregamento concluído com sucesso!")

    except Exception as e:
        logger.error(f"Erro durante o carregamento: {e}")
        raise


if __name__ == "__main__":
    load_data_to_mongodb()
