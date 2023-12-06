# IFCJSON_python - ifc2json.py
# Convert IFC.JSON to SPF
# https://github.com/IFCJSON-Team

# MIT License

# Copyright (c) 2020 Jan Brouwer <jan@brewsky.nl>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from time import perf_counter
import os
import argparse
from apps.tSdt.third_party.ifcjson.to_ifcopenshell import JSON2IFC

def convert2ifc(jsonFilePath, ifcFilePath):
    start_time = perf_counter()
    parser = argparse.ArgumentParser(
        description='Convert IFC.JSON to SPF')
    parser.add_argument('-i', type=str, help='input json file path')
    parser.add_argument('-o', type=str, help='output ifc file path')
    args = parser.parse_args()
    # jsonFilePath = 'files/demo2023/restore_results/t0307.ifcjson'
    # ifcFilePath = 'files/demo2023/restore_results/t0309.ifc'
    if args.i:
        jsonFilePath = args.i
    if os.path.isfile(jsonFilePath):
        if args.o:
            ifcFilePath = args.o
        else:
            ifcFilePath = os.path.splitext(jsonFilePath)[0] + '.ifc'
        ifc_json = JSON2IFC(jsonFilePath)
        ifc_model = ifc_json.ifcModel()
        ifc_model.write(ifcFilePath)
        print("Conversion took ", perf_counter()-start_time, " seconds")
    else:
        print(str(args.i) + ' is not a valid file')
