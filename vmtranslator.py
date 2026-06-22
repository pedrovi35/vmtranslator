import os
import sys
from parser.parser import Parser
from codewriter.code_writer import CodeWriter

def main():
    if len(sys.argv) < 2:
        print("Uso: python vmtranslator.py <caminho_arquivo_ou_diretorio>")
        sys.exit(1)

    input_path = sys.argv[1]
    vm_files = []

    # 1. Verifica se a entrada é um diretório ou um arquivo único
    if os.path.isdir(input_path):
        for f in os.listdir(input_path):
            if f.endswith('.vm'):
                vm_files.append(os.path.join(input_path, f))
        
        dirname = os.path.basename(os.path.normpath(input_path))
        output_file = os.path.join(input_path, f"{dirname}.asm")
    else:
        vm_files.append(input_path)
        output_file = input_path.replace('.vm', '.asm')

    if not vm_files:
        print("Nenhum arquivo .vm encontrado.")
        sys.exit(1)

    # 2. Instancia o CodeWriter
    cw = CodeWriter(output_file)

    # 3. Executa o Bootstrap explicitamente para a compilação final real
    cw.write_bootstrap()

    # 4. Processa cada arquivo .vm encontrado sequencialmente
    for vm_file in vm_files:
        filename_only = os.path.basename(vm_file).replace('.vm', '')
        cw.set_filename(filename_only)

        parser = Parser(vm_file)
        while parser.has_more_commands():
            parser.advance()
            cmd_type = parser.command_type()

            if cmd_type == "C_ARITHMETIC":
                cw.write_arithmetic(parser.arg1())
            elif cmd_type in ("C_PUSH", "C_POP"):
                cw.write_push_pop(cmd_type, parser.arg1(), parser.arg2())
            elif cmd_type == "C_LABEL":
                cw.write_label(parser.arg1())
            elif cmd_type == "C_GOTO":
                cw.write_goto(parser.arg1())
            elif cmd_type == "C_IF":
                cw.write_if(parser.arg1())
            elif cmd_type == "C_FUNCTION":
                cw.write_function(parser.arg1(), parser.arg2())
            elif cmd_type == "C_CALL":
                cw.write_call(parser.arg1(), parser.arg2())
            elif cmd_type == "C_RETURN":
                cw.write_return()

    cw.close()
    print(f"Tradução concluída! Arquivo gerado em: {output_file}")

if __name__ == "__main__":
    main()