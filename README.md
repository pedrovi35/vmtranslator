# VMTranslator — Versão Completa (Partes 1 & 2)

> **Disciplina:** Elementos de Sistemas de Computação (Nand to Tetris)
> **Instituição:** UFMA — Universidade Federal do Maranhão
> **Campus:** São Luís — Centro de Ciências Exatas e Tecnologia (CCET)
> **Curso:** Ciência e Tecnologia

---

## 👥 Autores

| Nome | Matrícula | GitHub |
|---|---|---|
| Pedro Victor Rocha Gonçalves | 2022029920 | [@pedrovi35](https://github.com/pedrovi35) |
| Sara Ferreira de Souza | 2022029911 | - | [@SaraFereira45]( https://github.com/SaraFerreira42)|

---

## 📝 Sobre o Projeto

Este projeto consiste na implementação completa de um **VMTranslator** (Tradutor de Máquina Virtual → Assembly Hack) em **Python 3.14**, cobrindo os requisitos de especificação das partes 1 e 2 do curso *Nand to Tetris* (Projetos 07 e 08 do livro *The Elements of Computing Systems*).

O software é capaz de ler arquivos de bytecode de máquina virtual (`.vm`), interpretar suas instruções aritméticas, lógicas, de manipulação de memória, de controle de fluxo e chamadas de sub-rotinas, traduzindo-as em códigos correspondentes legíveis e válidos para a CPU Hack (`.asm`).

---

## 📁 Estrutura do Repositório 
vmtranslator/
├── codewriter/
│   ├── __init__.py
│   └── code_writer.py     # Tradutor Assembly para aritmética, push/pop, bootstrap, fluxos e sub-rotinas
├── parser/
│   ├── __init__.py
│   └── parser.py          # Tokenização, filtro e classificação de TODOS os comandos (C_LABEL, C_CALL, etc.)
├── tests/
│   ├── __init__.py
│   ├── test_parser.py     # Testes unitários do Parser expandidos (27 casos)
│   ├── test_code_writer.py # Testes unitários do CodeWriter expandidos (24 casos)
│   └── projects08/        # Pasta de testes oficiais do projeto 08 integrado ao repositório
│       ├── FunctionCalls/ # Testes de funções (SimpleFunction, NestedCall, etc.)
│       └── ProgramFlow/   # Testes de controle de fluxo (BasicLoop, FibonacciSeries)
├── StackArithmetic/       # Amostras de testes da Parte 1
│   └── SimpleAdd/SimpleAdd.vm
├── MemoryAccess/          # Amostras de testes da Parte 1
│   └── BasicTest/BasicTest.vm
├── vmtranslator.py        # Ponto de entrada — Orquestrador com suporte a múltiplos arquivos/diretórios
├── vmtranslator           # Wrapper executável para Unix (requisito do projeto)
├── conftest.py            # Configuração do pytest
├── requirements.txt
└── README.md
---

## Como Executar

### Pré-requisitos
- Python 3.10 ou superior (Desenvolvido e validado em **Python 3.14**)
- Dependências de testes instaladas (Opcional):
  ```bash
  pip install -r requirements.txt

```bash
pip install -r requirements.txt
```

### Traduzir um arquivo `.vm`

```bash
python vmtranslator.py <caminho/para/Arquivo.vm>
```

O arquivo `.asm` gerado é salvo no **mesmo diretório** do arquivo de entrada.

---

## Exemplos de Uso

```bash
# Teste 1 — operação aritmética simples
python vmtranslator.py StackArithmetic/SimpleAdd/SimpleAdd.vm
# Saída: StackArithmetic/SimpleAdd/SimpleAdd.asm

# Teste 2 — acesso a segmentos de memória
python vmtranslator.py MemoryAccess/BasicTest/BasicTest.vm
# Saída: MemoryAccess/BasicTest/BasicTest.asm
```

---

## Executar os Testes Unitários

```bash
pytest tests/ -v
```

Resultado esperado: **51 testes passando**.

---

## Segmentos de Memória Suportados

| Segmento | Descrição | Mapeamento |
|---|---|---|
| `constant` | Valor literal (sem leitura de RAM) | Direto na instrução |
| `local` | Variáveis locais da função | `LCL` → RAM[1] |
| `argument` | Argumentos da função | `ARG` → RAM[2] |
| `this` | Base para objetos/arrays | `THIS` → RAM[3] |
| `that` | Base para estruturas dinâmicas | `THAT` → RAM[4] |
| `temp` | Registradores temporários | RAM[5] – RAM[12] |
| `pointer` | Acesso direto a `this`/`that` | RAM[3] ou RAM[4] |
| `static` | Variáveis estáticas do módulo | Símbolo `Módulo.índice` |

---

## Operações Suportadas

| Categoria | Comandos |
|---|---|
| Aritmética | `add`, `sub`, `neg` |
| Lógica bitwise | `and`, `or`, `not` |
| Comparação | `eq`, `gt`, `lt` |
| Memória | `push` / `pop` (todos os segmentos acima) |

---

## Decisões de Implementação

- **Labels de comparação** (`eq`, `gt`, `lt`) usam um contador interno (`VM_TRUE_0`, `VM_END_0`, …) para garantir unicidade quando o mesmo arquivo contém múltiplas comparações.
- **Segmentos com ponteiro** (`local`, `argument`, `this`, `that`) calculam o endereço final em `R13` antes do pop, evitando corrupção do SP durante a escrita.
- **`temp`** usa endereço absoluto fixo (`5 + índice`) sem necessidade de `R13`.
- **`static`** gera o símbolo Assembly `NomeDoMódulo.índice`, resolvido pelo assembler Hack.

## 🧪 Exemplos de Uso e Saídas de Testes
Teste de Fluxo de Programa (Parte 2 — Arquivo Único)
python vmtranslator.py ProgramFlow/BasicLoop
#Saída gerada: ProgramFlow/BasicLoop/BasicLoop.asm (Com comandos label, goto, if-goto)

## Teste de Integração Completo (Parte 2 — Múltiplos Arquivos + Bootstrap)
python vmtranslator.py FunctionCalls/NestedCall
#Saída gerada: FunctionCalls/NestedCall/NestedCall.asm 
#(Une Sys.vm e NestedCall.vm em uma única saída iniciada pelo código de Bootstrap da VM)

## 📈 Executar a Suíte de Testes Unitários
Mantivemos e expandimos a cobertura de testes via pytest. Para validar a integridade estrutural das rotinas base do código, execute:
python -m pytest
Resultado esperado: 51 passed (Todos os testes de regressão passando com sucesso).

## 🛠️ Funcionalidades Suportadas e Mapeamento
1. Segmentos de Memória & Aritmética (Legado da Parte 1)
Segmentos: constant, local, argument, this, that, temp, pointer, static.

Operações ALU: add, sub, neg, and, or, not, eq, gt, lt.

2. Controle de Fluxo (Novidade da Parte 2)
label LABEL_NAME: Mapeado como (NOME_DA_FUNCAO$LABEL_NAME) para criar escopos únicos por função e impedir colisões de saltos.

goto LABEL_NAME: Salto incondicional direto em Assembly Hack.

if-goto LABEL_NAME: Desempilha o elemento do topo da pilha; se o valor for diferente de 0 (True), realiza o salto.

3. Gerenciamento de Funções & Sub-rotinas (Novidade da Parte 2)
function funcName nLocals: Cria o ponto de entrada da sub-rotina e inicializa nLocals variáveis na pilha com o valor zero.

call funcName nArgs: Salva o frame do chamador empilhando o endereço de retorno, LCL, ARG, THIS, THAT, reconfigura os ponteiros de base para a nova sub-rotina e desvia a execução.

return: Limpa o frame atual, copia o valor de retorno para a base do argumento do chamador, restaura os registradores originais (THAT, THIS, ARG, LCL) e retorna o ponteiro de execução para a instrução subsequente ao call.

## ⚙️ Decisões de Implementação & Evolução do Projeto
Rotina de Bootstrap: Implementada no topo da compilação de diretórios finais. Configura fisicamente o ponteiro da pilha SP = 256 na RAM da CPU Hack e faz uma chamada oculta estrita a Sys.init sem argumentos para inicializar o sistema operacional simulado.

Rótulos Dinâmicos: Para manter o isolamento de variáveis e escopo locais de funções, os labels internos de controle de fluxo e blocos condicionais concatenam dinamicamente a string da função ativa no momento da tradução (self._current_function).

Múltiplos Arquivos & Variáveis Estáticas (static): O método set_filename reconfigura em tempo de execução o prefixo do módulo processado. Isso isola o mapeamento de variáveis do segmento static para gerar símbolos exclusivos estruturados como @NomeDoModulo.Indice no Assembly final.
