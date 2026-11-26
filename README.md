Softmax and Kernel Fusion in CUDA

Parallel & Distributed Computing Laboratory · KLE Technological University (KLETECH), Hubballi

Team: Mudit Nayak · Kartik · Manoj · Vinayak

Evaluation Theme: 10 – Softmax and Kernel Fusion

A CUDA-based study of row-wise Softmax used in classifiers and attention mechanisms. The project implements and compares separate CUDA kernels, a fused shared-memory kernel, online Softmax, warp-per-row processing and a fast-math variant.

All implementations are verified against a CPU reference and benchmarked using CUDA events across five experiments.

⸻

Contents

1. Problem
2. Kernel Design
3. Repository Layout
4. Test Machine
5. Build and Run
6. Screenshots from Actual Runs
7. Results
8. Analysis
9. Correctness
10. Limitations
11. Future Work

⸻

1. Problem

For each row of a matrix, Softmax converts input values into probabilities.

The mathematical formula is:

[
\operatorname{softmax}(x)_i =
\frac{\exp(x_i-m)}
{\sum_j \exp(x_j-m)}
]

where (m) is the maximum value in the row.

Subtracting the maximum helps prevent numerical overflow during exponential calculations.

Softmax involves three main operations:

1. Finding the maximum value in each row.
2. Calculating exponential values and their sum.
3. Normalising the values to obtain probabilities.

When implemented using separate CUDA kernels, the input matrix is accessed multiple times through GPU global memory.

Since Softmax performs relatively little computation per memory access, reducing memory traffic is an important optimisation.

Project Objective:

To implement and optimise row-wise Softmax using CUDA by exploring different GPU processing techniques, reducing memory access and improving execution performance while maintaining numerical correctness.

Softmax is commonly used in:

* Classification models to convert output scores into probabilities.
* Transformer attention mechanisms to normalise attention scores.

2. Kernel Design

The project implements five CUDA kernel variants.

Variant	Global accesses per element	Implementation
Separate	4	Uses three kernels: k_max, k_sumexp and k_norm
Fused (Shared Memory)	2	Combines operations into one kernel and stores the row in shared memory
Online Softmax	3	Maintains a running maximum and rescaled sum
Warp-per-row	2	Assigns one warp to each row and uses registers
Fused + __expf	2	Uses a faster approximate exponential function

2.1 Separate Kernels

The traditional implementation uses three separate CUDA kernels:

* k_max: Finds the maximum value in each row.
* k_sumexp: Calculates the sum of exponential values.
* k_norm: Normalises the values to produce the final output.

Each row is processed by one CUDA block. Warp shuffle operations and shared memory are used for reductions.

2.2 Fused Softmax Using Shared Memory

This implementation combines the three operations into a single CUDA kernel.

Working:

1. Load the row into shared memory.
2. Find the maximum value.
3. Calculate exponential values and their sum.
4. Normalise the values.
5. Write the final output.

This reduces global memory accesses from four to two per element.

The implementation requires the row to fit in shared memory, with a maximum of 48 KB in the configured implementation.

2.3 Online Softmax

Online Softmax maintains two running values:

* Running maximum.
* Running sum.

When a larger value is encountered, the running sum is adjusted accordingly.

This allows the maximum and exponential sum to be calculated in one pass, followed by a separate output pass.

2.4 Warp-per-row

In this implementation, one GPU warp processes one row.

A warp consists of 32 GPU threads. Intermediate values are stored in registers, reducing the need for shared memory and block-wide synchronisation.

The implementation supports rows up to 1024 columns.

2.5 Fast Math

This implementation uses NVIDIA’s __expf() function instead of the standard expf() function.

It provides a faster approximate exponential calculation, and its execution time and numerical accuracy are compared with the standard fused implementation.

Benchmarking Method: CUDA events are used for timing, with 3 warm-up runs followed by an average of 30 runs.

The memory bandwidth calculations use estimated memory traffic based on the number of global memory accesses.

3. Repository Layout

cuda_softmax_fusion/
│
├── Makefile
├── PLAN.md
├── README.md
│
├── src/
│   ├── kernels.cuh
│   └── bench.cu
│
├── scripts/
│   ├── run_all.sh
│   ├── sweep.sh
│   ├── plot.py
│   ├── make_readme.py
│   ├── make_ppt.py
│   └── package.py
│
├── results/
│   ├── data.csv
│   ├── summary.md
│   ├── figures
│   └── logs
│
├── docs/
│   └── screenshots/
│
└── presentation/
    └── CUDA_Softmax_Kernel_Fusion.pptx

