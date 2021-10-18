# CORAD: Correlation-Aware Compression of Massive Time Series using Sparse Dictionary Coding

We introduced CORAD, a new real-time technique to effectively compress time series streams. CORAD relies on a dictionary-based technique that exploits the correlation across time series. In addition, CORAD allows to adjust the degree of accuracy that is acceptable depending on the use-case. Technical details can be found in our 
Big Data 2019 paper:  <a href = "https://exascale.info/assets/pdf/khelifati2019bigdata.pdf">CORAD: Correlation-Aware Compression of Massive Time Series using Sparse Dictionary Coding </a>. 

- All the datasets used in this benchmark can be found [here](https://github.com/eXascaleInfolab/bench-vldb20/tree/mastdatasets).
- The full list of recovery scenarios can be found [here](https://github.com/eXascaleInfolab/bench-vldb20/blob/master/TestingFramework/README.md).

[**Prerequisites**](#prerequisites) | [**Build**](#build) | [**Execution**](#execution) | [**Arguments**](#arguments)  | [**Results**](#results) | [**Contributors**](#contributors) | [**Citation**](#citation)

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

 | arg  |
 | -------- | 
 | --dataset    |
 | --datasetPath  | 
 | --datasetPathDictionary   | 
 | --len_tricklet     | 
 | --error_thres  |
 | --nb_atoms   |


### Execution examples


```bash

python3 main.py 

python3 main.py --dataset 'Gas' --datasetPath 'datasets/20160930_203718-2.csv' --datasetPathDictionary '../datasets/archive_ics/gas-sensor-array-temperature-modulation/20160930_203718-2.csv' --len_tricklet 40 --error_thres 0.4 --nb_atoms 4

python3 main.py --dataset 'Bafu' --datasetPath 'datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TEST.tsv' --datasetPathDictionary 'datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TRAIN.tsv' --len_tricklet 14 --error_thres 0.4 --nb_atoms 6

python3 main.py --dataset 'PigAirwayPressure' --datasetPath 'datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TEST.tsv' --datasetPathDictionary 'datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TRAIN.tsv' --len_tricklet 14 --error_thres 0.2 --nb_atoms 6

python3 main.py --dataset 'Bafu' --datasetPath 'datasets/UCRArchive_2018/Wafer/Wafer_TEST.tsv' --datasetPathDictionary 'datasets/UCRArchive_2018/Wafer/Wafer_TRAIN.tsv' --len_tricklet 14 --error_thres 0.4 --nb_atoms 6

python3 main.py 'Bafu' 'datasets/bafu_normal.csv' 'datasets/bafu_normal.csv' 14 0.4 1

python3 main.py 'Yoga' 'datasets/UCRArchive_2018/Yoga/Yoga_TEST.tsv' 'datasets/UCRArchive_2018/Yoga/Yoga_TRAIN.tsv' 20 0.4 4

python3 main.py 'ACSF1' 'datasets/UCRArchive_2018/ACSF1/ACSF1_TEST.tsv' 'datasets/UCRArchive_2018/ACSF1/ACSF1_TRAIN.tsv' 5 0.4 4

python3 main.py 'SonyAIBORobotSurface2' 'datasets/UCRArchive_2018/SonyAIBORobotSurface2/SonyAIBORobotSurface2_TEST.tsv' 'datasets/UCRArchive_2018/SonyAIBORobotSurface2/SonyAIBORobotSurface2_TRAIN.tsv' 14 0.4 6

python3 main.py 'Wafer' 'datasets/UCRArchive_2018/Wafer/Wafer_TEST.tsv' 'datasets/UCRArchive_2018/Wafer/Wafer_TRAIN.tsv' 14 0.4 6
```
___

### Results
All results and plots will be added to `outputs/` folder. 

___

## Contributors
Abdelouahab Khelifati (abdel@exascale.info).

___

## Citation
```bibtex
@inproceedings{DBLP:conf/bigdataconf/KhelifatiKC19,
  author    = {Abdelouahab Khelifati and
               Mourad Khayati and
               Philippe Cudr{\'{e}}{-}Mauroux},
  title     = {{CORAD:} Correlation-Aware Compression of Massive Time Series using
               Sparse Dictionary Coding},
  booktitle = {2019 {IEEE} International Conference on Big Data (Big Data), Los Angeles,
               CA, USA, December 9-12, 2019},
  pages     = {2289--2298},
  publisher = {{IEEE}},
  year      = {2019},
  url       = {https://doi.org/10.1109/BigData47090.2019.9005580},
  doi       = {10.1109/BigData47090.2019.9005580},
  timestamp = {Fri, 09 Apr 2021 17:11:11 +0200},
  biburl    = {https://dblp.org/rec/conf/bigdataconf/KhelifatiKC19.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
```
