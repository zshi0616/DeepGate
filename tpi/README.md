# Test Point Insertion (TPI)
## Background
The test point insertion (TPI) techniques try to improve the fault detection likelihood. The statistical approaches of testability analysis such as COP and SCOAP are not accurate as the do not consider the reconvergence and signal correlation in logic gates. Logic simulation give accurate testabiltiy analysis result but it is very costly because large number of patterns are required to achieve accurate measures. The ideal insertion position should be the gate with probability close to the pole values (0 or 1), but typically the optimal TPI with reconvergent fan-outs is an NP-completed task. With our DeepGate probability prediction model, we can easily get the Boolean probability of each gate and identify the ideal position with pole probability value.

## Data Prepare
* Generate the dataset from circuits (only support .bench format yet). The dataset should be in ``` ./tpi/sub_circuits/ ``` folder, named as \$circuit_name\$.txt
* Generate the probability predictions for each node in this circuit, named also as \$circuit_name\$.txt in ``` ./tpi/predictions/ ``` folder.


## TPI and ATPG Procedure
Test points include control point (CP) and observation point (OP), the control point will provide a 0/1 input to the specific gate with enable itself, the observation point is a primary output which can allow user observing the internal value of the specific gate in netlist. Here we only consider which is the ideal position to insert the control point. 

1. Generate the inserted netlist (in .bench format)
```sh
python tpi_top.py
```
The inserted netlists will appear in ``` ./tpi/cop_bench/ ``` and ``` ./tpi/deepgate_bench/ ```, under two test point analyze strategies: COP metrics and DeepGate probability predictions, respectively. The enable port of CPs are primary inputs. 

2. Use the opensource Automatic Test Pattern Generation (ATPG) tool [Atalanta](https://github.com/hsluoyz/Atalanta) to report the test converage (TC) and pattern counts (PC). 
```sh
atalanta ./tpi/cop_bench/$circuit_name$.bench
atalanta ./tpi/deepgate_bench/$circuit_name$.bench
```

## Result
(cannot ensure validity yet)


