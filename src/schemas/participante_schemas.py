"""Schemas para operações com participantes"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ParticipanteResponse(BaseModel):
    """Schema para resposta de participante"""

    id: str
    nu_inscricao: str
    nu_ano: int
    faixa_etaria: int
    sexo: str
    estado_civil: int
    cor_raca: int
    treineiro: bool
    uf_prova: str

    class Config:
        from_attributes = True


class ParticipanteCreate(BaseModel):
    """Schema para criação de participante"""

    nu_inscricao: str
    nu_ano: int
    faixa_etaria: Optional[int] = None
    sexo: Optional[str] = None
    estado_civil: Optional[int] = None
    cor_raca: Optional[int] = None
    treineiro: Optional[bool] = False
    uf_prova_sigla: Optional[str] = None
    uf_residencia_sigla: Optional[str] = None
    municipio_residencia_nome: Optional[str] = None
    escola_codigo: Optional[int] = None


class ParticipanteUpdate(BaseModel):
    """Schema para atualização de participante"""

    faixa_etaria: Optional[int] = None
    sexo: Optional[str] = None
    estado_civil: Optional[int] = None
    cor_raca: Optional[int] = None
    treineiro: Optional[bool] = None
    uf_prova_sigla: Optional[str] = None
    uf_residencia_sigla: Optional[str] = None
    municipio_residencia_nome: Optional[str] = None
    escola_codigo: Optional[int] = None


class ParticipanteOperationResponse(BaseModel):
    """Resposta para operações de CRUD em participantes"""

    success: bool = Field(..., description="Se a operação foi bem-sucedida")
    message: Optional[str] = Field(None, description="Mensagem da operação")
    participante_id: Optional[str] = Field(
        None, description="ID do participante afetado"
    )


# ==================== RESPONSE SCHEMAS ====================


class ParticipanteDetalhado(BaseModel):
    """Detalhes completos de um participante"""

    nu_inscricao: str = Field(..., description="Número de inscrição")
    nu_ano: int = Field(..., description="Ano do ENEM")
    faixa_etaria: Optional[int] = Field(None, description="Faixa etária")
    sexo: Optional[str] = Field(None, description="Sexo (M/F)")
    estado_civil: Optional[int] = Field(None, description="Estado civil")
    cor_raca: Optional[int] = Field(None, description="Cor/raça")
    treineiro: Optional[bool] = Field(None, description="Se é treineiro")
    uf_prova_sigla: Optional[str] = Field(None, description="UF onde fez a prova")
    uf_residencia_sigla: Optional[str] = Field(None, description="UF de residência")
    municipio_residencia_nome: Optional[str] = Field(
        None, description="Município de residência"
    )
    escola_codigo: Optional[int] = Field(None, description="Código da escola")
    escola_nome: Optional[str] = Field(None, description="Nome da escola")
    id: Optional[str] = Field(None, description="ID do documento", alias="_id")

    class Config:
        populate_by_name = True


class ParticipanteSimples(BaseModel):
    """Resposta simples para participante por ID ou inscrição"""

    nu_inscricao: Optional[str] = Field(None, description="Número de inscrição")
    nu_ano: Optional[int] = Field(None, description="Ano do ENEM")
    faixa_etaria: Optional[int] = Field(None, description="Faixa etária")
    sexo: Optional[str] = Field(None, description="Sexo")
    uf_prova_sigla: Optional[str] = Field(None, description="UF da prova")
    uf_residencia_sigla: Optional[str] = Field(None, description="UF de residência")
    treineiro: Optional[bool] = Field(None, description="Se é treineiro")
    id: Optional[str] = Field(None, description="ID do documento", alias="_id")

    class Config:
        populate_by_name = True


class ParticipantePaginadoResponse(BaseModel):
    """Resposta paginada para listagem de participantes"""

    items: List[Dict[str, Any]] = Field(..., description="Lista de participantes")
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Registros pulados")
    limit: int = Field(..., description="Limite por página")
    has_more: bool = Field(..., description="Se há mais registros")
    current_page: int = Field(..., description="Página atual")
    total_pages: int = Field(..., description="Total de páginas")


class EstatisticaSexo(BaseModel):
    """Estatística por sexo"""

    sexo: str = Field(..., description="Sexo")
    sexo_descricao: str = Field(..., description="Descrição do sexo")
    total: int = Field(..., description="Total de participantes")
    percentual: float = Field(..., description="Percentual do total")
    treineiros: int = Field(..., description="Quantidade de treineiros")
    regulares: int = Field(..., description="Quantidade de participantes regulares")
    percentual_treineiros: float = Field(..., description="Percentual de treineiros")


class EstatisticaIdade(BaseModel):
    """Estatística por faixa etária"""

    faixa_etaria: int = Field(..., description="Código da faixa etária")
    faixa_descricao: str = Field(..., description="Descrição da faixa etária")
    total: int = Field(..., description="Total de participantes")
    percentual: float = Field(..., description="Percentual do total")
    media_idade: Optional[float] = Field(None, description="Média de idade da faixa")


class EstatisticaRaca(BaseModel):
    """Estatística por cor/raça"""

    cor_raca: int = Field(..., description="Código da cor/raça")
    cor_raca_descricao: str = Field(..., description="Descrição da cor/raça")
    total: int = Field(..., description="Total de participantes")
    percentual: float = Field(..., description="Percentual do total")


class ResumoGlobalParticipantes(BaseModel):
    """Resumo geral dos participantes"""

    total_participantes: int = Field(..., description="Total de participantes")
    total_treineiros: int = Field(..., description="Total de treineiros")
    total_regulares: int = Field(..., description="Total de participantes regulares")
    percentual_treineiros: float = Field(..., description="Percentual de treineiros")
    distribuicao_anos: List[Dict[str, Any]] = Field(
        ..., description="Distribuição por anos"
    )


class EstatisticasDemograficasResponse(BaseModel):
    """Resposta das estatísticas demográficas"""

    resumo_geral: ResumoGlobalParticipantes = Field(..., description="Resumo geral")
    por_sexo: List[EstatisticaSexo] = Field(..., description="Estatísticas por sexo")
    por_faixa_etaria: List[EstatisticaIdade] = Field(
        ..., description="Estatísticas por idade"
    )
    por_cor_raca: List[EstatisticaRaca] = Field(
        ..., description="Estatísticas por cor/raça"
    )


class ParticipantePorUF(BaseModel):
    """Participantes por UF"""

    uf_sigla: str = Field(..., description="Sigla da UF")
    uf_nome: str = Field(..., description="Nome da UF")
    total_participantes: int = Field(..., description="Total de participantes")
    percentual: float = Field(..., description="Percentual do total")
    total_treineiros: int = Field(..., description="Total de treineiros")
    total_regulares: int = Field(..., description="Total de regulares")
    densidade_participacao: Optional[str] = Field(
        None, description="Densidade de participação"
    )


class ParticipantesPorUFResponse(BaseModel):
    """Resposta dos participantes por UF"""

    participantes_por_uf: List[ParticipantePorUF] = Field(
        ..., description="Lista de participantes por UF"
    )
    total_geral: int = Field(..., description="Total geral de participantes")
    total_ufs: int = Field(..., description="Total de UFs com participantes")
    uf_com_maior_participacao: Optional[str] = Field(
        None, description="UF com maior participação"
    )


class FaixaIdadeDistribuicao(BaseModel):
    """Distribuição por faixa de idade"""

    faixa_etaria: int = Field(..., description="Código da faixa etária")
    descricao_faixa: str = Field(..., description="Descrição da faixa")
    total_participantes: int = Field(..., description="Total de participantes")
    percentual: float = Field(..., description="Percentual do total")
    idade_media_aproximada: Optional[float] = Field(
        None, description="Idade média aproximada"
    )
    predominancia_sexo: Optional[str] = Field(
        None, description="Sexo predominante na faixa"
    )


class DistribuicaoIdadeResponse(BaseModel):
    """Resposta da distribuição de idades"""

    distribuicao_por_faixa: List[FaixaIdadeDistribuicao] = Field(
        ..., description="Distribuição por faixas"
    )
    total_participantes: int = Field(..., description="Total de participantes")
    faixa_predominante: str = Field(..., description="Faixa etária predominante")
    estatisticas_gerais: Dict[str, Any] = Field(
        ..., description="Estatísticas gerais de idade"
    )