Important Files

File	Purpose
kernels.cuh	Contains CUDA Softmax implementations and reduction functions
bench.cu	Runs experiments, verifies outputs and generates benchmark data
Makefile	Compiles the CUDA program
run_all.sh	Executes the complete project workflow
sweep.sh	Runs all benchmark experiments
plot.py	Generates performance graphs and result summaries
make_readme.py	Generates the README
make_ppt.py	Generates the PowerPoint presentation
package.py	Packages project results

4. Test Machine

Component	Configuration
GPU	NVIDIA GeForce RTX 5060 Ti
GPU Memory	16 GB
CUDA Cores Architecture	Compute Capability 12.0
Streaming Multiprocessors	36
L2 Cache	32 MB
CUDA Toolkit	CUDA 13.3
Compiler	NVIDIA NVCC
Operating System	Ubuntu on WSL2 (Windows 11)
Programming Language	C++17 and CUDA C++

Compiler flags:

nvcc -O3 -std=c++17 -arch=sm_120 -lineinfo

5. Build and Run, Step by Step

All commands are executed inside Ubuntu on WSL.

Step 1: Check GPU and CUDA Availability

nvidia-smi
nvcc --version

These commands verify that the NVIDIA GPU is accessible and the CUDA compiler is installed.

Step 2: Copy the Project into WSL

cp /mnt/c/Users/Intel/Downloads/cuda_softmax_fusion.zip ~/
cd ~
unzip cuda_softmax_fusion.zip
cd cuda_softmax_fusion

Replace Intel with the appropriate Windows username.

Step 3: Compile the Project

make gpu ARCH=sm_120

The architecture sm_120 is used for the NVIDIA RTX 50-series GPU.

Step 4: Execute All Experiments

bash scripts/sweep.sh

This executes the benchmark experiments and generates the results in CSV format.

Step 5: Generate Graphs and Reports

Install the required Python libraries:

pip install matplotlib pandas numpy python-pptx pillow

Generate the graphs, README and presentation:

python3 scripts/plot.py
python3 scripts/make_readme.py
python3 scripts/make_ppt.py

Alternatively, execute the complete workflow using:

bash scripts/run_all.sh

6. Screenshots from the Actual Runs

The following screenshots document the actual GPU environment, benchmark execution and report generation.

6.1 GPU and CUDA Environment

GPU: NVIDIA GeForce RTX 5060 Ti

CUDA Toolkit: 13.3

Operating System: Ubuntu on WSL2

The environment was verified using nvidia-smi and nvcc --version.

6.2 Baseline Benchmark and Row-Length Sweep

The screenshot shows:

* GPU configuration and benchmark execution.
* Comparison between separate and fused kernels.
* Performance testing across row lengths from 128 to 8192 columns.
* Correctness verification against the CPU reference.

At 4096 × 4096, the fused implementation achieves approximately 1.93× speedup.

Original screenshot: docs/screenshots/01_benchmark_run_baseline_and_colsweep_original.png

6.3 Block-Size Sweep and DRAM-Bound Experiments

The screenshot shows:

* Testing different CUDA block sizes from 64 to 1024 threads.
* Comparing execution time for different configurations.
* Performance evaluation using large matrices.

Original screenshot: docs/screenshots/02_benchmark_run_blocksweep_and_dram_original.png

6.4 DRAM-Bound and Attention-Shape Experiments

The screenshot shows:

* Large matrix performance measurements.
* Effective memory bandwidth.
* Attention-score matrix experiments.
* Completion of benchmark execution.

Original screenshot: docs/screenshots/03_benchmark_run_dram_attention_done_original.png

6.5 Report Generation

The screenshot shows the execution of the report-generation scripts and the creation of graphs, README and PowerPoint files.

Original screenshot: docs/screenshots/04_report_build_original.png

7. Results

All benchmark results are generated using scripts/plot.py from results/data.csv.

7.1 Baseline Performance Comparison

The following table compares the traditional separate-kernel implementation with the fused implementation.

Matrix Size	Separate (ms)	Fused (ms)	Speedup
4096 × 1024	0.074	0.039	1.89×
4096 × 2048	0.326	0.178	1.83×
2048 × 8192	0.694	0.494	1.41×
4096 × 4096	0.702	0.364	1.93×
8192 × 2048	0.687	0.356	1.93×

