cd src
python main.py prob --exp_id recgnn_imply_m --data_dir ../data/benchmarks/merged_mask --test_data_dir ../data/benchmarks/merged_no_mask --num_rounds 10 --dataset benchmarks --gpus 0 --gate_types INPUT,AND,NOT --dim_node_feature 3 --no_node_cop --aggr_function aggnconv --wx_update --mask
