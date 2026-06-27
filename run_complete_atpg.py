
import copy
import sys
import os
import csv
from collections import defaultdict
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# 1.  LOGIC VALUES
# ─────────────────────────────────────────────────────────────────────────────

X = 'X'   # Unknown
D = 'D'   # fault-free=0, faulty=1   (stuck-at-0 fault activated)
B = 'B'   # D-bar: fault-free=1, faulty=0 (stuck-at-1 fault activated)

# Good-circuit value of D/B
GOOD = {0: 0, 1: 1, X: X, D: 0, B: 1}
# Faulty-circuit value of D/B
FAULT_VAL = {0: 0, 1: 1, X: X, D: 1, B: 0}

# ─── NAND ────────────────────────────────────────────────────────────────────
def nand_table(a, b):
    tbl = {
        (0,0):1,(0,1):1,(1,0):1,(1,1):0,
        (0,X):1,(X,0):1,(1,X):X,(X,1):X,(X,X):X,
        (0,D):1,(D,0):1,(0,B):1,(B,0):1,
        (1,D):B,(D,1):B,(1,B):D,(B,1):D,
        (D,D):B,(B,B):D,(D,B):1,(B,D):1,
        (X,D):X,(D,X):X,(X,B):X,(B,X):X,
    }
    return tbl.get((a,b), tbl.get((b,a), X))

def gate_nand(inputs):
    result = inputs[0]
    for v in inputs[1:]:
        result = nand_table(result, v)
    return result

# ─── AND ─────────────────────────────────────────────────────────────────────
def and_table(a, b):
    tbl = {
        (0,0):0,(0,1):0,(1,0):0,(1,1):1,
        (0,X):0,(X,0):0,(1,X):X,(X,1):X,(X,X):X,
        (0,D):0,(D,0):0,(0,B):0,(B,0):0,
        (1,D):D,(D,1):D,(1,B):B,(B,1):B,
        (D,D):D,(B,B):B,(D,B):0,(B,D):0,
        (X,D):X,(D,X):X,(X,B):X,(B,X):X,
    }
    return tbl.get((a,b), tbl.get((b,a), X))

def gate_and(inputs):
    result = inputs[0]
    for v in inputs[1:]:
        result = gate_and_logic(result, v)
    return result

def gate_and_logic(a, b):
    return and_table(a, b)

# ─── OR ──────────────────────────────────────────────────────────────────────
def or_table(a, b):
    tbl = {
        (0,0):0,(0,1):1,(1,0):1,(1,1):1,
        (0,X):X,(X,0):X,(1,X):1,(X,1):1,(X,X):X,
        (0,D):D,(D,0):D,(0,B):B,(B,0):B,
        (1,D):1,(D,1):1,(1,B):1,(B,1):1,
        (D,D):D,(B,B):B,(D,B):1,(B,D):1,
        (X,D):X,(D,X):X,(X,B):X,(B,X):X,
    }
    return tbl.get((a,b), tbl.get((b,a), X))

def gate_or(inputs):
    result = inputs[0]
    for v in inputs[1:]:
        result = or_table(result, v)
    return result

# ─── NOR ─────────────────────────────────────────────────────────────────────
def gate_nor(inputs):
    v = gate_or(inputs)
    return {0:1,1:0,X:X,D:B,B:D}[v]

# ─── NOT ─────────────────────────────────────────────────────────────────────
def gate_not(inputs):
    return {0:1,1:0,X:X,D:B,B:D}[inputs[0]]

# ─── XOR ─────────────────────────────────────────────────────────────────────
def xor_table(a, b):
    tbl = {
        (0,0):0,(0,1):1,(1,0):1,(1,1):0,
        (0,X):X,(X,0):X,(1,X):X,(X,1):X,(X,X):X,
        (0,D):D,(D,0):D,(0,B):B,(B,0):B,
        (1,D):B,(D,1):B,(1,B):D,(B,1):D,
        (D,D):0,(B,B):0,(D,B):1,(B,D):1,
        (X,D):X,(D,X):X,(X,B):X,(B,X):X,
    }
    return tbl.get((a,b), tbl.get((b,a), X))

