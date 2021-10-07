# Protein Folding through Logical Encodings

Repository for my Taste of Research project.

## Description of field of Research

Protein Folding is a notoriously difficult task from computational biology.
The HP model simplifies this problem into a Boolean optimization problem where a string made out of 0s and 1s needs to be embedded into a 3D Grid following certain rules.
This problem is computationally intractable (NP-complete) even for short sequences of 20 positions.
SAT solving is an Artificial Intelligence approach to solve computational problems by translating them into propositional logic.
The objective of this project is to examine the HP Model of protein folding under the lense of SAT solving.

- Study the existing logical encodings formulations of the HP model [1].
- Establish a benchmark suite and reproduce the previously published results.
- Develop a new logical encoding for the problem.
- Use the benchmark suite to compare the performance of the new encoding against the existing ones.

### Research Material/Links

[1] Hannah Brown, Lei Zuo, and Dan Gusfield. Comparing Integer Linear Programming to SAT-Solving for Hard Problems in Computational and Systems Biology. In: Algorithms for Computational Biology 12099 (2020), p. 63. url: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7197060/

## Setup

### Files

| File                    | Purpose                                                                                                                   |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| gen_random_sequence.py  | Writes to a file a random string of "0"s and "1"s                                                                         |
| get_sequences.py        | Reads in the data from the `Dataset` folder and generates file containing "0"s and "1s"                                   |
| encode.py               | Generates bule2 encoding for a protein. If given the `--solve` flag, finds the max num of contacts through binary search. |
| constraints.bul         | Bule2 encoding of the prototein problem                                                                                   |
| order.bul, sort_tot.bul | Bule2 encoding of the linear constraints by Olivier Bailleux and Yacine Boufkhad                                          |

Note that a temporary file called `temp` is created / overwritten to hold the output of running the SAT solver, so avoid creating your own files called temp to hold information (`os.system` is used rather than something like `subprocess.run` as the latter seems to have worse performance).

The project uses the [Bule SAT programming language](https://github.com/vale1410/bule).

Some testing files are modified versions of files found [here](https://github.com/hannah-aught/prototein-problem).
