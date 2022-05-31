# DeepGate: Learning Neural Representations of Logic Gates

Code repository for the paper:  
**DeepGate: Learning Neural Representations of Logic Gates**, ACM/IEEE Design Automation Conference (**DAC**), 2022.  
[Min Li\*](https://scholar.google.com/citations?user=X5gRH80AAAAJ&hl=zh-CN), [Sadaf Khan\*](https://khan-sadaf.github.io/), [Zhengyuan Shi](https://cure-lab.github.io/people/zhengyuan_shi/index.html) and [Qiang Xu](https://cure-lab.github.io/qiang_xu.html)

## Abstract
Applying deep learning (DL) techniques in the electronic design automation (EDA) field has become a trending topic in recent years. Most existing solutions apply well-developed DL models to solve specific EDA problems. While demonstrating promising results, they require careful model tuning for every problem. The fundamental question on *"How to obtain a general and effective neural representation of circuits?"* has not been answered yet. In this work, we take the first step towards solving this problem. We propose *DeepGate*, a novel representation learning solution that effectively embeds both logic function and structural information of a circuit as vectors on each gate. Specifically, we propose transforming circuits into unified and-inverter graph format for learning and using signal probabilities as the supervision task in DeepGate. We then introduce a novel graph neural network that uses strong inductive biases in practical circuits as learning priors for signal probability prediction. Our experimental results show the efficacy and generalization capability of DeepGate.


## Installation
The experiments are conducted on Linux, with Python version 3.7.4, PyTorch version 1.8.1, and [Pytorch Geometric](https://github.com/pyg-team/pytorch_geometric) version 2.0.1.

To set up the environment:
```sh
git clone https://github.com/Ironprop-Stone/DeepGate.git
cd deepgate
conda create -n deepgate python=3.7.4
conda activate deepgate
pip install -r requirements.txt
```

## Prepare dataset
Please refer to [`DATASETS.md`](DATASETS.md) for the preparation of the dataset files.

## Running training code
To train the DeepGate,
```sh
cd src
python main.py [--args]
```
For settings of experiments, run the scripts in directory `./experiments/prob/`. For example: 
```sh
bash ./experiments/prob/recgnn_deepgate.sh
```
## Run evaluation code
Run `test.sh`  in directory `./experiments/prob/`.


## Test point insertion
After training the DeepGate model, we can apply it for the downstream task: **test point insertion**. We provide a separate directory `./tpi` for this task. Please read [`./tpi/README.md`](tpi/README.md) first. More details about how to run the TPI will be coming soon.


## SAT solving
The repo supports [NeuroSAT](https://arxiv.org/abs/1802.03685)/[CircuitSAT](https://openreview.net/forum?id=BJxgz2R9t7) and the DeepGate-SAT.

1. NeuroSAT: the CNF-based problems are converted into bipartite graphs, and the edge_index defines the edge from literals to clauses. Run [neurosat.sh](experiments/neurosat.sh) to train the model. The visualization of voter will be added soon.
2. CircuitSAT: Run [circuitsat.sh](experiments/circuitsat.sh) to train the DG-DAGRNN described in the CircuitSAT paper. The evaluation will be coming soon.

## Acknowledgements
This code uses [DAGNN](https://github.com/vthost/DAGNN), [D-VAE](https://github.com/muhanzhang/D-VAE) and [neurosat](https://github.com/dselsam/neurosat)/[NeuroSAT](https://github.com/ryanzhangfan/NeuroSAT) as backbone. We gratefully appreciate the impact these libraries had on our work. If you use our code, please consider citing the original papers as well. The code organization follows the one from [CenterNet](https://github.com/xingyizhou/CenterNet). Thanks!