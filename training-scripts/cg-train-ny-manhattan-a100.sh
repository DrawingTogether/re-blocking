#!/bin/bash
#SBATCH --nodes=1
#SBATCH --time=8:00:00
#SBATCH --job-name=train-ny-m-cg-a100
#SBATCH --partition=gpu
##SBATCH --gres=gpu:v100-sxm2:1
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=40GB
#SBATCH --mail-type=ALL
#SBATCH --mail-user=l.schrage@northeastern.edu

module load anaconda3/2022.05 cuda/11.8
source activate /home/l.schrage/.conda/envs/re-blocking_env

python3 /work/re-blocking/pytorch-CycleGAN-and-pix2pix/train.py --dataroot /work/re-blocking/data/ny-manhattan --checkpoints_dir /work/re-blocking/checkpoints --name ny-manhattan-cg-200-10-a100-40gb --model cycle_gan --direction AtoB --n_epochs 200 --batch_size 10