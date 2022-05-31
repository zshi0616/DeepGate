import argparse
import glob
import os
import sys
import platform

import numpy as np

prj_path = os.path.dirname(os.path.realpath('__file__'))
sys.path.append(prj_path + '/../../src')


import utils.data_utils as data_utils
import utils.circuit_utils as circuit_utils


output_filename_circuit = 'benchmarks_circuits_graphs'
output_filename_labels = 'benchmarks_circuits_labels'

graphs = {}
labels = {}

def create_dataset(bench_dir, num_patterns, gate_to_index):
    bench_folder = bench_dir + "/*.bench"
    bench_idx = 0
    for file in glob.glob(bench_folder):
        if platform.system() == 'Windows':
            name = file.split("\\")
            name = name[1].split(".")
        else:
            name = file.split("/")
            name = name[-1].split(".")

        print("." * 10)
        print("No. %d Circuit Name: " % bench_idx, name[0])
        bench_idx += 1

        data = data_utils.read_file(file)

        # updata the bench and also calculate the number of nodes
        data, num_nodes, index_map = circuit_utils.add_node_index(data)

        # base feature generation, node name, type, logic level
        data, edge_data, level_list, fanin_list, fanout_list = circuit_utils.feature_generation(data, gate_to_index)

        # calculate the logic depth of the circuit
        print("Circuit Depth: ", len(level_list)-1)
        num_nodes = len(data)
        print("# Nodes : ", num_nodes)
        PI_indexes = level_list[0]

        # After synthesize, some circuit only
        if len(level_list) == 1 or num_nodes == 0:
            continue

        # adding COP measurements in feature set.
        print('Add the COP measurements.')
        x = data
        x = circuit_utils.generate_prob_cont(x, PI_indexes, level_list, fanin_list)
        x = circuit_utils.generate_prob_obs(x, level_list, fanin_list, fanout_list)

        '''
        x : list(list((str, int, int))), the node feature matrix with shape [num_nodes, num_node_features], the current dimension of num_node_features is 3, wherein 0th - node_name defined in bench (str); 1st - integer index for the gate type; 2nd - logic level; 3rd - C1, 4th - C0, 5th - Obs.
        '''

        print("Identifying reconvergence.")
        x, _ = circuit_utils.identify_reconvergence(x, level_list, fanin_list, fanout_list)
        '''
        x : list(list((str, int, int))), the node feature matrix with shape [num_nodes, num_node_features], the current dimension of num_node_features is 3, wherein 0th - node_name defined in bench (str); 1st - integer index for the gate type; 2nd - logic level; 3rd - C1; 4th - C0; 5th - Obs; 6th - fan-out, 7th - boolean recovengence, 8th - index of the source node (-1 for non recovengence).
        '''
        # circuit_utils.check_reconvergence(x_data_obj, sub_edge_data[index])
        # circuit_utils.circuit_statistics(name[0], x_data_obj, sub_edge_data[index])

        # Convert node name (str) to node index (int)
        x = circuit_utils.rename_node(x)
        graphs[name[0]] = {'x': np.array(x).astype('float32'), "edge_index": np.array(edge_data)}

        # saving circuits_figs on disk
        # data_utils.write_subcircuits(name[0] + "_" + str(index), x, sub_edge_data[index])

        # generating simulated labels
        # calling simulator
        print('Start the logic simulation.')
        y_data = circuit_utils.simulator(x, PI_indexes, level_list, fanin_list, num_patterns)
        labels[name[0]] = {'y': np.array(y_data)}

        # saving combine_labels on disk
        # data_utils.write_file(name[0] + "_" + str(index), y_data)

    # save to numpy npz compressed format
    print('Saving...')
    np.savez_compressed(output_filename_circuit, circuits=graphs)
    np.savez_compressed(output_filename_labels, labels=labels)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Random circuits dataset processor')


    parser.add_argument('--bench-dir', default='../../data_raw/benchmarks/bench', type=str, metavar='PATH', help='the path that contains all circuits in bench')
    parser.add_argument('--gate_types', default='*', type=str, metavar='LIST', help='gate types in the circuits')
    parser.add_argument('--sub-circuit-size', default=25, type=int,
                    help='size of subcircuit to extract from original circuit')
    parser.add_argument('--num-patterns', default=15000, type=int,
                    help='no of patterns to apply for logic simulation')

    args = parser.parse_args()

    # update data settings
    DEFAULT_GATE_TO_INDEX = {"INPUT": 0, "AND": 1, "NAND": 2, "OR": 3, "NOR": 4, "NOT": 5, "XOR": 6}
    gate_to_index = {}
    if args.gate_types == '*':
        gate_to_index = DEFAULT_GATE_TO_INDEX
    else:
        gate_types = args.gate_types.split(',')
        for i in range(len(gate_types)):
            gate_to_index[gate_types[i]] = i

    if not os.path.exists(args.bench_dir):
        print('The bench data directory dose not exist: ', args.bench_dir)
        exit(0)
    
    bench_folder = args.bench_dir + "/*.bench"
    if len(list(glob.glob(bench_folder))) == 0:
        print('No bench file in the data directory: ', args.bench_dir)
        exit(0)

    if os.path.exists(output_filename_circuit + '.npz'):
        print('The dataset already exists at', output_filename_circuit + '.npz')
        # exit(0)

    print('Extracting random circuits from: ', args.bench_dir)
    
    create_dataset(args.bench_dir, args.num_patterns, gate_to_index)

    print('Finish circuit extraction.')

    
    

