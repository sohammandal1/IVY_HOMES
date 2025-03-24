import os
import multiprocessing

# Method 1: Using os module
print("Number of threads (logical CPUs):", os.cpu_count())

# Method 2: Using multiprocessing module
print("Number of threads (logical CPUs):", multiprocessing.cpu_count())
