#!/usr/bin/env python3

# gen_data.py -- generate random data in TTL format

# Copyright (C) 2023-2025 Alexios Zavras
# SPDX-License-Identifier: Apache-2.0

# With apologies for the very conservative and traditional definitions
# of people, genders, and families.

import argparse
import itertools
import logging
import random
import sys
from pathlib import Path

# Default configuration values
DEFAULT_INITIAL_FAMS = 10
DEFAULT_MAX_CHILDREN = 7
DEFAULT_PRISTINE_GENS = 4
DEFAULT_MIXED_FAMS = 10_000
DEFAULT_SEED = 2025


class Person:
    p_id = itertools.count()
    instances = []

    def __init__(self, sex):
        self.id = next(self.p_id)
        self.name = f"I{self.id:08}"
        self.sex = sex
        Person.instances.append(self)

    def gen_ttl(self):
        p = f"d:{self.name}"
        triples = [
            (p, "a", "s:Person"),
            (p, "s:name", '"' + self.name + '"'),
            (p, "s:sex", f"s:sex-{self.sex}"),
        ]
        return triples

    def __str__(self):
        return f"<Person {self.name} ({self.sex})>"


class Family:
    f_id = itertools.count()
    instances = []

    def __init__(self, m, f):
        self.id = next(self.f_id)
        self.name = f"F{self.id:08}"
        self.m = m
        self.f = f
        self.children = []
        Family.instances.append(self)

    def add_child(self, c):
        self.children.append(c)

    def gen_ttl(self):
        p = f"d:{self.name}"
        triples = [
            (p, "a", "s:Family"),
            (p, "s:husband", f"d:{self.m.name}"),
            (p, "s:wife", f"d:{self.f.name}"),
        ]
        triples.extend((p, "s:child", f"d:{c.name}") for c in self.children)
        return triples

    def __str__(self):
        children_names = ", ".join([c.name for c in self.children])
        return f"<Family {self.name} (H:{self.m.name}, W:{self.f.name}, C:[{children_names}])>"


def gen_all_data(config):
    to_expand = []  # People eligible to get married in the next stage

    # Initial families
    for _f in range(config["initial_fams"]):
        m = Person("male")
        f = Person("female")
        family = Family(m, f)
        for _c in range(random.randint(0, config["max_children"])):
            child = Person(random.choice(["male", "female"]))
            family.add_child(child)
            to_expand.append(child)

    # Variables to store individuals available for mixed families
    # These will be populated by the children of the last pristine generation
    # or by children of initial families if pristine_gens is 0.
    free_m = []
    free_f = []

    # Pristine generations
    # `to_expand` contains children from the previous generation stage.
    for _lvl in range(config["pristine_gens"]):
        parents_for_this_gen = to_expand.copy()
        to_expand = []  # Children born in this generation will go here

        if not parents_for_this_gen:  # Population died out
            logging.warning(f"Population died out before pristine generation {_lvl + 1}.")
            break

        for parent in parents_for_this_gen:
            # Create a new partner for p_parent
            if parent.sex == "male":
                husband = parent
                wife = Person("female")
            else:
                husband = Person("male")
                wife = parent

            family = Family(husband, wife)
            for _c in range(random.randint(0, config["max_children"])):
                c_sex = random.choice(["male", "female"])
                child = Person(c_sex)
                family.add_child(child)
                to_expand.append(child)  # These children are candidates for the next generation/stage

                # If this is the last pristine generation, its children populate the mixed marriage pool
                if _lvl == config["pristine_gens"] - 1:
                    if c_sex == "male":
                        free_m.append(child)
                    else:
                        free_f.append(child)

        if not to_expand and _lvl < config["pristine_gens"] - 1:
            logging.warning(f"Population died out during pristine generation {_lvl + 1}.")
            break

    # If pristine_gens is 0, children from initial_fams form the pool for mixed families.
    if config["pristine_gens"] == 0:
        for p in to_expand:
            if p.sex == "male":
                free_m.append(p)
            else:
                free_f.append(p)
    # If pristine_gens > 0, free_m_for_mixed/free_f_for_mixed were populated by the last iteration.
    # If population died out before last pristine gen, they might be empty.

    # Mixed families
    for _f in range(config["mixed_fams"]):
        if not free_m or not free_f:
            logging.warning(f"Not enough individuals for mixed family {_f + 1}. Required 1M, 1F. Have M:{len(free_m)}, F:{len(free_f)}. Stopping.")
            break

        m_parent = random.choice(free_m)
        f_parent = random.choice(free_f)

        free_m.remove(m_parent)
        free_f.remove(f_parent)

        family = Family(m_parent, f_parent)
        for _c in range(random.randint(0, config["max_children"])):
            c_sex = random.choice(["male", "female"])
            child = Person(c_sex)
            family.add_child(child)
            # Add new children to the pool of available singles
            if c_sex == "male":
                free_m.append(child)
            else:
                free_f.append(child)


def print_all_triples(outfile):
    print("@prefix s: <http://rdf.zvr.invalid/demofamilydata/> .", file=outfile)
    print("@prefix d: <http://rdf.zvr.invalid/demofamilydata/data/> .", file=outfile)
    print(file=outfile)

    for person in Person.instances:
        for t in person.gen_ttl():
            (s, p, o) = t
            print(f"{s}\t{p}\t{o} .", file=outfile)
    for family in Family.instances:
        for t in family.gen_ttl():
            (s, p, o) = t
            print(f"{s}\t{p}\t{o} .", file=outfile)


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Generate random family data in TTL format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # Shows defaults in help
    )
    parser.add_argument(
        "--initial-fams",
        type=int,
        default=DEFAULT_INITIAL_FAMS,
        help="Number of initial couples (families).",
    )
    parser.add_argument(
        "--max-children",
        type=int,
        default=DEFAULT_MAX_CHILDREN,
        help="Maximum number of children per family (0 to N, uniform).",
    )
    parser.add_argument(
        "--pristine-gens",
        type=int,
        default=DEFAULT_PRISTINE_GENS,
        help="Number of pristine generations (depth until mixing).",
    )
    parser.add_argument(
        "--mixed-fams",
        type=int,
        default=DEFAULT_MIXED_FAMS,
        help="Number of mixed families to generate after pristine generations.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Random seed for reproducibility.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output file for TTL data. If not specified, prints to standard output.",
    )

    args = parser.parse_args()

    run_config = {
        "initial_fams": args.initial_fams,
        "max_children": args.max_children,
        "pristine_gens": args.pristine_gens,
        "mixed_fams": args.mixed_fams,
    }

    random.seed(args.seed)

    # Reset global state for Person and Family classes -- just in case
    Person.p_id = itertools.count()
    Person.instances = []
    Family.f_id = itertools.count()
    Family.instances = []

    # Generate data
    gen_all_data(run_config)

    # Handle output
    if args.output:
        with Path(args.output).open("w", encoding="utf-8") as f_out:
            print_all_triples(f_out)
    else:
        print_all_triples(sys.stdout)


if __name__ == "__main__":
    main()
