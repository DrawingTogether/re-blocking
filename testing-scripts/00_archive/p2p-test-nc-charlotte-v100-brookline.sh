#!/bin/bash
#SBATCH --nodes=1
#SBATCH --time=2:00:00
#SBATCH --job-name=test-nc-c-v100
#SBATCH --partition=gpu
#SBATCH --gres=gpu:v100-sxm2:1
##SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=10GB
#SBATCH --mail-type=ALL
#SBATCH --mail-user=l.schrage@northeastern.edu

module load anaconda3/2022.05 cuda/11.8
source activate /home/l.schrage/.conda/envs/re-blocking_env

python3 /work/re-blocking/pytorch-CycleGAN-and-pix2pix/test.py --dataroot /work/re-blocking/data/ma-brookline --checkpoints_dir /work/re-blocking/checkpoints --results_dir /work/re-blocking/results --name nc-charlotte-200-150-v100 --model pix2pix --num_test 1000