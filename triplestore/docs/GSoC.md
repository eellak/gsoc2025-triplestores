# GSoC 2025 Project: Exploring and Abstracting Triplestore Alternatives

## Introduction

### Project Goal
**Exploring and Abstracting Triplestore Alternatives** is a project focused on developing a Python library that provides a unified abstraction layer over multiple RDF triplestore systems. The main goal of this library is to decouple applications from the specific details of individual triplestore implementations. By doing so, developers can easily switch between different backends without modifying their application logic, ensuring flexibility, portability, and ease of experimentation across various triplestore technologies.

### Project’s Organization and Mentorship
This project was proposed and supported by **Open Technologies Alliance (GFOSS)**, a Greek non-profit organization established by major Universities and Research Institutes in Greece, with the mission to promote open-source software, open data, and open standards.

My mentor throughout the project was **Alexios Zavras**, who provided continuous guidance, technical feedback, and valuable insights that helped shape the design and implementation of the library.

### Open-Source and Semantic Web Goals
This project directly supports the open-source mission of the **Open Technologies Alliance (GFOSS)** by developing a freely available and extensible Python library that promotes openness, interoperability, and collaboration. By abstracting over multiple RDF triplestore systems, the project simplifies the use of Semantic Web technologies and encourages developers to experiment with Linked Data without being tied to a specific backend. In doing so, it contributes to the broader goal of making semantic technologies more accessible, modular, and aligned with open standards.

### Achieved vs. Initially Planned
The project followed the original plan closely, with a few improvements in structure and execution. Initially, the plan involved researching triplestore alternatives, benchmarking them, and then developing the abstraction layer. In practice, the work progressed in four clear phases:
- A detailed research and comparative analysis of multiple triplestores.
- Preliminary benchmarking to understand their performance characteristics before implementation.
- Development of the abstraction layer, successfully supporting five different triplestores.
- Unified testing and benchmarking of the implemented backends, followed by comprehensive documentation to ensure usability and future extensibility.

Overall, all major objectives were achieved as planned, resulting in a stable, well-documented, and extensible library.

## Project Overview

### Problem
Working with RDF triplestores often requires developers to adapt to the unique APIs, connection methods, and data management models of each system. This leads to vendor lock-in, repetitive code, and difficulty in migrating between different backends. The lack of a unified interface makes benchmarking, experimentation, and maintenance unnecessarily complex.

### Solution
The `triplestore` library was developed to solve this interoperability problem by introducing a unified abstraction layer. Through this layer, applications can interact with various triplestores in a consistent way—executing SPARQL queries, loading data, or clearing repositories—without changing their application code. This design enables flexibility, portability, and easier evaluation of different triplestore systems.

### Architectural Design
The library follows an object-oriented architecture.
- At its core lies an abstract base class, `Triplestore`, which defines a common interface for all backends (methods such as `connect()`, `load()`, `add()`, `delete()`, `query()`, and `clear()`).
- Each backend is implemented as a **subclass** of `Triplestore`, providing backend-specific logic for communication (HTTP endpoints, command-line tools).
- This modular structure makes the library easily **extensible**: new triplestores can be integrated simply by implementing the defined interface.

### Supported Backends
During the GSoC implementation, the library was developed to support five major triplestore systems:

- **AllegroGraph**
- **Apache Jena Fuseki (TDB2 integration)**
- **Blazegraph**
- **GraphDB**
- **Oxigraph**

Each backend was tested, documented, and validated through unified benchmarking to ensure consistency and correctness.


## Project Details
The project was divided into five main phases: **research**, **testing**, **analysis**, **development**, and **documentation**.

### Research
The first stage involved an extensive comparative study of several RDF triplestore systems to understand their architectures, data loading mechanisms, and query execution models. The triplestores examined included **Apache Jena, AllegroGraph, AnzoGraph, Blazegraph, GraphDB, KùzuDB, MillenniumDB, Oxigraph, and Stardog.**

Among these, five were successfully integrated into the library: **Apache Jena, AllegroGraph, Blazegraph, GraphDB, and Oxigraph**. Each of these supports SPARQL endpoints and allows RDF data ingestion in common formats such as Turtle (`.ttl`) and RDF/XML.

