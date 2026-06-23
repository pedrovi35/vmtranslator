import os


class CodeWriter:

    def __init__(self, output_filename):
        self.file = open(output_filename, "w")
        self.current_vm_file = ""
        self.current_function = "none"
        self.label_counter = 0

        self.segments_map = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT",
        }

    def set_file_name(self, filename):
        """Define o contexto do arquivo limpando qualquer resíduo de extensão."""
        self.current_vm_file = filename.replace(".vm", "").replace(".VM", "")

    def write_bootstrap(self):
        self.file.write("// --- BOOTSTRAP INITIALIZATION ---\n")
        self.file.write("@256\nD=A\n@SP\nM=D\n")
        self.write_call("Sys.init", 0)

    def write_arithmetic(self, command):
        self.file.write(f"// {command}\n")
        if command in ["add", "sub", "and", "or"]:
            self.file.write("@SP\nAM=M-1\nD=M\nA=A-1\n")
            if command == "add":
                self.file.write("M=D+M\n")
            elif command == "sub":
                self.file.write("M=M-D\n")
            elif command == "and":
                self.file.write("M=D&M\n")
            elif command == "or":
                self.file.write("M=D|M\n")

        elif command in ["neg", "not"]:
            self.file.write("@SP\nA=M-1\n")
            if command == "neg":
                self.file.write("M=-M\n")
            elif command == "not":
                self.file.write("M=!M\n")

        elif command in ["eq", "gt", "lt"]:
            label_true = f"COMP_TRUE_{self.current_vm_file}_{self.label_counter}"
            label_end = f"COMP_END_{self.current_vm_file}_{self.label_counter}"
            self.label_counter += 1

            self.file.write("@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n")
            self.file.write(f"@{label_true}\n")

            if command == "eq":
                self.file.write("D;JEQ\n")
            elif command == "gt":
                self.file.write("D;JGT\n")
            elif command == "lt":
                self.file.write("D;JLT\n")

            self.file.write("@SP\nA=M-1\nM=0\n")
            self.file.write(f"@{label_end}\n0;JMP\n")
            self.file.write(f"({label_true})\n@SP\nA=M-1\nM=-1\n")
            self.file.write(f"({label_end})\n")

    def write_push_pop(self, command, segment, index):
        self.file.write(f"// {command} {segment} {index}\n")

        if command == "push":
            if segment == "constant":
                self.file.write(f"@{index}\nD=A\n")
            elif segment in self.segments_map:
                self.file.write(
                    f"@{index}\nD=A\n@{self.segments_map[segment]}\nA=D+M\nD=M\n"
                )
            elif segment in ["pointer", "temp"]:
                base = 3 if segment == "pointer" else 5
                self.file.write(f"@{base + index}\nD=M\n")
            elif segment == "static":
                self.file.write(f"@{self.current_vm_file}.{index}\nD=M\n")

            self.file.write("@SP\nA=M\nM=D\n@SP\nM=M+1\n")

        elif command == "pop":
            if segment in self.segments_map:
                self.file.write(
                    f"@{index}\nD=A\n@{self.segments_map[segment]}\nD=D+M\n@R13\nM=D\n"
                )
                self.file.write("@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n")
            elif segment in ["pointer", "temp"]:
                base = 3 if segment == "pointer" else 5
                self.file.write(f"@SP\nAM=M-1\nD=M\n@{base + index}\nM=D\n")
            elif segment == "static":
                self.file.write(
                    f"@SP\nAM=M-1\nD=M\n@{self.current_vm_file}.{index}\nM=D\n"
                )

    def _get_full_label(self, label):
        """Mapeia dinamicamente o escopo do label atual garantindo isolamento sem pontos."""
        if self.current_function != "none" and self.current_function != "":
            return f"{self.current_function}${label}"
        return f"{self.current_vm_file}${label}"

    def write_label(self, label):
        full_label = self._get_full_label(label)
        self.file.write(f"({full_label})\n")

    def write_goto(self, label):
        full_label = self._get_full_label(label)
        self.file.write(f"@{full_label}\n0;JMP\n")

    def write_if_goto(self, label):
        full_label = self._get_full_label(label)
        self.file.write(f"@SP\nAM=M-1\nD=M\n@{full_label}\nD;JNE\n")

    def write_function(self, function_name, num_locals):
        self.current_function = function_name
        self.file.write(f"({function_name})\n")
        for _ in range(num_locals):
            self.file.write("@0\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")

    def write_call(self, function_name, num_args):
        return_label = f"{function_name}$ret.{self.label_counter}"
        self.label_counter += 1

        self.file.write(f"@{return_label}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        for seg in ["LCL", "ARG", "THIS", "THAT"]:
            self.file.write(f"@{seg}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")

        self.file.write(f"@SP\nD=M\n@{5 + num_args}\nD=D-A\n@ARG\nM=D\n")
        self.file.write("@SP\nD=M\n@LCL\nM=D\n")
        self.file.write(f"@{function_name}\n0;JMP\n")
        self.file.write(f"({return_label})\n")

    def write_return(self):
        self.file.write("// return\n")
        # 1. R14 = FRAME (guarda valor de LCL)
        self.file.write("@LCL\nD=M\n@R14\nM=D\n")
        # 2. R15 = RET_ADDRESS = *(FRAME - 5)
        self.file.write("@5\nA=D-A\nD=M\n@R15\nM=D\n")
        # 3. *ARG = pop()
        self.file.write("@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n")
        # 4. SP = ARG + 1
        self.file.write("@ARG\nD=M+1\n@SP\nM=D\n")
        # 5. Restaura segmentos usando offset fixo sobre R14
        self.file.write("@R14\nD=M\n@1\nA=D-A\nD=M\n@THAT\nM=D\n")
        self.file.write("@R14\nD=M\n@2\nA=D-A\nD=M\n@THIS\nM=D\n")
        self.file.write("@R14\nD=M\n@3\nA=D-A\nD=M\n@ARG\nM=D\n")
        self.file.write("@R14\nD=M\n@4\nA=D-A\nD=M\n@LCL\nM=D\n")
        # 6. Pula para o endereço de retorno
        self.file.write("@R15\nA=M\n0;JMP\n")

    def close(self):
        # Garante um loop infinito estruturado de segurança no fim do arquivo físico
        self.file.write("// --- END SECURITY LOOP ---\n(INFINITE_LOOP)\n@INFINITE_LOOP\n0;JMP\n")
        self.file.close()