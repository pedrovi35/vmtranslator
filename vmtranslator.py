import os
import sys
from codewriter.code_writer import CodeWriter


def translate_file(file_path, code_writer):
    """Lê um arquivo .vm linha por linha e envia os comandos para o CodeWriter."""
    with open(file_path, "r") as file:
        for line in file:
            # Remove comentários e espaços em branco nas pontas
            line = line.split("//")[0].strip()
            if not line:
                continue

            tokens = line.split()
            command_type = tokens[0]

            # Comandos Aritméticos / Lógicos
            if command_type in [
                "add",
                "sub",
                "neg",
                "eq",
                "gt",
                "lt",
                "and",
                "or",
                "not",
            ]:
                code_writer.write_arithmetic(command_type)

            # Comandos de Memória (Push / Pop)
            elif command_type in ["push", "pop"]:
                segment = tokens[1]
                index = int(tokens[2])
                code_writer.write_push_pop(command_type, segment, index)

            # Comandos de Controle de Fluxo
            elif command_type == "label":
                code_writer.write_label(tokens[1])
            elif command_type == "goto":
                code_writer.write_goto(tokens[1])
            elif command_type == "if-goto":
                code_writer.write_if_goto(tokens[1])

            # Comandos de Funções
            elif command_type == "function":
                code_writer.write_function(tokens[1], int(tokens[2]))
            elif command_type == "call":
                code_writer.write_call(tokens[1], int(tokens[2]))
            elif command_type == "return":
                code_writer.write_return()


def clean_filename(path):
    """Extrai apenas o nome do arquivo sem caminho e sem extensão .vm de forma robusta."""
    base = os.path.basename(path)
    if base.lower().endswith(".vm"):
        base = base[:-3]
    return base


def main():
    if len(sys.argv) < 2:
        print("Uso: python vmtranslator.py <arquivo.vm ou diretorio>")
        return

    argument_path = os.path.abspath(sys.argv[1])

    if os.path.isdir(argument_path):
        dir_name = os.path.basename(os.path.normpath(argument_path))
        output_file = os.path.join(argument_path, f"{dir_name}.asm")
        is_directory = True
    else:
        output_file = argument_path.replace(".vm", ".asm")
        is_directory = False

    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cw = CodeWriter(output_file)

    if is_directory:
        # Só injeta Bootstrap se for um diretório completo com múltiplos arquivos
        cw.write_bootstrap()
        for file in os.listdir(argument_path):
            if file.endswith(".vm"):
                full_path = os.path.join(argument_path, file)
                cw.set_file_name(clean_filename(file))
                translate_file(full_path, cw)
    else:
        # Arquivos individuais (BasicLoop, FibonacciSeries, SimpleFunction) iniciam sem Bootstrap
        cw.set_file_name(clean_filename(argument_path))
        translate_file(argument_path, cw)

    cw.close()
    print(f"Tradução concluída! Gerado: {output_file}")


if __name__ == "__main__":
    main()