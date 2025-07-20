from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas a partir de variáveis de ambiente.

    Esta classe utiliza Pydantic Settings para carregar e validar configurações
    da aplicação a partir de variáveis de ambiente ou arquivo .env.

    Note:
        As variáveis de ambiente devem ser definidas ou um arquivo .env deve
        estar presente no diretório raiz do projeto.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    MONGO_URL: str
    DATABASE_NAME: str


settings = Settings()
