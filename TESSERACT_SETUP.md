# Configuração do Tesseract OCR

## Problema

O Tesseract está instalado no seu PC, mas o Python não consegue encontrá-lo porque não está no PATH do sistema ou o `pytesseract` precisa saber o caminho exato.

## Solução Automática

O bot agora tenta encontrar automaticamente o Tesseract nos locais comuns de instalação no Windows:

- `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
- `C:\Users\[SEU_USUARIO]\AppData\Local\Tesseract-OCR\tesseract.exe`
- `C:\Tesseract-OCR\tesseract.exe`

## Solução Manual

Se o bot não encontrar automaticamente, você pode configurar manualmente:

### Opção 1: Adicionar ao PATH do Sistema

1. Encontre onde o Tesseract está instalado (geralmente em `C:\Program Files\Tesseract-OCR\`)
2. Copie o caminho completo até a pasta `Tesseract-OCR`
3. Adicione ao PATH do Windows:
   - Pressione `Win + R`, digite `sysdm.cpl` e pressione Enter
   - Vá em "Avançado" → "Variáveis de Ambiente"
   - Em "Variáveis do sistema", encontre "Path" e clique em "Editar"
   - Clique em "Novo" e cole o caminho
   - Clique em "OK" em todas as janelas
   - Reinicie o terminal/PowerShell

### Opção 2: Configurar no settings.yaml

Edite o arquivo `config/settings.yaml` e adicione o caminho completo:

```yaml
# Configurações de OCR
ocr:
  tesseract_path: "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # Caminho completo
  use_easyocr: false  # Usar EasyOCR ao invés de Tesseract
```

**Importante**: Use barras duplas (`\\`) ou barras normais (`/`) no caminho.

### Opção 3: Encontrar o Caminho Manualmente

1. Abra o Explorador de Arquivos
2. Navegue até onde o Tesseract está instalado
3. Procure pelo arquivo `tesseract.exe`
4. Clique com o botão direito → "Propriedades"
5. Copie o caminho completo mostrado em "Local"
6. Use esse caminho no `settings.yaml`

## Verificar se Funcionou

Após configurar, execute o bot novamente. Você deve ver no log:

```
INFO: Tesseract encontrado em: C:\Program Files\Tesseract-OCR\tesseract.exe
INFO: Tesseract configurado: C:\Program Files\Tesseract-OCR\tesseract.exe
```

Se ainda não funcionar, verifique:
- O caminho está correto?
- O arquivo `tesseract.exe` existe nesse caminho?
- Você tem permissões para acessar o arquivo?

## Alternativa: Usar EasyOCR

Se não conseguir configurar o Tesseract, você pode usar EasyOCR (já instalado):

```yaml
ocr:
  use_easyocr: true  # Usar EasyOCR
```

O EasyOCR é mais lento, mas não requer configuração adicional.

