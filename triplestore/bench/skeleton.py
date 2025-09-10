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
        self.begin = time.perf_counter_ns()

    def stop(self):
        self.end = time.perf_counter_ns()
        if not self.begin:
            msg = "Timer is not running. Use .start() to start it"
            raise TimerError(msg)
        self.duration = self.end - self.begin


# query setup
ttlname = "data.ttl"

random.seed(2025)
persons = []
for _ in range(100):
    pid = random.randint(1000, 100_000)
    name = f"I{pid:08}"
    persons.append(name)


def qperson(triplestore, name, query_proc):
    base = "http://rdf.zvr.invalid/demofamilydata/"

    if triplestore == "KùzuDB":
        name_quoted = f'"{name}"'

        queries = {
            "sex": f"""
                MATCH (t:Triple)
                WHERE t.predicate = "{base}name" AND t.object = {name_quoted}
                WITH t.subject AS person
                MATCH (s:Triple)
                WHERE s.subject = person AND s.predicate = "{base}sex"
                RETURN s.object
            """,
            "father": f"""
                MATCH (t:Triple)
                WHERE t.predicate = "{base}name" AND t.object = {name_quoted}
                WITH t.subject AS person
                MATCH (f:Triple)
                WHERE f.predicate = "{base}child" AND f.object = person
                WITH f.subject AS fam
                MATCH (h:Triple)
                WHERE h.subject = fam AND h.predicate = "{base}husband"
                WITH h.object AS dad
                MATCH (n:Triple)
                WHERE n.subject = dad AND n.predicate = "{base}name"
                RETURN n.object
            """,
            "mother": f"""
                MATCH (t:Triple)
                WHERE t.predicate = "{base}name" AND t.object = {name_quoted}
                WITH t.subject AS person
                MATCH (f:Triple)
                WHERE f.predicate = "{base}child" AND f.object = person
                WITH f.subject AS fam
                MATCH (w:Triple)
                WHERE w.subject = fam AND w.predicate = "{base}wife"
                WITH w.object AS mom
                MATCH (n:Triple)
                WHERE n.subject = mom AND n.predicate = "{base}name"
                RETURN n.object
            """
        }

        results = []
        for key in ["sex", "father", "mother"]:
            row = query_proc(queries[key], None)
            results.append(str(row[0]) if row else "?")
        return tuple(results)

    query = f"""
    PREFIX : <http://rdf.zvr.invalid/demofamilydata/>
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
    ret = query_proc(query, base)
    if ret is None:
        return ("?", "?", "?")
    return (str(ret["sex"]), str(ret["father"]), str(ret["mother"]))


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
        res = qperson(s, p, query_proc)
    time_query.stop()

    time_all.stop()
    return time_all, time_load, time_query, res


def bench_report(s, time_all, time_load, time_query, res):
    """Prints the benchmark report."""
    print(f"Benchmark Report: {s}")
    print("----------------")
    print(f"Last result: Person is of sex {res[0]}, father is {res[1]} mother is {res[2]}")
    print(f"Overall time:  {time_all.duration / 1e9:.2f} s")
    print(f"Load time: {time_load.duration / 1e9:.2f} s")
    print(f"Query time: {time_query.duration / 1e9:.2f} s")
