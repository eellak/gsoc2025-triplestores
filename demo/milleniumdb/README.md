# MilleniumDB Demo

## MilleniumDB setup

Unfortunately, the latest MilleniumDB version,
in its [development repository]()
(commit 017abf7a85c76bcf3791441eded6e7391a4934a8 dated 2025-03-19)
does not compile cleanly.
Until a [PR fixing this](https://github.com/MillenniumDB/MillenniumDB/pull/36)
is merged, here's how to reproduce it locally.

Once the code is downloaded (git cloned) locally,
a single-line patch has to be applied to a header file:

```sh
sed -i '6i #include <cstdint>' src/storage/index/text_search/trie_iter_list.h
```

Afterwards the Boost library inserted into `third_party/boost_1_82/include`,
and the project can then be compiled with the commands:
```sh
cmake  -DCMAKE_BUILD_TYPE=Release -Bzbuild
cmake --build zbuild
```

From then on, one can use the executables
`mdb-cli`, `mdb-import`, and `mdb-server`
from `zbuild/bin`.

## Overview

## Requirements

## Setup
1. Setup MilleniumDB as per the instructions above


