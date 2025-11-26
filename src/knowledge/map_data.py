"""
Dados de mapas e navegação
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from loguru import logger


class MapData:
    """Classe para gerenciar dados de mapas"""
    
    def __init__(self):
        """Inicializa os dados de mapa"""
        self.maps: Dict = {}
        self.current_map: Optional[str] = None
        self._load_map_data()
        logger.info("MapData inicializado")
    
    def _load_map_data(self):
        """Carrega dados de mapas"""
        map_path = Path("data/maps/maps.json")
        
        if map_path.exists():
            try:
                with open(map_path, 'r', encoding='utf-8') as f:
                    self.maps = json.load(f)
                logger.info(f"Dados de mapa carregados: {len(self.maps)} mapas")
            except Exception as e:
                logger.error(f"Erro ao carregar dados de mapa: {e}")
                self._create_default_maps()
        else:
            logger.warning("Arquivo de mapas não encontrado, criando padrão")
            self._create_default_maps()
            self._save_map_data()
    
    def _create_default_maps(self):
        """Cria dados padrão de mapas"""
        self.maps = {
            "pallet_town": {
                "name": "Pallet Town",
                "region": "kanto",
                "spawn_points": [
                    {"x": 100, "y": 100, "name": "spawn_1"},
                    {"x": 200, "y": 150, "name": "spawn_2"}
                ],
                "pokemon_centers": [
                    {"x": 150, "y": 120, "name": "pokemon_center_1"}
                ]
            }
        }
    
    def _save_map_data(self):
        """Salva dados de mapas"""
        map_path = Path("data/maps/maps.json")
        map_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(map_path, 'w', encoding='utf-8') as f:
                json.dump(self.maps, f, indent=2, ensure_ascii=False)
            logger.info("Dados de mapa salvos")
        except Exception as e:
            logger.error(f"Erro ao salvar dados de mapa: {e}")
    
    def get_map_info(self, map_name: str) -> Optional[Dict]:
        """
        Obtém informações de um mapa
        
        Args:
            map_name: Nome do mapa
            
        Returns:
            Dicionário com informações ou None
        """
        key = map_name.lower().strip()
        return self.maps.get(key)
    
    def set_current_map(self, map_name: str):
        """
        Define o mapa atual
        
        Args:
            map_name: Nome do mapa
        """
        if map_name in self.maps:
            self.current_map = map_name
            logger.info(f"Mapa atual definido: {map_name}")
        else:
            logger.warning(f"Mapa não encontrado: {map_name}")
    
    def get_spawn_points(self, map_name: Optional[str] = None) -> List[Dict]:
        """
        Obtém pontos de spawn de um mapa
        
        Args:
            map_name: Nome do mapa (se None, usa mapa atual)
            
        Returns:
            Lista de pontos de spawn
        """
        map_name = map_name or self.current_map
        if not map_name:
            return []
        
        map_info = self.get_map_info(map_name)
        return map_info.get('spawn_points', []) if map_info else []
    
    def get_pokemon_centers(self, map_name: Optional[str] = None) -> List[Dict]:
        """
        Obtém Pokémon Centers de um mapa
        
        Args:
            map_name: Nome do mapa (se None, usa mapa atual)
            
        Returns:
            Lista de Pokémon Centers
        """
        map_name = map_name or self.current_map
        if not map_name:
            return []
        
        map_info = self.get_map_info(map_name)
        return map_info.get('pokemon_centers', []) if map_info else []

