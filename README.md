# CodeS: Natural Language to Code Repository via Multi-Layer Sketch

[Paper](https://arxiv.org/pdf/2403.16443.pdf) | [Video Demo](./assets/codes_demo.mp4)

## What is this about?
The impressive performance of large language models (LLMs) on code-related tasks has shown the potential of fully automated software development. In light of this, we introduce a new software engineering task, namely Natural Language to code Repository (NL2Repo). This task aims to generate an entire code repository from its natural language requirements. To address this task, we propose a simple yet effective framework CodeS, which decomposes NL2Repo into multiple sub-tasks by a multi-layer sketch. Specifically, CodeS includes three modules: RepoSketcher, FileSketcher, and SketchFiller. RepoSketcher first generates a repository's directory structure for given requirements; FileSketcher then generates a file sketch for each file in the generated structure; SketchFiller finally fills in the details for each function in the generated file sketch. To rigorously assess CodeS on the NL2Repo task, we carry out evaluations through both automated benchmarking and manual feedback analysis. For benchmark-based evaluation, we craft a repository-oriented benchmark, SketchEval, and design an evaluation metric, SketchBLEU. For feedback-based evaluation, we develop a VSCode plugin for CodeS and engage 30 participants in conducting empirical studies. Extensive experiments prove the effectiveness and practicality of CodeS on the NL2Repo task.

## Project Directory

```python
.
├── assets
├── clean_repo.py # ./repos/ -> ./cleaned_repos/
├── cleaned_repos
├── craft_train_data.py # ./output -> ./training_data
├── extract_sketch.py # ./cleaned_repos/ -> ./output
├── outputs
├── projects # two projects
├── prompt_construction_utils.py
├── repos
├── requirements.txt
├── run_step1_clean.sh # runing ./clean_repo.py
├── run_step2_extract_sketch.sh # runing ./extract_sketch.py
├── run_step3_make_data.sh # runing ./craft_train_data.py
├── scripts
├── train # *train codes model* scripts
├── training_data
└── validation # *evaluation* scripts
```

## Creating Instruction Data for 100 Repositories

1. Download the selected repositories to the `./repos` directory and unzip them;
2. Preprocess the repositories;
```bash
bash run_step1_clean.sh
```
3. Extract instruction training data for `RepoSketcher`, `FileSketcher`, and `SketchFiller`.
```bash
bash run_step2_extract_sketch.sh
bash run_step3_make_data.sh
```

## Training

1. Place the created instruction data into `./train/data` and configure `dataset_info.json` according to the structure described at https://github.com/hiyouga/LLaMA-Factory/tree/main/data.

2. Start the training process:

```bash
cd train
vim run_train_multi_gpu.sh
bash run_train_multi_gpu.sh
```

## Evaluation

1. Install `SketchBLEU`, similar to `CodeBLEU`.

2. Perform inference on `SketchEval`:
```bash
HF_ENDPOINT=https://hf-mirror.com python /data/data_public/dtw_data/CodeS2/CodeS/validation/evaluation_scripts/from_scratch_inference.py
```

3. Convert the inference results for the entire repository:
```bash
HF_ENDPOINT=https://hf-mirror.com python /data/data_public/dtw_data/CodeS2/CodeS/validation/evaluation_scripts/transfer_output_to_repo.py
```

4. Evaluate the generated repository as with `CodeBLEU`:

```bash
python /data/data_public/dtw_data/CodeS/validation/evaluation_scripts/batch_eval/batch_get_metric.py --output_dir /data/data_public/dtw_data/CodeS2/CodeS/validation/evaluation_results/transferred_repos --valid_dir /data/data_public/dtw_data/CodeS2/CodeS/cleaned_repos-test
```
