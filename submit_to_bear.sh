#!/bin/bash
#SBATCH --ntasks 36
#SBATCH --mem=244G
#SBATCH --time 12:00:00
#SBATCH --qos=bbdefault
#SBATCH --mail-type ALL
#SBATCH --job-name=mbmflex_model
#SBATCH -o mbmflex_out.log
#SBATCH -e mbmflex_err.log

set -e

module purge; module load bluebear
module load bear-apps/2023a
module load tqdm/4.66.1-GCCcore-12.3.0
module load numba/0.58.1-foss-2023a
module load multiprocess/0.70.15-gfbf-2023a
module load JupyterLab/4.0.5-GCCcore-12

python run_mbm.py
