# CORAD: Correlation-Aware Compression of Massive Time Series using Sparse Dictionary Coding

- **Overview**: CORAD is a new real-time technique to effectively compress time series streams. It relies on a dictionary-based technique that exploits the correlation across time series. In addition, CORAD allows to adjust the degree of accuracy that is acceptable depending on the use-case. Technical details can be found in our 
Big Data 2019 paper:  <a href = "https://exascale.info/assets/pdf/khelifati2019bigdata.pdf">CORAD: Correlation-Aware Compression of Massive Time Series using Sparse Dictionary Coding </a>. 

- **Compression steps**:
    1. Create the tricklets
    2. Compute the subsequence correlations
    3. Learn the dictionary
    4. Sparse code the data 

- **Datasets**: We use datasets from the UCR Time Series Classification Archive (UCR), the UCI Machine Learning Repository (UCI), and the Swiss Federal Office for the Environment(FOEN). All the datasets used in the paper can be found [here](https://github.com/eXascaleInfolab/CORAD/tree/master/datasets/UCRArchive_2018).


[**Prerequisites**](#prerequisites) | [**Build**](#build) | [**Execution**](#execution) | [**Arguments**](#arguments)  | [**Contributors**](#contributors) | [**Citation**](#citation)

___


## Prerequisites

- Ubuntu 18 and 20 (including the same distribution under WSL) or Mac OS.
- Clone this repo
___

## Build

- To install all the dependencies, run the following installation script:
```bash
sudo apt install python3.9
sudo apt install python3.9-venv
python3.9 -m venv venv
source ./venv/bin/activate
sh install.sh
```
___

## Execution


```bash
    $ python3 corad.py [args]
```

### Arguments

 | args  |  Interpretation | 
 | --------    | ------- | 
 | -d   |  Name of the dataset (comma-separated-values, tabular-seperated-values, etc.) |
 | -t     | Length of the tricklets  |
 | -e       | Max loss between the original data and the compressed one |
 | -a     | Number of atoms used for the representation of each tricklet | 


### Execution Examples

1. Compress the *PigAirwayPressure* dataset with the default parameters (trick=40, err=0.4, atoms=4)
 
```bash 
python3 corad.py -d 'datasets/PigAirwayPressure_TEST.tsv'
```

2 . Compress the *PigAirwayPressure* dataset with a customized error threshold

```bash 
python3 corad.py -d 'datasets/PigAirwayPressure_TEST.tsv' -e 0.1
 ```

3 . Compress the *PigAirwayPressure* dataset with customized error threshold, and number of atoms

```bash 
python3 corad.py -d 'datasets/PigAirwayPressure_TEST.tsv' -e 0.1 -a 6
 ```

4 . Compress the *PigAirwayPressure* dataset with customized tricklets length, error threshold, and number of atoms 

```bash 
python3 corad.py -d 'datasets/PigAirwayPressure_TEST.tsv' -t 20 -e 0.1 -a 6
 ```
 
### Results

All the results including the compressed data, runtime, accuracy error, and the compression ratios will be added to `results/{dataset_name}.txt` file. The results of the baseline TRISTAN technique will be also added. 

The compressed data are exported using Python's pickle library into the `results/compressed_data/{dataset}/` folder and could be opened using the following command: 

### Decompression

In addition to data decompression in the main scripts, `decompression.py` allows to perform a decompression as follows: 

```
python3 corad.py -d 'datasets/PigAirwayPressure_TEST.tsv'

python3 decompress.py -d 'results/compressed_data/PigAirwayPressure_TEST.tsv/originalData.out'
```
___

## Contributors
- Abdelouahab Khelifati (abdel@exascale.info)
- Dr. Mourad Khayati (mourad@khayati.unifr.ch)

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
