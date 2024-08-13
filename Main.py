import sys
import os

from Parser import Parser
from CodeWriter import CodeWriter

USAGE_ERR_MSG = "USAGE: Please use: VMtranslator <input path>"


class VMTranslator:
    def __init__(self, out_file):
        self.parser = None
        self.code_writer = CodeWriter(out_file)
        self.code_writer.write_init()

    def change_file(self, filename):
        self.parser = Parser(filename)
        self.code_writer.set_cur_file(filename)

    def translate(self):
        while self.parser.has_more_cmds():
            self.parser.advance()
            if self.parser.get_cmd_type() == self.parser.cmd_types["arithmetic"]:
                self.code_writer.write_arithmetic(self.parser.get_cmd())
            elif self.parser.get_cmd_type() == self.parser.cmd_types["push"]:
                self.code_writer.write_push(self.parser.get_arg1(), self.parser.get_arg2())
            elif self.parser.get_cmd_type() == self.parser.cmd_types["pop"]:
                self.code_writer.write_pop(self.parser.get_arg1(), self.parser.get_arg2())
            elif self.parser.get_cmd_type() == self.parser.cmd_types["label"]:
                self.code_writer.write_label(self.parser.get_arg1())
            elif self.parser.get_cmd_type() == self.parser.cmd_types["goto"]:
                self.code_writer.write_goto(self.parser.get_arg1())
            elif self.parser.get_cmd_type() == self.parser.cmd_types["if"]:
                self.code_writer.write_if(self.parser.get_arg1())
            elif self.parser.get_cmd_type() == self.parser.cmd_types["function"]:
                self.code_writer.write_function(self.parser.get_arg1(), self.parser.get_arg2())
            elif self.parser.get_cmd_type() == self.parser.cmd_types["return"]:
                self.code_writer.write_return()
            elif self.parser.get_cmd_type() == self.parser.cmd_types["call"]:
                self.code_writer.write_call(self.parser.get_arg1(), self.parser.get_arg2())
            else:
                continue


if __name__ == '__main__':
    if not len(sys.argv) == 2:
        sys.exit(USAGE_ERR_MSG)
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [os.path.join(argument_path, filename)
                              for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    with open(output_path, 'w') as output_file:
        vm_translator = VMTranslator(output_file)
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            vm_translator.change_file(input_path)
            vm_translator.translate()
