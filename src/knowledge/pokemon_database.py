import json
import requests
import os
from pathlib import Path
from loguru import logger

class PokemonDatabase:
    def __init__(self):
        self.local_db_path = Path("data/pokemon_local_db.json")
        self.api_url = "https://pokeapi.co/api/v2/pokemon/"
        self.data = {}
        self._load_local_db()

    def _load_local_db(self):
        """Carrega o JSON local na memória"""
        if self.local_db_path.exists():
            try:
                with open(self.local_db_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info(f"DB Local carregado: {len(self.data)} Pokémons conhecidos.")
            except Exception as e:
                logger.error(f"Erro ao carregar DB local: {e}")
                self.data = {}

    def _save_local_db(self):
        """Salva a memória no arquivo JSON"""
        try:
            with open(self.local_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar DB local: {e}")

    def get_pokemon_info(self, name: str):
        name = name.lower().strip()
        
        # 1. Tenta pegar do Local
        if name in self.data:
            return self.data[name]
            
        # 2. Se não tem, busca na API, salva e retorna
        logger.warning(f"Pokemon '{name}' desconhecido. Buscando na API...")
        return self._fetch_and_save(name)

    def _fetch_and_save(self, name: str):
        try:
            response = requests.get(f"{self.api_url}{name}", timeout=5)
            if response.status_code == 200:
                api_data = response.json()
                
                # Filtramos apenas o essencial para salvar espaço
                clean_data = {
                    "types": [t['type']['name'] for t in api_data['types']],
                    "base_stats": {s['stat']['name']: s['base_stat'] for s in api_data['stats']}
                }
                
                self.data[name] = clean_data
                self._save_local_db() # Persistência imediata
                return clean_data
        except Exception as e:
            logger.error(f"Falha ao buscar '{name}': {e}")
        
        return None