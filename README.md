## Installation

 - Clone "llama_v2_comparator"
 - Open Anaconda prompt ( Recommended)
 - cd to "llama_v2_comparator" directory
 
Run following command to create conda environment
 
```
conda create -n llama_v2
conda activate llama_v2
pip install -e .
cd llama_v2
pip install -r requirements.txt
```
For python environment, open command prompt, and cd to "llama_v2_comparator" directory. Run following command:
```
pip install -e .
cd llama_v2
pip install -r requirements.txt
```
## Run Test
 - Copy Llama_V2 models from [Llama_v2_modesl]() 
 - Unzip " models" directory and put it inside "llama_v2_comparator/llama_v2"
 - From conda or command prompt, cd path to "llama_v2_comparator/llama_v2" directory  
 
 Sample Run: 
 ```
 python compare.py
 ```
 
 - You can set different threshold values as per requirement. For an example:
 ```
 python compare.py --threshold 5
 ```
 - Command line argument options:
 
```
usage: compare.py [-h] [--threshold THRESHOLD] [--compare_mode COMPARE_MODE] [--platform PLATFORM] [--verbosity]

optional arguments:
  -h, --help            show this help message and exit

text comparator params:
  --threshold THRESHOLD
                        Maximum number of difference between generated and golden text.
  --compare_mode COMPARE_MODE
                        Compare mode : Character, Word or Line
  --platform PLATFORM   Platform: DG2 or MTL
  --verbosity           Print error details

```
