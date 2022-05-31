from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import torch
from torch_geometric.data import Data
from utils.data_utils import one_hot
from utils.dag_utils import return_order_info, subgraph
from utils.utils import pyg_simulation
from models.deepsat import SoftEvaluator
from models.losses import SmoothStep
from models.mlp import MLP
from models.deepsat_copy import get_deepsat_gnn
from config import get_parse_args



def main():
    print('==> Building sample circuit （SR3): ')

    edge_index = torch.tensor([[0, 1, 1, 2, 4, 3, 5],
                               [3, 3, 5, 4, 5, 6, 6]], dtype=torch.long)
    x = []
    # PIs
    x += [one_hot(0, 3)]
    x += [one_hot(0, 3)]
    x += [one_hot(0, 3)]
    # internal nodes
    x += [one_hot(1, 3)]
    x += [one_hot(2, 3)]
    x += [one_hot(1, 3)]
    x += [one_hot(1, 3)]

    x = torch.cat(x, dim=0).float()
    # x.requires_grad = False
    forward_level, forward_index, backward_level, backward_index = return_order_info(edge_index, x.size(0))
    data = Data(x=x, edge_index=edge_index,
    forward_level=forward_level, forward_index=forward_index, 
    backward_level=backward_level, backward_index=backward_index)

    print(data)

    print('==> Check the logic level info:')
    print('Forward level: ', forward_level)
    print('Backward level: ', backward_level)
    
    print('==> Create the SoftEvaluator...')
    evaluator = SoftEvaluator(temperature=0.001, use_aig=True)

    print('==> Feed input [1, 1, 0]')
    pred = torch.zeros(size=[x.size(0), 1])
    pred[0] = 1
    pred[1] = 1
    pred[2] = 0

    num_layers_f = max(data.forward_level).item() + 1
    for l_idx in range(1, num_layers_f):
        # forward layer
        layer_mask = data.forward_level == l_idx
        l_node = data.forward_index[layer_mask]
        
        l_edge_index, _ = subgraph(l_node, edge_index, dim=1)
        msg = evaluator(pred, l_edge_index, x)
        l_msg = torch.index_select(msg, dim=0, index=l_node)
        
        pred[l_node, :] = l_msg

    print('Pred: \n', pred)

    # test the aig_simulation
    # literal index
    layer_mask = data.forward_level == 0
    l_node = data.forward_index[layer_mask]
    soft_assignment = pred[l_node]
    print('Soft Assignment: ', soft_assignment)
    hard_assignment = (soft_assignment > 0.5).int()
    print('Hard Assignmennt', hard_assignment)
    ret, _ = pyg_simulation(data, hard_assignment)
    print('Logic calculation results: ', ret)

    # sink index
    layer_mask = data.backward_level == 0
    sink_node = data.backward_index[layer_mask]
    sat = torch.index_select(pred, dim=0, index=sink_node)
    print('==> SAT: ', sat)

    # loss part
    sat_crit = SmoothStep()
    loss = sat_crit(sat)
    print('Loss: ', loss)

    # Overfitting part
    data = Data(x=x, edge_index=edge_index,
    forward_level=forward_level, forward_index=forward_index, 
    backward_level=backward_level, backward_index=backward_index)

    # model part
    args = get_parse_args()
    args.device = torch.device('cpu')
    deepsat = get_deepsat_gnn(args)
    # deepsat.aggr_forward.requires_grad = False
    # deepsat.aggr_backward.requires_grad = False
    # deepsat.update_forward.requires_grad = False
    # deepsat.update_backward.requires_grad = False
    print(deepsat)
    deepsat.train()


    # mlp = MLP(3, 32, 1, num_layer=2, sigmoid=True)
    # print(mlp)
    # mlp.train()

    evaluator = SoftEvaluator(temperature=0.1, use_aig=True)
    # loss and optimization
    # optimizer = torch.optim.Adam(mlp.parameters(), lr=1e-3, weight_decay=1e-10)
    optimizer = torch.optim.Adam(deepsat.parameters(), lr=1e-5, weight_decay=1e-10)

    
    # node_feature = torch.zeros_like(x) # [7, 3]
    # node_feature[0] = torch.tensor([1, 0, 0])
    # node_feature[1] = torch.tensor([0, 1, 0])
    # node_feature[2] = torch.tensor([0, 0, 1])
    # node_feature.requires_grad = False
    
    for i in range(100):
        
        # literal index
        # layer_mask = data.forward_level == 0
        # l_node = data.forward_index[layer_mask]
        # literal_mask = torch.zeros(x.size(0))
        # literal_mask = literal_mask.scatter(dim=0, index=l_node, src=torch.ones(len(l_node))).unsqueeze(1)
        # literal_mask.requires_grad = False

        # soft_assign = mlp(node_feature) * literal_mask # [7, 1] tensor
        # # print(soft_assign)

        # num_layers_f = max(data.forward_level).item() + 1
        # for l_idx in range(1, num_layers_f):
        #     # forward layer
        #     layer_mask = data.forward_level == l_idx
        #     l_node = data.forward_index[layer_mask]
            
        #     l_edge_index, _ = subgraph(l_node, edge_index, dim=1)
        #     msg = evaluator(soft_assign, l_edge_index, x)
        #     l_msg = torch.index_select(msg, dim=0, index=l_node)
            
        #     soft_assign[l_node, :] = l_msg
        # print(soft_assign)
        # # sink index
        # layer_mask = data.backward_level == 0
        # sink_node = data.backward_index[layer_mask]
        # sat = torch.index_select(soft_assign, dim=0, index=sink_node)
        # print(sat)
        

        
        sat, _, soft_assign = deepsat.solve_and_evaluate(data)
        print(soft_assign)
        print(sat)


        loss = sat_crit(sat).mean()

        optimizer.zero_grad()
        loss.backward()
        # torch.nn.utils.clip_grad_norm_(deepsat.parameters(), 0.65)
        optimizer.step()

        print('No. ', i, ', SAT value: ', sat.item(), ', loss:', loss.item())
        # exit()




    






if __name__ == '__main__':
    # args = get_parse_args()
    # set_seed(args)

    main()