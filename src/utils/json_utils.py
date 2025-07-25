from bson import ObjectId
from typing import Any, Dict, List, Union


def convert_objectid_to_str(obj: Any) -> Any:
    """
    Converte ObjectId para string recursivamente em estruturas de dados.

    Args:
        obj: Objeto a ser convertido

    Returns:
        Objeto com ObjectIds convertidos para strings
    """
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: convert_objectid_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_objectid_to_str(item) for item in obj)
    else:
        return obj


def serialize_mongo_document(doc: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
    """
    Serializa documentos do MongoDB convertendo ObjectIds para strings.

    Args:
        doc: Documento ou lista de documentos do MongoDB

    Returns:
        Documento serializado
    """
    if doc is None:
        return None

    return convert_objectid_to_str(doc)
