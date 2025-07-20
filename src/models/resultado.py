from typing import Optional

from pydantic import Field

from .base import MongoBaseModel, PyObjectId


class Resultado(MongoBaseModel):
    nu_sequencial: str = Field(..., description="Número sequencial único")
    nu_ano: int = Field(..., description="Ano da prova")

    # Referências para outras entidades
    participante_inscricao: str = Field(
        ..., description="Número de inscrição do participante"
    )
    participante_id: Optional[PyObjectId] = Field(
        None, description="Referência ao participante"
    )
    escola_codigo: Optional[int] = Field(None, description="Código da escola")
    escola_id: Optional[PyObjectId] = Field(None, description="Referência à escola")

    # Localização da escola
    municipio_escola_codigo: Optional[int] = Field(
        None, description="Código do município da escola"
    )
    municipio_escola_nome: Optional[str] = Field(
        None, description="Nome do município da escola"
    )
    uf_escola_codigo: Optional[int] = Field(None, description="Código da UF da escola")
    uf_escola_sigla: Optional[str] = Field(None, description="Sigla da UF da escola")

    # Informações da escola
    dependencia_administrativa: Optional[int] = Field(
        None, description="Dependência administrativa da escola"
    )
    localizacao_escola: Optional[int] = Field(None, description="Localização da escola")
    situacao_funcionamento: Optional[int] = Field(
        None, description="Situação de funcionamento da escola"
    )

    # Localização da prova
    municipio_prova_codigo: int = Field(..., description="Código do município da prova")
    municipio_prova_nome: str = Field(..., description="Nome do município da prova")
    uf_prova_codigo: int = Field(..., description="Código da UF da prova")
    uf_prova_sigla: str = Field(..., description="Sigla da UF da prova")

    # Presença nas provas
    presenca_cn: Optional[int] = Field(
        None, description="Presença em Ciências da Natureza"
    )
    presenca_ch: Optional[int] = Field(None, description="Presença em Ciências Humanas")
    presenca_lc: Optional[int] = Field(
        None, description="Presença em Linguagens e Códigos"
    )
    presenca_mt: Optional[int] = Field(None, description="Presença em Matemática")

    # Códigos das provas
    codigo_prova_cn: Optional[str] = Field(
        None, description="Código da prova de Ciências da Natureza"
    )
    codigo_prova_ch: Optional[str] = Field(
        None, description="Código da prova de Ciências Humanas"
    )
    codigo_prova_lc: Optional[str] = Field(
        None, description="Código da prova de Linguagens e Códigos"
    )
    codigo_prova_mt: Optional[str] = Field(
        None, description="Código da prova de Matemática"
    )

    # Notas das provas objetivas
    nota_cn: Optional[float] = Field(None, description="Nota em Ciências da Natureza")
    nota_ch: Optional[float] = Field(None, description="Nota em Ciências Humanas")
    nota_lc: Optional[float] = Field(None, description="Nota em Linguagens e Códigos")
    nota_mt: Optional[float] = Field(None, description="Nota em Matemática")

    # Respostas do participante
    respostas_cn: Optional[str] = Field(
        None, description="Respostas de Ciências da Natureza"
    )
    respostas_ch: Optional[str] = Field(
        None, description="Respostas de Ciências Humanas"
    )
    respostas_lc: Optional[str] = Field(
        None, description="Respostas de Linguagens e Códigos"
    )
    respostas_mt: Optional[str] = Field(None, description="Respostas de Matemática")

    # Língua estrangeira
    lingua_estrangeira: Optional[int] = Field(
        None, description="Língua estrangeira escolhida"
    )

    # Gabaritos
    gabarito_cn: Optional[str] = Field(
        None, description="Gabarito de Ciências da Natureza"
    )
    gabarito_ch: Optional[str] = Field(None, description="Gabarito de Ciências Humanas")
    gabarito_lc: Optional[str] = Field(
        None, description="Gabarito de Linguagens e Códigos"
    )
    gabarito_mt: Optional[str] = Field(None, description="Gabarito de Matemática")

    # Redação
    status_redacao: Optional[int] = Field(None, description="Status da redação")
    nota_comp1: Optional[float] = Field(
        None, description="Nota competência 1 da redação"
    )
    nota_comp2: Optional[float] = Field(
        None, description="Nota competência 2 da redação"
    )
    nota_comp3: Optional[float] = Field(
        None, description="Nota competência 3 da redação"
    )
    nota_comp4: Optional[float] = Field(
        None, description="Nota competência 4 da redação"
    )
    nota_comp5: Optional[float] = Field(
        None, description="Nota competência 5 da redação"
    )
    nota_redacao: Optional[float] = Field(None, description="Nota final da redação")

    # Campos calculados
    media_provas_objetivas: Optional[float] = Field(
        None, description="Média das provas objetivas"
    )
    total_acertos: Optional[int] = Field(None, description="Total de acertos")

    class Config:
        collection = "resultados"
