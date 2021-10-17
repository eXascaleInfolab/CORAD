# CORAD: Correlation-Aware Compression of Massive Time Series using Sparse Dictionary Coding

We introduced CORAD, a new real-time technique to effectively compress time series streams. CORAD relies on a dictionary-based technique that exploits the correlation across time series. In addition, CORAD allows to adjust the degree of accuracy that is acceptable depending on the use-case. Technical details can be found in our 
Big Data 2019 paper:  <a href = "https://exascale.info/assets/pdf/khelifati2019bigdata.pdf">CORAD: Correlation-Aware Compression of Massive Time Series using Sparse Dictionary Coding </a>. 

- All the datasets used in this benchmark can be found [here](https://github.com/eXascaleInfolab/bench-vldb20/tree/master/Datasets).
- The full list of recovery scenarios can be found [here](https://github.com/eXascaleInfolab/bench-vldb20/blob/master/TestingFramework/README.md).

[**Prerequisites**](#prerequisites) | [**Build**](#build) | [**Execution**](#execution) | [**Extension**](#extension)  | [**Contributors**](#contributors) | [**Citation**](#citation)

___


## Prerequisites

- Python 3

___



## Build

- Run the installation librairies. 
```bash
    $ sh install.sh
```

___

## Execution


```bash
    $ python3 main.py [arguments]
```

### Arguments

 | alg  | pos  | 
 | -------- | -------- | 
 | dataset    | 1        | 
 | datasetPath  | 2        | 
 | datasetPathDictionary   | 3    | 
 | LEN_TRICKLET     | 4     | 
 | ERROR_THRES  | 5     |
 | NB_ATOMS   | 6 |




### Results
All results and plots will be added to `Results` folder. The accuracy results of all algorithms will be sequentially added for each scenario and dataset to: `Results/.../.../error/`. The runtime results of all algorithms will be added to: `Results/.../.../runtime/`. The plots of the recovered blocks will be added to the folder `Results/.../.../recovery/plots/`.


### Execution examples


1. Run a single algorithm (cdrec) on a single dataset (drift10) using one scenario (missing percentage)
```bash
python3 main.py 'Bafu' '../Datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TEST.tsv' '../Datasets/UCRArchive_2018/PigAirwayPressure/ PigAirwayPressure_TRAIN.tsv' 14 0.4 6
```

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