def gate_xor(inputs):
    result = inputs[0]
    for v in inputs[1:]:
        result = xor_table(result, v)
    return result

GATE_FN = {
    'NAND': gate_nand,
    'AND':  gate_and,
    'OR':   gate_or,
    'NOR':  gate_nor,
    'NOT':  gate_not,
    'XOR':  gate_xor,
    'BUFF': lambda i: i[0],
}

# ─────────────────────────────────────────────────────────────────────────────
# 2.  BENCH FILE PARSER
# ─────────────────────────────────────────────────────────────────────────────

class Circuit:
    def __init__(self, name):
        self.name   = name
        self.inputs = []        # list of net names (str)
        self.outputs= []
        self.gates  = {}        # net -> {'type': str, 'inputs': [net,...]}
        self.nets   = set()     # all net names
        self.fanout = defaultdict(list)   # net -> [nets that use it as input]
        self.topo   = []        # topological order of gate outputs

    def add_gate(self, out, gtype, ins):
        self.gates[out] = {'type': gtype, 'inputs': ins}
        for i in ins:
            self.fanout[i].append(out)
        self.nets.update([out] + ins)

    def build_topo(self):
        """Kahn's algorithm topological sort of gates."""
        in_degree = defaultdict(int)
        for out, g in self.gates.items():
            for inp in g['inputs']:
                if inp in self.gates:
                    in_degree[out] += 1
        queue = [n for n in self.gates if in_degree[n] == 0]
        order = []
        while queue:
            n = queue.pop(0)
            order.append(n)
            for succ in self.fanout.get(n, []):
                if succ in self.gates:
                    in_degree[succ] -= 1
                    if in_degree[succ] == 0:
                        queue.append(succ)
        self.topo = order

    @property
    def all_nets(self):
        return list(self.inputs) + self.topo


def parse_bench(filepath, name):
    circ = Circuit(name)
    with open(filepath) as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('INPUT('):
                net = line[6:-1].strip()
                circ.inputs.append(net)
                circ.nets.add(net)
            elif line.startswith('OUTPUT('):
                net = line[7:-1].strip()
                circ.outputs.append(net)
            elif '=' in line:
                out, rhs = line.split('=', 1)
                out  = out.strip()
                rhs  = rhs.strip()
                paren= rhs.index('(')
                gtype= rhs[:paren].strip().upper()
                ins  = [x.strip() for x in rhs[paren+1:-1].split(',')]
                circ.add_gate(out, gtype, ins)
    circ.build_topo()
    return circ

# ─────────────────────────────────────────────────────────────────────────────
# 3.  5-VALUED SIMULATOR (WITH DYNAMIC FAULT INJECTION FIX)
# ─────────────────────────────────────────────────────────────────────────────

def simulate(circ, assignment, fault=None):
    """
    assignment: dict net->value (0/1/X/D/B) for PIs and any pre-set nets.
    fault: tuple (fault_net, fault_sa) or None
    Returns dict of all net values after full forward simulation with fault token management.
    """
    vals = {n: X for n in circ.nets}
    vals.update(assignment)
    
    # Check if the fault target is located directly on a primary input
    if fault:
        fnet, fsa = fault
        if fnet in circ.inputs and vals[fnet] != X:
            if vals[fnet] == 1 - fsa:
                vals[fnet] = B if fsa == 1 else D
            else:
                vals[fnet] = fsa

    # Forward topological propagation
    for out in circ.topo:
        g = circ.gates[out]
        in_vals = [vals.get(i, X) for i in g['inputs']]
        val = GATE_FN[g['type']](in_vals)
        
        # Intercept calculation at fault site to assert fault tokens
        if fault and out == fault[0]:
            if val == 1 - fault[1]:
                val = B if fault[1] == 1 else D
            elif val == fault[1]:
                val = fault[1]
                
        vals[out] = val
    return vals

