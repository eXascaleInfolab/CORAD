sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.9
sudo apt install python3.9-venv
python3.9 -m venv venv
source ./venv/bin/activate
#sudo apt -y install python3
sudo apt-get -y --purge autoremove python3-pip
sudo apt -y install python3-pip
pip3 install matplotlib
pip3 install luminol
pip3 install sklearn
pip3 install scikit-learn
pip3 install numpy
pip3 install pandas
pip3 install tqdm
pip3 install sklearn
pip3 install plotly
