# VMTranslator

Traduz arquivos `.vm` (bytecode da máquina virtual do curso *Nand to Tetris*) para Assembly Hack.

## Dupla

| Nome | GitHub |
|------|--------|
| Pedro Vinicius | [@pedrovi35](https://github.com/pedrovi35) |
| *(Parceiro)*   | — |

## Linguagem e versão

**Python 3.10+** — sem dependências externas além de `pytest` para testes.

## Estrutura do projeto

```
vmtranslator/
├── parser/
│   ├── __init__.py
│   └── parser.py        # Tokenisation e classificação de comandos VM
├── codewriter/
│   ├── __init__.py
│   └── code_writer.py   # Geração de Assembly Hack
├── tests/
│   ├── test_parser.py
│   └── test_code_writer.py
├── vmtranslator.py      # Ponto de entrada (orquestrador)
├── conftest.py          # Configuração do pytest
└── requirements.txt
```

## Como executar

```bash
# Instalar dependências de teste (opcional)
pip install -r requirements.txt

# Traduzir um arquivo .vm
python vmtranslator.py caminho/para/Arquivo.vm
# → gera caminho/para/Arquivo.asm
```

## Exemplo de uso

```bash
python vmtranslator.py StackArithmetic/SimpleAdd/SimpleAdd.vm
# Saída: StackArithmetic/SimpleAdd/SimpleAdd.asm

python vmtranslator.py MemoryAccess/BasicTest/BasicTest.vm
# Saída: MemoryAccess/BasicTest/BasicTest.asm
```

## Executar testes

```bash
pytest tests/ -v
```

## Segmentos suportados

| Segmento   | Endereço base / mapeamento    |
|------------|-------------------------------|
| `constant` | Valor literal (sem leitura RAM) |
| `local`    | `LCL` (RAM[1])                |
| `argument` | `ARG` (RAM[2])                |
| `this`     | `THIS` (RAM[3])               |
| `that`     | `THAT` (RAM[4])               |
| `temp`     | RAM[5]–RAM[12]                |
| `pointer`  | RAM[3] (`this`) / RAM[4] (`that`) |
| `static`   | `Módulo.índice` (símbolo Assembly) |

## Operações suportadas

- **Aritméticas:** `add`, `sub`, `neg`
- **Lógicas:** `and`, `or`, `not`
- **Relacionais:** `eq`, `gt`, `lt`
- **Memória:** `push` / `pop` para todos os segmentos acima
