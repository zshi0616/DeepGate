import glob
import platform
from util import *

# Parameter
cp_cnt = 1
insert_each_time = 10

if __name__ == '__main__':
    for file in glob.glob('./sub_circuits/' + "*.txt"):
        if platform.system() == 'Linux':
            name = file.split("/")
            name = name[-1].split(".")
        else:
            name = file.split("\\")
            name = name[1].split(".")

        circuit_name = name[0]
        print('[INFO] Circuit Name: {}'.format(circuit_name))

        x_data, edge_data = read_subcircuits(circuit_name)
        cc1, cc0 = read_cop(x_data)
        pred = read_prob(circuit_name)

        pre_list = []
        next_list = []
        for x_data_info in x_data:
            pre_list.append([])
            next_list.append([])
        for edge_info in edge_data:
            pre_list[edge_info[1]].append(edge_info[0])
            next_list[edge_info[0]].append(edge_info[1])

        depth = 0
        for idx, x in enumerate(x_data):
            if x[2] > depth:
                depth = x[2]
        level_list = []
        for level in range(depth+1):
            level_list.append([])
        for idx, x_data_info in enumerate(x_data):
            level_list[x_data_info[2]].append(idx)

        depth += 1
        print("[INFO] Circuit Depth: ", depth)
        print("[INFO] No of Nodes : ", len(x_data))
        output_bench(circuit_name, x_data, pre_list, next_list, level_list, folder='./bench/')
        continue

        # =============================================
        x_data_cop = hard_copy(x_data)
        x_data_dg = hard_copy(x_data)
        pre_list_cop = hard_copy(pre_list)
        pre_list_dg = hard_copy(pre_list)
        next_list_cop = hard_copy(next_list)
        next_list_dg = hard_copy(next_list)
        level_list_cop = hard_copy(level_list)
        level_list_dg = hard_copy(level_list)

        for insert_times in range(cp_cnt):
            cop_metric, _ = read_cop(x_data)
            cop_pos, cop_type, cop_val = get_position(cop_metric, next_list_cop, insert_each_time)
            for idx in range(len(cop_pos)):
                insert_cp(cop_pos[idx], x_data_cop, level_list_cop, pre_list_cop, next_list_cop, cop_type[idx])
                print('[INFO] COP Insert {} CP on {:}, with metric: {:}'.format(cop_type[idx], cop_pos[idx], cop_val[idx]))

            dg_metric = read_prob(circuit_name)
            dg_pos, dg_type, dg_val = get_position(dg_metric, next_list_dg, insert_each_time)
            for idx in range(len(dg_pos)):
                insert_cp(dg_pos[idx], x_data_dg, level_list_dg, pre_list_dg, next_list_dg, dg_type[idx])
                print('[INFO] DeepGate Insert {} CP on {:}, with metric: {:}'.format(dg_type[idx], dg_pos[idx], dg_val[idx]))

        output_bench(circuit_name, x_data_cop, pre_list_cop, next_list_cop, level_list_cop, folder='./cop_bench/')
        print('[SUCCESS] Save {}'.format(circuit_name))
        output_bench(circuit_name, x_data_dg, pre_list_dg, next_list_dg, level_list_dg)
        print('[SUCCESS] Save {}'.format(circuit_name))




