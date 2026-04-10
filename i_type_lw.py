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