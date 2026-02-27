"""
Configuração compartilhada dos testes.
Garante que o pacote `src` esteja no PYTHONPATH para imports bronze/silver/gold_core/ml/registry.
"""
import sys
from pathlib import Path

# Permite imports como: from bronze.bronze_ingestion import ingest_raw
_root = Path(__file__).resolve().parent.parent
_src = _root / "src"
# também adiciona a raiz do projeto para permitir imports de pacotes de nível superior
# como `orchestration`
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
