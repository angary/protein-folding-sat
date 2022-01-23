#!/bin/bash

echo "Making models and results directory"
mkdir -p models/{bul,cnf}
mkdir -p results/{encoding,policy,sat,search}
echo


echo "Checking SAT solvers"
declare -a solvers=("glucose" "kissat" "minisat")
passed=0
for i in "${solvers[@]}"
do
    if ! command -v ${i} &> /dev/null
    then
        echo "WARNING: ${i} could not be found"
        passed=1
    fi
done
if [ $passed -eq 0 ];
then 
    echo "All solvers installed"
else
    echo "Missing solver(s) may be a problem during testing"
fi
echo 


echo "Checking bule installation"
if ! command -v bule2 &> /dev/null
then
    echo "Could not find bule2, install bule at https://github.com/vale1410/bule"
else
    echo "bule2 installed"
fi
echo


echo "Unzipping Dataset.zip"
rm -rf Dataset
unzip Dataset &> /dev/null
echo 


echo "Adding sequences to input/ directory"
mkdir -p input
python3 -m src.get_sequences &> /dev/null
python3 -m src.gen_rand_sequence &> /dev/null
echo


echo "Removing sequences longer than 50"
for f in $(ls input)
do 
    if [ $(cat input/$f | wc -m) -gt 51 ];
    then
        rm input/$f
    fi
done
echo 


echo "Done"
