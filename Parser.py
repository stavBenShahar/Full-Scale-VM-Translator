import re


class Parser:
    """
    Parses a single .vm file.
    A command is composed by three parts:
    <command> <segment> <index>
    Where when an arithmetic command is given,
    the segment and index part are not present.
    """

    cmd_types = {'arithmetic': 0,   'push':       1,   'pop':        2,
                 'label':      3,   'goto':       4,   'if':         5,
                 'function':   6,   'return':     7,   'call':       8}

    arithmetic_cmds = ['add', 'sub', 'neg', 'shiftleft', 'shiftright',
                       'eq', 'gt', 'lt', 'and', 'or', 'not']

    def __init__(self, fp):
        with open(fp, 'r') as vm_file:
            raw_lines = self._remove_comments(vm_file.read().split('\n'))
            self._lines = self._remove_empty_strings(raw_lines)
        self._lines.reverse()
        self._cur_line = None

    def _remove_comments(self, lines):
        return [re.sub(r'//(.+)*', '', line) for line in lines]

    def _remove_empty_strings(self, str_list):
        return list(filter(None, str_list))

    def advance(self):
        self._cur_line = self._lines.pop()

    def has_more_cmds(self):
        return self._lines != []

    def _is_arithmetic(self, line):
        for cmd in Parser.arithmetic_cmds:
            if cmd in line:
                return True
        return False

    def _is_push(self, line):
        return 'push' in line

    def _is_pop(self, line):
        return 'pop' in line

    def _is_label(self, line):
        return 'label' in line

    def _is_goto(self, line):
        return 'goto' in line

    def _is_if(self, line):
        return 'if-goto' in line

    def _is_function(self, line):
        return 'function' in line

    def _is_return(self, line):
        return 'return' in line

    def _is_call(self, line):
        return 'call' in line

    def get_cmd_type(self):
        if self._is_call(self._cur_line):
            return Parser.cmd_types["call"]
        if self._is_return(self._cur_line):
            return Parser.cmd_types["return"]
        if self._is_function(self._cur_line):
            return Parser.cmd_types["function"]
        if self._is_if(self._cur_line):
            return Parser.cmd_types["if"]
        if self._is_goto(self._cur_line):
            return Parser.cmd_types["goto"]
        if self._is_label(self._cur_line):
            return Parser.cmd_types["label"]
        if self._is_arithmetic(self._cur_line):
            return Parser.cmd_types["arithmetic"]
        if self._is_push(self._cur_line):
            return Parser.cmd_types["push"]
        if self._is_pop(self._cur_line):
            return Parser.cmd_types["pop"]
        return None

    def get_cmd(self):
        return self._cur_line.split()[0]

    def get_arg1(self):
        return self._cur_line.split()[1]

    def get_arg2(self):
        return int(self._cur_line.split()[2])
