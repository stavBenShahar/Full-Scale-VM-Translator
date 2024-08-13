import re


class CodeWriter:
    TEMP = 5

    def __init__(self, file):
        self._outfile = file
        self.segments = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT'}
        # In case of repetitions
        self._eq_num = self._gt_num = self._lt_num = self._ret_num = 0
        self._cur_file = None
        self._clean_cur_file = None

    def set_cur_file(self, cur_file):
        self._cur_file = re.sub('.+/', '', cur_file.split('.')[0])
        pos_of_backslash = self._cur_file.rfind('\\')
        pos_of_slash = self._cur_file.rfind('/')
        pos = max(pos_of_backslash, pos_of_slash)
        self._clean_cur_file = self._cur_file[pos + 1:]
        self._clean_cur_file = self._clean_cur_file.replace(" ", "_")

    # Writing operations
    def write_arithmetic(self, cmd):
        self._outfile.write(f'// {cmd}\n')  # For debugging purposes
        if cmd == 'add':
            self._add()
        elif cmd == 'sub':
            self._sub()
        elif cmd == 'neg':
            self._neg()
        elif cmd == 'and':
            self._and()
        elif cmd == 'or':
            self._or()
        elif cmd == 'not':
            self._not()
        elif cmd == 'shiftleft':
            self._shift_left()
        elif cmd == 'shiftright':
            self._shift_right()
        elif cmd == 'eq':
            self._eq()
        elif cmd == 'gt':
            self._gt()
        elif cmd == 'lt':
            self._lt()

    def write_push(self, segment, i):
        self._outfile.write(f'// push {segment} {i}\n')  # For debugging purposes
        if segment == 'constant':
            lines = [f'@{i}\n',
                     'D=A\n',
                     '@SP\n',
                     'A=M\n',
                     'M=D\n',
                     '@SP\n',
                     'M=M+1\n']
            self._outfile.writelines(lines)
        elif segment == 'temp':
            lines = [f'@{CodeWriter.TEMP + i}\n',
                     'D=A\n',
                     '@addr\n',
                     'M=D\n',

                     '@addr\n',
                     'A=M\n',
                     'D=M\n',
                     '@SP\n',
                     'A=M\n',
                     'M=D\n',

                     '@SP\n',
                     'M=M+1\n']
            self._outfile.writelines(lines)

        elif segment == 'pointer':
            symbol = 'THAT' if i == 1 else 'THIS'
            lines = [f'@{symbol}\n',
                     'D=M\n',

                     '@SP\n',
                     'A=M\n',
                     'M=D\n',

                     '@SP\n',
                     'M=M+1\n']
            self._outfile.writelines(lines)
        elif segment == 'static':
            lines = [f'@{self._clean_cur_file}.{i}\n',
                     'D=M\n',

                     '@SP\n',
                     'A=M\n',
                     'M=D\n',

                     '@SP\n',
                     'M=M+1\n']
            self._outfile.writelines(lines)
        else:
            lines = [f'@{i}\n',
                     'D=A\n',
                     f'@{self.segments[segment]}\n',
                     'D=D+M\n',
                     '@addr\n',
                     'M=D\n',

                     '@addr\n',
                     'A=M\n',
                     'D=M\n',
                     '@SP\n',
                     'A=M\n',
                     'M=D\n',

                     '@SP\n',
                     'M=M+1\n']
            self._outfile.writelines(lines)

    def write_pop(self, segment, i):
        self._outfile.write(f'// pop {segment} {i}\n')  # For debugging purposes
        if segment == 'temp':
            lines = [f'@{CodeWriter.TEMP + i}\n',
                     'D=A\n',
                     '@addr\n',
                     'M=D\n',

                     '@SP\n',
                     'M=M-1\n',

                     '@SP\n',
                     'A=M\n',
                     'D=M\n',
                     '@addr\n',
                     'A=M\n',
                     'M=D\n']
            self._outfile.writelines(lines)
        elif segment == 'pointer':
            symbol = 'THAT' if i == 1 else 'THIS'
            lines = ['@SP\n',
                     'M=M-1\n',
                     'A=M\n',
                     'D=M\n',
                     f'@{symbol}\n',
                     'M=D\n']
            self._outfile.writelines(lines)
        elif segment == 'static':
            lines = ['@SP\n',
                     'M=M-1\n',
                     'A=M\n',
                     'D=M\n',
                     f'@{self._clean_cur_file}.{i}\n',
                     'M=D\n']
            self._outfile.writelines(lines)
        else:
            lines = [f'@{i}\n',
                     'D=A\n',
                     f'@{self.segments[segment]}\n',
                     'D=D+M\n',
                     '@addr\n',
                     'M=D\n',

                     '@SP\n',
                     'M=M-1\n',

                     '@SP\n',
                     'A=M\n',
                     'D=M\n',
                     '@addr\n',
                     'A=M\n',
                     'M=D\n']
            self._outfile.writelines(lines)

    def write_label(self, label):
        self._outfile.write(f'// label {label}\n')  # For debugging purposes
        self._outfile.writelines(f'({label})\n')

    def write_goto(self, label):
        self._outfile.write(f'// goto {label}\n')  # For debugging purposes
        lines = [f'@{label}\n',
                 '0;JMP\n']
        self._outfile.writelines(lines)

    def write_if(self, label):
        self._outfile.write(f'// if-goto {label}\n')  # For debugging purposes
        lines = [f'@SP\n',
                 'M=M-1\n',
                 'A=M\n',
                 'D=M\n',
                 f'@{label}\n',
                 'D;JNE\n']
        self._outfile.writelines(lines)

    def write_function(self, func_name, num_locals):
        self._outfile.write(f'// function {func_name} {num_locals}\n')  # For debugging purposes
        lines = [f'({func_name})\n',
                 '@i\n',
                 'M=0\n',
                 f'@{num_locals}\n',
                 'D=A\n',
                 '@n\n',
                 f'M=D\n',

                 # while (i > n)
                 f'({func_name}$LOOP)\n',
                 '@n\n',
                 'D=M\n',
                 '@i\n',
                 'D=D-M\n',
                 f'@{func_name}$ENDLOOP\n',
                 'D;JEQ\n',

                 # push 0
                 '@SP\n',
                 'A=M\n',
                 'M=0\n',

                 # i++
                 '@i\n',
                 'M=M+1\n',

                 # SP++
                 '@SP\n',
                 'M=M+1\n',

                 f'@{func_name}$LOOP\n',
                 '0;JMP\n',

                 f'({func_name}$ENDLOOP)\n']
        self._outfile.writelines(lines)

    def write_return(self):
        self._outfile.write(f'// return\n')  # For debugging purposes
        lines = [  # endFrame = LCL
                   '@LCL\n',
                   'D=M\n',
                   '@endFrame\n',
                   'M=D\n',

                   # retAddr = *(endFrame - 5)
                   '@endFrame\n',
                   'D=M\n',
                   '@5\n',
                   'A=D-A\n',
                   'D=M\n',
                   '@retAddr\n',
                   'M=D\n',

                   # *ARG = pop()
                   '@SP\n',
                   'M=M-1\n',
                   'A=M\n',
                   'D=M\n',
                   '@ARG\n',
                   'A=M\n',
                   'M=D\n',

                   # SP = ARG + 1
                   '@ARG\n',
                   'M=M+1\n',
                   'D=M\n',
                   '@SP\n',
                   'M=D\n',

                   # {THIS/THAT/ARG/LCL} = *(endFrame - {1/2/3/4})
                   '@endFrame\n',
                   'M=M-1\n',
                   'A=M\n',
                   'D=M\n',
                   '@THAT\n',
                   'M=D\n',
                   '@endFrame\n',
                   'M=M-1\n',
                   'A=M\n',
                   'D=M\n',
                   '@THIS\n',
                   'M=D\n',
                   '@endFrame\n',
                   'M=M-1\n',
                   'A=M\n',
                   'D=M\n',
                   '@ARG\n',
                   'M=D\n',
                   '@endFrame\n',
                   'M=M-1\n',
                   'A=M\n',
                   'D=M\n',
                   '@LCL\n',
                   'M=D\n',

                   # goto retAddr
                   '@retAddr\n',
                   'A=M\n',
                   '0;JMP\n']
        self._outfile.writelines(lines)

    def write_call(self, func_name, num_args):
        self._outfile.write(f'// call {func_name} {num_args}\n')  # For debugging purposes
        lines = [f'@{func_name}$ret.{self._ret_num}\n',
                 'D=A\n',
                 '@SP\n',
                 'A=M\n',
                 'M=D\n',
                 '@SP\n',
                 'M=M+1\n',

                 # Push frame
                 '@LCL\n',
                 'D=M\n',
                 '@SP\n',
                 'A=M\n',
                 'M=D\n',
                 '@SP\n',
                 'M=M+1\n',

                 '@ARG\n',
                 'D=M\n',
                 '@SP\n',
                 'A=M\n',
                 'M=D\n',
                 '@SP\n',
                 'M=M+1\n',

                 '@THIS\n',
                 'D=M\n',
                 '@SP\n',
                 'A=M\n',
                 'M=D\n',
                 '@SP\n',
                 'M=M+1\n',

                 '@THAT\n',
                 'D=M\n',
                 '@SP\n',
                 'A=M\n',
                 'M=D\n',
                 '@SP\n',
                 'M=M+1\n',

                 # ARG = SP - 5 - num_args
                 '@SP\n',
                 'D=M\n',
                 '@5\n',
                 'D=D-A\n',
                 f'@{num_args}\n',
                 'D=D-A\n',
                 '@ARG\n',
                 'M=D\n',

                 # LCL = SP
                 '@SP\n',
                 'D=M\n',
                 '@LCL\n',
                 'M=D\n',

                 # goto function_name
                 f'@{func_name}\n',
                 '0;JMP\n',

                 f'({func_name}$ret.{self._ret_num})\n']
        self._outfile.writelines(lines)
        self._ret_num += 1

    def write_init(self):
        lines = ['@256\n',
                 'D=A\n',
                 '@SP\n',
                 'M=D\n']
        self._outfile.writelines(lines)
        self.write_call('Sys.init', '0')

    # Arithmetic operations
    def _add(self):
        lines = ['@SP\n',
                 'M=M-1\n',

                 'A=M\n',
                 'D=M\n',

                 '@SP\n',
                 'M=M-1\n',

                 'A=M\n',
                 'M=D+M\n',

                 '@SP\n',
                 'M=M+1\n']
        self._outfile.writelines(lines)

    def _sub(self):
        lines = ['@SP\n',
                 'M=M-1\n',

                 'A=M\n',
                 'D=M\n',

                 '@SP\n',
                 'M=M-1\n',

                 'A=M\n',
                 'M=M-D\n',

                 '@SP\n',
                 'M=M+1\n']
        self._outfile.writelines(lines)

    def _neg(self):
        lines = ['@SP\n',
                 'M=M-1\n',

                 'A=M\n',
                 'M=-M\n',

                 '@SP\n',
                 'M=M+1\n']
        self._outfile.writelines(lines)

    def _and(self):
        lines = ['@SP\n',
                 'M=M-1\n',

                 'A=M\n',
                 'D=M\n',

                 '@SP\n',
                 'M=M-1\n',

                 'A=M\n',
                 'M=D&M\n',

                 '@SP\n',
                 'M=M+1\n']
        self._outfile.writelines(lines)

    def _or(self):
        lines = ['@SP\n',
                 'M=M-1\n',

                 'A=M\n',
                 'D=M\n',

                 '@SP\n',
                 'M=M-1\n',

                 'A=M\n',
                 'M=D|M\n',

                 '@SP\n',
                 'M=M+1\n']
        self._outfile.writelines(lines)

    def _not(self):
        lines = ['@SP\n',
                 'M=M-1\n',

                 'A=M\n',
                 'M=!M\n',

                 '@SP\n',
                 'M=M+1\n']
        self._outfile.writelines(lines)

    def _shift_left(self):
        lines = ['@SP\n',
                 'M=M-1\n',

                 'A=M\n',
                 'M=M<<\n',

                 '@SP\n',
                 'M=M+1\n']
        self._outfile.writelines(lines)

    def _shift_right(self):
        lines = ['@SP\n',
                 'M=M-1\n',

                 'A=M\n',
                 'M=M>>\n',

                 '@SP\n',
                 'M=M+1\n']
        self._outfile.writelines(lines)

    def _eq(self):
        lines = ['@SP\n',
                 'M=M-1\n',
                 'A=M\n',
                 'D=M\n',

                 '@SP\n',
                 'M=M-1\n',
                 'A=M\n',
                 'D=D-M\n',

                 f'@eq{self._eq_num}\n',
                 'D;JEQ\n',
                 'D=0\n',
                 f'@eq.end{self._eq_num}\n',
                 '0;JMP\n',

                 f'(eq{self._eq_num})\n',
                 'D=-1\n',
                 f'(eq.end{self._eq_num})\n',
                 '@SP\n',
                 'A=M\n',
                 'M=D\n',

                 '@SP\n',
                 'M=M+1\n']
        self._outfile.writelines(lines)
        self._eq_num += 1

    def _gt(self):
        lines = ['@SP\n',
                 'M=M-1\n',
                 'A=M\n',
                 'D=M\n',

                 '@SP\n',
                 'M=M-1\n',
                 'A=M\n',
                 'D=D-M\n',

                 f'@gt{self._gt_num}\n',
                 'D;JLT\n',
                 'D=0\n',
                 f'@gt.end{self._gt_num}\n',
                 '0;JMP\n',

                 f'(gt{self._gt_num})\n',
                 'D=-1\n',
                 f'(gt.end{self._gt_num})\n',
                 '@SP\n',
                 'A=M\n',
                 'M=D\n',

                 '@SP\n',
                 'M=M+1\n']
        self._outfile.writelines(lines)
        self._gt_num += 1

    def _lt(self):
        lines = ['@SP\n',
                 'M=M-1\n',
                 'A=M\n',
                 'D=M\n',

                 '@SP\n',
                 'M=M-1\n',
                 'A=M\n',
                 'D=D-M\n',

                 f'@lt{self._lt_num}\n',
                 'D;JGT\n',
                 'D=0\n',
                 f'@lt.end{self._lt_num}\n',
                 '0;JMP\n',

                 f'(lt{self._lt_num})\n',
                 'D=-1\n',
                 f'(lt.end{self._lt_num})\n',
                 '@SP\n',
                 'A=M\n',
                 'M=D\n',

                 '@SP\n',
                 'M=M+1\n']
        self._outfile.writelines(lines)
        self._lt_num += 1
