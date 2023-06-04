#!/bin/bash
# The interpreter used to execute the script

#SBATCH --job-name TES_model
#SBATCH --mail-type=NONE
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=20gb 
#SBATCH --time=1:00:00
#SBATCH --account=mtcraig1
#SBATCH --partition=standard-oc

module load python3.9-anaconda/2021.11

# Run the job
python ./ProcessPeak.py log.PeakProcess
