# the base training script
cd src
# train
python main.py diff --exp_id test --data_dir ../data/benchmarks/iscas85/syn/ --num_rounds 10 --dataset benchmarks --gpus 0 --batch_size 1 --dim_hidden 64 --dim_node_feature 7 --no_node_cop --predict_diff

# test/demo
# python test.py diff --exp_id test --data_dir ../data/benchmarks/iscas85/syn/ --num_rounds 10 --dataset benchmarks --batch_size 1 --dim_hidden 64 --debug 1 --resume --dim_node_feature 7 --no_node_cop --predict_diff