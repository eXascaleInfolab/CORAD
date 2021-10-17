# CORAD: Correlation-Aware Compression of Massive Time Series using Sparse Dictionary Coding

We introduced CORAD, a new real-time technique to effectively compress time series streams. CORAD relies on a dictionary-based technique that exploits the correlation across time series. In addition, CORAD allows to adjust the degree of accuracy that is acceptable depending on the use-case. Technical details can be found in our 
Big Data 2019 paper:  <a href = "https://exascale.info/assets/pdf/khelifati2019bigdata.pdf">CORAD: Correlation-Aware Compression of Massive Time Series using Sparse Dictionary Coding </a>. 

- All the datasets used in this benchmark can be found [here](https://github.com/eXascaleInfolab/bench-vldb20/tree/master/Datasets).
- The full list of recovery scenarios can be found [here](https://github.com/eXascaleInfolab/bench-vldb20/blob/master/TestingFramework/README.md).

[**Prerequisites**](#prerequisites) | [**Build**](#build) | [**Execution**](#execution) | [**Extension**](#extension)  | [**Contributors**](#contributors) | [**Citation**](#citation)

___


## Prerequisites

- Python 3. 

___



## Build

- Run the installation librairies. 
```bash
    $ sh install.sh
```

___

## Execution


```bash
    $ cd TestingFramework/bin/Debug/
    $ mono TestingFramework.exe [arguments]
```

### Arguments
 | -arg  | -pos |
 | -------- | -------- | -------- |
 | dataset 						| sys.argv[1]			|
 | datasetPath 					| sys.argv[2]			|
 | datasetPathDictionary 		| sys.argv[3]			|
 | # NBWEEKS 					| sys.argv[2]			|
 | LEN_TRICKLET 				| int(sys.argv[4])		|
 | ERROR_THRES 					| float(sys.argv[5])	|
 | # LEN_TRICKLET 				| NBWEEKS * 7			|
 | NB_ATOMS 					| int(sys.argv[6])		|





### Results
All results and plots will be added to `Results` folder. The accuracy results of all algorithms will be sequentially added for each scenario and dataset to: `Results/.../.../error/`. The runtime results of all algorithms will be added to: `Results/.../.../runtime/`. The plots of the recovered blocks will be added to the folder `Results/.../.../recovery/plots/`.


### Execution examples


1. Run a single algorithm (cdrec) on a single dataset (drift10) using one scenario (missing percentage)
```bash
    $ mono TestingFramework.exe -alg cdrec -d drift10 -scen miss_perc
```

2. Run two algorithms (cdrec, spirit) on a single dataset (drift10) using one scenario (missing percentage)
```bash
    $ mono TestingFramework.exe -alg cdrec,spirit -d drift10 -scen miss_perc
```

3. Run point 2 without runtime results
```bash
    $ mono TestingFramework.exe -alg cdrec,spirit -d drift10 -scen miss_perc -nort
```

4. Run the whole VLDB'20 benchmark (all algorithms, all datasets, all scenarios, precision and runtime)
```bash
    $ mono TestingFramework.exe -alg all -d all -scen all
```
**Warning**: Running the whole benchmark will take a sizeable amount of time (up to 4 days depending on the hardware) and will produce up to 15GB of output files with all recovered data and plots unless stopped early.

5. Create files with missing values on one dataset (airq) using a single scenario (missing percentage)
```bash
    $ mono TestingFramework.exe -alg mvexport -d airq -scen miss_perc
```
**Note**: You need to run each scenario seperately on one or multiple datasets. Each time you execute one scenario, the `Results` folder will be overwritten with the new files.

6. Additional command-line parameters
```bash
    $ mono TestingFramework.exe --help
```

**Remark**: Algorithms `tkcm`,  `spirit`, `ssa`, `brits` and `mr-nn`  cannot handle multiple incomplete time series. These allgorithms will not produce results for the following scenarios: `miss_disj`, `miss_over`, `mcar` and `blackout`.

### Parametrized execution

- You can parametrize each algorithm using the command `-algx`. For example, you can run
the svdimp algorithm with a reduction value of 4 on the drift dataset and by varying the sequence length as follows:

```bash
    $ mono TestingFramework.exe -algx svdimp 4 -d drift10 -scen ts_nbr
```

- If you want to run some algorithms with default parameters, and some with customized ones, you can use `-alg` and `-algx` together. For example, you can run stmvl algorithm with default parameter and cdrec algorithm with a reduction value of 4 on the airq dataset and by varying the sequence length as follows:

```bash
    $ mono TestingFramework.exe -alg stmvl -algx cdrec 4 -d airq -scen ts_nbr
```

**Remark**: The command `-algx` cannot be executed in group and thus must preceed the name of each algorithm.

___

## Contributors
Abdelouahab Khelifati (abdel@exascale.info).


___

## Citation
```bibtex
@INPROCEEDINGS{9005580,
  author={Khelifati, Abdelouahab and Khayati, Mourad and Cudré-Mauroux, Philippe},
  booktitle={2019 IEEE International Conference on Big Data (Big Data)}, 
  title={CORAD: Correlation-Aware Compression of Massive Time Series using Sparse Dictionary Coding}, 
  year={2019},
  volume={},
  number={},
  pages={2289-2298},
  doi={10.1109/BigData47090.2019.9005580}}
```


