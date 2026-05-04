# Pasta Pipeline

Esta pasta contém o orquestrador que une todas as peças do sistema e gerencia o fluxo de trabalho de ponta a ponta.

## Componentes

### 1. `document.py` (O Maestro)
Coordena a sequência de classificação, extração, tradução e redação. Suas principais responsabilidades incluem:
- **Batching**: Processamento de páginas em lotes para otimização de memória.
- **Checkpointing**: Mecanismo de persistência que permite retomar o processamento de grandes documentos em caso de falha.
- **Auditoria**: Geração automática do relatório de qualidade (`.quality.json`) ao final de cada execução.

---
*O objetivo desta pasta é isolar a lógica de "como um documento é orquestrado" da lógica de baixo nível de processamento, garantindo um código modular e fácil de escalar.*
