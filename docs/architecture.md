# Arquitetura | LayrPDF

## Visão Geral

O LayrPDF é um sistema híbrido de tradução de documentos PDF focado em preservação total de layout, hierarquia tipográfica, tabelas, links e estrutura do documento.

A arquitetura é baseada em separação rigorosa de responsabilidades entre três camadas:

- **Core Determinístico:** Gerencia geometria, extração, medição real de texto, redação e reinserção. Aplica regras matemáticas e geométricas sem adivinhação de contexto.
- **Camada de IA Semântica:** Responsável por classificação de blocos, geração de glossários, detecção de termos protegidos e reparo de fragmentos. Nunca decide coordenadas de página.
- **DocumentMap:** Representação estruturada única do documento. Todos os módulos consomem e enriquecem o mesmo objeto, eliminando cópias paralelas de estado.

---

## Princípios Arquiteturais

1. **IA nunca controla geometria.** Pode classificar ou reescrever texto, mas as coordenadas de página são sempre tratadas pelo Core.
2. **Core nunca controla semântica.** Não inventa contexto, apenas aplica resultados estruturados.
3. **DocumentMap é a única fonte de verdade.** Todos os módulos partem da mesma representação canônica.
4. **Precisão no nível de span.** Spans coloridos, fórmulas inline e formatação mista exigem granularidade de span para garantir fidelidade visual.
5. **Reconstrução em vez de substituição.** O documento traduzido é reconstruído a partir de dados de layout medidos.
6. **Preservar antes de transformar.** Em regiões ambíguas ou de risco, o sistema prefere manter o original a corromper o layout.
7. **Operações em lote.** Redações, chamadas de tradução e análises de IA são agrupadas para otimizar a performance.
8. **Estratégia de Fallback.** Todo comportamento de risco possui um caminho de contingência, especialmente para fontes e tabelas.

---

## Pipeline de Processamento

```
PDF de Entrada
      |
      v
[Stage 0] Abertura e Inspeção
      - Detecta PDFs criptografados ou protegidos
      - Extrai metadados
      - Cria sessão de processamento com ID único
      |
      v
[Stage 1] Construção do DocumentMap
      - Normaliza coordenadas de página
      - Extrai texto no nível de span (fonte, cor, bbox, flags)
      - Coleta anotações de links
      - Detecta estilo de corpo dominante
      - Marca regiões de math, código e spans protegidos
      - Detecta regiões de tabela
      |
      v
[Stage 2] Enriquecimento Semântico (IA)
      - Classifica blocos (título, corpo, rodapé, tabela, código...)
      - Gera glossário do documento
      - Coleta termos protegidos
      - Sugere fallbacks de fonte
      |
      v
[Stage 3] Planejamento de Tradução
      - Agrupa spans por traduzibilidade
      - Exclui spans protegidos, math e código
      - Monta batches de tradução
      - Preserva IDs estáveis para reconstrução
      |
      v
[Stage 4] Tradução
      - Executa batches no motor de tradução
      - Restaura placeholders e travas de glossário
      - Anexa texto traduzido aos spans correspondentes
      |
      v
[Stage 5] Resolução de Layout (Font Fitting)
      - Mede spans traduzidos com precisão via PyMuPDF
      - Reduz em decrementos de 0.5pt se necessário
      - Se não resolver, aciona reescrita por IA com restrições de glossário
      |
      v
[Stage 6] Reconstrução de Página
      - Computa plano de redação por página
      - Aplica redações uma vez por página
      - Reinsere conteúdo traduzido
      - Preserva estilo visual e metadado clicável de hiperlinks
      - Reinsere tabelas e regiões de math protegidas
      - Aplica reflow local conservador
      |
      v
[Stage 7] Validação e Score de Qualidade
      - Contagem de páginas deve bater com o original
      - Divergências de blocos são explícitas, nunca silenciosas
      - Métrica de overlap de bounding boxes
      - Verificações de sanidade de imagens e tabelas
      |
      v
PDF de Saída
```

---

## Estrutura de Pastas

```
layrpdf/
├── pipeline.py                  # Orquestrador principal dos stages
├── models/
│   ├── document_map.py          # Estruturas de dados do DocumentMap
│   ├── intelligence.py          # Modelos de saída da camada de IA
│   └── enums.py                 # Enums compartilhados
├── tools/
│   └── coordinate_map.py        # Construção do DocumentMap a partir do PDF
├── core/
│   ├── extractor.py             # Extração de spans, links e geometria
│   ├── translation_batcher.py   # Agrupamento e execução de traduções
│   ├── overflow.py              # Detecção e resolução de overflow de texto
│   ├── inserter.py              # Redação e reinserção de texto nas páginas
│   ├── table_handler.py         # Extração e reconstrução de tabelas
│   ├── font_manager.py          # Resolução de fontes e fallback
│   ├── validation.py            # Validação e score de qualidade
│   └── math_preservation.py     # Proteção de fórmulas e expressões matemáticas
├── ai/
│   ├── document_intelligence.py # Classificação de blocos e glossário
│   └── rewrite_for_fit.py       # Reescrita de texto para encaixe em overflow
├── tests/
│   ├── test_coordinate_map.py
│   ├── test_overflow.py
│   ├── test_font_manager.py
│   ├── test_math_detection.py
│   ├── test_tables.py
│   └── test_validation.py
└── docs/
    ├── architecture.md
    ├── data-model.md
    └── pipeline.md
```

---

## Referências de Design

**DeepL** utiliza uma abordagem de reconstrução para tradução de documentos: coleta de dados de layout, extração de texto estruturado e reconstrução via motor de renderização. O sistema também adota métricas de fidelidade baseadas em overlap e estratégias de font fitting incremental, padrões seguidos pelo Stage 5 do LayrPDF.

**Adobe Acrobat** distingue entre os modos de retenção de fluxo e retenção de layout. O LayrPDF é otimizado explicitamente para a retenção fiel do layout original.

**PDFMathTranslate** e sistemas acadêmicos de preservação de layout seguem o padrão de pipeline adotado: detecção de layout, extração estruturada, tradução e renderização com integridade visual preservada.
