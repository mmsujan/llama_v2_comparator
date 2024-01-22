import argparse
import numpy as np 
import os
from os import listdir
import errno
import sys
from run_llama_v2_io_binding import llama_params
from run_llama_v2_io_binding import llama_main

SUCCESS = 0
ERROR = 1
UNKNOWN_FAILURE = 2


def compare(threshold, compare_mode, platform, verbosity):
    
    file1_path = "./goldenOutput/output.txt"
    file2_path = "./generatedOutput/output.txt"
    
    if not os.path.isfile(file2_path) or not os.path.isfile(file1_path):
        if verbosity:
         raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file2_path)
         sys.exit(1)
        return UNKNOWN_FAILURE
    with open(file1_path, 'r') as file1:
        content1 = None
        if compare_mode == "Word":
            content1 = file1.read().split()
        elif compare_mode == "Character":
            content1 = file1.read()
        else:
            content1 = file1.readlines()
    with open(file2_path, 'r') as file2:
        content2 = None 
        if compare_mode == "Word":
            content2 = file2.read().split()
        elif compare_mode == "Character":
            content2 = file2.read()
        else:
            content2 = file2.readlines()
    
    mismatch_count = 0
    err_code = SUCCESS
    
    if (compare_mode == "Word" or compare_mode == "Character") and len(content1) != len(content2):
        if verbosity:
            print("Files have different length.")
        err_code = ERROR
        return err_code
        
    for i, (item1, item2) in enumerate(zip(content1, content2)):
        if item1 != item2:
            mismatch_count += 1
            if verbosity:
                print ( item1, " != ", item2)
    if mismatch_count > threshold:
        err_code = ERROR
        if verbosity:
            print("Mismatch count = ", mismatch_count, " and threshold = ", threshold)
    
    return err_code
    
    
    
def run_comparator(threshold, compare_mode, platform, verbosity):
    
    #compare generated image with golden image
    print("Comparing generated text with golden text...")
    ret_code = compare(threshold, compare_mode, platform, verbosity)
    print("code : ", ret_code)
    if verbosity:
        if ret_code == SUCCESS:
            print("PASS!")
        elif ret_code == ERROR:
            print("ERROR!")
        else:
            print("Unknown Failure!")   
    return ret_code
    
def add_text_compare_params(parser):
    parser.add_argument("--threshold", default= 10, type=int, help="Maximum number of difference between generated and golden text.")
    parser.add_argument("--compare_mode", default="Line", type=str, help="Compare mode : Character, Word or Line")
    parser.add_argument("--platform", default="DG2", type=str, help="Platform: DG2 or MTLH")
    parser.add_argument("--verbosity", action="store_true", help="Print error details")
## main function for other script    
def main():
    parser = argparse.ArgumentParser()
    text_com_group = parser.add_argument_group(title="text comparator params")
    llama_group = parser.add_argument_group(title="llama params")
    add_text_compare_params(text_com_group)
    llama_params(llama_group)
    args = parser.parse_args()
    #create image using stable diffusion 
    llama_main(args);
    
    return run_comparator(args.threshold, args.compare_mode, args.platform, args.verbosity)
    
if __name__ == "__main__":
    main()
    
#path1= "./generatedOutput/output.txt"
#path2 = "./goldenOutput/output.txt"

#compare_output(path1, path2)