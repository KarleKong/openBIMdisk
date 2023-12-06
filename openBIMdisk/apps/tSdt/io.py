import base64
import gzip
import json
import os.path


class SdtIO:
  def dict_to_base85file(sdt_filename: str, jsonData: dict):
    """
      gzip + base85 compression.
      useful for compressing long names like 'IfcRelDefinesByProperties-01ee860a187e8be6356508532080e6e05648c63c'
    """
    content = json.dumps(jsonData, indent=None, separators=(',', ':'))
    bytes_com = gzip.compress(content.encode('utf-8'))
    base64_data = base64.b85encode(bytes_com)
    base64_str = str(base64_data.decode())
    with open(sdt_filename, 'w') as outfile:
      outfile.write(base64_str)
    return sdt_filename
  

  def base85file_to_dict(sdt_filename: str) -> dict:
    """
      gzip + base85 compression.
      useful for compressing long names like "Ifc"
    """
    with open(sdt_filename, 'r') as infile:
      content = infile.read()
    base64_data = base64.b85decode(content)
    bytes_decom = gzip.decompress(base64_data)
    str_unzip = bytes_decom.decode()
    ret = json.loads(str_unzip)
    return ret