The remaining triplestores were excluded for specific technical or practical reasons:
- **KùzuDB** does not currently support SPARQL and lacks the ability to ingest RDF/Turtle data.
- **MillenniumDB** is still under active development and exhibits certain instabilities and missing REST functionality.
- **AnzoGraph** has been discontinued and is no longer publicly available.
- **Stardog** offers strong SPARQL support but is only distributed as a commercial product, making it incompatible with the open-source goals of this project.

This research phase provided a clear understanding of each system’s capabilities and limitations, which informed both the design and scope of the abstraction layer implemented later in the project.

### Testing & Analysis before the Library Development
The next phase focused on **empirical testing and performance analysis** of the triplestores prior to the actual implementation of the abstraction layer. Together with my mentor, we designed a general benchmarking script called `skeleton.py`, which served as a reusable template for evaluating each triplestore under identical conditions.

A dedicated [bench/](/bench/) directory was then created to organize and run the performance tests. These scripts measured key performance metrics such as:
- Data loading time – how efficiently each triplestore ingests RDF datasets.
- Query execution time – how quickly each system responds to representative SPARQL queries.

This testing phase provided valuable insights into the internal behavior, stability, and performance trade-offs of each backend. The results guided important architectural decisions, such as which triplestores to prioritize for integration and what kind of optimizations would be required for uniform API support.

Through this process, it became evident that MillenniumDB, while promising in design, was not yet mature enough for integration due to incomplete REST functionality. These findings helped refine the project’s scope and ensured that the subsequent development phase was based on realistic, well-evaluated choices.

### Development of the Library
#### Architecture & Core Design

The development phase focused on designing a modular and extensible architecture that could dynamically support multiple triplestore backends under a unified interface.
- Abstract Base Class `TriplestoreBackend`:

The core of the system is an abstract base class that defines the essential API methods, `load()`, `query()`, `execute()`, `add()`, `delete()`, and `clear()`, which all backend implementations must provide. This design ensures that each backend adheres to a consistent contract while allowing flexibility in how operations are executed internally. Implemented in [base.py](/triplestore/src/triplestore/base.py).

- Dynamic Backend Discovery:

The library uses Python’s entry points mechanism to dynamically discover and register available backends at runtime. The modules [registration.py](/triplestore/src/triplestore/registration.py) and [triplestore.py](/triplestore/src/triplestore/triplestore.py) handle this process, exposing helper functions such as `available_backends()` and a factory constructor `Triplestore(backend, config)`.
This allows users to instantiate any supported backend without hardcoding imports or dependencies.
- Factory Design Pattern:

The factory function `Triplestore()` validates input parameters, ensures that the requested backend is registered and importable, and returns an instance of the corresponding backend class. This encapsulation simplifies user experience while maintaining strict type and dependency checks.
- Exception Hierarchy:

A dedicated exception system was introduced to provide precise error reporting and improve debuggability. Custom exceptions such as `BackendNotFoundError` and `BackendNotInstalledError` clearly communicate configuration or installation issues to the user. Defined in [exceptions.py](/triplestore/src/triplestore/exceptions.py)

#### Backend Implementation

As it was mentioned before the library provides support for 5 triplestores **Apache Jena, AllegroGraph, Blazegraph, GraphDB and Oxigraph**.

- Apache Jena:

The Apache Jena backend required special handling due to its slow data-loading performance when operating through the default Fuseki server setup. To address this, I developed a dedicated utility module, [jena_utils.py](/triplestore/src/triplestore/backends/jena_utils.py) , which configures and launches the Fuseki server with optimized parameters. The key improvement was the introduction of a configurable environment variable, `FUSEKI_HOME`, which allows users to specify the local installation path of Fuseki. This enables the backend to start the server directly from a local setup with custom memory and configuration settings, resulting in noticeably faster data ingestion. Once these optimizations were implemented, all core functions— `load()`, `query()`, `execute()`, `add()`, `delete()`, and `clear()` —operated reliably within the unified abstraction layer.

- AllegroGraph: 

All core methods of the abstraction interface were successfully implemented for the AllegroGraph backend. One of the main challenges during this process was the platform dependency of the AllegroGraph server, which provides official support primarily for Linux environments. This meant that the backend’s local testing and automation scripts could only be executed under Linux-based systems. Another difficulty was authentication handling, since AllegroGraph requires valid user credentials for executing SPARQL queries and managing repositories. To address this, the implementation was designed to support both configuration parameters and environment variables, allowing users to securely pass authentication details without hardcoding them in scripts. Once these issues were resolved, the AllegroGraph backend achieved full functionality, supporting all required operations,data loading, querying, updates, and repository management—through the abstraction layer.

