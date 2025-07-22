import asyncio
from pathlib import Path

from fastapi import APIRouter

from config.logs import logger

router = APIRouter(prefix="/admin", tags=["Administração"])


@router.post("/load-data")
async def load_data_endpoint():
    """Endpoint para carregar dados iniciais do CSV para o MongoDB"""
    try:
        data_path = Path("data")
        csv_participantes = data_path / "amostra_participantes.csv"
        csv_resultados = data_path / "amostra_resultados.csv"

        if csv_participantes.exists() and csv_resultados.exists():
            logger.info("Iniciando carregamento de dados...")
            from scripts.load_data import load_data_to_mongodb

            await asyncio.get_event_loop().run_in_executor(None, load_data_to_mongodb)
            logger.info("Dados carregados com sucesso!")

            return {
                "status": "success",
                "message": "Dados carregados com sucesso!",
                "files_processed": [str(csv_participantes), str(csv_resultados)],
            }
        else:
            logger.warning(
                "Arquivos CSV não encontrados em 'data/'. Carregamento cancelado."
            )
            return {
                "status": "error",
                "message": "Arquivos CSV não encontrados em 'data/'",
                "expected_files": [str(csv_participantes), str(csv_resultados)],
            }

    except Exception as e:
        logger.error(f"Erro ao carregar dados: {e}")
        return {"status": "error", "message": f"Erro ao carregar dados: {str(e)}"}
