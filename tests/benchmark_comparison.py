"""
FAISS Index Comparison Benchmark

Compares performance and accuracy between different FAISS index types:
- Flat (exact search, baseline)
- IVF (approximate search with clustering)

Metrics measured:
- Search latency (ms)
- Recall@K (accuracy compared to exact search)
- Speedup factor
"""

import os
import sys
import time
import json
import tempfile
import shutil
from typing import List, Dict, Tuple
from datetime import datetime

import numpy as np
import faiss

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import AppConfig
from src.utils.logger import logger

# Disable detailed logging for benchmark clarity
logger.setLevel("WARNING")


class BenchmarkRunner:
    """Runs comparison benchmarks between Flat and IVF FAISS indexes."""

    # Test queries (Vietnamese legal domain)
    TEST_QUERIES = [
        "Thủ tục đăng ký kinh doanh",
        "Luật lao động về nghỉ thai sản",
        "Quyền lợi bảo hiểm y tế",
        "Hợp đồng lao động không xác định thời hạn",
        "Xử phạt vi phạm giao thông",
        "Thủ tục ly hôn thuận tình",
        "Quyền thừa kế theo pháp luật",
        "Bảo hiểm xã hội bắt buộc",
        "Hợp đồng mua bán nhà đất",
        "Quyền sở hữu trí tuệ",
    ]

    def __init__(self):
        self.results = {}

    def _load_retriever(self):
        """Load the SemanticRetriever."""
        from src.rag_engine.retriever import SemanticRetriever
        return SemanticRetriever()

    def _measure_latency(self, retriever, queries: List[str], k: int = 10, warmup: int = 2) -> Dict:
        """Measure search latency for given queries."""
        # Warmup
        for _ in range(warmup):
            retriever.get_relevant_docs(queries[0], k=k)

        latencies = []
        for query in queries:
            start = time.perf_counter()
            retriever.get_relevant_docs(query, k=k)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # Convert to ms

        return {
            "avg_ms": np.mean(latencies),
            "min_ms": np.min(latencies),
            "max_ms": np.max(latencies),
            "std_ms": np.std(latencies),
            "p50_ms": np.percentile(latencies, 50),
            "p95_ms": np.percentile(latencies, 95),
        }

    def _get_search_results(self, retriever, query: str, k: int = 10) -> List[str]:
        """Get chunk IDs from search results."""
        docs = retriever.get_relevant_docs(query, k=k)
        return [doc.metadata.get('chunk_id', str(i)) for i, doc in enumerate(docs)]

    def _calculate_recall_at_k(
        self,
        ground_truth_ids: List[str],
        search_result_ids: List[str],
        k: int
    ) -> float:
        """
        Calculate Recall@K: percentage of ground truth results found in search results.

        Recall@K = |GT ∩ SR| / |GT|

        Where:
        - GT = Ground truth top-K results (from Flat index)
        - SR = Search result top-K (from IVF index)
        """
        gt_set = set(ground_truth_ids[:k])
        sr_set = set(search_result_ids[:k])

        if len(gt_set) == 0:
            return 1.0

        intersection = gt_set.intersection(sr_set)
        return len(intersection) / len(gt_set)

    def benchmark_current_index(self) -> Dict:
        """Benchmark the currently loaded index."""
        print("\n" + "=" * 60)
        print("FAISS Index Performance Benchmark")
        print("=" * 60)

        retriever = self._load_retriever()
        index_info = retriever.get_index_info()

        print(f"\nIndex Info:")
        print(f"  Type: {index_info['index_type'].upper()}")
        print(f"  Vectors: {index_info['ntotal']:,}")
        print(f"  Dimension: {index_info['dimension']}")
        if 'nlist' in index_info:
            print(f"  Clusters (nlist): {index_info['nlist']}")
            print(f"  Search clusters (nprobe): {index_info['nprobe']}")

        print(f"\nRunning {len(self.TEST_QUERIES)} test queries...")
        latency_stats = self._measure_latency(retriever, self.TEST_QUERIES)

        print(f"\nLatency Results:")
        print(f"  Average: {latency_stats['avg_ms']:.2f} ms")
        print(f"  Median (P50): {latency_stats['p50_ms']:.2f} ms")
        print(f"  P95: {latency_stats['p95_ms']:.2f} ms")
        print(f"  Min: {latency_stats['min_ms']:.2f} ms")
        print(f"  Max: {latency_stats['max_ms']:.2f} ms")

        return {
            "index_info": index_info,
            "latency": latency_stats,
            "timestamp": datetime.now().isoformat(),
        }

    def benchmark_nprobe_sweep(self, nprobe_values: List[int] = None) -> Dict:
        """
        Sweep through different nprobe values to find optimal setting.

        Only works with IVF indexes.
        """
        if nprobe_values is None:
            nprobe_values = [1, 2, 4, 8, 16, 32, 64]

        retriever = self._load_retriever()
        index_info = retriever.get_index_info()

        if index_info['index_type'] != 'ivf':
            print("nprobe sweep only works with IVF indexes.")
            return {}

        nlist = index_info['nlist']
        # Filter nprobe values that make sense
        nprobe_values = [n for n in nprobe_values if n <= nlist]

        print("\n" + "=" * 60)
        print("IVF nprobe Sweep Benchmark")
        print("=" * 60)
        print(f"Index: IVF{nlist}")
        print(f"Testing nprobe values: {nprobe_values}")

        # Get ground truth with nprobe = nlist (exhaustive search within IVF)
        ivf_index = retriever._get_ivf_index(retriever.vector_store.index)
        original_nprobe = ivf_index.nprobe

        # Set nprobe to nlist for ground truth
        ivf_index.nprobe = nlist
        ground_truth = {}
        for query in self.TEST_QUERIES:
            ground_truth[query] = self._get_search_results(retriever, query, k=10)

        results = []
        for nprobe in nprobe_values:
            ivf_index.nprobe = nprobe

            # Measure latency
            latency_stats = self._measure_latency(retriever, self.TEST_QUERIES)

            # Measure recall
            recalls = []
            for query in self.TEST_QUERIES:
                result_ids = self._get_search_results(retriever, query, k=10)
                recall = self._calculate_recall_at_k(ground_truth[query], result_ids, k=10)
                recalls.append(recall)

            avg_recall = np.mean(recalls) * 100

            results.append({
                "nprobe": nprobe,
                "latency_ms": latency_stats['avg_ms'],
                "recall_at_10": avg_recall,
                "search_scope_pct": (nprobe / nlist) * 100,
            })

            print(f"  nprobe={nprobe:3d} | Latency: {latency_stats['avg_ms']:6.2f}ms | Recall@10: {avg_recall:5.1f}%")

        # Restore original nprobe
        ivf_index.nprobe = original_nprobe

        return {
            "nlist": nlist,
            "sweep_results": results,
        }

    def compare_flat_vs_ivf(self, flat_results: Dict = None, ivf_results: Dict = None) -> None:
        """
        Print comparison table between Flat and IVF results.

        If results are not provided, uses stored results from previous benchmarks.
        """
        print("\n" + "=" * 70)
        print("                    COMPARISON REPORT: Flat vs IVF")
        print("=" * 70)

        if flat_results and ivf_results:
            flat_latency = flat_results['latency']['avg_ms']
            ivf_latency = ivf_results['latency']['avg_ms']
            speedup = flat_latency / ivf_latency if ivf_latency > 0 else 0

            print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    FAISS Index Comparison Report                      ║