- Blazegraph:

All core methods for the Blazegraph backend were implemented successfully, and the integration process was overall straightforward thanks to its stable SPARQL endpoint and well-documented REST interface. The only challenge encountered was related to data loading performance. Specifically, the `load()` operation proved to be relatively slow, taking approximately 50 seconds to ingest a 6 MB Turtle file.
This limitation appears to be inherent to Blazegraph’s internal data ingestion mechanism rather than to the abstraction layer itself. Despite various optimization attempts, including batching and endpoint configuration adjustments, the performance bottleneck persisted. Nevertheless, the backend remains fully functional and compatible with the unified API, allowing reliable querying and dataset management within the library.

- GraphDB:

The GraphDB backend was relatively easy to integrate, as it provides a well-structured SPARQL HTTP interface and thorough documentation. All core methods—`load()`, `query()`, `execute()`, `add()`, `delete()`, and `clear()`—were successfully implemented and tested. Its REST-based design allowed smooth communication with the server, making GraphDB one of the most stable and reliable backends in the library.

- Oxigraph:

The Oxigraph backend was by far the fastest and most straightforward to integrate. Its official Python library, `pyoxigraph`, provided a fully functional and well-documented interface for interacting directly with the triplestore, significantly simplifying the implementation process.
Thanks to this library, all core methods, including data loading, querying, and dataset management, were implemented with minimal overhead and performed efficiently.

#### Testing and Validation
Throughout the development process, `pytest` was used extensively to validate the correctness and consistency of the abstraction layer. Each backend—**AllegroGraph, Blazegraph, GraphDB, Apache Jena, and Oxigraph**—was assigned its own dedicated test file under the [tests/](/triplestore/tests) directory, ensuring backend-specific coverage and reproducibility.

The tests verified all core operations defined by the abstraction layer, including:
- Adding and deleting triples
- Querying and executing SPARQL statements (`SELECT`, `ASK`, `CONSTRUCT`, `DESCRIBE`, `INSERT`, `DELETE`, `CLEAR`)
- Loading data from `.ttl` files
- Ensuring consistent state across repeated operations

Additionally, a meta-test runner (`test_all_backends.py`) was created to execute all backend tests together, simplifying unified validation of the library. These tests confirmed the reliability of the unified API, the correctness of SPARQL query handling, and the stability of data operations across all supported backends.

#### Packaging & Distribution
The library was packaged according to modern Python standards. The configuration is defined in the [pyproject.toml](/triplestore/pyproject.toml) file, ensuring a clean, reproducible, and dependency-managed installation process.

To provide flexibility, users can choose to install the unified abstraction layer either as a minimal package or with support for a specific triplestore. This is achieved through the `optional-dependencies` section in `pyproject.toml`, which defines extras such as:
- `triplestore[allegrograph]`
- `triplestore[blazegraph]`
- `triplestore[graphdb]`
- `triplestore[jena]`
- `triplestore[oxigraph]`

A combined extra, `triplestore[all]`, installs all supported backends simultaneously for developers who wish to experiment across multiple systems. This modular packaging design reduces unnecessary dependencies and aligns with Python’s best practices for extensible, backend-agnostic libraries.

### Benchmarking
To evaluate the impact of the unified abstraction layer, an extensive benchmarking study was conducted across five RDF triplestores — **AllegroGraph, Apache Jena, Blazegraph, GraphDB, and Oxigraph** — both before and after integrating the `triplestore` library.

The benchmarking framework, implemented in [skeleton.py](/triplestore/bench/skeleton.py), ensured consistent testing conditions through nanosecond-precision timers and a standardized execution workflow. Each benchmark followed the same sequence: backend initialization, data loading from a Turtle (`.ttl`) file, and SPARQL query execution on a generated family dataset. Datasets of three sizes (≈20k, 200k, and 2M triples) were created using [generate-data.py](/data/generate/generate-data.py).

