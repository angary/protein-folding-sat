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

<table>
  <tbody>
    <tr>
      <th>Files / Folder</th>
      <th>Purpose</th>
    </tr>
    <tr>
      <td><b>bule</b></td>
      <td>
         Folder with files that contain protein sequences in the HP model
         <ul>
            <li>The number after the <code>v</code> denotes the version of the encoding</li>
            <li> <code>v0</code> is the <b>Original Encoding</b> and has one for 2D and 3D embeddings</li>
            <li> <code>v1</code> is the <b>Dimension Encoding</b> and works for any dimension</li>
            <li> <code>v2</code> is the <b>Order Encoding</b> (and an improvement of the Dimension Encoding)</li>
         </ul>
      </td>
    </tr>
    <tr>
      <td><b>models</b></td>
      <td>Folder containing the Bule and DIMACS CNF format encoding of the inputs</td>
    </tr>
    <tr>
      <td><b>src</b></td>
      <td>
         Folder containing Python scripts for generating encodings and running tests
         <ul>
            <li>The <b>util</b> folder contains helper scripts used for comparing encodings, or visualising embeddings</li>
            <ul>
              <li>To visualise a grid, run <code>bule --solve &lt;model> &lt;constraints> 2> temp.bul; python3 -m src.util.visualise_grid temp.bul</code>
            </ul>
         </ul>
      </td>
    </tr>
  </tbody>
</table>

Note that some of these folders are not tracked by git due to large sizes.

The project uses the [Bule SAT programming language](https://github.com/vale1410/bule) for generating the encodings, and the following SAT solvers: 
- [glucose](https://github.com/mi-ki/glucose-syrup)
- [kissat](https://github.com/arminbiere/kissat)
- [minisat](https://github.com/niklasso/minisat)

## Usage

Inside the `input` directory are files, each of which contain a string of 1s and 0s, used to model a protein sequence used in the prototein problem.
These files are used as inputs for the protein folding problem.
They can then be encoded in a bule (`.bule`) or DIMACS CNF format (`.cnf`) which contains a problem of solving for a random walk on a sequence that results in a certain number of H-H contacts.

Running the following command in the root directory of the project

```
python3 -m src.encode <input_file> -c <contact_count> -d <dimension>
```

will create a bule encoding inside the `models/bul` directory, and a DIMACS CNF encoding in the `models/cnf` directory.

Use `python3 -m src.encode -h` for the full list of arguments.

The GitHub repository from the original research paper can be found [here](https://github.com/hannah-aught/prototein-problem).
