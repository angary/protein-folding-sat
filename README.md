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

| **File**                         | **Purpose**                                                                                            |
| -------------------------------- | ------------------------------------------------------------------------------------------------------ |
| [bule](bule)                     | Bule2 encodings of the prototein problem, and linear constraints                                       |
| [input](input)                   | Folder with files that contain protein sequences in the HP model                                       |
| [models](models)                 | Folder containing the Bule2 and DIMACS CNF format encoding of the inputs                               |
| [src](src)                       | Folder containing Python scripts for generating encodings and running tests                            |
| [analysis.ipynb](analysis.ipynb) | Check that the new and old encoding produces the same number of contacts and compare their performance |

Note that some of these folders are not tracked by git due to large sizes.

The project uses the [Bule SAT programming language](https://github.com/vale1410/bule) for generating the encodings, and [kissat](https://github.com/arminbiere/kissat) for solving the encodings.

## Usage

Inside the `input` directory are files, each of which contain a string of 1s and 0s, used to model a protein sequence used in the prototein problem.
These files are used as inputs for the protein folding problem.
They can then be encoded in a bule (`.bule`) or DIMACS CNF format (`.cnf`) which contains a problem of solving for a random walk on a sequence that results in a certain number of H-H contacts.

Running the following command in the root directory of the project

```
python3 -m src.encode <input_file> -c <contact_count> -d <dimension>
```

will create a bule encoding inside the `models/bul` directory, and a DIMACS CNF encoding in the `models/cnf` directory.

Adding the `-s` or `--solve` flag will result in a binary search for the maximum number of contacts possible.

Adding the `-t` or `--track` flag will result in storing details such as time, contacts, variables and clauses for solving an encoding in a csv file in the `results` directory.

The GitHub repository from the original research paper can be found [here](https://github.com/hannah-aught/prototein-problem).
