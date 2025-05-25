# Generate synthetic data

The [generate-data.py script](./generate-data.py) in this directory
generates synthetic data in RDF triples format.

The unrelying [ontology](./schema.ttl) is very simple.
It is based on people, of two sexes, forming families
and having a number of children.
Apologies for the very conservative and traditional definitions of people, genders, and families.

Besides the direct relationships `married-to` and `child-of`
(and their inverse like `parent-of`),
the schema can be used to formulate queries based on reasoning,
combining different facts.
The [reasoning](./reasoning.ttl) file provides some initial ideas
on further relationships that could be used in queries.

## How to run

The script accepts a number of command-line parameters.

```
usage: generate-data.py [-h] [--initial-fams INITIAL_FAMS]
                        [--max-children MAX_CHILDREN]
                        [--pristine-gens PRISTINE_GENS]
                        [--mixed-fams MIXED_FAMS] [--seed SEED] [-o OUTPUT]

Generate random family data in TTL format.

options:
  -h, --help            show this help message and exit
  --initial-fams INITIAL_FAMS
                        Number of initial couples (families). (default: 10)
  --max-children MAX_CHILDREN
                        Maximum number of children per family (0 to N,
                        uniform). (default: 7)
  --pristine-gens PRISTINE_GENS
                        Number of pristine generations (depth until mixing).
                        (default: 4)
  --mixed-fams MIXED_FAMS
                        Number of mixed families to generate after pristine
                        generations. (default: 10000)
  --seed SEED           Random seed for reproducibility. (default: 2025)
  -o, --output OUTPUT   Output file for TTL data. If not specified, prints to
                        standard output. (default: None)
```

It starts with `INITIAL_FAMS` each growing independently for `PRISTINE_GENS` generations
and then all people are mixed until `MIXED_FAMS` are generated.
Each family has between `0` and `MAX_CHILDREN` children.

One can generate deterministic and reproducible output by setting the random `SEED`.

Output can be written to an `OUTPUT` file.

