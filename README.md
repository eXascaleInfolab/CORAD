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
    $ python3 corad.py [arguments]
```



The ```corad.py``` script would be done with the following steps: 
- Reading the dataset and z-normalisation. 
- Creating the tricklets .
- Correlation computation for each segment.
- Dictionary learning .
- Sparse coding the data with TRISTAN method.
- Sparse coding the data with CORAD method.
- Save the compressed data to the disk.
- Compute the compression ratios. 
- Print and export the time/errors/compression ratios results. 


### Arguments

 | arg  |  Interpretation | 
 | -------- | ------- | 
 | --dataset    |  Path towards the dataset (comma-separated-values, tabular-seperated-values, etc.) |
 | --trick     | Length of the tricklets used in the compression |
 | --err  | Threshold of the acceptable loss resulted by the compression |
 | --atoms   | Number of atoms used for the representation of each tricklet | 


### Execution examples





1. Run CORAD and TRISTAN methods on the *Gas* dataset with default parameters (trick=40, err=0.4, atoms=4): 
```bash 
python3 corad.py 
```

1. Run the TRISTAN and CORAD methods on the *PigAirwayPressure* dataset with default parameters (trick=40, err=0.4, atoms=4): 
```bash 
python3 corad.py --dataset 'datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TEST.tsv'
```

1. Run the TRISTAN and CORAD methods on the *Gas* dataset with a custom error threshold and the default values for the rest of the parameters (trick=40, atoms=4): 
```bash 
python3 corad.py --err 0.1
```

1. Run the TRISTAN and CORAD methods on the *Gas* dataset with a custom number of atoms and the default values for the rest of the parameters (trick=40, err=0.4): 
```bash 
python3 corad.py --atoms 6
```

1. Run the TRISTAN and CORAD methods on the *Gas* dataset with a custom tricklets length and error threshold and the default value for the number of atoms: 
```bash 
python3 corad.py --trick 20 --err 0.2
```


___

### Results
All the results (the compressed data, the runtimes, the errors and the compression ratios) will be exported to `results/` folder. 

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
