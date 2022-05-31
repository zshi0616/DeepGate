import glob
import platform

# File
data_dir = './sub_circuits/'
label_dir = './predictions/'

def read_subcircuits(filename):
    graph_edges = []
    graph_nodes = []
    f = open(data_dir+filename+'.txt', 'r')
    lines = f.readlines()

    x_data = lines[0]
    edges_data = lines[1]

    edges_arr = edges_data.split(";")
    for ind, edge in enumerate(edges_arr):
        if ind != len(edges_arr) - 1:
            e = edge.split(",")
            source = e[0].split("(")
            dest = e[1].split(")")
            graph_edges.append([int(source[1]), int(dest[0])])

    x_arr = x_data.split(";")
    for ind, x in enumerate(x_arr):
        if ind != len(x_arr) - 1:
            att = x.split(":")
            new_node = []
            for i, a in enumerate(att):
                if i != len(att) - 1:
                    if i == 0:
                        new_node.append(a)
                    elif i == 1 or i == 2 or i == 6 or i == 7 or i == 8:
                        new_node.append(int(a))
                    else:
                        new_node.append(float(a))
            graph_nodes.append(new_node)

    f.close()
    return graph_nodes, graph_edges

def read_cop(x_data):
    cc0_list = []
    cc1_list = []
    for x_data_info in x_data:
        cc0_list.append(x_data_info[3])
        cc1_list.append(x_data_info[4])
    return cc0_list, cc1_list

def read_prob(filename):
    f = open(label_dir + filename + '.txt', 'r')
    prob_list = []
    lines = f.readlines()
    for line in lines:
        line = line.replace(' ', '').replace('\n', '')
        prob_list.append(float(line))
    return prob_list

def num_to_gate_type(num):
    if num == 0:
        return 'INPUT'
    elif num == 1:
        return 'AND'
    elif num == 2:
        return 'NAND'
    elif num == 3:
        return 'OR'
    elif num == 4:
        return 'NOR'
    elif num == 5:
        return 'NOT'
    elif num == 6:
        return 'XOR'
    else:
        return 'Unknown'

def get_gate_type(node_type):
    if "INPUT" in node_type:
        vector_row = 0
    elif "NAND" in node_type:
        vector_row = 2
    elif "AND" in node_type:
        vector_row = 1
    elif "NOR" in node_type:
        vector_row = 4
    elif "OR" in node_type:
        vector_row = 3
    elif "NOT" in node_type:
        vector_row = 5
    # elif " BUFF" in node_type:
    #   vector_row = 6
    elif "XOR" in node_type:
        vector_row = 6
    else:
        vector_row = -1
    return vector_row


def get_position(val, next_list, cnt=1):
    insert_val = []
    types = []
    for ele in val:
        if ele > 0.5:
            insert_val.append(1 - ele)
            types.append('AND')
        else:
            insert_val.append(ele - 0)
            types.append('OR')

    sorted_index = sorted(range(len(insert_val)), key=lambda  k: insert_val[k])
    index_res = []
    type_res = []
    val_res = []
    tmp_cnt = 0
    for idx in sorted_index:
        if len(next_list[idx]) > 0:
            index_res.append(idx)
            type_res.append(types[idx])
            val_res.append(val[idx])
            tmp_cnt += 1
        if tmp_cnt == cnt:
            break
    return index_res, type_res, val_res

def output_bench(filename, x_data, pre_list, next_list, level_list, folder='./deepgate_bench/'):
    output_file = open(folder + filename + '.bench', 'w')
    
    # Write PI and PO
    pi_list = level_list[0]
    po_list = []
    
    for idx, fanout_nodes in enumerate(next_list):
        if len(fanout_nodes) == 0:
            po_list.append(idx)

    output_file.write('# {}\n'.format(filename))
    output_file.write('# {:} inputs\n'.format(len(pi_list)))
    output_file.write('# {:} outputs\n'.format(len(po_list)))
    output_file.write('# {:} gates\n'.format(len(x_data) - len(level_list[0])))
    output_file.write('\n')

    for pi_idx in pi_list:
        output_file.write('INPUT({})\n'.format(x_data[pi_idx][0]))
    output_file.write('\n')
    for po_idx in po_list:
        output_file.write('OUTPUT({})\n'.format(x_data[po_idx][0]))
    output_file.write('\n')

    # Write Gates
    for level in range(1, len(level_list), 1):
        for idx in level_list[level]:
            x_data_info = x_data[idx]
            line = x_data_info[0] + ' = ' + num_to_gate_type(x_data_info[1]) + '('
            for pre_idx, pre_ele in enumerate(pre_list[idx]):
                line += x_data[pre_ele][0]
                if pre_idx != len(pre_list[idx]) - 1:
                    line += ', '
            line += ')\n'
            output_file.write(line)

    output_file.close()

def insert_cp(pos, x_data, level_list, pre_list, next_list, type='AND'):
    cp_name = x_data[pos][0] + '_' + type + '_CP'
    pi_name = x_data[pos][0] + '_' + 'CP' + '_EN'
    # Name, Gate_type, Gate_level, CC0, CC1, CO, is_branch, is_RC, RC_src
    new_x_data_info = [cp_name, get_gate_type(type), x_data[pos][2]+1, -1, -1, -1, 0, 0, -1]
    new_pi_info = [pi_name, get_gate_type('INPUT'), 0, 0.5, 0.5, -1, 0, 0, -1]
    if type == 'AND':
        new_x_data_info[3] = 0.5 * x_data[pos][3]
        new_x_data_info[4] = 1 - new_x_data_info[3]
        new_x_data_info[5] = x_data[next_list[pos][0]][5] * 0.5
        new_pi_info[5] = new_x_data_info[5] * x_data[pos][3]
    else:
        new_x_data_info[3] = 1 - 0.5 * x_data[pos][4]
        new_x_data_info[4] = 1 - new_x_data_info[3]
        new_x_data_info[5] = x_data[next_list[pos][0]][5] * 0.5
        new_pi_info[5] = new_x_data_info[5] * x_data[pos][4]

    # New PI
    pi_idx = len(x_data)
    cp_idx = len(x_data)+1
    x_data.append(new_pi_info)
    level_list[0].append(pi_idx)
    pre_list.append([])
    next_list.append([cp_idx])

    # New CP
    x_data.append(new_x_data_info)
    level_list[new_x_data_info[2]].append(cp_idx)
    pre_list.append([pos, pi_idx])
    next_list.append([])
    for fanout_idx in next_list[pos]:
        for k, fanin_idx_of_fanout_node in enumerate(pre_list[fanout_idx]):
            if fanin_idx_of_fanout_node == pos:
                pre_list[fanout_idx][k] = cp_idx
        next_list[cp_idx].append(fanout_idx)
    next_list[pos] = [cp_idx]

def hard_copy(val):
    res = []
    if len(val) > 1:
        for ele in val:
            res.append(ele.copy())
    else:
        res = val.copy()
    return res

if __name__ == '__main__':
    a = [0.1, 0.05, 0.99]
    pos = get_position(a)
    print(pos)