"""Schemas para operações com resultados"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ResultadoCreate(BaseModel):
    """Schema para criação de resultado"""

    nu_sequencial: str
    nu_ano: int
    participante_inscricao: str
    escola_codigo: Optional[int] = None
    municipio_escola_codigo: Optional[int] = None
    municipio_escola_nome: Optional[str] = None
    uf_escola_codigo: Optional[int] = None
    uf_escola_sigla: Optional[str] = None
    municipio_prova_codigo: int
    municipio_prova_nome: str
    uf_prova_codigo: int
    uf_prova_sigla: str
    presenca_cn: Optional[int] = None
    presenca_ch: Optional[int] = None
    presenca_lc: Optional[int] = None
    presenca_mt: Optional[int] = None
    nota_cn: Optional[float] = None
    nota_ch: Optional[float] = None
    nota_lc: Optional[float] = None
    nota_mt: Optional[float] = None
    nota_redacao: Optional[float] = None


class ResultadoUpdate(BaseModel):
    """Schema para atualização de resultado"""

    escola_codigo: Optional[int] = None
    municipio_escola_codigo: Optional[int] = None
    municipio_escola_nome: Optional[str] = None
    uf_escola_codigo: Optional[int] = None
    uf_escola_sigla: Optional[str] = None
    municipio_prova_codigo: Optional[int] = None
    municipio_prova_nome: Optional[str] = None
    uf_prova_codigo: Optional[int] = None
    uf_prova_sigla: Optional[str] = None
    presenca_cn: Optional[int] = None
    presenca_ch: Optional[int] = None
    presenca_lc: Optional[int] = None
    presenca_mt: Optional[int] = None
    nota_cn: Optional[float] = None
    nota_ch: Optional[float] = None
    nota_lc: Optional[float] = None
    nota_mt: Optional[float] = None
    nota_redacao: Optional[float] = None


class ResultadoOperationResponse(BaseModel):
    """Resposta para operações de CRUD em resultados"""

    success: bool = Field(..., description="Se a operação foi bem-sucedida")
    message: Optional[str] = Field(None, description="Mensagem da operação")
    resultado_id: Optional[str] = Field(None, description="ID do resultado afetado")


# ==================== RESPONSE SCHEMAS ====================


class UFInfo(BaseModel):
    """Informações sobre UF"""

    sigla: str = Field(..., description="Sigla da UF")
    nome: str = Field(..., description="Nome completo da UF")


class AreaEstatistica(BaseModel):
    """Estatísticas de uma área específica"""

    nome: str = Field(..., description="Nome da área")
    media: float = Field(..., description="Média da área")


class AreasDetalhadas(BaseModel):
    """Detalhamento das áreas do ENEM"""

    ciencias_natureza: AreaEstatistica = Field(..., description="Ciências da Natureza")
    ciencias_humanas: AreaEstatistica = Field(..., description="Ciências Humanas")
    linguagens_codigos: AreaEstatistica = Field(..., description="Linguagens e Códigos")
    matematica: AreaEstatistica = Field(..., description="Matemática")
    redacao: AreaEstatistica = Field(..., description="Redação")


class RankingUFItem(BaseModel):
    """Item do ranking de UFs"""

    posicao: int = Field(..., description="Posição no ranking")
    uf: UFInfo = Field(..., description="Informações da UF")
    total_participantes: int = Field(..., description="Total de participantes da UF")
    media_geral_objetivas: float = Field(
        ..., description="Média geral das provas objetivas"
    )
    areas: AreasDetalhadas = Field(..., description="Detalhamento por área")


class ResumoRankingUF(BaseModel):
    """Resumo do ranking de UFs"""

    melhor_uf: Optional[UFInfo] = Field(None, description="UF com melhor desempenho")
    maior_participacao: Optional[UFInfo] = Field(
        None, description="UF com maior participação"
    )
    total_participantes: int = Field(
        ..., description="Total de participantes no ranking"
    )


class RankingUFResponse(BaseModel):
    """Resposta do endpoint de ranking de UFs"""

    ranking: List[RankingUFItem] = Field(..., description="Lista do ranking das UFs")
    total_ufs: int = Field(..., description="Total de UFs no ranking")
    criterio_ordenacao: str = Field(..., description="Critério usado para ordenação")
    resumo: ResumoRankingUF = Field(..., description="Resumo do ranking")


class MediaPorArea(BaseModel):
    """Média por área específica"""

    area: str = Field(..., description="Nome da área")
    codigo_area: str = Field(..., description="Código da área")
    media: float = Field(..., description="Média da área")
    total_participantes: int = Field(..., description="Total de participantes")
    percentual_participacao: float = Field(
        ..., description="Percentual de participação"
    )


class ResumoGeral(BaseModel):
    """Resumo geral das estatísticas"""

    total_resultados: int = Field(..., description="Total de resultados")
    media_geral_enem: Union[float, str] = Field(..., description="Média geral do ENEM")


class MediasGeraisResponse(BaseModel):
    """Resposta do endpoint de médias gerais"""

    resumo_geral: ResumoGeral = Field(..., description="Resumo geral")
    medias_por_area: List[MediaPorArea] = Field(
        ..., description="Médias detalhadas por área"
    )


class FaixaInfo(BaseModel):
    """Informações sobre faixa de notas"""

    nome: str = Field(..., description="Nome da faixa")
    descricao: str = Field(..., description="Descrição da faixa")
    limite_inferior: Optional[int] = Field(None, description="Limite inferior da faixa")
    limite_superior: Optional[int] = Field(None, description="Limite superior da faixa")
    intervalo: str = Field(..., description="Intervalo da faixa em formato legível")


class EstatisticasFaixa(BaseModel):
    """Estatísticas de uma faixa"""

    total_participantes: int = Field(..., description="Total de participantes na faixa")
    percentual: float = Field(..., description="Percentual do total")
    media_faixa: Optional[float] = Field(None, description="Média da faixa")
    nota_maxima: Optional[float] = Field(None, description="Nota máxima da faixa")
    nota_minima: Optional[float] = Field(None, description="Nota mínima da faixa")


class DistribuicaoFaixa(BaseModel):
    """Item da distribuição por faixa"""

    faixa: FaixaInfo = Field(..., description="Informações da faixa")
    estatisticas: EstatisticasFaixa = Field(..., description="Estatísticas da faixa")


class ResumoDistribuicao(BaseModel):
    """Resumo da distribuição de notas"""

    total_participantes: int = Field(..., description="Total de participantes")
    faixa_predominante: str = Field(..., description="Faixa com mais participantes")
    participantes_com_nota_valida: int = Field(
        ..., description="Participantes com nota válida"
    )
    media_geral_redacao: float = Field(..., description="Média geral de redação")


class DistribuicaoRedacaoResponse(BaseModel):
    """Resposta do endpoint de distribuição de redação"""

    distribuicao_por_faixas: List[DistribuicaoFaixa] = Field(
        ..., description="Distribuição por faixas"
    )
    resumo_geral: ResumoDistribuicao = Field(..., description="Resumo da distribuição")


class MetadodosPaginacao(BaseModel):
    """Metadados de paginação"""

    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Registros pulados")
    limit: int = Field(..., description="Limite por página")
    has_more: bool = Field(..., description="Se há mais registros")
    current_page: int = Field(..., description="Página atual")
    total_pages: int = Field(..., description="Total de páginas")
    criterio: str = Field(..., description="Critério usado para filtro")


class ParticipantesDestaqueResponse(BaseModel):
    """Resposta do endpoint de participantes destaque"""

    items: List[Dict[str, Any]] = Field(..., description="Lista de participantes")
    total: int = Field(
        ..., description="Total de participantes que atendem ao critério"
    )
    skip: int = Field(..., description="Registros pulados")
    limit: int = Field(..., description="Limite por página")
    has_more: bool = Field(..., description="Se há mais registros")
    current_page: int = Field(..., description="Página atual")
    total_pages: int = Field(..., description="Total de páginas")
    criterio: str = Field(..., description="Critério usado para filtro")


class PeriodoInfo(BaseModel):
    """Informações do período"""

    inicio: Optional[str] = Field(None, description="Data de início")
    fim: Optional[str] = Field(None, description="Data de fim")


class EstatisticasPeriodoResponse(BaseModel):
    """Resposta do endpoint de estatísticas por período"""

    total_resultados: int = Field(..., description="Total de resultados no período")
    periodo: PeriodoInfo = Field(..., description="Informações do período")
    estatisticas: Dict[str, Any] = Field(..., description="Estatísticas do período")


class ResultadoPaginadoResponse(BaseModel):
    """Resposta padrão para listagens paginadas de resultados"""

    items: List[Dict[str, Any]] = Field(..., description="Lista de resultados")
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Registros pulados")
    limit: int = Field(..., description="Limite por página")
    has_more: bool = Field(..., description="Se há mais registros")


class ResultadoDetalhado(BaseModel):
    """Detalhes completos de um resultado"""

    participante_inscricao: str = Field(
        ..., description="Número de inscrição do participante"
    )
    nota_cn: Optional[float] = Field(None, description="Nota de Ciências da Natureza")
    nota_ch: Optional[float] = Field(None, description="Nota de Ciências Humanas")
    nota_lc: Optional[float] = Field(None, description="Nota de Linguagens e Códigos")
    nota_mt: Optional[float] = Field(None, description="Nota de Matemática")
    nota_redacao: Optional[float] = Field(None, description="Nota da Redação")
    media_provas_objetivas: Optional[float] = Field(
        None, description="Média das provas objetivas"
    )
    uf_prova_sigla: Optional[str] = Field(
        None, description="Sigla da UF onde fez a prova"
    )
    escola_codigo: Optional[int] = Field(None, description="Código da escola")
    nu_ano: Optional[int] = Field(None, description="Ano do ENEM")


class ResultadoResponse(BaseModel):
    """Resposta para endpoint de resultado individual"""

    resultado: ResultadoDetalhado = Field(
        ..., description="Dados detalhados do resultado"
    )


class ResultadoSimples(BaseModel):
    """Resposta simples para resultado por ID ou participante"""

    participante_inscricao: Optional[str] = Field(
        None, description="Número de inscrição"
    )
    nota_cn: Optional[float] = Field(None, description="Nota Ciências da Natureza")
    nota_ch: Optional[float] = Field(None, description="Nota Ciências Humanas")
    nota_lc: Optional[float] = Field(None, description="Nota Linguagens e Códigos")
    nota_mt: Optional[float] = Field(None, description="Nota Matemática")
    nota_redacao: Optional[float] = Field(None, description="Nota Redação")
    media_provas_objetivas: Optional[float] = Field(
        None, description="Média provas objetivas"
    )
    uf_prova_sigla: Optional[str] = Field(None, description="UF da prova")
    escola_codigo: Optional[int] = Field(None, description="Código da escola")
    nu_ano: Optional[int] = Field(None, description="Ano")
    id: Optional[str] = Field(None, description="ID do documento", alias="_id")

    class Config:
        populate_by_name = True  # Permite usar tanto 'id' quanto '_id'
