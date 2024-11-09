# Open BIM exchange on Blockchain 3.0 virtual disk: A traceable semantic differential transaction approach

## Citation
Please consider citing our work if you found this code or our paper beneficial to your research.
```
@article{KONG,
    title = {Open BIM exchange on Blockchain 3.0 virtual disk: A traceable semantic differential transaction approach},
    author = {Lingming Kong and Rui Zhao and Chimay J. ANUMBA and Weisheng Lu and Fan Xue},
    journal = {Frontiers of Engineering Management},
    issue = {4},
    year = {2024},
    doi = {https://doi.org/10.1007/s42524-024-4006-x},
    url = {https://frankxue.com/pdf/kong24openbim.pdf}
}
```

## Introduction
This repository contains the code for openBIMdisk, a Flask-backed DApp for semantics-level BIM exchange and tracing in the Blockchain 3.0 environment. It is endowed with diverse functionalities, including file management, semantic BIM exchange, and blockchain interaction, all aimed at serving the needs of BIM stakeholders. All the functions are supported by a traceable semantic difference transaction (tSDT) approach. The pilot case study demonstrates that the tSDT approach successfully eliminates 60.56% of meaningless IFC semantics within a reasonable operation time cost of 94.01s, marking a remarkable 71.1% decrease compared to the previous SDT approach. furthermore, it achieves this through an average Open BIM’s disk size reduction of 99.3% for IFC and 99.6% for IFCJSON formats. 
## Architecture
![image](https://github.com/KarleKong/openBIMdisk/blob/main/openBIMdisk/Architecture.svg)
## Usage
$ # Get the code (he recommanded python version is 3.8)        
`git clone https://github.com/KarleKong/openBIMdisk`    
`cd openBIMdisk/apps`    
$ # Install the required dependencies    
`pip install -r requirements.txt`  
$ # Set the FLASK_APP environment variable  
`cd ..`  
`(Unix/Mac) export FLASK_APP = run.py`  
`(Windows) set FLASK_APP=run.py`  
`(Powershell) $env:FLASK_APP=".\run.py"`  
$ # Start the application (development mode)  
`flask run --host=0.0.0.0 --port=5000`  
Now, you can access the dashboard in browser: http://127.0.0.1:5000/
## Blockchain 3.0 backbone
The Blockchain 3.0 backbone extends a cached layer for BIM data indexing, querying, and analysing. The BIM change contract (BCC) serves as a communication bridge between both the Blockchain 2.0 network and the cached layer, enabling off-line data storage and on-line data synchronization.
### Deploy the test fabric blockchain network
In this case, the fabric blockchain network is deployed on the windows subsystem for linux (WSL) with the ubuntu 20.04.6. Users can also deploy it on the remote server.

To deploy the test fabric blockchain network, please refer to **https://github.com/hyperledger/fabric-samples/tree/main/test-network**. Users can find the configuration files in **/fabric**. To deploy a simple fabric blockchain network in your devices, follow the steps (deploy in the WSL as an example):

$ # Access to the code  
`cp -r your/path/to/test-network your/server/folder`  
$ # Start the docker service  
`sudo service docker start`  
$ # Start the network  
`./network.sh up`  
$ # Check the docker status  
`docker ps -a`  
$ # Start the hyperledger explorer  
`cp -r your/path/to/explorer your/server/folder`  
`cd explorer`  
`docker-compose up -d`  
## tSDT model
The traceable Semantic Differential Transaction (tSDT) model incorporates two key features: (1) remove duplicated instances of BIM semantics; and (2) indexing BIM data such as Id, GUID, change type, etc., and further storing them on a local cached database for querying of BIM semantic changes.
## Application UI
![image](https://github.com/KarleKong/openBIMdisk/blob/main/openBIMdisk/GUI.svg)

## License
[Apache License 2.0](https://github.com/KarleKong/openBIMdisk/blob/main/LICENSE)
