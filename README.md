# PyPODEM

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![ATPG](https://img.shields.io/badge/EDA-ATPG-success)
![VLSI](https://img.shields.io/badge/VLSI-Testing-orange)


A robust, object-oriented **Automatic Test Pattern Generation (ATPG)** and fault simulation engine built entirely in **Python** from first principles.

The engine implements the classical **PODEM (Path-Oriented Decision Making)** implicit enumeration search framework, restricting all decisions exclusively to **Primary Inputs (PIs)** following **P. Goel's original formulation**.

Designed as a rigorous Electronic Design Automation (EDA) tool prototype, **PyPODEM** performs full topological circuit exploration, incorporates static look-ahead fault collapsing, and integrates incremental fault dropping for compact test generation.

The framework has been benchmarked against **Virginia Tech's ATALANTA ATPG engine** using standard **ISCAS'85 combinational benchmark circuits**.

---

## 🚀 Key Architectural Highlights

### 🔹 5-Valued D-Calculus Simulation

Implements Roth's five-valued logic system:


0
1
X
D
D'


using explicit lookup tables, enabling simultaneous simulation of both the fault-free and faulty circuits.

---

### 🔹 Agnostic Netlist DAG Construction

- Parses standard .bench netlists
- Builds directed acyclic graph (DAG) representations
- Uses **Kahn's Algorithm** for topological sorting
- Eliminates logic race conditions during simulation

---

### 🔹 Look-Ahead Fault Collapsing

Performs static fault equivalence analysis to reduce the initial single stuck-at fault universe before ATPG execution, significantly lowering search complexity.

---

### 🔹 Heuristic Search & Backtracing

Implements:

- Dynamic **D-Frontier** tracking
- Objective computation
- Structural backtrace through gate fan-in cones

while ensuring **all decision variables remain Primary Inputs**, exactly as defined in the original PODEM algorithm.

---

### 🔹 Dual-Core Verification Pipeline

Includes an independent **Boolean (0/1) fault simulator** with no D-token dependencies that verifies every generated test vector independently from the PODEM engine.

---

# 📦 System Architecture

The framework is organized into **10 modular computational components**.

---

## 1. Logic Values

Defines

- X
- D
- D'

along with truth tables for

- NAND
- AND
- OR
- NOR
- NOT
- XOR
- BUFF

using explicit lookup matrices for accurate D-calculus propagation.

---

## 2. Bench Parser

Reads .bench files and constructs

- Primary Inputs
- Primary Outputs
- Gate database
- Fanout map
- Topological ordering (self.topo)

using **Kahn's Algorithm**.

---

## 3. Logic & Fault Simulators

### `simulate()`

Performs complete forward propagation while injecting the target stuck-at fault during simulation.

### `simulate_incremental()`

Updates only the downstream logic cone after an input modification, reducing unnecessary recomputation.

---

## 4. D-Frontier & Backtrace

### `d_frontier()`

Identifies propagation candidates by locating gates with:

- D/D' inputs
- Unknown outputs

### `backtrace()`

Maps internal objectives back to Primary Inputs while correctly handling inversions through

- NAND
- NOR
- NOT

---

## 5. PODEM Search Engine

### `podem()`

Recursive branch-and-bound ATPG engine with configurable backtracking limits.

### `fault_simulate_vector()`

Applies every generated vector against the remaining fault list and immediately drops all detected faults to minimize the final vector set.

---

# 📊 Industrial Benchmark Results

| Circuit | PyPODEM Coverage | ATALANTA Coverage | PyPODEM Vectors | ATALANTA Patterns | Vector Ratio | Remarks |
|----------|-----------------|------------------|----------------|------------------|--------------|---------|
| **c17** | **100.00%** | **100.0%** | 7 | 7 | **1.00×** | Perfect agreement validates parser, simulator and backtrace implementation. |
| **c432** | **95.38%** | **99.0%** | 43 | 63 | **0.68×** | Generates 32% fewer vectors while maintaining high coverage. |
| **c499** | **100.00%** | **96.6%** | 63 | 56 | **1.13×** | Successfully resolves complex XOR propagation paths. |
| **c880** | **100.00%** | **100.0%** | 92 | 148 | **0.62×** | Achieves identical coverage using 38% fewer vectors. |

---

# 🔍 Verification & Debugging

The independent Boolean fault simulator helped identify two critical implementation bugs during development.

## ✅ Missing Fault Injection

The recursive simulator initially bypassed the targeted fault injection, causing the ATPG engine to evaluate only the fault-free circuit.

**Result:** 0% fault coverage.

---

## ✅ Incorrect Backtrace Rules

Corrected inversion handling for

- NAND
- NOR

where non-controlling values were mistakenly selected instead of controlling values.

---

# 🛠 Installation

## Prerequisites

- Python 3.8+
- Matplotlib *(optional, for analytics plots)*
- Atalanta Tool from Github -> https://github.com/hsluoyz/Atalanta

---

The framework will

- Parse benchmark circuits
- Generate collapsed fault lists
- Execute recursive PODEM
- Perform fault dropping
- Generate test vectors
- Export CSV reports
- Print execution statistics

---


# 🚀 Future Work

### ⚡ C++ / Rust Port

Port the validated Python implementation into a compiled language to improve execution speed and scalability.

---

### ⚡ FAN Algorithm

Upgrade the ATPG engine from classical PODEM to **FAN (Fan-Out Oriented ATPG)** for improved heuristic pruning.

---

### ⚡ Advanced Fault Models

Extend support to

- Transition Delay Faults (TDF)
- Bridging Faults
- IDDQ Testing
- Path Delay Faults

---

### ⚡ Parallel Fault Simulation

Implement

- Parallel Pattern Single Fault Simulation (PPSF)
- GPU acceleration
- Multi-threaded execution

to process multiple vectors simultaneously.

---

# 📚 References

1. P. Goel, **"An Implicit Enumeration Algorithm to Generate Tests for Combinational Logic Circuits,"** IEEE Transactions on Computers, 1981.

2. J. P. Roth, **"Diagnosis of Automata Failures: A Calculus and a Method,"** IBM Journal of Research and Development, 1966.

3. Brglez & Fujiwara, **ISCAS'85 Benchmark Suite**, IEEE ISCAS, 1985.

4. H. K. Lee and D. S. Ha, **ATALANTA ATPG Tool**, Virginia Tech.
