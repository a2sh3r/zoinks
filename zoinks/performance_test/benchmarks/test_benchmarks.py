import importlib.util
import sys


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


for i in range(1, 25):
    def make_benchmark(i):
        def benchmark_with(benchmark):
            mod = load_module(f"mod", f"./test_{i:02d}_with_annotations.py")
            benchmark(mod.run)

        def benchmark_without(benchmark):
            mod = load_module(f"mod", f"./test_{i:02d}_without_annotations.py")
            benchmark(mod.run)

        return benchmark_with, benchmark_without

    bench_with, bench_without = make_benchmark(i)
    globals()[f"test_test_{i:02d}_with_annotations"] = bench_with
    globals()[f"test_test_{i:02d}_without_annotations"] = bench_without