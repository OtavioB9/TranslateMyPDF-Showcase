# Pasta Utils

Esta pasta contém ferramentas de suporte (utilitários) que auxiliam o sistema a manter a organização, logs de execução e a qualidade dos dados.

## Utilitários

### 1. `logger.py` (Observabilidade)
Centraliza as mensagens de log do sistema (INFO, DEBUG, WARNING, ERROR), facilitando a depuração de processos de longa duração.

### 2. `text.py` (Processamento de Texto)
Contém a inteligência determinística para:
- **Detecção de Termos Protegidos**: Identificação de URLs, ISBNs e tokens técnicos via Regex.
- **Filtragem de Ruído**: Determina se um span de texto é relevante para tradução ou se é ruído de layout (números de página, fórmulas matemáticas isoladas).
- **Normalização**: Limpeza e preparação do texto para os provedores de tradução.
