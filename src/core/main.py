"""
Arquivo principal para executar o bot
"""
import sys
import yaml
from pathlib import Path
from loguru import logger

# Adicionar o diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.bot_controller import BotController


def load_config(config_path: str = "config/settings.yaml") -> dict:
    """
    Carrega configurações do arquivo YAML
    
    Args:
        config_path: Caminho para o arquivo de configuração
        
    Returns:
        Dicionário com configurações
    """
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            logger.error(f"Arquivo de configuração não encontrado: {config_path}")
            sys.exit(1)
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configurações carregadas de {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Arquivo de configuração não encontrado: {config_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {e}")
        sys.exit(1)


def setup_logging(config: dict):
    """Configura o sistema de logging"""
    log_config = config.get('logging', {})
    level = log_config.get('level', 'INFO')
    log_file = log_config.get('file', 'logs/bot.log')
    console_output = log_config.get('console', True)
    
    # Criar diretório de logs se não existir
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remover handlers padrão
    logger.remove()
    
    # Handler para console
    if console_output:
        logger.add(
            sys.stdout,
            level=level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            colorize=True
        )
    
    # Handler para arquivo
    logger.add(
        log_file,
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )


def main():
    """Função principal"""
    # Carregar configurações
    config = load_config()
    
    # Configurar logging
    setup_logging(config)
    
    # Verificar se o bot está habilitado
    if not config.get('bot', {}).get('enabled', True):
        logger.warning("Bot desabilitado nas configurações")
        return
    
    # Criar e iniciar bot
    bot = BotController(config)
    
    logger.info("=" * 50)
    logger.info("Pokeone Bot - Iniciando...")
    logger.info("=" * 50)
    logger.info("Pressione Ctrl+C para parar o bot")
    logger.info("=" * 50)
    
    try:
        bot.start()
    except KeyboardInterrupt:
        logger.info("\nBot interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
    finally:
        bot.stop()
        logger.info("Bot finalizado")


if __name__ == "__main__":
    main()

