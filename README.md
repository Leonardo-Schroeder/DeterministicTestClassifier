# DeterministicTestClassifier

> Artefato do artigo **"When Unit Tests Have an Identity Crisis: A Structural Analysis of the Elasticsearch Test Suite"**, aceito no **SBQS 2026** (Simpósio Brasileiro de Qualidade de Software, Maringá-PR, 10–13 de novembro de 2026).

| | |
|---|---|
| 🔗 **DOI deste depósito (REDU/Unicamp)** | [https://doi.org/10.25824/redu/0LU5JC](https://doi.org/10.25824/redu/0LU5JC) |
| 💻 **Repositório de desenvolvimento (GitHub)** | https://github.com/Leonardo-Schroeder/DeterministicTestClassifier |
| 📄 **Artigo (versão de autor)** | [Versão de autor (Zenodo)](https://doi.org/10.5281/zenodo.23274500) |
| 🏅 **Selos pretendidos** | Disponível e Funcional |
| 📜 **Licença** | [MIT](LICENSE) (código da ferramenta) |
| 👥 **Autores** | Leonardo Bonfá Schroeder ([l289156@dac.unicamp.br](mailto:l289156@dac.unicamp.br)), Plínio Vilela ([prvilela@unicamp.br](mailto:prvilela@unicamp.br)) e Ricardo Vilela ([rfvilela@unicamp.br](mailto:rfvilela@unicamp.br)) — Universidade Estadual de Campinas (Unicamp), Limeira, Brasil |

---

## 1. Descrição Geral

O **DeterministicTestClassifier** é uma ferramenta de **análise estática baseada em Árvore Sintática Abstrata (AST)** que identifica métodos de teste em projetos de código aberto e extrai evidências estruturais sobre **isolamento de dependências, uso de mocks, verificações explícitas (asserts), acoplamento interno e interação com recursos externos (I/O)**. A partir dessas evidências, um classificador determinístico (árvore de decisão com regras heurísticas) caracteriza cada método de teste como:

- **Teste Unitário** (espectro unitário), incluindo o subgrupo com **"Traço de Componente"** (`is_component_trait`): métodos com dependências simuladas e referências simultâneas a múltiplos pacotes do domínio interno;
- **Teste de Integração** (espectro de integração).

A análise **não exige compilação** do projeto analisado, o que viabiliza a escalabilidade para grandes bases de código. No artigo, a ferramenta foi aplicada ao **Elasticsearch** (commit `2d7c118`, obtido em 08/04/2026), analisando **32.160 métodos de teste** em ~3 min 40 s.

> ⚠️ **Limitação conhecida:** a resolução de tipos é puramente sintática; invocações sem tipo resolvível são registradas como `UNKNOWN`.

### Fases e componentes

| Fase | Módulo | Função |
|---|---|---|
| 1 | `src/Collector` | Busca e filtra repositórios Java/Python via API do GitHub |
| 2 | `src/Donwloader` | Baixa e descompacta (em memória) o código-fonte dos repositórios |
| 3 | `src/Analyzer` | Extrai a AST, mapeia mocks/asserts e classifica os testes |

Componentes internos da Fase 3 (Figura 1 e Tabela 1 do artigo): `ASTOrchestrator` → `JavaASTParser` (biblioteca `javalang`) / `PythonASTParser` (módulo `ast`) → `ASTContext` → `DeterministicClassifier` → `Reporter` (JSON).

> ℹ️ O `PythonASTParser` está disponível na ferramenta, mas **não foi utilizado** na análise do Elasticsearch apresentada no artigo.

---

## 2. Organização do Conteúdo

```text
DeterministicTestClassifier/
├─ data/                    # Dados dinâmicos consumidos e gerados pelas Fases 1 e 2
│  ├─ java_projects.json    # Metadados dos repositórios Java filtrados do GitHub
│  ├─ python_projects.json  # Metadados dos repositórios Python filtrados do GitHub
│  └─ zips/                 # Código-fonte (.zip) pronto para análise (inclui cópia do snapshot do Elasticsearch)
├─ dataset - research/      # Dados estáticos e resultados originais do artigo submetido
│  ├─ comparacao_ferramenta_manual.json  # Ground-truth: revisão manual vs. ferramenta (Seção 4.6)
│  ├─ elasticsearch-main.json            # Resultados da análise do Elasticsearch (Seção 4)
│  └─ elasticsearch-2d7c118534f65a6c91a2cad1b6c5f183253fcfd5.zip                   # Snapshot do Elasticsearch (commit 2d7c118) analisado no artigo
├─ reports/                 # Saída da Fase 3 (relatórios gerados)
├─ src/                     # Código-fonte principal
│  ├─ Analyzer/             # Extração de AST (Java/Python) e classificação
│  ├─ Collector/            # Busca e filtragem via API do GitHub
│  └─ Donwloader/           # Download e descompactação em memória
├─ docker-compose.yaml      # Orquestração dos volumes e do container
├─ Dockerfile               # Ambiente isolado (Python 3.10)
├─ main.py                  # Ponto de entrada (menu interativo no terminal)
├─ requirements.txt         # Dependências Python (ex.: javalang)
├─ .env.example             # Modelo de configuração do token do GitHub
└─ LICENSE                  # Licença MIT (código da ferramenta)
```

---

## 3. Requisitos do Sistema

A execução é padronizada **exclusivamente via Docker**, para garantir reprodutibilidade e evitar conflitos de bibliotecas locais.

| Requisito | Detalhes |
|---|---|
| **Docker Desktop** | Instalado e **em execução**. O container provê Python 3.10 e todas as dependências. |
| **Ambiente de referência** | Análise completa do Elasticsearch (32.160 métodos) em Intel Core i5-12450H, 16 GB de RAM, SO 64 bits, em ~3 min 40 s. |
| **Sistema operacional** | Qualquer SO 64 bits com suporte ao Docker Desktop (Windows, macOS ou Linux). Testado em **Windows**. |
| **Espaço em disco** | ~2 GB para a imagem Docker; 90+ GB adicionais para o Cenário 2. |
| **Internet** | Necessária para o *build* da imagem e para o Cenário 2. |
| **Token do GitHub (PAT)** | **Opcional** — apenas para o Cenário 2 (Fases 1 e 2), para contornar o limite de requisições da API. |

---

## 4. Instalação

```bash
# 1. Baixe e extraia o pacote deste depósito (REDU) e abra o terminal na pasta raiz
cd DeterministicTestClassifier

# 2. Confirme que o Docker está em execução
docker --version
docker compose version
```

Não é necessário instalar Python nem bibliotecas manualmente: a imagem é construída automaticamente no primeiro `docker compose run`.

> ⏱️ O primeiro *build* da imagem pode levar alguns minutos.

---

## 5. Como Executar

A ferramenta possui um **menu interativo no terminal**. Escolha o cenário conforme o objetivo da avaliação.

### Cenário 1 — Execução Rápida (apenas Análise AST) ⭐ *recomendado para o selo Funcional*

Não exige APIs, tokens nem download de grandes volumes de dados. Utiliza a base de repositórios já inclusa em `/data` (inclusive o snapshot do Elasticsearch usado no artigo, em `data/zips/`).

1. Abra o terminal na **pasta raiz** do projeto.
2. Certifique-se de que o **Docker Desktop** está em execução.
3. Inicie o container interativo:
   ```bash
   docker compose run --rm classifier
   ```
4. No menu, digite **`3`** para iniciar a **Fase 3: Análise AST**.
5. Aguarde o processamento. Os arquivos `.json` com o mapeamento de mocks e asserts serão salvos automaticamente em `/reports`.

⏱️ **Tempo estimado:** 4 a 6 minutos (depende do tamanho da amostra em `/data`).

✅ **Resultado esperado:** a pasta `reports/` passa a conter um arquivo `<nome-do-repositorio>.json` por repositório analisado, com um registro por método de teste no formato abaixo (exemplo real do artigo, Seção 3.5):

```json
{
  "method_name": "testWithPasswordProtectedKeystore",
  "group": "Teste Unitario",
  "has_assertions": true,
  "is_component_trait": true,
  "justification": "Unitario com caracteristicas de COMPONENTE (acoplou os dominios: KeyStoreWrapper, Terminal e UserException)."
}
```

Campos: `group` (`Teste Unitario` ou `Teste de Integracao`), `has_assertions` (há chamadas a mecanismos de verificação reconhecidos), `is_component_trait` (traço de componente) e `justification` (regra que determinou a classificação).

### Cenário 2 — Execução Completa (Coleta + Download + Análise)

Avalia o pipeline de ponta a ponta: busca novos repositórios no GitHub, baixa o código-fonte e realiza a extração de AST. ⚠️ *Pode demorar bastante, dependendo do volume de projetos.*

1. Na raiz do projeto, renomeie `.env.example` para `.env`.
2. Edite o `.env` e insira seu token do GitHub:
   ```env
   GITHUB_TOKEN=ghp_seu_token_aqui
   ```
   > 🔒 **Nunca** faça commit do `.env` com um token real. O token precisa apenas de leitura em repositórios públicos.
3. Inicie o container:
   ```bash
   docker compose run --rm classifier
   ```
4. No menu, digite **`4`** para o **Pipeline Completo**, ou escolha as **Fases 1, 2 e 3** individualmente, nessa sequência.
5. Os `.zip` dos repositórios serão baixados para `/data/zips/` e os relatórios serão gerados em `/reports`.

⏱️ **Tempo estimado:** cerca de 4 horas (depende do número de projetos e da conexão com a internet).

---

## 6. Reprodução dos Resultados do Artigo

| Resultado no artigo | Arquivo | Conteúdo |
|---|---|---|
| Tabela 4, Figura 2 e Tabela 5 (Seções 4.1–4.4): 32.160 métodos; 29.466 no espectro unitário (28.035 estritos + 1.431 traço de componente); 2.694 de integração | `dataset - research/elasticsearch-main.json` | Classificação dos métodos de teste do Elasticsearch |
| Seção 4.6 — Revisão manual: amostra estratificada de 225 métodos (85 unitários estritos, 70 integração, 70 traço de componente); 190 confirmados (84,4%) | `dataset - research/comparacao_ferramenta_manual.json` | Ground-truth da revisão manual vs. classificação da ferramenta |

**Para reexecutar a análise do Elasticsearch** na mesma revisão do estudo (commit `2d7c118`, obtido em 08/04/2026), o snapshot utilizado **já está incluído** neste pacote, em `data/zips/elasticsearch-2d7c118534f65a6c91a2cad1b6c5f183253fcfd5.zip` (cópia idêntica em `dataset - research/`):

1. Execute `docker compose run --rm classifier` e escolha a opção **`3`** (Fase 3: Análise AST).
2. O relatório será gerado em `reports/` e pode ser comparado com `dataset - research/elasticsearch-main.json`. Tempo de referência: ~3 min 40 s (i5-12450H, 16 GB de RAM).

> ℹ️ Os resultados da ferramenta são **classificações heurísticas** (não rótulos absolutos). Diferenças pequenas podem ocorrer caso outra revisão do Elasticsearch seja analisada.

---

## 7. Solução de Problemas

| Problema | Solução |
|---|---|
| `Cannot connect to the Docker daemon` | Abra o Docker Desktop e aguarde a inicialização completa. |
| `docker compose` não reconhecido | Atualize o Docker Desktop ou use `docker-compose run --rm classifier`. |
| Erro de *rate limit* da API do GitHub (Fases 1/2) | Configure o `GITHUB_TOKEN` no `.env` (Cenário 2). |
| Pasta `reports/` vazia | Verifique se a Fase 3 terminou sem erros e se há arquivos em `data/`. |

---

## 8. Informações sobre os Dados (Armazenamento e Aspectos Éticos)

- **Origem:** metadados e código-fonte de repositórios **públicos** do GitHub, obtidos via API oficial; o estudo principal utiliza o projeto de código aberto **Elasticsearch**.
- **Armazenamento:** este depósito (REDU/Unicamp) é a versão arquivada e persistente do artefato.
- **Aspectos éticos:** não há participantes humanos nem coleta de dados pessoais sensíveis. A revisão manual (Seção 4.6 do artigo) foi realizada por um único avaliador sobre código público.
- **Código de terceiros (Elasticsearch):** o snapshot em `dataset - research/` é uma cópia do projeto **Elasticsearch** no commit `2d7c118`, incluída apenas para reprodução. Ele **permanece sujeito às licenças originais do projeto** (consulte os arquivos de licença dentro do `.zip` e em https://github.com/elastic/elasticsearch); a Licença MIT deste artefato **não se aplica** a ele.

---

## 9. Elegibilidade para os Selos

**🏅 Disponível**
- ✅ Artefato alinhado ao artigo (ferramenta, dados e revisão manual descritos nas Seções 3 e 4).
- ✅ Depositado em repositório público, persistente e com DOI (REDU/Unicamp).
- ✅ README explicativo e licença MIT.


**🏅 Funcional**
- ✅ **Relevante:** implementa a ferramenta de análise e classificação apresentada no artigo.
- ✅ **Documentado:** passo a passo de instalação e execução (Seções 4 e 5).
- ✅ **Completo:** inclui código, dados de amostra (`/data`) e dados originais do estudo (`dataset - research/`); ambiente totalmente provisionado via Docker.
- ✅ **Executável por terceiros:** o Cenário 1 funciona sem token, sem APIs externas e sem dados adicionais.

---

## 10. Citação

```bibtex
@inproceedings{schroeder2026identity,
  title     = {When Unit Tests Have an Identity Crisis: A Structural Analysis of the Elasticsearch Test Suite},
  author    = {Schroeder, Leonardo and Vilela, Pl{\'i}nio and Vilela, Ricardo},
  booktitle = {Proceedings of the Brazilian Symposium on Software Quality (SBQS 2026)},
  year      = {2026},
  address   = {Maring{\'a}, PR, Brasil}
}
```

## 11. Licença

O **código da ferramenta** é distribuído sob a **Licença MIT** — consulte o arquivo [LICENSE](LICENSE). O snapshot do Elasticsearch incluído segue as licenças do projeto original (Seção 8).

## 12. Contato

Leonardo Bonfá Schroeder — l289156@dac.unicamp.br