from typing import Optional

from pydantic import BaseModel, Field


class QuestionarioSocioeconomico(BaseModel):
    """Questionário socioeconômico do ENEM"""

    # Perguntas sobre escolaridade dos pais
    Q001: Optional[str] = Field(
        None, description="Até que série seu pai ou responsável estudou?"
    )
    Q002: Optional[str] = Field(
        None, description="Até que série sua mãe ou responsável estudou?"
    )

    # Perguntas sobre ocupação
    Q003: Optional[str] = Field(
        None,
        description="A partir da apresentação de algumas ocupações, qual o nível de escolaridade mais próximo do seu pai?",
    )
    Q004: Optional[str] = Field(
        None,
        description="A partir da apresentação de algumas ocupações, qual o nível de escolaridade mais próximo do sua mãe?",
    )

    # Perguntas sobre renda
    Q005: Optional[str] = Field(
        None, description="Incluindo você, quantas pessoas moram na sua residência?"
    )
    Q006: Optional[str] = Field(
        None, description="Qual é aproximadamente a renda total de sua família?"
    )

    # Perguntas sobre bens da família
    Q007: Optional[str] = Field(
        None, description="Na sua residência trabalha empregado(a) doméstico(a)?"
    )
    Q008: Optional[str] = Field(
        None, description="Na sua residência há quantos quartos?"
    )
    Q009: Optional[str] = Field(
        None, description="Quantos banheiros há na sua residência?"
    )
    Q010: Optional[str] = Field(
        None, description="Na sua residência há quantos automóveis?"
    )
    Q011: Optional[str] = Field(
        None, description="Na sua residência há quantas motocicletas?"
    )
    Q012: Optional[str] = Field(None, description="Na sua residência há geladeira?")
    Q013: Optional[str] = Field(None, description="Na sua residência há freezer?")
    Q014: Optional[str] = Field(
        None, description="Na sua residência há máquina de lavar roupa?"
    )
    Q015: Optional[str] = Field(
        None, description="Na sua residência há máquina de secar roupa?"
    )
    Q016: Optional[str] = Field(
        None, description="Na sua residência há forno microondas?"
    )
    Q017: Optional[str] = Field(
        None, description="Na sua residência há máquina de lavar louça?"
    )
    Q018: Optional[str] = Field(
        None, description="Na sua residência há aspirador de pó?"
    )
    Q019: Optional[str] = Field(
        None, description="Na sua residência há televisão em cores?"
    )
    Q020: Optional[str] = Field(
        None, description="Na sua residência há acesso à Internet?"
    )
    Q021: Optional[str] = Field(
        None, description="Na sua residência há TV por assinatura?"
    )
    Q022: Optional[str] = Field(
        None, description="Na sua residência há telefone celular?"
    )
    Q023: Optional[str] = Field(None, description="Na sua residência há telefone fixo?")
