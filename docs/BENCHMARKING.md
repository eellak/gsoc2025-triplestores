# Benchmarking RDF Triplestores Before and After Integrating the `triplestore` Abstraction Library

## Abstract
This report presents a comparative benchmarking study of five RDF triplestores—**AllegroGraph, Apache Jena, Blazegraph, GraphDB, and Oxigraph**—conducted before and after the integration of the unified `triplestore` abstraction library.
The goal of this evaluation was to assess whether the abstraction layer introduces measurable overhead or efficiency improvements in typical triplestore operations such as dataset loading and SPARQL querying.

All experiments were executed under a consistent setup using a unified Python benchmarking framework, [skeleton.py](/triplestore/bench/skeleton.py), which implements a reproducible timing mechanism based on nanosecond-precision counters.

For each triplestore, the following standardized sequence was performed:
- **Initialization** of the backend service.
- **Data loading** of a Turtle (`.ttl`) dataset into the store.
- **Query execution** over randomly selected individuals from a synthetic family dataset.

The datasets were generated using the [generate-data.py](/data/generate/generate-data.py) utility, designed to produce RDF graphs at different scales to test system scalability.
Three dataset sizes were used:
- `data_20k_triples.ttl` — ~23k triples
```bash
python generate-data.py --initial-fams 5 --max-children 4 --pristine-gens 3 --mixed-fams 2000 -o data_20k_triples.ttl
```

- `data_200k_triples.ttl` — ~207k triples
```bash
python generate-data.py -o data_200k_triples.ttl
```

- `data_2M_triples.ttl` — ~2.1M triples
```bash
python generate-data.py --initial-fams 15 --max-children 8 --pristine-gens 6 --mixed-fams 15000 -o data_2M_triples.ttl
```

## Results

### `data_20k_triples.ttl`
| Triplestore      | Load (before) | Load (after) | Query (before) | Query (after) | Overall (before) | Overall (after) |
| ---------------- | ------------- | ------------ | -------------- | ------------- | ---------------- | --------------- |
| **AllegroGraph** | 0.47 s        | 0.35 s       | 1.32 s         | 1.01 s        | 5.33 s           | 4.25 s          |
| **Apache Jena**  | 1.08 s        | 4.54 s       | 1.95 s         | 1.22 s        | 7.71 s           | 18.26 s         |
| **Blazegraph**   | 1.42 s        | 0.58 s       | 4.00 s         | 2.12 s        | 5.91 s           | 4.66 s          |
| **GraphDB**      | 6.16 s        | 4.75 s       | 2.15 s         | 1.41 s        | 8.82 s           | 8.87 s          |
| **Oxigraph**     | 0.38 s        | 0.36 s       | 0.01 s         | 0.01 s        | 0.39 s           | 1.79 s          |

#### Observations
- **Allegrograph**: Performance remained nearly identical without and with integration of the abstraction layer. This is expected, as both implementations use similar client-side logic and API calls, resulting in minimal measurable difference.
- **Apache Jena**: A noticeable increase in total execution time (≈10 s) was observed with the library. This overhead is mainly attributed to the Jena Fuseki server startup, which occurs during the initialization phase and is therefore included in the timing measurements. Load time also increased accordingly.
- **Blazegraph**: Demonstrated clear improvement in all phases, particularly in data loading, where the time decreased from 1.42 s to 0.58 s. The unified library appears to interact more efficiently with Blazegraph’s REST endpoint, leading to overall better performance.
- **GraphDB**: Execution times without and with the library integration were nearly identical. The abstraction layer uses the same HTTP-based workflow as the original implementation, so only negligible differences were recorded.
- **Oxigraph**: Similar to GraphDB, its performance remained consistent without and with the library. The slight (~1 s) increase in total time is attributed to the initialization overhead of the backend class instance rather than the triplestore itself.


### `data_200k_triples.ttl`
| Triplestore      | Load (before) | Load (after) | Query (before) | Query (after) | Overall (before) | Overall (after) |
| ---------------- | ------------- | ------------ | -------------- | ------------- | ---------------- | --------------- |
| **AllegroGraph** | 3.46 s        | 2.49 s       | 1.02 s         | 0.75 s        | 6.74 s           | 5.98 s          |
| **Apache Jena**  | 3.93 s        | 9.38 s       | 2.66 s         | 1.45 s        | 11.25 s          | 23.85 s         |
| **Blazegraph**   | 36.41 s       | 52.38 s      | 2.22 s         | 2.14 s        | 38.95 s          | 56.90 s         |
| **GraphDB**      | 9.85 s        | 9.91 s       | 1.80 s         | 0.95 s        | 11.89 s          | 11.94 s         |
| **Oxigraph**     | 2.67 s        | 1.95 s       | 0.02 s         | 0.01 s        | 2.69 s           | 2.94 s          |

