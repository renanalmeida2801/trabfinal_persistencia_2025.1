import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger():
    """
    Configura e retorna o logger da aplicação com handlers para console e arquivo.

    Esta função configura um logger com as seguintes características:
    - Logs são salvos em arquivo rotativo (enem_api.log)
    - Logs também são exibidos no console
    - Rotação automática quando arquivo atinge 10MB
    - Mantém backup de até 5 arquivos antigos
    - Formato padronizado com timestamp, nível, nome e mensagem

    Args:
        None

    Returns:
        logging.Logger: Logger configurado pronto para uso

    Note:
        O diretório de logs é criado automaticamente se não existir.
        O logger é configurado apenas uma vez (singleton pattern).
    """

    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "enem_api.log"

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger("enem_api")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
