"""
Script de emergência para parar o bot
Execute este script se o bot ficar travado pressionando teclas
"""
import time
from pynput.keyboard import Key, Controller

print("Parando bot de emergência...")
print("Pressionando ESC várias vezes para parar ações...")

keyboard = Controller()

# Pressionar ESC várias vezes para parar qualquer ação
for i in range(10):
    keyboard.press(Key.esc)
    keyboard.release(Key.esc)
    time.sleep(0.1)

print("Bot parado!")

