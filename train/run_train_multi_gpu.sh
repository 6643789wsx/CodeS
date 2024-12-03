#!/bin/bash

# setup for wandb
export WANDB_PROJECT="codes"
export WANDB_API_KEY="26cba387a64cfbd93a5d06b6ed89670ec66bcafe"

# Disable NCCL P2P and IB
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1

deepspeed --include localhost:0,1,2,3,4,5,6 --master_port=9901 /data/data_public/dtw_data/CodeS/train/src/train_bash.py \
    --deepspeed /data/data_public/dtw_data/CodeS/train/configs/ds_config_zero3.json \
    --stage sft \
    --model_name_or_path /data/data_public/dtw_data/modelscop_hub/hub/AI-ModelScope/starcoder2-3b \
    --do_train True \
    --finetuning_type full \
    --template qwen \
    --output_dir /data/data_public/dtw_data/CodeS2/CodeS/models/starcoder2-3b \
    --overwrite_output_dir \
    --dataset_dir data \
    --dataset codes \
    --learning_rate 5e-05 \
    --per_device_train_batch_size 8 \
    --gradient_accumulation_steps 8 \
    --lr_scheduler_type cosine \
    --num_train_epochs 5.0 \
    --logging_steps 2 \
    --save_steps 20 \
    --fp16 True \
    --rope_scaling linear \
    --plot_loss True \
    --report_to wandb