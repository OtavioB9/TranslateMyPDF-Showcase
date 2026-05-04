# Pasta Core

Esta pasta contém o "coração" tecnológico do sistema LayrPDF. Cada módulo aqui é responsável por uma parte vital do motor de processamento, formando um pipeline coeso que garante a integridade visual e tipográfica durante a tradução.

## Arquitetura de Módulos

### 1. `models.py` (Estruturas de Dados)
Define as entidades fundamentais do sistema (`PageData`, `SpanData`, `TableRegionData`). Estas classes encapsulam toda a extração de texto, preservando coordenadas espaciais, tamanhos de fonte, cores RGB e flags de estilo.

### 2. `document_map.py` (Single Source of Truth)
Define a representação canônica do documento. Transforma os dados brutos de extração em uma hierarquia lógica de Blocos e Spans, facilitando a validação e a reconstrução visual.

### 3. `classifier.py` (Roteamento Inteligente)
Atua como o roteador inicial. Identifica se uma página é predominantemente vetorial ou baseada em imagem, redirecionando o fluxo automaticamente para o motor de extração adequado.

### 4. `extractor.py` (Extrator Vetorial)
O extrator principal que trata o PDF como um gráfico vetorial. Utiliza algoritmos de agrupamento espacial para unir palavras em sentenças lógicas e filtrar ruídos de formatação.

### 5. `ocr_extractor.py` (Extrator OCR)
Acionado como fallback pelo classificador. Utiliza o motor Tesseract para efetuar a leitura visual de páginas-imagem, gerando Bounding Boxes compatíveis com a arquitetura vetorial.

### 6. `table_detector.py` (Preservação de Tabelas)
Ferramenta preventiva contra corrupção geométrica. Escaneia proativamente vetores e grades para identificar células de tabelas, blindando suas coordenadas para evitar falhas em layouts colunares.

### 7. `translator.py` (Orquestrador de Tradução)
Integra chamadas às APIs de tradução. Implementa lógica de batching para otimização de custos e o mecanismo de "Tradução Cirúrgica" para preservar termos técnicos e fórmulas matemáticas.

### 8. `font_manager.py` (Gestão Tipográfica)
Garante a solidez visual substituindo fontes embutidas complexas por alternativas equivalentes, evitando falhas de renderização e garantindo suporte total a caracteres acentuados.

### 9. `redactor.py` (Composição Visual)
O módulo final que deleta o texto original e reinsere a tradução. Calcula restrições de colisão e ajusta dinamicamente o tamanho da fonte para o encaixe perfeito no espaço original.

### 10. `validation.py` (Auditoria de Qualidade)
Realiza uma análise heurística pós-tradução para identificar riscos de overflow, quebra de links ou perda de termos protegidos, gerando relatórios de qualidade detalhados.

### 11. `toc.py` (Estratégia de Sumário)
Gerencia a decomposição e reconstrução de entradas de Table of Contents (TOC). Garante que o sumário traduzido preserve a navegabilidade e o alinhamento visual original.
