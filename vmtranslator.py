"""VMTranslator – entry point.

Usage:
    python vmtranslator.py <file.vm>

Produces <file.asm> in the same directory as the input.
"""

import sys
from pathlib import Path

from parser import Parser
from codewriter import CodeWriter


def translate(input_path: str) -> str:
    output_path = str(Path(input_path).with_suffix(".asm"))

    parser = Parser(input_path)
    writer = CodeWriter(output_path)

    while parser.has_more_commands():
        parser.advance()
        cmd_type = parser.command_type()

        if cmd_type == "C_ARITHMETIC":
            writer.write_arithmetic(parser.arg1())
        elif cmd_type == "C_PUSH":
            writer.write_push(parser.arg1(), parser.arg2())
        elif cmd_type == "C_POP":
            writer.write_pop(parser.arg1(), parser.arg2())

    writer.close()
    return output_path


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python vmtranslator.py <file.vm>", file=sys.stderr)
        sys.exit(1)

    output = translate(sys.argv[1])
    print(f"Translated → {output}")


if __name__ == "__main__":
    main()
