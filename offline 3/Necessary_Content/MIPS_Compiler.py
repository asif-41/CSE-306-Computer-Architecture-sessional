#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys

const_dict = {
    '$t0': '0',
    '$t1': '1',
    '$t2': '2',
    '$t3': '3',
    '$t4': '4',
    '$zero': '5',
    '$sp': '7',
    '$temp': '6',
    'add': '2',
    'addi': '3',
    'sub': 'd',
    'subi': '4',
    'and': 'c',
    'andi': '1',
    'or': 'f',
    'ori': '0',
    'sll': 'b',
    'srl': 'e',
    'nor': '6',
    'sw': 'a',
    'lw': '7',
    'beq': '5',
    'bneq': '9',
    'j': '8',
    }

category_R = ['add', 'sub', 'and', 'or', 'nor']
category_R_s = ['sll', 'srl']
category_I = ['addi', 'subi', 'andi', 'ori']
category_I_m = ['sw', 'lw']
category_I_b = ['beq', 'bneq']

label_dict = {}
code_hex = []


def parse_R(line):
    line = line.strip(' ')
    code_units = line.split(' ')
    hex_str = const_dict[code_units[0]] \
        + const_dict[code_units[2].strip(',')] \
        + const_dict[code_units[3].strip(',')] \
        + const_dict[code_units[1].strip(',')] + '0'
    code_hex.append(hex_str)


def parse_R_s(line):
    line = line.strip(' ')
    code_units = line.split(' ')
    num = format(int(code_units[3]), 'x')
    hex_str = const_dict[code_units[0]] + '0' \
        + const_dict[code_units[2].strip(',')] \
        + const_dict[code_units[1].strip(',')] + num
    code_hex.append(hex_str)


def parse_I(line):  # -3
    line = line.strip(' ')
    code_units = line.split(' ')
    num = ''
    x = int(code_units[-1])
    if x >= 0:
        num = format(int(code_units[-1]), 'x')
        if len(num) == 1:
            num = '0' + num
    else:
        print ('imediate neg : ', x)
        y = 255 + x + 1
        num = format(y, 'x')

    hex_str = const_dict[code_units[0]] \
        + const_dict[code_units[2].strip(',')] \
        + const_dict[code_units[1].strip(',')] + num
    code_hex.append(hex_str)


def parse_I_m(line):
    line = line.strip(' ')
    code_units = line.split(' ')
    val = code_units[2].split('(')[0]
    val = format(int(val), 'x')
    if len(val) == 1:
        val = '0' + val
    reg = const_dict[code_units[2].split('(')[1].strip(')')]
    hex_str = const_dict[code_units[0]] + reg \
        + const_dict[code_units[1].strip(',')] + val

  # return hex_str

    code_hex.append(hex_str)


def parse_I_b(line, line_counter):
    line = line.strip(' ')
    code_units = line.split(' ')
    print ('label_dict :', label_dict[code_units[3]], 'line no : ',
           line_counter)

    diff = label_dict[code_units[3]] - line_counter - 1  # pc

    h = ''
    if diff >= 0:
        h = format(diff, 'x')
        if len(h) == 1:
            h = '0' + h
    else:
        negDiff = 255 + diff + 1
        h = format(negDiff, 'x')
        print('neg format: ' + h)

    hex_str = const_dict[code_units[0]] \
        + const_dict[code_units[1].strip(',')] \
        + const_dict[code_units[2].strip(',')] + h

  # return hex_str

    code_hex.append(hex_str)


def parse_J(line):
    line = line.strip(' ')
    code_units = line.split(' ')
    h = format(label_dict[code_units[1]] - 1, 'x')
    if len(h) == 1:
        h = '0' + h
    hex_str = const_dict[code_units[0]] + h + '00'
    code_hex.append(hex_str)


def remove_comments(line):
    line = line.strip()
    if line != '':
        x = line.find('//')
        line = (line if x == -1 else line[0:x])

    # line = line+"\n"

    return line


def format_line(line):
    if line != '':
        newLine = ' '.join([a.strip() for a in line.split()])
        print(newLine)
        newLine = ', '.join([a.strip() for a in newLine.split(',')])
        if '(' in newLine or ')' in newLine:
            newLine = '('.join([a.strip() for a in newLine.split('(')])
            newLine = ')'.join([a.strip() for a in newLine.split(')')])
        return newLine + '\n'
    return line


def create_intermediate_file(inputFileName):
    secondary_f = open('interim_code.txt', 'w')
    with open(inputFileName, 'r') as f:
        for line in f:
            line = remove_comments(line)
            if line.strip().split(' ')[0] == 'push':
                location = line.strip().split()[1]
                if '(' in location or ')' in location:
                    inc_val = location.split('(')[0]
                    reg_val = location.split('(')[1].strip(')')
                    secondary_f.write('addi $temp, ' + reg_val + ', '
                            + inc_val + '\n')
                    secondary_f.write('lw $temp, 0($temp)' + '\n')
                    secondary_f.write('sw $temp, 0($sp)' + '\n')
                else:
                    secondary_f.write('sw ' + location + ', 0($sp)'
                            + '\n')
                secondary_f.write('addi $sp, $sp, -1' + '\n')
            elif line.strip().split(' ')[0] == 'pop':
                reg_name = line.strip().split()[1]
                secondary_f.write('addi $sp, $sp, 1' + '\n')
                secondary_f.write('lw ' + reg_name + ', 0($sp)\n')
            else:

        # secondary_f.write(' '.join(line.split()))

                secondary_f.write(format_line(line))
        secondary_f.close()


def read_lines():
    lines = []
    with open('interim_code.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line != '':
                x = line.find('//')
                line = (line if x == -1 else line[0:x])
                lines.append(line)
    return lines


def construct_labels(lines):
    line_counter2 = 1
    for i in range(0, len(lines)):
        if lines[i][-1] == ':':
            label_dict[(lines[i])[:-1]] = line_counter2
        else:
            line_counter2 += 1


def parse_MIPS_code(lines):
    line_counter = 0
    for line in lines:
        line_counter += 1
        opcode = line.split(' ')[0]
        if line[-1] == ':':
            print ('(label) - >', line)
            line_counter -= 1
        elif opcode in category_R:
            print ('R - > ', line)
            parse_R(line)
        elif opcode in category_R_s:
            print ('R_2 -> ', line)
            parse_R_s(line)
        elif opcode in category_I:
            print ('I -> ', line)
            parse_I(line)
        elif opcode in category_I_m:
            print ('I_m -> ', line)
            parse_I_m(line)
        elif opcode in category_I_b:
            print ('I_b -> ', line)
            parse_I_b(line, line_counter)
        else:
            print ('J -> ', line)
            parse_J(line)


def create_output_file():
    output_file = open('hex_code.txt', 'w')
    output_file.write('v2.0 raw\n')
    for num in code_hex:
        output_file.write(num + '\n')
    print('Hex file created')
    output_file.close()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        fileName = 'input.txt'
    print('Input fileName: ' + fileName)
    create_intermediate_file(fileName)
    lines = read_lines()
    construct_labels(lines)
    parse_MIPS_code(lines)
    create_output_file()

			