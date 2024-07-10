#!/bin/bash
#SBATCH --ntasks 17
#SBATCH --nodes 1
#SBATCH --time 72:00:00
#SBATCH --qos=bbdefault
#SBATCH --mail-type ALL
#SBATCH --job-name=full_model
#SBATCH -o mbmflex_parallel_out.log
#SBATCH -e mbmflex_parallel_err.log

set -e

module purge; module load bluebear
module load Python/3.8.6-GCCcore-10.2.0
module load geopandas/0.9.0-foss-2020b
module load tqdm/4.56.2-GCCcore-10.2.0
module load numba/0.52.0-foss-2020b

python settings_parallel.py
