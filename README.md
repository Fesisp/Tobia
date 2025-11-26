# Pokeone Bot - Jogador Automatizado com IA

Bot autônomo para o jogo Pokeone MMORPG, capaz de jogar sem intervenção humana.

## ⚠️ AVISO IMPORTANTE

Este projeto é apenas para fins educacionais e de pesquisa. O uso de bots pode violar os termos de serviço do Pokeone e resultar em banimento permanente da sua conta. Use por sua própria conta e risco.

## 🚀 Características

- **Navegação Autônoma**: Exploração automática do mapa
- **Sistema de Quests**: Detecta e segue automaticamente objetivos de quests
- **Sistema de Batalha**: Batalhas automáticas com estratégias configuráveis
- **Captura de Pokémon**: Detecção e captura automática de Pokémon
- **Detecção de Estado**: Identifica automaticamente o estado do jogo
- **Comportamento Humano**: Padrões de movimento e timing realistas
- **Sistema de IA**: Suporte para aprendizado por reforço (opcional)
- **OCR**: Leitura de texto do jogo para melhor compreensão

## 📋 Requisitos

- Python 3.8 ou superior
- Windows 10/11 (testado)
- Tesseract OCR instalado (para funcionalidades de OCR)
- Acesso ao jogo Pokeone

## 🛠️ Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd pokeone-bot
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Instale o Tesseract OCR:
- Baixe de: https://github.com/UB-Mannheim/tesseract/wiki
- Adicione ao PATH do sistema

4. Configure o bot:
- Edite `config/settings.yaml` conforme necessário
- Ajuste a região de captura de tela se necessário

## 🎮 Uso

1. Inicie o jogo Pokeone
2. Execute o bot:
```bash
python src/core/main.py
```

3. O bot começará a operar automaticamente
4. Pressione `Ctrl+C` para parar

## ⚙️ Configuração

Edite `config/settings.yaml` para personalizar:

- **Região de captura**: Defina qual parte da tela capturar
- **Estratégia de batalha**: Escolha entre 'aggressive', 'defensive' ou 'balanced'
- **Auto-captura**: Habilite/desabilite captura automática
- **Auto-seguir quests**: Habilite/desabilite seguir objetivos de quests automaticamente
- **Delays**: Ajuste os delays para parecer mais humano

### Sistema de Quests

O bot pode detectar e seguir automaticamente objetivos de quests. Veja `QUESTS.md` para mais detalhes.

## 📁 Estrutura do Projeto

```
pokeone-bot/
├── src/
│   ├── perception/      # Módulos de percepção (captura, processamento)
│   ├── decision/        # Módulos de decisão (IA, estratégias)
│   ├── action/          # Módulos de ação (entrada, controle)
│   ├── knowledge/       # Base de conhecimento (dados do jogo)
│   └── core/           # Núcleo do bot
├── config/              # Arquivos de configuração
├── data/               # Dados e modelos
├── logs/               # Logs do bot
└── requirements.txt    # Dependências
```

## 🔧 Desenvolvimento

### Adicionar Novos Recursos

1. **Novos Estados**: Adicione em `GameState` enum e implemente detecção
2. **Novas Estratégias**: Crie classes em `src/decision/`
3. **Novos Templates**: Adicione imagens em `data/templates/`

### Treinar Modelo de IA

Para usar aprendizado por reforço:

1. Configure `ai.use_rl: true` em `settings.yaml`
2. Treine o modelo (implementar em `src/decision/rl_agent.py`)
3. Salve o modelo em `data/models/`

## 📝 Logs

Os logs são salvos em `logs/bot.log` e também exibidos no console.

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## 📄 Licença

Este projeto é fornecido "como está", sem garantias. Use por sua própria conta e risco.

## 🙏 Agradecimentos

- Comunidade Pokeone
- Desenvolvedores das bibliotecas utilizadas

