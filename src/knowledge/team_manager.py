import json
from pathlib import Path

class TeamManager:
    def __init__(self):
        self.moves_db_path = Path("data/known_moves.json")
        self.current_team = [] # Lista volátil, atualizada em tempo real
        self.known_moves = {}  # Dicionário persistente
        self._load_moves()

    def update_team_from_hud(self, ocr_results_list):
        """
        Chamado durante a Exploração.
        Recebe a lista de nomes lidos via OCR no canto inferior direito.
        """
        # Atualiza a lista atual (sobrescreve a anterior)
        self.current_team = [name.lower().strip() for name in ocr_results_list[:6]]
        # logger.info(f"Equipe atual detectada: {self.current_team}")

    def update_pokemon_moves(self, pokemon_name, moves_list):
        """
        Chamado durante a Batalha.
        Lê os botões de ataque e salva no banco permanente.
        """
        name = pokemon_name.lower().strip()
        
        # Se já conhecemos esse pokemon e os golpes mudaram (aprendeu novo), atualizamos
        if name not in self.known_moves or self.known_moves[name] != moves_list:
            self.known_moves[name] = moves_list
            self._save_moves()
            # logger.info(f"Movimentos atualizados para {name}: {moves_list}")

    def get_moves_for(self, pokemon_name):
        return self.known_moves.get(pokemon_name.lower().strip(), [])

    def _load_moves(self):
        if self.moves_db_path.exists():
            with open(self.moves_db_path, 'r') as f:
                self.known_moves = json.load(f)

    def _save_moves(self):
        with open(self.moves_db_path, 'w') as f:
            json.dump(self.known_moves, f, indent=2)