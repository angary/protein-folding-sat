# Protein Folding through Logical Encodings

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

| **File**                                     | **Purpose**                                                                                            |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| [gen_rand_sequence.py](gen_rand_sequence.py) | Writes to a file a random string of "0"s and "1"s                                                      |
| [get_sequences.py](get_sequences.py)         | Reads in the data from the `Dataset` folder and generates file containing "0"s and "1s"                |
| [encode.py](encode.py)                       | Generates bule2 encoding for a protein. If given the `--solve` flag, finds the max num of contacts     |
| [run_tests.py](run_tests.py)                 | Go through the input sequences and benchmark the encodings, writing results into the results folder    |
| [helpers](helpers/)                           | Contains scripts to visualise the protein embedding from clauses / validate new encoding               |
| [analysis.ipynb](analysis.ipynb)             | Check that the new and old encoding produces the same number of contacts and compare their performance |

The project uses the [Bule SAT programming language](https://github.com/vale1410/bule) for generating the encodings, and [kissat](https://github.com/arminbiere/kissat) for solving the encodings.

The GitHub repository from the original research paper can be found [here](https://github.com/hannah-aught/prototein-problem).