The measurements captured loading, query, and overall execution time for each triplestore. The results demonstrated that, while raw timings varied depending on the backend, the abstraction layer introduced negligible or no performance penalty in most cases. AllegroGraph, GraphDB, and Oxigraph maintained nearly identical or slightly improved performance. Blazegraph showed stable behavior on small datasets but slower ingestion on large ones, a limitation inherent to its internal batching. Apache Jena exhibited longer load times, mainly because the Fuseki server startup is now handled automatically and thus included in the total runtime.

Despite these differences, the unified library significantly improved usability. Previously, developers had to manually manage HTTP endpoints and upload datasets through backend-specific commands. Now, library's operations fully abstract these steps, providing a consistent API across all systems. Overall, the benchmarking confirmed that the abstraction layer achieves a major gain in consistency and ease of use without compromising efficiency.

## Results and Outcomes
The final implementation closely followed the goals outlined in the original proposal while introducing several improvements in design, structure, and extensibility.

### Alignment with the Original Proposal

According to the initial plan, the project aimed to:
- Conduct research and benchmarking on several RDF triplestore systems.
- Develop a unified abstraction layer providing a consistent Python API.
- Implement support for multiple backends such as Blazegraph, GraphDB, Apache Jena, and KùzuDB.
- Produce comprehensive documentation and testing coverage.

All of these objectives were achieved, with the final outcome expanding beyond the initial scope.

### Achievements Beyond the Proposal
#### Broader Backend Support: 
The final library supports **five** triplestores—Apache Jena, AllegroGraph, Blazegraph, GraphDB, and Oxigraph—instead of the initially proposed four. Each backend is fully integrated through a standardized interface that supports operations such as `load()`, `query()`, `execute()`, `add()`, `delete()`, and `clear()`.

#### Refined Architecture and Dynamic Discovery
While the proposal envisioned a design inspired by SQLAlchemy, the final implementation evolved this concept further by introducing dynamic backend discovery using Python entry points (`registration.py`) and a centralized factory constructor (`Triplestore()`). This mechanism, built on top of an abstract base class, enables automatic backend loading at runtime, eliminating hardcoded imports and making the system truly extensible.

#### Improved Exception Handling
An entirely new exception hierarchy was introduced (`exceptions.py`) to enhance robustness and developer experience. This addition provides detailed, user-friendly error messages and clearer debugging feedback, going beyond what was initially planned in the proposal.

#### Documentation and Packaging Improvements
The documentation was written directly in Markdown and integrated into the repository, replacing the originally proposed LaTeX format. This choice improved maintainability and accessibility for contributors.
In addition, the project introduced modular packaging via `pyproject.toml`, allowing users to install only the specific triplestore backends they require (e.g., `triplestore[jena]`, `triplestore[graphdb]`, or `triplestore[all]`). This approach reduces dependencies and improves flexibility for both users and developers.

## Future Work
Building upon the benchmarking outcomes, several directions for further enhancement can be explored.
In terms of performance, introducing concurrent data loading mechanisms and incorporating memory profiling could significantly accelerate dataset ingestion for large RDF graphs. Functionally, future iterations of the library could extend the `add()` operation to support literal additions, and expand the `load()` method to recognize multiple RDF syntaxes such as N-Triples, RDF/XML, and JSON-LD. Such improvements would make the abstraction layer more versatile and efficient, reinforcing its goal of providing a seamless and unified interface across diverse triplestore systems.

## Conclusion
Participating in Google Summer of Code 2025 with Open Technologies Alliance (GFOSS) has been an immensely valuable experience, both technically and personally. Throughout this project, I had the opportunity to deepen my understanding of Semantic Web technologies, RDF triplestores, and SPARQL query processing, while also strengthening my skills in software design, Python development, and modular packaging.

From a technical standpoint, I learned how to structure a complex, extensible Python library using concepts such as abstract base classes, dynamic entry points, and exception hierarchies, while maintaining clean and reusable code. I also gained practical experience with tools like pytest, hatchling, and PyPI packaging, which gave me a more complete view of real-world open-source software engineering workflows.

Equally important were the collaborative aspects of the project. Working closely with my mentor, Alexios Zavras, helped me adopt an iterative, feedback-driven development process. I learned how to communicate technical decisions effectively, write clear documentation, and manage the evolution of a public open-source repository in a professional way.

I would like to sincerely thank my mentor, Alexios Zavras, for his continuous guidance, constructive feedback, and encouragement throughout the entire program, as well as GFOSS for giving me the opportunity to contribute to a meaningful and impactful open-source initiative.