# Pipeline de Processamento | LayrPDF

O LayrPDF processa documentos em 8 stages sequenciais. Cada stage tem uma responsabilidade única e passa seus resultados para o próximo exclusivamente através do `DocumentMap`.

---

## Stage 0: Abertura e Inspeção

**Módulo:** `pipeline.py`

Antes de qualquer processamento, o sistema verifica se o arquivo é válido e acessível.

- Abre o PDF e verifica se está criptografado ou protegido por senha
- Extrai metadados (título, autor, número de páginas, versão do PDF)
- Cria um ID de sessão único para rastreabilidade dos logs
- Aborta imediatamente se o arquivo não puder ser processado, evitando erros silenciosos nos stages seguintes

---

## Stage 1: Construção do DocumentMap

**Módulo:** `tools/coordinate_map.py`

O stage mais crítico do pipeline. Extrai toda a informação estrutural do PDF em uma única passagem.

- Normaliza coordenadas de página (trata rotações)
- Extrai texto no nível de **span**: fonte, tamanho, cor, bbox, flags, origem
- Coleta anotações de hiperlinks e associa aos spans correspondentes
- Detecta o estilo de corpo dominante por página (fonte e tamanho mais frequentes)
- Marca spans candidatos a math, código e proteção via heurísticas de font-family e regex
- Detecta regiões de tabela via pdfplumber ou PyMuPDF
- Monta o `DocumentMap` completo antes de qualquer transformação

**Saída:** `DocumentMap` preenchido com `PageMap`, `BlockMap`, `SpanMap` e `TableRegion`.

---

## Stage 2: Enriquecimento Semântico

**Módulo:** `ai/document_intelligence.py`

A camada de IA atua aqui. Ela nunca decide geometria, apenas enriquece os dados que o Core já extraiu.

- Classifica cada `BlockMap` por tipo: título, corpo, rodapé, tabela, código, legenda, etc.
- Gera um glossário do documento para manter consistência na tradução
- Identifica termos que não devem ser traduzidos (nomes próprios, siglas, termos de domínio)
- Sugere famílias de fonte para fallback caso a fonte original não esteja disponível

**Este stage é opcional no modo determinístico.** O pipeline pode avançar sem ele se a camada de IA estiver desabilitada.

---

## Stage 3: Planejamento de Tradução

**Módulo:** `core/translation_batcher.py`

Prepara o conteúdo para tradução antes de realizar chamadas de API.

- Percorre todos os spans do `DocumentMap`
- Exclui spans marcados como `is_protected`, `is_math` ou pertencentes a regiões de tabela
- Agrupa os spans traduzíveis em batches eficientes respeitando limites de tokens
- Atribui IDs estáveis a cada batch para mapeamento de retorno
- Deduplicação: strings idênticas são traduzidas uma única vez e reutilizadas via cache

---

## Stage 4: Tradução

**Módulo:** `core/translation_batcher.py`

Executa os batches planejados no Stage 3.

- Envia batches para o motor de tradução configurado (Google Translate por padrão)
- Aplica restrições de glossário para preservar termos travados
- Restaura placeholders de termos protegidos após a tradução
- Anexa o texto traduzido ao campo correspondente em cada `SpanMap`

---

## Stage 5: Resolução de Layout (Font Fitting)

**Módulo:** `core/overflow.py`

Traduções frequentemente produzem texto maior que o original. Este stage resolve o encaixe antes da reconstrução.

**Algoritmo:**
1. Mede a largura real do texto traduzido via PyMuPDF (sem estimativas)
2. Se o texto cabe no `bbox` original, o fluxo avança
3. Se não cabe, reduz o tamanho da fonte em **0.5pt** e mede novamente
4. Repete até encontrar o encaixe ou atingir o limite mínimo de tamanho
5. Se ainda não couber, aciona o fluxo de reescrita semântica

O incremento de 0.5pt garante precisão sem distorção perceptível na hierarquia tipográfica.

---

## Stage 6: Reconstrução de Página

**Módulo:** `core/inserter.py`, `core/table_handler.py`

Reconstrói cada página do PDF com o conteúdo traduzido, respeitando o layout original.

**Sequência por página:**
1. Computa o plano de redação: quais regiões serão apagadas
2. Aplica todas as redações de uma única vez para evitar conflitos de Z-order
3. Reinsere os spans traduzidos com suas coordenadas e atributos originais
4. Reinsere regiões de tabela com reconstrução célula a célula
5. Reintegra spans protegidos e regiões de math preservadas
6. Restaura metadados de hiperlinks clicáveis

---

## Stage 7: Validação e Score de Qualidade

**Módulo:** `core/validation.py`

Verifica a integridade estrutural do PDF de saída e gera o `QualityReport`.

**Verificações:**
- Contagem de páginas deve ser idêntica ao original
- Divergências de blocos são registradas explicitamente (sem silenciamento por zip)
- Contagem de regiões de tabela comparada entre original e saída
- Verificações de sanidade de imagens
- **Métrica de overlap de bounding boxes:** mede a sobreposição para quantificar fidelidade visual
- Páginas com risco alto são sinalizadas no relatório

O `QualityReport` é exposto via endpoint da API para inspeção durante o desenvolvimento.

---

## Fluxo de Fallback

Cada stage crítico possui um caminho de fallback explícito:

| Situação | Fallback |
|---|---|
| Fonte original indisponível | Substituição determinística via `font_manager.py` |
| Overflow persistente | Reescrita semântica com restrições |
| Página escaneada | OCR via Tesseract para alimentar o DocumentMap |
| Região de math complexa | Rasterização da região e reinserção como imagem |
| Tabela com baixa confiança | Preservação da região original sem tradução |
| Falha na API de tradução | Retorno do span original com registro no QualityReport |
