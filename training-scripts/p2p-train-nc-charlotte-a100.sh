#!/bin/bash
#SBATCH --nodes=1
#SBATCH --time=8:00:00
#SBATCH --job-name=train-nc-c-a100
#SBATCH --partition=gpu
##SBATCH --gres=gpu:v100-sxm2:1
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24GB
#SBATCH --mail-type=ALL
#SBATCH --mail-user=l.schrage@northeastern.edu

module load anaconda3/2022.05 cuda/11.8
source activate /home/l.schrage/.conda/envs/re-blocking_env

python3 /work/re-blocking/pytorch-CycleGAN-and-pix2pix/train.py --dataroot /work/re-blocking/data/nc-charlotte --checkpoints_dir /work/re-blocking/checkpoints --name nc-charlotte-100-60-a100 --model pix2pix --direction AtoB --n_epochs 100 --batch_size 60