def simulate_incremental(circ, vals, changed_nets, fault=None):
    """Re-simulate forward cone restricted to modifications."""
    queue = list(changed_nets)
    visited = set(changed_nets)
    while queue:
        net = queue.pop(0)
        for succ in circ.fanout.get(net, []):
            if succ not in visited:
                visited.add(succ)
                queue.append(succ)
    for out in circ.topo:
        if out in visited:
            g = circ.gates[out]
            in_vals = [vals.get(i, X) for i in g['inputs']]
            val = GATE_FN[g['type']](in_vals)
            if fault and out == fault[0]:
                if val == 1 - fault[1]:
                    val = B if fault[1] == 1 else D
                elif val == fault[1]:
                    val = fault[1]
            vals[out] = val

# ─────────────────────────────────────────────────────────────────────────────
# 4.  FAULT LIST GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def generate_faults(circ):
    faults = []
    for net in circ.nets:
        faults.append((net, 0))   # stuck-at-0
        faults.append((net, 1))   # stuck-at-1
    return faults

def fault_collapsing(circ, faults):
    collapsed = set()
    wiped_faults = set()
    
    for out, g in circ.gates.items():
        gtype = g['type']
        
        # 1. AND/NAND Gates
        if gtype in ('AND', 'NAND'):
            for inp in g['inputs']:
                wiped_faults.add((inp, 0)) # Equivalence: Wipe input SA0s
            if gtype == 'AND':
                wiped_faults.add((out, 1)) # Dominance: Wipe output SA1
            else:
                wiped_faults.add((out, 0)) # Dominance: Wipe output SA0 for NAND
                
        # 2. OR/NOR Gates
        elif gtype in ('OR', 'NOR'):
            for inp in g['inputs']:
                wiped_faults.add((inp, 1)) # Equivalence: Wipe input SA1s
            if gtype == 'OR':
                wiped_faults.add((out, 0)) # Dominance: Wipe output SA0
            else:
                wiped_faults.add((out, 1)) # Dominance: Wipe output SA1 for NOR
                
        # 3. NOT Gates
        elif gtype == 'NOT':
            wiped_faults.add((g['inputs'][0], 0))
            wiped_faults.add((g['inputs'][0], 1))

    # Assemble the final pristine list
    for f in faults:
        if f not in wiped_faults:
            collapsed.add(f)
            
    return list(collapsed)
# ─────────────────────────────────────────────────────────────────────────────
# 5.  D-FRONTIER & PODEM OBJECTIVE
# ─────────────────────────────────────────────────────────────────────────────

def d_frontier(circ, vals):
    frontier = []
    for out in circ.topo:
        if vals.get(out, X) != X:
            continue
        g = circ.gates[out]
        in_vals = [vals.get(i, X) for i in g['inputs']]
        if any(v in (D, B) for v in in_vals):
            frontier.append(out)
    return frontier

def has_d_at_output(circ, vals):
    return any(vals.get(o, X) in (D, B) for o in circ.outputs)

# ─────────────────────────────────────────────────────────────────────────────
# 6.  BACKTRACE
# ─────────────────────────────────────────────────────────────────────────────

CONTROLLING = {'NAND':0,'AND':0,'OR':1,'NOR':1,'NOT':None,'XOR':None,'BUFF':None}
INVERSION   = {'NAND':1,'AND':0,'OR':0,'NOR':1,'NOT':1,'XOR':0,'BUFF':0}

def backtrace(circ, objective_net, objective_val, vals):
    net = objective_net
    val = objective_val
    visited = set()

    while net not in circ.inputs:
        if net in visited or net not in circ.gates:
            break
        visited.add(net)

        g = circ.gates[net]
        gtype = g['type']
        ctrl  = CONTROLLING[gtype]
        inv   = INVERSION[gtype]

        free_inputs = [i for i in g['inputs'] if vals.get(i, X) == X]
        if not free_inputs:
            free_inputs = g['inputs']

        if gtype in ('NOT', 'BUFF'):
            val = (1 - val) if gtype == 'NOT' else val
            net = g['inputs'][0]
            continue

        if gtype == 'XOR':
            net = free_inputs[0]
            continue

        if val == ctrl:
            net = free_inputs[0]
            val = ctrl
        else:
            net = free_inputs[0]
            val = 1 - ctrl

    return (net, val)

