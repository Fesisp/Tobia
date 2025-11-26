"""
Módulo para simular entrada de teclado e mouse
"""
import time
import random
from typing import Optional
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
from loguru import logger


class InputSimulator:
    """Classe para simular entrada de teclado e mouse"""
    
    def __init__(self, human_like: bool = True, 
                 min_delay: float = 0.05, 
                 max_delay: float = 0.3):
        """
        Inicializa o simulador de entrada
        
        Args:
            human_like: Se True, adiciona delays humanos
            min_delay: Delay mínimo entre ações
            max_delay: Delay máximo entre ações
        """
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        self.human_like = human_like
        self.min_delay = min_delay
        self.max_delay = max_delay
        
        logger.info("InputSimulator inicializado")
    
    def _random_delay(self):
        """Adiciona um delay aleatório se human_like estiver ativado"""
        if self.human_like:
            delay = random.uniform(self.min_delay, self.max_delay)
            time.sleep(delay)
    
    def press_key(self, key: str, duration: float = 0.1):
        """
        Pressiona uma tecla
        
        Args:
            key: Tecla para pressionar (ex: 'w', 'a', 's', 'd', 'space')
            duration: Duração do pressionamento
        """
        try:
            key_map = {
                'w': 'w', 'a': 'a', 's': 's', 'd': 'd',
                'up': Key.up, 'down': Key.down,
                'left': Key.left, 'right': Key.right,
                'space': Key.space, 'enter': Key.enter,
                'esc': Key.esc, 'tab': Key.tab,
                '1': '1', '2': '2', '3': '3', '4': '4',
                '5': '5', '6': '6', '7': '7', '8': '8',
                '9': '9', '0': '0'
            }
            
            key_to_press = key_map.get(key.lower(), key)
            
            if isinstance(key_to_press, Key):
                self.keyboard.press(key_to_press)
                time.sleep(duration)
                self.keyboard.release(key_to_press)
            else:
                self.keyboard.press(key_to_press)
                time.sleep(duration)
                self.keyboard.release(key_to_press)
            
            self._random_delay()
            logger.debug(f"Tecla pressionada: {key}")
        except Exception as e:
            logger.error(f"Erro ao pressionar tecla {key}: {e}")
    
    def move(self, direction: str, duration: float = 0.1):
        """
        Move o personagem na direção especificada
        
        Args:
            direction: Direção ('up', 'down', 'left', 'right')
            duration: Duração do movimento
        """
        direction_map = {
            'up': 'w',
            'down': 's',
            'left': 'a',
            'right': 'd'
        }
        
        key = direction_map.get(direction.lower())
        if key:
            self.press_key(key, duration)
    
    def click(self, x: Optional[int] = None, 
              y: Optional[int] = None, 
              button: str = 'left'):
        """
        Clica na posição especificada
        
        Args:
            x: Coordenada X (se None, usa posição atual do mouse)
            y: Coordenada Y (se None, usa posição atual do mouse)
            button: Botão do mouse ('left' ou 'right')
        """
        try:
            if x is not None and y is not None:
                self.mouse.position = (x, y)
                self._random_delay()
            
            btn = Button.left if button == 'left' else Button.right
            self.mouse.click(btn)
            
            self._random_delay()
            logger.debug(f"Clique em ({x}, {y})")
        except Exception as e:
            logger.error(f"Erro ao clicar: {e}")
    
    def type_text(self, text: str, delay: float = 0.1):
        """
        Digita um texto
        
        Args:
            text: Texto para digitar
            delay: Delay entre caracteres
        """
        try:
            for char in text:
                self.keyboard.type(char)
                time.sleep(delay)
            self._random_delay()
        except Exception as e:
            logger.error(f"Erro ao digitar texto: {e}")
    
    def press_sequence(self, keys: list, delay: float = 0.1):
        """
        Pressiona uma sequência de teclas
        
        Args:
            keys: Lista de teclas
            delay: Delay entre teclas
        """
        for key in keys:
            self.press_key(key, delay)
            time.sleep(delay)
    
    def hold_key(self, key: str, duration: float):
        """
        Segura uma tecla por um período
        
        Args:
            key: Tecla para segurar
            duration: Duração em segundos
        """
        try:
            key_map = {
                'w': 'w', 'a': 'a', 's': 's', 'd': 'd',
                'up': Key.up, 'down': Key.down,
                'left': Key.left, 'right': Key.right,
            }
            
            key_to_press = key_map.get(key.lower(), key)
            
            if isinstance(key_to_press, Key):
                self.keyboard.press(key_to_press)
                time.sleep(duration)
                self.keyboard.release(key_to_press)
            else:
                self.keyboard.press(key_to_press)
                time.sleep(duration)
                self.keyboard.release(key_to_press)
        except Exception as e:
            logger.error(f"Erro ao segurar tecla {key}: {e}")

