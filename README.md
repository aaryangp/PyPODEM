# PyPODEM

> A Python implementation of the **PODEM (Path-Oriented Decision Making)** Automatic Test Pattern Generation (ATPG) algorithm for combinational circuits using the single stuck-at fault model.

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![ATPG](https://img.shields.io/badge/EDA-ATPG-success)
![VLSI](https://img.shields.io/badge/VLSI-Testing-orange)

## Overview

PyPODEM is a from-scratch implementation of the classical **PODEM ATPG algorithm**, developed to generate test vectors for detecting **single stuck-at faults** in combinational digital circuits.

The project implements the complete ATPG flow including:

- Parsing ISCAS'85 .bench netlists
- Five-valued D-Calculus logic simulation
- Recursive PODEM search algorithm
- Gate-aware backtrace
- D-Frontier computation
- Fault collapsing
- Fault dropping
- Independent fault simulation for verification

The implementation was benchmarked against the industry-standard **ATALANTA ATPG** tool on ISCAS'85 benchmark circuits.

---

## Features

- ✅ Complete PODEM implementation in Python
- ✅ Five-valued logic (0, 1, X, D, D')
- ✅ ISCAS'85 .bench parser
- ✅ Topological circuit construction (Kahn's Algorithm)
- ✅ Recursive backtracking search
- ✅ Gate-aware backtrace
- ✅ D-Frontier based fault propagation
- ✅ Stuck-at fault generation (SA0 / SA1)
- ✅ Fault equivalence collapsing
- ✅ Fault dropping for vector minimization
- ✅ Independent Boolean fault simulator for verification
- ✅ Coverage reporting and test vector generation

---

## Supported Gates

- AND
- OR
- NAND
- NOR
- NOT
- XOR
- BUFFER

---

## Algorithm Flow


Read .bench file
        │
        ▼
Build Circuit Graph
        │
        ▼
Generate Stuck-at Fault List
        │
        ▼
Fault Collapsing
        │
        ▼
For every remaining fault
        │
        ▼
Run PODEM
        │
        ▼
Generate Test Vector
        │
        ▼
Fault Simulation
        │
        ▼
Drop Detected Faults
        │
        ▼
Repeat until all faults processed


---

## Benchmark Circuits

The implementation has been evaluated on standard ISCAS'85 combinational benchmark circuits.

| Circuit | Inputs | Outputs | Gates |
|----------|--------|----------|-------|
| c17 | 5 | 2 | 6 |
| c432 | 36 | 7 | 160 |
| c499 | 41 | 32 | 202 |
| c880 | 60 | 26 | 383 |

---

## Results

| Circuit | Fault Coverage | Test Vectors |
|----------|---------------|--------------|
| c17 | **100%** | 7 |
| c432 | **95.38%** | 43 |
| c499 | **100%** | 63 |
| c880 | **100%** | 92 |

---

## Comparison with ATALANTA

| Circuit | PyPODEM | ATALANTA |
|----------|----------|-----------|
| c17 | 100% | 100% |
| c432 | 95.38% | 99.0% |
| c499 | 100% | 96.6% |
| c880 | 100% | 100% |

The implementation achieves full coverage on three benchmark circuits while producing fewer test vectors than ATALANTA for selected cases through efficient fault dropping.

---

## Concepts Used

- Automatic Test Pattern Generation (ATPG)
- PODEM Algorithm
- D-Calculus
- Five-Valued Logic
- Fault Activation
- Fault Propagation
- D-Frontier
- Objective Selection
- Gate-Aware Backtrace
- Fault Simulation
- Fault Collapsing
- Topological Sorting
- Recursive Backtracking

---

## Future Improvements

- FAN ATPG implementation
- Transition Delay Fault ATPG
- Bridging Fault Model
- Parallel Fault Simulation
- Multi-threaded execution
- C++/Rust implementation for higher performance
- Sequential circuit support

---

## References

- P. Goel, *An Implicit Enumeration Algorithm to Generate Tests for Combinational Logic Circuits*, IEEE Transactions on Computers, 1981.
- J. P. Roth, *Diagnosis of Automata Failures: A Calculus and a Method*, IBM Journal of Research and Development, 1966.
- Brglez & Fujiwara, *ISCAS'85 Benchmark Suite*, IEEE ISCAS, 1985.
- ATALANTA ATPG Tool (Virginia Tech)

---
