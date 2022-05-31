from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import os
from cmd2 import py_bridge
from progress.bar import Bar
import torch

from config import get_parse_args
from utils.logger import Logger
from utils.utils import AverageMeter, pyg_simulation
from utils.random_seed import set_seed
from utils.circuit_utils import check_difference
from utils.sat_utils import solve_sat_iteratively
from datasets.dataset_factory import dataset_factory
from detectors.detector_factory import detector_factory


def test(args):
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpus_str

    print(args)
    args.num_rounds = args.test_num_rounds
    Logger(args)

    dataset = dataset_factory[args.dataset](args.data_dir, args)
    # Do the shuffle
    perm = torch.randperm(len(dataset))
    dataset = dataset[perm]
    split = args.test_split
    data_len = len(dataset)
    # dataset = dataset[:10]
    # training_cutoff = int(data_len * args.trainval_split)
    # if split == 'train':
    #     dataset = dataset[:training_cutoff]
    # else:
    #     dataset = dataset[training_cutoff:]
    # print('Check Validation dataset...')
    # check_difference(dataset)


    detector = detector_factory['base'](args)

    print('Start Solving the SAT problem using DeepGate with Logic Implication...')

    num_cir = len(dataset)
    print('Tot num of circuits: ', num_cir)
    
    correct = 0
    total = 0
    for ind, g in enumerate(dataset):
        if 'Mask' in g.name:
            continue
        total += 1
        sol, sat = solve_sat_iteratively(g, detector)

        print('SAT: ', sat)

        if sat:
            correct +=1

    print('ACC: {:.2f}%'.format(100*correct/total))      
    '''
    results = {}
    num_iters = len(dataset)
    bar = Bar('{}'.format(args.exp_id), max=num_iters)
    time_stats = ['tot', 'net', 'post']
    avg_time_stats = {t: AverageMeter() for t in time_stats}
    for ind, g in enumerate(dataset):
        if args.cop_only:
            detector.show_results(g, None, args.debug_dir)
            Bar.suffix = '[{0}/{1}]|Tot: {total:} |ETA: {eta:} '.format(
            ind, num_iters, total=bar.elapsed_td, eta=bar.eta_td)
        else:
            results[g.name] = {}
            ret = detector.run(g)
            results[g.name]['pred'] = ret['results'].cpu()
            results[g.name]['gt'] = g.y.cpu()
            results[g.name]['rec'] = g.rec.cpu()
            Bar.suffix = '[{0}/{1}]|Tot: {total:} |ETA: {eta:} '.format(
                ind, num_iters, total=bar.elapsed_td, eta=bar.eta_td)
            for t in avg_time_stats:
                avg_time_stats[t].update(ret[t])
                Bar.suffix = Bar.suffix + '|{} {tm.val:.3f}s ({tm.avg:.3f}s) '.format(
                    t, tm=avg_time_stats[t])
        bar.next()
    bar.finish()

    # Run evaluation
    print('Evaluation...')
    diff = 0
    tot = 0
    diff_tot = None
    rec_tot = None
    for i in results.keys():
        if diff_tot is None:
            diff_tot = torch.abs((results[i]['pred'] - results[i]['gt']))
            rec_tot = results[i]['rec']
        else:
            diff_tot = torch.cat((diff_tot, torch.abs((results[i]['pred'] - results[i]['gt']))), dim=0)
            rec_tot = torch.cat((rec_tot, results[i]['rec']), dim=0)
    top_5 = int((diff_tot.size(0) * 0.05))
    diff = torch.sum(torch.topk(diff_tot, k=top_5, dim=0)[0])
    tot = top_5
    print('Average difference between Prediction and GT for Top 5 percents is: ', (diff/tot).item())

    print('Average difference between Prediction and GT is: ', (torch.sum(diff_tot)/diff_tot.size(0)).item())

    print('Average difference between Prediction and GT (reconvergent nodes) is: ', (torch.sum(diff_tot * rec_tot)/torch.sum(rec_tot)).item())

    print('Average difference between Prediction and GT (non-reconvergent nodes) is: ', (torch.sum(diff_tot * (1 - rec_tot))/torch.sum(1 - rec_tot)).item())
    '''


if __name__ == '__main__':
    args = get_parse_args()
    set_seed(args)

    test(args)