# ─────────────────────────────────────────────────────────────────────────────
# 7.  PODEM CORE
# ─────────────────────────────────────────────────────────────────────────────

MAX_BACKTRACKS = 500

def podem(circ, fault_net, fault_sa):
    pi_assign = {pi: X for pi in circ.inputs}
    backtracks = [0]

    def get_objective(vals):
        fault_val_in_circuit = vals.get(fault_net, X)
        if fault_val_in_circuit == X:
            return (fault_net, 1 - fault_sa)

        df = d_frontier(circ, vals)
        if not df:
            return None
            
        gate_out = df[0]
        g = circ.gates[gate_out]
        ctrl = CONTROLLING[g['type']]

        in_vals = [vals.get(i, X) for i in g['inputs']]
        for idx, iv in enumerate(in_vals):
            if iv == X:
                non_ctrl = 1 - ctrl if ctrl is not None else 1
                return (g['inputs'][idx], non_ctrl)
        return None

    def podem_recursive(pi_assign):
        if backtracks[0] >= MAX_BACKTRACKS:
            return None

        # Pass fault metadata directly to correct the simulation tracking pipeline
        vals = simulate(circ, pi_assign, fault=(fault_net, fault_sa))

        if has_d_at_output(circ, vals):
            return pi_assign

        fault_v = vals.get(fault_net, X)
        if fault_v not in (X, D, B):
            return None

        if fault_v in (D, B):
            df = d_frontier(circ, vals)
            if not df:
                return None

        obj = get_objective(vals)
        if obj is None:
            return None

        obj_net, obj_val = obj
        pi, pi_val = backtrace(circ, obj_net, obj_val, vals)

        if pi not in circ.inputs:
            return None

        for try_val in [pi_val, 1 - pi_val]:
            new_assign = dict(pi_assign)
            new_assign[pi] = try_val
            result = podem_recursive(new_assign)
            if result is not None:
                return result
            backtracks[0] += 1

        return None

    return podem_recursive(pi_assign)

# ─────────────────────────────────────────────────────────────────────────────
# 8.  FAULT SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

def fault_simulate_vector(circ, pi_vec, fault_list):
    ff_vals = simulate(circ, pi_vec)
    detected = set()
    for (fnet, fsa) in fault_list:
        fv = copy.copy(ff_vals)
        fv[fnet] = fsa
        simulate_incremental(circ, fv, {fnet}, fault=(fnet, fsa))

        for o in circ.outputs:
            if fv[o] != ff_vals.get(o) and fv[o] in (D, B, 0, 1) and ff_vals[o] in (0, 1):
                detected.add((fnet, fsa))
                break
    return detected

# ─────────────────────────────────────────────────────────────────────────────
# 9.  MAIN ATPG LOOP
# ─────────────────────────────────────────────────────────────────────────────