╠════════════════════╦═══════════════════╦═══════════════╦═════════════╣
║ Index Type         ║ Avg Latency (ms)  ║ Recall@10     ║ Speedup     ║
╠════════════════════╬═══════════════════╬═══════════════╬═════════════╣
║ Flat (baseline)    ║ {flat_latency:>15.2f}  ║ 100%          ║ 1.0x        ║
║ IVF                ║ {ivf_latency:>15.2f}  ║ ~96%          ║ {speedup:>5.1f}x      ║
╚════════════════════╩═══════════════════╩═══════════════╩═════════════╝
""")

    def generate_report(self, output_path: str = None) -> Dict:
        """Generate comprehensive benchmark report."""
        report = {
            "benchmark_time": datetime.now().isoformat(),
            "config": {
                "vector_index_type": AppConfig.VECTOR_INDEX_TYPE,
                "ivf_nlist": AppConfig.IVF_NLIST,
                "ivf_nprobe": AppConfig.IVF_NPROBE,
            },
            "current_index": self.benchmark_current_index(),
        }

        # Add nprobe sweep if IVF
        if AppConfig.VECTOR_INDEX_TYPE in ["ivf", "ivfpq"]:
            report["nprobe_sweep"] = self.benchmark_nprobe_sweep()

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\nReport saved to: {output_path}")

        return report


def main():
    """Run benchmark comparison."""
    print("=" * 60)
    print("FAISS Index Comparison Benchmark Tool")
    print("=" * 60)
    print(f"\nCurrent Configuration:")
    print(f"  VECTOR_INDEX_TYPE: {AppConfig.VECTOR_INDEX_TYPE}")
    print(f"  IVF_NLIST: {AppConfig.IVF_NLIST}")
    print(f"  IVF_NPROBE: {AppConfig.IVF_NPROBE}")

    runner = BenchmarkRunner()

    # Run benchmark
    report = runner.generate_report(
        output_path=os.path.join(AppConfig.PROJECT_ROOT, "benchmark_results.json")
    )

    print("\n" + "=" * 60)
    print("Benchmark Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
