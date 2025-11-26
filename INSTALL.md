# Guia de Instalação - Pokeone Bot

## Pré-requisitos

1. **Python 3.8 ou superior**
   - Baixe em: https://www.python.org/downloads/
   - Certifique-se de marcar "Add Python to PATH" durante a instalação

2. **Tesseract OCR** (opcional, mas recomendado)
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki
   - Adicione ao PATH do sistema após instalação

## Instalação Passo a Passo

### 1. Clone ou baixe o projeto

```bash
git clone <repository-url>
cd pokeone-bot
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o bot

Edite o arquivo `config/settings.yaml`:

- Ajuste a região de captura de tela se necessário
- Configure estratégias de batalha
- Ajuste delays e comportamento humano

### 5. Execute o bot

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
python src/core/main.py
```

## Configuração Avançada

### Região de Captura de Tela

Se o jogo não estiver em tela cheia, você pode especificar a região:

```yaml
screen:
  region: [100, 100, 800, 600]  # [x, y, width, height]
```

### Estratégias de Batalha

Escolha entre:
- `aggressive`: Sempre ataca, troca apenas em emergência
- `defensive`: Prioriza sobrevivência, troca frequentemente
- `balanced`: Equilibra ataque e defesa

## Solução de Problemas

### Erro: "mss não encontrado"
```bash
pip install mss
```

### Erro: "pytesseract não encontrado"
- Instale o Tesseract OCR
- Configure o PATH do sistema

### Erro: "pynput não funciona"
- No Windows, pode precisar de permissões de administrador
- Verifique se o antivírus não está bloqueando

### Bot não detecta o jogo
- Verifique se a região de captura está correta
- Certifique-se de que o jogo está visível na tela
- Tente aumentar o FPS em `config/settings.yaml`

## Próximos Passos

1. Teste o bot em uma área segura
2. Ajuste as configurações conforme necessário
3. Monitore os logs em `logs/bot.log`
4. Adicione templates de imagem para melhor detecção

## Suporte

Para problemas ou dúvidas, consulte:
- README.md
- Logs em `logs/bot.log`
- Issues no repositório

