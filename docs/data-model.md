# Modelo de Dados | DocumentMap

O `DocumentMap` é a estrutura central do LayrPDF. Todos os módulos do pipeline consomem e enriquecem esse objeto, tornando-o a única fonte de verdade sobre o estado do documento durante todo o processamento.

---

## Hierarquia

```
DocumentMap
└── PageMap[]           (uma entrada por página)
    ├── BlockMap[]      (blocos de texto da página)
    │   └── SpanMap[]   (spans individuais dentro de cada bloco)
    └── TableRegion[]   (regiões de tabela detectadas)
```

---

## SpanMap

Representa um span individual: a menor unidade de texto com atributos próprios como fonte, cor, tamanho e posição.

```python
@dataclass
class SpanMap:
    id: str                          # Identificador único do span
    text: str                        # Texto original
    bbox: tuple[float, float, float, float]   # Bounding box (x0, y0, x1, y1)
    origin: tuple[float, float]      # Ponto de origem do texto
    page_number: int                 # Número da página (base 0)
    block_id: str                    # ID do bloco pai
    line_no: int                     # Índice da linha dentro do bloco
    font_raw: str                    # Nome da fonte como aparece no PDF
    font_clean: str                  # Nome da fonte normalizado
    font_family: str                 # Família tipográfica inferida
    size: float                      # Tamanho da fonte em pontos
    color: int                       # Cor em inteiro RGB
    color_hex: str                   # Cor em hexadecimal (#rrggbb)
    flags: int                       # Flags do span (bold, italic, etc.)
    has_non_body_color: bool         # True se a cor for diferente do corpo dominante
    is_hyperlink: bool               # True se o span fizer parte de um link
    hyperlink_uri: str | None        # URI do link, se aplicável
    is_math: bool                    # True se detectado como expressão matemática
    math_font_type: str              # Tipo de fonte math (cmmi, stix, symbol, etc.)
    math_strategy: Literal["protect", "rasterize", ""]  # Estratégia de preservação
    is_protected: bool               # True se o span não deve ser traduzido
    protection_reason: str           # Motivo da proteção (math, code, url, isbn...)
    reading_order: int               # Ordem de leitura dentro da página
```

---

## BlockMap

Agrupa spans em blocos semânticos. O tipo do bloco é inferido pela camada de IA no Stage 2.

```python
@dataclass
class BlockMap:
    id: str
    page_number: int
    bbox: tuple[float, float, float, float]
    spans: list[SpanMap]
    block_type: Literal[
        "text", "title", "body", "caption",
        "header", "footer", "footnote",
        "table", "table_cell", "image", "code", "unknown"
    ]
    column_index: int        # Índice da coluna (para layouts multi-coluna)
    reading_order: int       # Ordem de leitura na página
    is_protected: bool       # True se o bloco inteiro for preservado
    protection_reason: str
```

---

## TableRegion

Marca regiões de tabela detectadas para tratamento separado na reconstrução.

```python
@dataclass
class TableRegion:
    id: str
    page_number: int
    bbox: tuple[float, float, float, float]
    extraction_strategy: Literal["pdfplumber", "pymupdf", "manual"]
```

---

## PageMap

Representa uma página completa com todos os seus blocos, tabelas e propriedades visuais dominantes.

```python
@dataclass
class PageMap:
    page_number: int
    width: float
    height: float
    rotation: int            # Rotação da página em graus (0, 90, 180, 270)
    blocks: list[BlockMap]
    tables: list[TableRegion]
    dominant_body_color: int # Cor de texto mais comum na página
    dominant_font: str       # Fonte mais comum
    dominant_size: float     # Tamanho de fonte mais comum
```

---

## DocumentMap

Raiz da representação do documento.

```python
@dataclass
class DocumentMap:
    source_path: str         # Caminho do arquivo original
    pages: list[PageMap]
    metadata: dict           # Metadados extraídos do PDF (título, autor, etc.)
```

---

## Por que esse modelo existe

Abordagens tradicionais extraem texto bruto e aplicam a tradução diretamente sobre ele, perdendo posição, fonte, cor e relação entre elementos. O DocumentMap captura toda essa informação antes de qualquer transformação. Isso garante que o Stage 6 de reconstrução possa reposicionar cada span com as coordenadas e atributos originais totalmente preservados.
