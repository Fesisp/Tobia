# Sistema de Gerenciamento de Quests

## Visão Geral

O bot agora possui um sistema completo de gerenciamento de quests que permite:
- Detectar automaticamente quests ativas na UI
- Ler o título e objetivo da quest
- Navegar até o objetivo usando o botão "Goto" ou navegação manual
- Seguir quests automaticamente durante a exploração

## Como Funciona

### 1. Detecção de Quests

O sistema detecta a UI de Quests no canto superior direito da tela usando:
- **OCR (Optical Character Recognition)**: Lê o texto da região de quests
- **Processamento de Imagem**: Identifica elementos visuais da UI
- **Análise de Texto**: Extrai título e objetivo da quest

### 2. Extração de Informações

O bot extrai:
- **Título da Quest**: Nome da missão (ex: "Hard as a Rock")
- **Objetivo**: Descrição do que precisa ser feito (ex: "Challenge Brock in Pewter City Gym")
- **Botão Goto**: Detecta se há um botão "Goto" disponível

### 3. Navegação até Objetivo

Quando uma quest está ativa, o bot:
1. Tenta usar o botão "Goto" se disponível (clica automaticamente)
2. Se não houver botão, extrai a localização do objetivo e navega manualmente
3. Continua seguindo a quest até completá-la

## Configuração

Edite `config/settings.yaml`:

```yaml
# Configurações de Quests
quests:
  auto_follow: true  # Seguir automaticamente objetivos de quests
  check_interval: 5.0  # Intervalo para verificar quests (segundos)
  use_goto_button: true  # Usar botão Goto quando disponível
```

### Parâmetros

- **auto_follow**: Se `true`, o bot seguirá automaticamente os objetivos das quests. Se `false`, apenas detecta mas não segue.
- **check_interval**: Intervalo em segundos entre verificações de quests. Valores menores = mais responsivo, mas mais uso de CPU.
- **use_goto_button**: Se `true`, tenta usar o botão "Goto" quando disponível.

## Ajustes de Região de Detecção

Se a detecção não estiver funcionando corretamente, você pode ajustar a região de detecção em `src/perception/quest_detector.py`:

```python
# Região aproximada da UI de Quests (canto superior direito)
# Ajustar conforme necessário baseado na resolução
quest_region_x = int(width * 0.7)  # 70% da largura
quest_region_y = int(height * 0.05)  # 5% da altura
quest_region_w = int(width * 0.28)  # 28% da largura
quest_region_h = int(height * 0.25)  # 25% da altura
```

## Localizações Suportadas

O bot reconhece automaticamente as seguintes localizações nos objetivos:

- Pewter City
- Pewter City Gym
- Viridian City
- Cerulean City
- Pallet Town
- Gym (qualquer ginásio)
- Pokemon Center

Para adicionar mais localizações, edite `src/action/quest_controller.py`:

```python
location_keywords = {
    'pewter city': 'pewter_city',
    'pewter city gym': 'pewter_city_gym',
    # Adicione mais aqui
}
```

## Troubleshooting

### Bot não detecta quests

1. Verifique se a região de detecção está correta para sua resolução
2. Aumente o nível de log para DEBUG para ver mensagens detalhadas
3. Verifique se o OCR está funcionando corretamente (Tesseract instalado)

### Bot não clica no botão Goto

1. Verifique se o botão está visível na tela
2. Ajuste as cores de detecção em `find_goto_button()` se necessário
3. Tente aumentar o intervalo de verificação

### Bot não navega até o objetivo

1. Verifique se a localização está na lista de localizações suportadas
2. Adicione a localização manualmente se necessário
3. O bot pode precisar de navegação manual implementada para localizações específicas

## Melhorias Futuras

- [ ] Navegação automática até localizações específicas
- [ ] Detecção de conclusão de quest
- [ ] Sistema de priorização de quests
- [ ] Suporte para múltiplas quests ativas
- [ ] Integração com sistema de mapas

## Logs

O bot registra informações sobre quests nos logs:

```
INFO: Quest detectada: Hard as a Rock
DEBUG: Objetivo: Challenge Brock in Pewter City Gym
INFO: Clicando no botão Goto da quest
INFO: Seguindo objetivo da quest
```

Para ver logs detalhados, configure `logging.level: "DEBUG"` em `config/settings.yaml`.

