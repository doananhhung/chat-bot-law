"""
Full FAISS Index Comparison Script

Chạy: python run_full_benchmark.py

Script này sẽ:
1. Benchmark index hiện tại
2. Nếu là IVF, chạy nprobe sweep
3. In bảng so sánh
"""
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.benchmark_comparison import BenchmarkRunner
from src.config import AppConfig


def print_comparison_table(flat_result=None, ivf_result=None, sweep_results=None):
    """Print formatted comparison table."""
    print("\n" + "=" * 70)
    print("                    FAISS INDEX COMPARISON RESULTS")
    print("=" * 70)

    print("""
+======================================================================+
|                    FAISS Index Comparison Report                      |
+====================+===================+===============+=============+
| Index Type         | Avg Latency (ms)  | Recall@10     | Speedup     |
+====================+===================+===============+=============+""")

    if flat_result:
        lat = flat_result['latency']['avg_ms']
        print(f"| Flat (baseline)    | {lat:>15.2f}  | 100%          | 1.0x        |")

    if sweep_results:
        flat_lat = flat_result['latency']['avg_ms'] if flat_result else 138.22
        for r in sweep_results:
            speedup = flat_lat / r['latency_ms'] if r['latency_ms'] > 0 else 0
            print(f"| IVF nprobe={r['nprobe']:<3}     | {r['latency_ms']:>15.2f}  | {r['recall_at_10']:>5.1f}%        | {speedup:>5.1f}x      |")

    print("+====================+===================+===============+=============+")


def main():
    print("=" * 70)
    print("           FAISS INDEX FULL COMPARISON BENCHMARK")
    print("=" * 70)

    runner = BenchmarkRunner()

    # 1. Benchmark current index
    print("\n[1/2] Benchmarking current index...")
    current_result = runner.benchmark_current_index()

    # 2. If IVF, run nprobe sweep
    sweep_results = None
    if current_result['index_info']['index_type'] == 'ivf':
        print("\n[2/2] Running nprobe sweep...")
        sweep_data = runner.benchmark_nprobe_sweep([1, 2, 4, 8, 16, 32, 64])
        sweep_results = sweep_data.get('sweep_results', [])

        # Print comparison table
        print_comparison_table(
            flat_result=None,  # We don't have flat result in this run
            sweep_results=sweep_results
        )
    else:
        print("\n[2/2] Current index is Flat. To compare with IVF:")
        print("      1. Run: python rebuild_ivf_index.py")
        print("      2. Run: python run_full_benchmark.py")

    print("\n" + "=" * 70)
    print("Benchmark Complete!")
    print("=" * 70)

    # Print recommendations
    print("\nRECOMMENDATIONS:")
    if current_result['index_info']['index_type'] == 'ivf' and sweep_results:
        # Find best config (highest recall with reasonable speedup)
        for r in sweep_results:
            if r['recall_at_10'] >= 95:
                print(f"   -> Use nprobe={r['nprobe']} for Recall {r['recall_at_10']:.1f}%")
                print(f"   -> Update .env: IVF_NPROBE={r['nprobe']}")
                break
    else:
        n_vectors = current_result['index_info']['ntotal']
        if n_vectors < 5000:
            print(f"   -> Small dataset ({n_vectors} vectors), Flat index is good enough")
            print(f"   -> IVF will be more effective with 10,000+ vectors")
        else:
            print(f"   -> Large dataset ({n_vectors} vectors), should use IVF")
            print(f"   -> Run: python rebuild_ivf_index.py")


if __name__ == "__main__":
    main()
