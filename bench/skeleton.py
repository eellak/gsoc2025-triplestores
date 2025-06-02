# rudimentary benchmarking framework

# Copyright (C) 2025 Alexios Zavras
# SPDX-License-Identifier: Apache-2.0


import random
import time

# basic timer implementation


class TimerError(Exception):
    pass


class Timer:
    def __init__(self):
        self.begin = None
        self.end = None
        self.duration = None

    def start(self):
        self.begin = time.perf_counter_ns

    def stop(self):
        self.end = time.perf_counter_ns
        if not self.begin:
            msg = "Timer is not running. Use .start() to start it"
            raise TimerError(msg)
        self.duration = self.end - self.begin


# query setup
ttlname = "data.py"

random.seed(2025)
persons = []
for _ in range(100):
    pid = random.randint(1000, 100_000)
    name = f"I{pid:08}"
    persons.append(name)


def qperson(name, query_proc):
    base = "http://intel.com/rdf/azavras/demofamilydata/"
    query = f"""
    SELECT ?sex ?father ?mother
    WHERE {{
        ?p :name "{name}" .
        ?p :sex ?sex .
        ?fam :child ?p .
        ?fam :husband ?fp .
        ?fp :name ?father .
        ?fam :wife ?mp .
        ?mp :name ?mother .
    }}
    """
    ret = query_proc(query, base_iri=base)
    return (ret["sex"], ret["father"], ret["mother"])


def benchmark(s, init_proc, load_proc, query_proc):
    print(f"Benchmarking {s}")
    # benchmark run
    time_all = Timer()
    time_load = Timer()
    time_query = Timer()

    time_all.start()

    init_proc()

    time_load.start()
    load_proc(ttlname)
    time_load.stop()

    time_query.start()
    for p in persons:
        res = qperson(p, query_proc)
    time_query.end()

    time_all.end()
    return time_all, time_load, time_query, res


def bench_report(s, time_all, time_load, time_query, res):
    """Prints the benchmark report."""
    print(f"Benchmark Report: {s}")
    print("----------------")
    print(f"Last result: Person is of sex {res[0]}, father is {res[1]} mother is {res[2]}")
    print(f"Overall time: f{time_all.duration}")
    print(f"Load time: f{time_load.duration}")
    print(f"Query time: f{time_query.duration}")
