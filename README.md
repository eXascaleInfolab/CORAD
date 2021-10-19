# CORAD: Correlation-Aware Compression of Massive Time Series using Sparse Dictionary Coding

CORAD is a new real-time technique to effectively compress time series streams. It relies on a dictionary-based technique that exploits the correlation across time series. In addition, CORAD allows to adjust the degree of accuracy that is acceptable depending on the use-case. Technical details can be found in our 
Big Data 2019 paper:  <a href = "https://exascale.info/assets/pdf/khelifati2019bigdata.pdf">CORAD: Correlation-Aware Compression of Massive Time Series using Sparse Dictionary Coding </a>. 

- CORAD performs the following steps:

    - Normalize the input dataset using z-normalisation
    - Create the tricklets
    - Compute correlation for each segment
    - Learn the dictionary learning
    - Sparse coding of the data 
    - Compute the compression ratios

- All the datasets used in this benchmark can be found [here](https://github.com/eXascaleInfolab/bench-vldb20/tree/mastdatasets).

[**Prerequisites**](#prerequisites) | [**Build**](#build) | [**Execution**](#execution) | [**Arguments**](#arguments)  | [**Results**](#results) | [**Contributors**](#contributors) | [**Citation**](#citation)

___


## Prerequisites

- Install Python 3
- Clone this repo: `git clone https://github.com/eXascaleInfolab/CORAD.git`

___

## Build

- To install all the dependencies, run the following installation script:
```bash
    $ sh install.sh
```

___

## Execution


```bash
    $ python3 corad.py [arguments]
```



### Arguments

 | arg  |  Interpretation | 
 | -------- | ------- | 
 | --dataset    |  Name of the dataset (comma-separated-values, tabular-seperated-values, etc.) |
 | --trick     | Length of the tricklets  |
 | --err  | Threshold of the loss |
 | --atoms   | Number of atoms used for the representation of each tricklet | 


### Execution examples





1. Compress the *PigAirwayPressure* dataset with default parameters (trick=40, err=0.4, atoms=4)
 
```bash 
python3 corad.py --dataset 'datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TEST.tsv'
```

2 . Compress the *PigAirwayPressure* dataset with a custom error threshold

```bash 
python3 corad.py --dataset 'datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TEST.tsv' --err 0.1
 ```

3 . Compress the *PigAirwayPressure* dataset with a custom error threshold and number of atoms

```bash 
python3 corad.py --dataset 'datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TEST.tsv' --err 0.1 --atoms 6
 ```

4 . Compress the *PigAirwayPressure* dataset with a custom error threshold, number of atoms and tricklets length

```bash 
python3 corad.py --dataset 'datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TEST.tsv' --trick 20 --err 0.1 --atoms 6
 ```

___

### Results
All the results (the compressed data, the runtimes, the errors and the compression ratios) will be exported to `results/{dataset}` folder. 

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
