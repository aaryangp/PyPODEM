import os
import subprocess
import matplotlib.pyplot as plt

class SCLTestingFramework:
    def __init__(self, base_dir="~/SCL_ATPG_Project"):
        self.base_dir = os.path.expanduser(base_dir)
        self.bench_dir = os.path.join(self.base_dir, "benchmarks")
        self.report_dir = os.path.join(self.base_dir, "reports")
        self.atalanta_path = os.path.expanduser("~/Atalanta/atalanta")
        
        os.makedirs(self.report_dir, exist_ok=True)
        self.plot_data = {'circuits': [], 'stuck_at': []}

    def run_atalanta_backend(self, circuit_name):
        """Runs Atalanta and parses coverage by searching for the structural colon separator."""
        bench_file = os.path.join(self.bench_dir, f"{circuit_name}.bench")
        output_test = os.path.join(self.report_dir, f"{circuit_name}.test")
        if not os.path.exists(bench_file):
            return None
        
        cmd = [self.atalanta_path, "-t", output_test, bench_file]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            full_output = result.stdout + "\n" + result.stderr
            
            coverage = "0.0%"
            for line in full_output.split('\n'):
                if "fault coverage" in line.lower() and ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        raw_val = parts[1].strip().split()[0].replace('%', '')
                        coverage = f"{float(raw_val):.1f}%"
                        break
            return coverage
        except subprocess.CalledProcessError:
            return None

    def parse_patterns(self, circuit_name):
        """Extracts text vectors by strictly matching lines containing index colons."""
        test_file = os.path.join(self.report_dir, f"{circuit_name}.test")
        vectors = []
        if not os.path.exists(test_file):
            return []

        with open(test_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("*") or line.startswith("#") or not line:
                    continue
                
                if ":" in line:
                    parts = line.split(":")
                    index_part = parts[0].strip()
                    data_part = parts[1].strip()
                    
                    if index_part.isdigit():
                        data_sub_parts = data_part.split()
                        if data_sub_parts:
                            vectors.append(data_sub_parts[0])
        return vectors

    def generate_analytics_plot(self):
        """Generates and saves a high-quality chart showing true pattern scaling trends."""
        plt.figure(figsize=(10, 5))
        x = range(len(self.plot_data['circuits']))
        
        plt.bar(x, self.plot_data['stuck_at'], width=0.4, label='Static Stuck-At Vectors', color='#1f77b4')
        
        plt.xlabel('ISCAS\'85 Benchmark Circuits', fontweight='bold', fontsize=11)
        plt.ylabel('Calculated Pattern Volume Count', fontweight='bold', fontsize=11)
        plt.title('SCL EFTG Unit: Test Pattern Generation Volume Scaling Analysis', fontweight='bold', fontsize=14, pad=15)
        plt.xticks(x, self.plot_data['circuits'], rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.legend(fontsize=10, loc='upper left')
        plt.tight_layout()
        
        plot_path = os.path.join(self.report_dir, "atpg_scaling_analysis.png")
        plt.savefig(plot_path, dpi=300)
        print(f"\n[+] Success! Visual analytics plot generated and saved to:\n    {plot_path}")

    def execute_suite(self):
        print("=========================================================================")
        print("    SCL EFTG UNIT: BATCH PROCESSING SYSTEM WITH COVERAGE METRICS        ")
        print("=========================================================================\n")
        
        if not os.path.exists(self.bench_dir):
            print(f"[-] Error: Benchmark directory missing at {self.bench_dir}")
            return

        circuits = [os.path.splitext(f)[0] for f in os.listdir(self.bench_dir) if f.endswith('.bench')]
        circuits.sort(key=lambda item: int(item[1:]) if item[1:].isdigit() else 0)
        
        print(f"[+] Found {len(circuits)} target circuits for evaluation.\n")
        print(f"{'Circuit':<12}{'Stuck-At Cov':<16}{'Patterns':<14}")
        print("-" * 42)

        for ckt in circuits:
            coverage_metric = self.run_atalanta_backend(ckt)
            if coverage_metric:
                vectors = self.parse_patterns(ckt)
                if vectors:
                    print(f"{ckt:<12}{coverage_metric:<16}{len(vectors):<14}")
                    
                    self.plot_data['circuits'].append(ckt)
                    self.plot_data['stuck_at'].append(len(vectors))
        
        if self.plot_data['circuits']:
            self.generate_analytics_plot()

if __name__ == "__main__":
    framework = SCLTestingFramework()
    framework.execute_suite()