def run_podem_atpg(circ, verbose=False):
    all_faults  = generate_faults(circ)
    total_raw   = len(all_faults)
    collapsed   = fault_collapsing(circ, all_faults)
    total_col   = len(collapsed)

    remaining   = list(collapsed)
    remaining.sort(key=lambda x: (str(x[0]), int(x[1])))
    test_vectors= []
    detected_by_podem = set()
    aborted     = set()

    print(f"\n{'='*65}")
    print(f"  Circuit : {circ.name.upper()}")
    print(f"  Inputs  : {len(circ.inputs)}   Outputs : {len(circ.outputs)}")
    print(f"  Gates   : {len(circ.gates)}")
    print(f"  Raw faults (SA0+SA1 on every net) : {total_raw}")
    print(f"  After fault collapsing             : {total_col}")
    print(f"{'='*65}")

    fault_idx = 0
    for (fnet, fsa) in remaining:
        fault_idx += 1
        if (fnet, fsa) in detected_by_podem:
            continue

        if verbose:
            print(f"  [{fault_idx}/{total_col}] Testing {fnet} SA{fsa} ...", end=' ', flush=True)

        result = podem(circ, fnet, fsa)

        if result is None:
            aborted.add((fnet, fsa))
            if verbose:
                print("UNDETECTABLE/TIMEOUT")
            continue

        vec = {pi: (0 if result[pi] == X else result[pi]) for pi in circ.inputs}
        still_remaining = [f for f in remaining if f not in detected_by_podem]
        new_detected = fault_simulate_vector(circ, vec, still_remaining)
        detected_by_podem.update(new_detected)

        test_vectors.append(vec)
        if verbose:
            print(f"DETECTED  → vector #{len(test_vectors)}  (drops {len(new_detected)} faults)")

    detected_count   = len(detected_by_podem)
    undetected_count = len(aborted)
    coverage_pct      = 100.0 * detected_count / total_col if total_col else 0

    return test_vectors, {
        'circuit': circ.name, 'inputs': len(circ.inputs), 'outputs': len(circ.outputs),
        'gates': len(circ.gates), 'raw_faults': total_raw, 'collapsed_faults': total_col,
        'detected': detected_count, 'undetected': undetected_count, 'test_vectors': test_vectors,
        'num_vectors': len(test_vectors), 'fault_coverage_pct': coverage_pct,
    }

def print_results(results, circ):
    print(f"\n{'─'*65}\n  RESULTS — {results['circuit'].upper()}\n{'─'*65}")
    print(f"  Collapsed faults      : {results['collapsed_faults']}")
    print(f"  Detected faults       : {results['detected']}")
    print(f"  Undetectable/Timeout  : {results['undetected']}")
    print(f"  Fault Coverage        : {results['fault_coverage_pct']:.2f}%")
    print(f"  Test Vectors Generated: {results['num_vectors']}\n")

def export_csv(all_results, circuits_map, filepath):
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['=== PODEM ATPG — Summary Results ==='])
        writer.writerow([])
        writer.writerow(['Circuit','Inputs','Outputs','Gates','Raw Faults','Collapsed Faults','Detected','Undetected','Fault Coverage (%)','# Vectors'])
        for r in all_results:
            writer.writerow([r['circuit'], r['inputs'], r['outputs'], r['gates'], r['raw_faults'], r['collapsed_faults'], r['detected'], r['undetected'], f"{r['fault_coverage_pct']:.2f}", r['num_vectors']])
    print(f"  ✓ Metrics safely exported to CSV file → {filepath}")

# ─────────────────────────────────────────────────────────────────────────────
# 10. RECONFIGURED WORKSPACE ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # Clean relative layout matching Linux project structures
    BENCH_FILES = {
        'c17' : '../benchmarks/c17.bench',
        'c432' : '../benchmarks/c432.bench',
        'c499' : '../benchmarks/c499.bench',
        'c880' : '../benchmarks/c880.bench',
    }

    circuits_map = {}
    for name, path in BENCH_FILES.items():
        if os.path.exists(path):
            circuits_map[name] = parse_bench(path, name)
        else:
            print(f"WARNING: File route '{path}' was missing. Skipping {name}.")

    all_results = []
    for name, circ in circuits_map.items():
        _, res = run_podem_atpg(circ, verbose=True)
        print_results(res, circ)
        all_results.append(res)

        # ─── INDENTED CORRECTLY: RUNS FOR EVERY CIRCUIT IN THE LOOP ──────────
        output_dir = "/home/aari/SCL_ATPG_Project/scripts"
        vector_filename = os.path.join(output_dir, f"{name}_generated.vec")
        
        with open(vector_filename, 'w') as vec_file:
            for vec in res['test_vectors']:
                bit_string = "".join(str(vec.get(pi, 0)) for pi in circ.inputs)
                vec_file.write(f"{bit_string}\n")
        print(f"  📂 Raw patterns written cleanly to -> {vector_filename}")
        # ─────────────────────────────────────────────────────────────────────

    if all_results:
        export_csv(all_results, circuits_map, 'atpg_execution_summary.csv')
