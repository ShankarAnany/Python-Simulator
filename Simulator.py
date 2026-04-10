import sys

## Ease Of Use functions
def get_bin(num, length):
    # Returns num in binary format extended to given length
    b = "0b" + format((num % (1 << length)) , f"0{length}b")
    return b

def get_hex(num, length):
    # Returns num in hex format extended to given length
    h = "0x" + format(num, f"0{length}x").upper()
    return h

def get_field(s):
    # Returns int from binary
    return int(s, 2)

def get_num(s, length = 32, unsigned = False):
    # Returns int from binary, handles 2's complement form & unsigned form
    num = int(s, 0)
    num &= (1 << length) - 1

    if not unsigned and num >= (1 << (length - 1)):
        num -= (1 << length)

    return num

## Initialization and Write functions
def create_memory_and_reg_set():
    # Initializes data_memory and registers and sets all values to 0, and stack pointer to 380
    data_memory = []
    stack_memory = []
    program_memory = []
    reg_set = []

    for i in range(32):
        temp = get_bin(0, 32)
        data_memory.append(temp)
        stack_memory.append(temp)
        program_memory.extend([temp[2:], temp[2:]])
        reg_set.append(temp)
    
    reg_set[2] = get_bin(380, 32)
    
    return data_memory, stack_memory, program_memory, reg_set

def memory_dump(data_memory, file):
    # Writes all data_memory data to file
    address = int("0x00010000", 0)

    for word in data_memory:
        file.write(f"{get_hex(address, 8)}:{word}\n")
        address += 4

def reg_dump(pc, reg_set, file):
    # Writes all register data to file
    file.write(get_bin(pc, 32))

    for reg in reg_set:
        file.write(f" {reg}")
    
    file.write("\n")

## Simulator functions
def r_type(instr, reg_set):
    return reg_set

def i_type_alu(instr, reg_set):
    return reg_set

def i_type_lw(instr, reg_set, data_memory, stack_memory):
    imm = instr[0:12]
    rs_1 = get_field(instr[12:17])
    funct_3 = instr[17:20]
    rd = get_field(instr[20:25])

    off_set = get_num("0b" + imm, 12)
    base = get_num(reg_set[rs_1])

    adress = base + off_set

    if adress in range(65536, 65664):
        base_adress = 65536
    elif adress in range(256, 380):
        base_adress = 256

    rel_adress = (adress - base_adress)

    if rel_adress % 4 != 0:
        print("Illegal Memory Access", end = "")
        return reg_set

    index = rel_adress // 4

    result = get_bin(0, 32)
    if funct_3 == "010":
        if base_adress == 65536:
            result = data_memory[index]
        elif base_adress == 256:
            result = stack_memory[index]

    if rd != 0:
        reg_set[rd] = result

    return reg_set

def i_type_jalr(instr, reg_set, pc):
    return reg_set, pc

def s_type(instr, reg_set, data_memory, stack_memory):
    return data_memory, stack_memory

def b_type(instr, reg_set, pc):
    return pc

def u_type_lui(instr, reg_set):
    return reg_set

def u_type_auipc(instr, reg_set, pc):
    return reg_set

def j_type(instr, reg_set, pc):
    return reg_set, pc

## Main Program
def main():
    data_memory, stack_memory, program_memory, reg_set = create_memory_and_reg_set()

    # Read bin File
    in_file_name = sys.argv[1]
    out_file_name = sys.argv[2]

    with open(in_file_name, "r") as f:
        program = f.readlines()
    
    for i in range(len(program)): # Program Memory is 256 bit only - can have only 64 instructions
        program_memory[i] = program[i].strip()

    if len(program) > 64:
        print("Insufficient Program Memory: Program Too Long")

    out_file = open(out_file_name, "w")
    
    # Main Program Loop
    custom_pc_change = False
    pc = 0
    while True:
        instr = program_memory[pc // 4]
        if instr == "00000000000000000000000001100011":
            break

        opcode = instr[-7:]
        if opcode == "0110011":
            reg_set = r_type(instr, reg_set)
        elif opcode == "0010011":
            reg_set = i_type_alu(instr, reg_set)
        elif opcode == "0000011":
            reg_set = i_type_lw(instr, reg_set, data_memory, stack_memory)
        elif opcode == "1100111":
            reg_set, pc = i_type_jalr(instr, reg_set, pc)
            custom_pc_change = True
        elif opcode == "0100011":
            data_memory, stack_memory = s_type(instr, reg_set, data_memory, stack_memory)
        elif opcode == "1100011":
            pc = b_type(instr, reg_set, pc)
            custom_pc_change = True
        elif opcode == "0110111":
            reg_set = u_type_lui(instr, reg_set)
        elif opcode == "0010111":
            reg_set = u_type_auipc(instr, reg_set, pc)
        elif opcode == "1101111":
            reg_set, pc = j_type(instr, reg_set, pc)
            custom_pc_change = True

        if not custom_pc_change:
            pc += 4
        custom_pc_change = False

        reg_dump(pc, reg_set, out_file)

    reg_dump(pc, reg_set, out_file)
    memory_dump(data_memory, out_file)

    out_file.close()

if __name__ == "__main__":
    main()
