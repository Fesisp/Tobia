"""
Base de dados de Pokémon
"""
import json
from pathlib import Path
from typing import Dict, Optional, List
from loguru import logger


class PokemonDatabase:
    """Classe para gerenciar dados de Pokémon"""
    
    def __init__(self):
        """Inicializa a base de dados"""
        self.pokemon_data: Dict = {}
        self._load_database()
        logger.info("PokemonDatabase inicializado")
    
    def _load_database(self):
        """Carrega a base de dados de Pokémon"""
        db_path = Path("data/pokemon_stats.json")
        
        if db_path.exists():
            try:
                with open(db_path, 'r', encoding='utf-8') as f:
                    self.pokemon_data = json.load(f)
                logger.info(f"Base de dados carregada: {len(self.pokemon_data)} Pokémon")
            except Exception as e:
                logger.error(f"Erro ao carregar base de dados: {e}")
                self._create_default_database()
        else:
            logger.warning("Arquivo de base de dados não encontrado, criando padrão")
            self._create_default_database()
            self._save_database()
    
    def _create_default_database(self):
        """Cria uma base de dados padrão com alguns Pokémon comuns"""
        self.pokemon_data = {
            "pikachu": {
                "name": "Pikachu",
                "types": ["electric"],
                "base_stats": {
                    "hp": 35,
                    "attack": 55,
                    "defense": 40,
                    "sp_attack": 50,
                    "sp_defense": 50,
                    "speed": 90
                }
            },
            "charizard": {
                "name": "Charizard",
                "types": ["fire", "flying"],
                "base_stats": {
                    "hp": 78,
                    "attack": 84,
                    "defense": 78,
                    "sp_attack": 109,
                    "sp_defense": 85,
                    "speed": 100
                }
            },
            "blastoise": {
                "name": "Blastoise",
                "types": ["water"],
                "base_stats": {
                    "hp": 79,
                    "attack": 83,
                    "defense": 100,
                    "sp_attack": 85,
                    "sp_defense": 105,
                    "speed": 78
                }
            }
        }
    
    def _save_database(self):
        """Salva a base de dados em arquivo"""
        db_path = Path("data/pokemon_stats.json")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(self.pokemon_data, f, indent=2, ensure_ascii=False)
            logger.info("Base de dados salva")
        except Exception as e:
            logger.error(f"Erro ao salvar base de dados: {e}")
    
    def get_pokemon_info(self, pokemon_name: str) -> Optional[Dict]:
        """
        Obtém informações de um Pokémon
        
        Args:
            pokemon_name: Nome do Pokémon
            
        Returns:
            Dicionário com informações ou None
        """
        key = pokemon_name.lower().strip()
        return self.pokemon_data.get(key)
    
    def get_pokemon_types(self, pokemon_name: str) -> List[str]:
        """
        Obtém os tipos de um Pokémon
        
        Args:
            pokemon_name: Nome do Pokémon
            
        Returns:
            Lista de tipos
        """
        info = self.get_pokemon_info(pokemon_name)
        return info.get('types', []) if info else []
    
    def add_pokemon(self, pokemon_name: str, data: Dict):
        """
        Adiciona ou atualiza um Pokémon na base de dados
        
        Args:
            pokemon_name: Nome do Pokémon
            data: Dados do Pokémon
        """
        key = pokemon_name.lower().strip()
        self.pokemon_data[key] = data
        self._save_database()
        logger.info(f"Pokémon {pokemon_name} adicionado/atualizado na base de dados")

