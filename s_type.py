def s_type(instr, reg_set, data_memory, stack_memory):
    imm = instr[0:7] + instr[20:25]
    rs_2 = get_field(instr[7:12])
    rs_1 = get_field(instr[12:17])
    funct3 = instr[17:20]

    off_set = get_num("0b" + imm, 12)
    base = get_num(reg_set[rs_1])
    data = reg_set[rs_2]

    adress = base + off_set

    if adress in range(65536, 65664):
        base_adress = 65536
    elif adress in range(256, 380):
        base_adress = 256

    rel_adress = (adress - base_adress)

    if rel_adress % 4 != 0:
        print("Illegal Memory Access")
        return data_memory, stack_memory

    index = rel_adress // 4

    if funct3 == "010":
        if base_adress == 65536:
            data_memory[index] = data
        elif base_adress == 256:
            stack_memory[index] = data

    return data_memory, stack_memory