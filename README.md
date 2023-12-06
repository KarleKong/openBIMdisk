# openBIMdisk: a Flask-backed DApp for semantics-level BIM exchange in the Blockchain 3.0 environment
## Introduction
This repository contains the code for openBIMdisk, a Flask-backed DApp for semantics-level BIM exchange and tracing in the Blockchain 3.0 environment. It is endowed with diverse functionalities, including file management, semantic BIM exchange, and blockchain interaction, all aimed at serving the needs of BIM stakeholders. All the functions are supported by a traceable semantic difference transaction (tSDT) approach. The pilot case study demonstrates that the tSDT approach successfully eliminates 60.56% of meaningless IFC semantics within a reasonable operation time cost of 94.01s, marking a remarkable 71.14% decrease compared to the previous SDT approach. furthermore, it achieves this through an average Open BIM’s disk size reduction of 99.3% for IFC and 99.6% for IFCJSON formats. 
## Architecture
![image](https://github.com/KarleKong/openBIMdisk/blob/main/openBIMdisk/Architecture.png)
## Usage
You can use the <kbd>clone</kbd> script to download this repository to your local devices.
<p>`git clone https://github.com/KarleKong/openBIMdisk`
<p>The recommanded python version is 3.8. To run the openBIMdisk, firstly `cd openBIMdisk/apps`, then install the required dependencies through `pip install -r requirements.txt`.
### Blockchain 3.0 backbone
The Blockchain 3.0 backbone extends a cached layer for BIM data indexing, querying, and analysing. The BIM change contract (BCC) serves as a communication bridge between both the Blockchain 2.0 network and the cached layer, enabling off-line data storage and on-line data synchronization.
### tSDT model
The traceable Semantic Differential Transaction (tSDT) model incorporates two key features: (1) remove duplicated instances of BIM semantics; and (2) indexing BIM data such as Id, GUID, change type, etc., and further storing them on a local cached database for querying of BIM semantic changes.
## Application UI
![image](https://github.com/KarleKong/openBIMdisk/blob/main/openBIMdisk/UserInterface.png)
## License
[Apache License 2.0](https://github.com/KarleKong/openBIMdisk/blob/main/LICENSE)