The fused implementation achieves up to 1.93× speedup over the separate implementation on the tested baseline matrix sizes.

7.2 Row-Length Sweep

The following experiment compares different Softmax implementations using 4096 rows and different column sizes.

Columns	Separate	Fused	Online	Warp-per-row	Fused + __expf
128	0.040	0.024	0.021	0.010	0.021
256	0.045	0.023	0.023	0.013	0.023
512	0.068	0.027	0.030	0.012	0.027
1024	0.069	0.038	0.044	0.022	0.038
2048	0.344	0.178	0.186	–	0.186
4096	0.694	0.374	0.367	–	0.367
8192	1.366	0.970	0.733	–	0.988

Execution times are in milliseconds.

7.3 Block-Size Sweep

The fused implementation was tested using different CUDA block sizes.

Columns	Best Block Size	Best Time (ms)	Worst Block Size	Worst Time (ms)
1024	128	0.036	1024	0.140
2048	128	0.178	1024	0.239
4096	512	0.354	64	0.661
8192	512	0.724	64	2.811

The results show that the best block size depends on the row length.

7.4 Figures

The following graphs are generated from the benchmark results.

Speedup vs Row Length

Execution Time vs Row Length

Effective Bandwidth vs Row Length

Kernel Execution Breakdown

Block-Size Comparison

DRAM-Bound Performance

Attention-Shape Performance

8. Analysis

The experiments provide the following observations:

1. Kernel Fusion: Combining three separate kernels into one reduces global memory accesses from four to two per element. The fused implementation achieves 1.41× to 1.93× speedup on baseline sizes.
2. Row-Length Dependency: Different implementations perform differently depending on the number of columns in each row.
3. Warp-per-row: Performs well for smaller rows because it uses registers and avoids block-wide synchronisation.
4. Online Softmax: Performs particularly well for larger rows, achieving the best measured time at 8192 columns.
5. Block Size: The optimal number of threads changes with row length. Smaller block sizes work better for some configurations, while larger blocks perform better for others.
6. Fast Math: Replacing expf() with __expf() does not provide a consistent performance improvement across all tested configurations.
7. Memory Bandwidth: On large DRAM-bound matrices, the fused kernel achieves approximately 375–378 GB/s effective bandwidth, around 84% of the specified 448 GB/s peak.
8. Cache Effects: Smaller matrices can fit into the GPU’s L2 cache, which can result in calculated effective bandwidth values higher than the physical DRAM bandwidth.

The memory bandwidth values are estimates based on ideal memory traffic rather than direct hardware-counter measurements.

Overall, the results demonstrate that kernel fusion reduces memory traffic, while the choice of the best implementation depends on the workload.

9. Correctness

Every CUDA implementation is compared against a double-precision CPU Softmax reference.

The verification process:

1. Generate input data.
2. Calculate the reference output using the CPU.
3. Execute the CUDA implementation.
4. Compare the GPU output with the CPU reference.
5. Calculate the maximum absolute error.

The first 64 rows of each tested matrix are used for CPU verification.

Verification Results:

Parameter	Result
Total verified kernel runs	139
Maximum absolute error	3.0 × 10⁻⁸
Accepted error threshold	1 × 10⁻⁵
Verification status	All MATCH

All 139 verified kernel runs passed the numerical correctness threshold.

10. Limitations

* Experiments were conducted on one GPU and one machine.
* Synthetic random input data in the range [-10, 10] was used instead of real neural-network activations.
* Matrices that fit into the L2 cache may be served from cache during repeated benchmark runs.
* Only the first 64 rows of each matrix are verified against the CPU reference.
* The fused implementation requires the row to fit into shared memory, limiting the supported row size to 12,288 columns under the configured 48 KB shared-memory limit.
* GPU clock variations and other running processes can affect execution time.

11. Future Work

The following improvements can be explored in future versions:

* Implement vectorised memory loading using float4 for improved memory access.
* Explore hybrid register and shared-memory implementations.
* Develop a fallback implementation for rows exceeding the shared-memory limit.
* Integrate Softmax directly into attention-score computation to avoid writing intermediate score matrices.
* Use NVIDIA Nsight Compute to analyse memory throughput, register usage and GPU occupancy.

⸻