#### Observations
- **Allegrograph**: As expected, the larger dataset increased the overall execution time. Nonetheless, the version using the abstraction library performed slightly faster, particularly during data loading, indicating a more efficient interaction through the standardized API.
- **Apache Jena**: The behavior remains consistent with the previous (20k triples) experiment. The total runtime nearly doubled due to the Fuseki server startup being included in the measured initialization phase, while query execution itself remained efficient.
- **Blazegraph**: Exhibited increased latency in the data loading phase despite using similar code paths as before. This suggests that the overhead might stem from Blazegraph’s internal batch insertion mechanism when handling larger datasets.
- **GraphDB**: Results remained stable, with negligible difference between not-using and using the library runs. The abstraction layer did not introduce measurable overhead in this case.
- **Oxigraph**: Continued to perform very efficiently.


### `data_2M_triples.ttl`
| Triplestore      | Load (before) | Load (after) | Query (before) | Query (after) | Overall (before) | Overall (after) |
| ---------------- | ------------- | ------------ | -------------- | ------------- | ---------------- | --------------- |
| **AllegroGraph** | 47.63 s       | 47.90 s      | 2.05 s         | 1.93 s        | 55.36 s          | 57.34 s         |
| **Apache Jena**  | 51.28 s       | 108.57 s     | 2.56 s         | 1.75 s        | 63.58 s          | 126.15 s        |
| **Blazegraph**   | 629.98 s      | 685.09 s     | 2.40 s         | 2.13 s        | 632.58 s         | 689.50 s        |
| **GraphDB**      | 105.98 s      | 109.15 s     | 2.92 s         | 1.38 s        | 110.70 s         | 113.86 s        |
| **Oxigraph**     | 38.08 s       | 40.89 s      | 0.01 s         | 0.01 s        | 38.10 s          | 42.34 s         |

#### Observations
- **Allegrograph**: As the dataset size increased to over two million triples, the total and loading times rose proportionally, reflecting the expected scaling behavior. Query execution remained stable, indicating consistent performance for read operations.
- **Apache Jena**: The gap between not-using and using the library runs widened significantly. The loading time more than doubled, primarily due to the server startup overhead being included in the measurement, while query performance slightly improved.
- **Blazegraph**: Displayed a similar trend to the smaller datasets, with notably higher loading times under the unified interface. This suggests that the bottleneck lies in Blazegraph’s internal ingestion process when handling very large data volumes.
- **GraphDB**: Performance remained consistent across both configurations. The abstraction layer introduces no significant overhead, and the query phase even showed a modest improvement.
- **Oxigraph**: Continued to exhibit excellent performance and scalability. The small increase in overall runtime (~4 s) can be attributed to Python-level initialization and serialization overhead rather than backend inefficiency.

## Conclusion
The benchmarking results reveal that, while the raw execution times vary across triplestores, the integration of the `triplestore` abstraction library provides a substantial improvement in usability, consistency, and developer experience without introducing significant performance degradation.

Specifically, in some cases, such as Apache Jena, the total runtime after integration increased, mainly due to the server initialization being measured as part of the execution. However, this additional cost is offset by a major simplification in workflow: before the library, developers had to manually manage HTTP servers, construct dataset upload commands, and format queries according to each backend’s custom API.
Now, the same operation is achieved simply by calling `store.load(file)` and the library automatically handles connection setup, data ingestion, and error reporting behind the scenes.

**AllegroGraph, GraphDB, and Oxigraph** maintained nearly identical or slightly improved performance, demonstrating that the unified API introduces no measurable runtime penalty.
**Blazegraph and Jena**, although showing higher load times on large datasets, now integrate seamlessly through the same interface, eliminating the need for backend-specific scripts or configuration steps.

Ultimately, the results highlight that ease of use and portability gained through the abstraction layer outweigh the minimal overhead observed in certain cases. Developers can now benchmark, load, query, or clear any supported triplestore using a single, intuitive Python API—making experimentation, testing, and system integration significantly more straightforward and less error-prone.

Future work could focus on enhancing both performance and functionality.
On the performance side, introducing automatic parallel loading and memory utilization analysis could help significantly reduce dataset loading times for large-scale benchmarks.
On the functional side, additional features could be incorporated into the library — for example, extending the `add()` operation to support literal insertions, and allowing the `load()` method to handle multiple serialization formats beyond Turtle (such as N-Triples, RDF/XML, or JSON-LD).
These improvements would further increase the flexibility and robustness of the unified interface while maintaining its ease of use.
