# LayrPDF — Motor de Tradução de PDF com Preservação de Layout

![CI](https://github.com/OtavioB9/LayrPDF/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB.svg?style=flat&logo=react&logoColor=black)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)

Sistema híbrido de tradução de documentos com preservação espacial de layout.
Pipeline de 8 estágios · OCR Híbrido · Reconstrução via DocumentMap

[Arquitetura](docs/architecture.md) | [Pipeline](docs/pipeline.md) | [Modelo de Dados](docs/data-model.md) | [Screenshots](frontend/src/reference-screenshots/) | [Stack](#tecnologias-e-stack)

---

## Filosofia do Projeto

A arquitetura do LayrPDF é fundamentada em separação rigorosa de responsabilidades:

- **Core Determinístico:** Responsável por geometria, extração, medição real de texto, redação e reinserção. Aplica regras matemáticas e geométricas sem adivinhação de contexto.
- **IA Semântica:** Responsável por classificação de blocos, geração de glossários, proteção de termos e fallback de fontes. As coordenadas de página são sempre tratadas pelo Core.
- **DocumentMap como fonte única de verdade:** Todos os módulos consomem e enriquecem uma representação hierárquica única do documento, garantindo consistência total do estado.

---

## Demonstração

O sistema prioriza a integridade visual absoluta. Abaixo, exemplos reais da preservação de layout em diferentes cenários:

### 1. Capas e Identidade Visual
Comparação entre o documento original (EN) e o resultado processado (PT-BR), mantendo a identidade visual e tipográfica:

<p align="center">
  <img src="frontend/src/reference-screenshots/01-preview-side-by-side.png" width="100%" alt="Comparação de Capas">
</p>

### 2. Preservação de Estruturas Complexas
O motor de processamento garante a integridade de elementos geométricos sensíveis, como tabelas de conteúdo (ToC), recuos e estilos tipográficos específicos:

<p align="center">
  <img src="frontend/src/reference-screenshots/02-toc-comparison-1.png" width="49%" alt="Comparação de Índice 1">
  <img src="frontend/src/reference-screenshots/03-toc-comparison-2.png" width="49%" alt="Comparação de Índice 2">
</p>

<p align="center">
  <img src="frontend/src/reference-screenshots/04-praise-comparison.png" width="49%" alt="Comparação de Estilos">
  <img src="frontend/src/reference-screenshots/05-intro-comparison.png" width="49%" alt="Comparação de Listas">
</p>

---

## Desafios de Engenharia

### 1. Deduplicação e cache de traduções
Strings idênticas ou semanticamente equivalentes em diferentes páginas são processadas uma única vez e armazenadas em cache (SQLite), eliminando requisições redundantes e reduzindo latência.

### 2. Font Fitting em incrementos de 0.5pt
Traduções PT→EN aumentam o volume textual em até 20%. O motor itera em decrementos de 0.5pt, medindo a largura real do texto via PyMuPDF até encontrar o encaixe exato no bounding box.

### 3. Fencing de elementos técnicos
Fórmulas matemáticas e blocos de código são detectados por heurísticas de regex e font-family e isolados como placeholders, sendo preservados intactos durante a tradução.

### 4. Pipeline OCR híbrido
O sistema detecta automaticamente se a página é vetorial ou escaneada. Páginas-imagem ativam um fluxo paralelo via Tesseract OCR para alimentar o DocumentMap.

---

## Tecnologias e Stack

- **Motor LayrPDF (Backend):** Python 3.12 · PyMuPDF · FastAPI · Pydantic · SQLite (Cache).
- **Interface (Frontend):** React 19 · Vite · TailwindCSS · Framer Motion.
- **Qualidade & Tooling:** UV · Ruff · Pyrefly · Pytest · GitHub Actions (CI/CD).

---

## Estrutura do Repositório

O projeto segue uma organização modular, separando a lógica de baixo nível do PDF da interface de usuário:

- [`core/`](./core/) : Modelos, extratores, redatores e FontManager.
- [`pipeline/`](./pipeline/) : Orquestração dos estágios de processamento e sistema de checkpoints.
- [`frontend/`](./frontend/) : Interface SPA em React 19 com hooks customizados e integração com o backend.
- [`api_server.py`](./api_server.py) : Gateway FastAPI que integra o motor LayrPDF ao frontend.
- [`tests/`](./tests/) : Suíte de testes unitários e de integração (TDD).
- [`docs/`](./docs/) : Documentação técnica detalhada da arquitetura e modelos.
- [`tools/`](./tools/) : Utilitários para mapeamento de coordenadas e inspeção de geometria.

**O núcleo de processamento é mantido em repositório privado.**
