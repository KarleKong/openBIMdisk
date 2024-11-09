import pathlib
import time
from apps.tSdt.third_party.jsondiff import diff
from apps.tSdt.third_party.ifcjson import *
from apps.tSdt.IfcSemantics import *
from apps.tSdt.io import *
import os


class IfcSdt:
  Verbose = False
  time_elapsed = 0
  current_sdt = None
  result_folder = 'result/'

  # def logfolder(projName):
  #   folder_name = projName
  #   LOG_FOLDER = 'log/'
  #   logfolder = os.path.join(LOG_FOLDER, folder_name)
  #   if not os.path.exists(logfolder):
  #       os.makedirs(logfolder)
  #   return logfolder
  
  # log_folder = logfolder("demo/")
  
  
  def load_ifc(self, ifc_filename: str, jsonfile: str) -> IfcSemantics:
    pathlib.Path(self.log_folder).mkdir(parents=True, exist_ok=True)
    jsonData = IFC2JSON4(ifc_filename, COMPACT=True, NO_INVERSE=True).spf2Json()
    idDict = jsonData['idMap']
    groupObj = jsonData['group']
    jsonData.pop('timeStamp', None)
    jsonData.pop('idMap', None)
    jsonData.pop('group', None)
    ifc = IfcSemantics()
    ifc.setjson(jsonData)
    return ifc, idDict, groupObj

  
  def load_ifcjson(self, ifcjson_filename: str) -> IfcSemantics:
    ifc = IfcSemantics()
    ifc.loadjson(ifcjson_filename)
    return ifc

  def load_ifcxml(self, ifcxml_filename: str, jsonfile: str) -> IfcSemantics:
    pathlib.Path(self.log_folder).mkdir(parents=True, exist_ok=True)
    fileptr = open(ifcxml_filename, 'r', encoding="utf8")
    xmlcontent = fileptr.read()
    jsonData = xmltodict.parse(xmlcontent)
    ifc = IfcSemantics()
    ifc.setjson(jsonData)
    if self.Verbose:
      with open(self.log_folder + '0-' +jsonfile, 'w') as outfile:
        json.dump(jsonData, outfile, sort_keys=True, indent=2)
    return ifc
  
  def reporting_instance_mapping(self, ifc0, ifc1, msg):
    print(msg)
    print('File\t', 'Identical', 'Map-RvtID', 'Intersection', 'As-None')
    print('IFC0\t', ifc0.countIdentical(),'\t', ifc0.countMapped(), '\t', ifc0.countIntersect(ifc1), '\t', ifc0.countNone())
    print('IFC1\t', ifc1.countIdentical(),'\t', ifc1.countMapped(), '\t', ifc1.countIntersect(ifc0), '\t', ifc1.countNone())
    print()

  def log_ifc_data(self, ifc0, ifc1, fname):
    pathlib.Path(self.log_folder).mkdir(parents=True, exist_ok=True)
    with open(self.log_folder + fname + '-0.json', 'w') as outfile:
      data = {'ifc': ifc0.data}
      json.dump(data, outfile, indent=2, sort_keys=True)
    with open(self.log_folder + fname + '-1.json', 'w') as outfile:
      data = {'ifc': ifc1.data}
      json.dump(data, outfile, indent=2, sort_keys=True)

  def log_ifcjson(self, ifc0, fname):
    pathlib.Path(self.log_folder).mkdir(parents=True, exist_ok=True)
    with open(self.log_folder + fname + '.ifcjson', 'w') as outfile:
      data = {'data': ifc0.data}
      json.dump(data, outfile, indent=2, sort_keys=True)

  def log_model_dicts(self, ifc0, ifc1, fname):
    pathlib.Path(self.log_folder).mkdir(parents=True, exist_ok=True)
    with open(self.log_folder + fname +'-0.json', 'w') as outfile:
      data = {'guid_dict': ifc0.dict, 'guid_dict_rev': ifc0.dict_rev}
      json.dump(data, outfile, indent=2, sort_keys=True)
    with open(self.log_folder + fname +'-1.json', 'w') as outfile:
      data = {'guid_dict': ifc1.dict, 'guid_dict_rev': ifc1.dict_rev}
      json.dump(data, outfile, indent=2, sort_keys=True)

  def log_model_hashed_dicts(self, ifc0, ifc1, fname):
    pathlib.Path(self.log_folder).mkdir(parents=True, exist_ok=True)
    with open(self.log_folder + fname + '-0.json', 'w') as outfile:
      data = {'hash_dict': ifc0.hashed_type_cnt}
      json.dump(data, outfile, indent=2, sort_keys=True)
    with open(self.log_folder + fname + '-1.json', 'w') as outfile:
      data = {'hash_dict': ifc1.hashed_type_cnt}
      json.dump(data, outfile, indent=2, sort_keys=True)

  def log_object_dicts(self, ifc0, ifc_name, fname):
    pathlib.Path(self.log_folder).mkdir(parents=True, exist_ok=True)
    with open(self.log_folder + fname + '-' + ifc_name + '.json', 'w') as outfile:
      data = {'obj_dict': ifc0.dict_obj_trim}
      json.dump(data, outfile, indent=2, sort_keys=True)

  def log_hash_dicts(self, ifc, ifc_name, fname):
    pathlib.Path(self.log_folder).mkdir(parents=True, exist_ok=True)
    with open(self.log_folder + fname + '-' + ifc_name + '.json', 'w') as outfile:
        data = {'hash_dict': ifc.dict_hash, 'hash_dict_rev': ifc.dict_hash_rev}
        json.dump(data, outfile, indent=2, sort_keys=True)
    with open(self.log_folder + fname + '-' + ifc_name + '-cnt.json', 'w') as outfile:
        data = {'hash_dict_cnt': ifc.dict_hash_cnt}
        json.dump(data, outfile, indent=2, sort_keys=True)

  def log_dict_cnt(self, ifc0, ifc1, fname):
    pathlib.Path(self.log_folder).mkdir(parents=True, exist_ok=True)
    with open(self.log_folder + fname + '-0.json', 'w') as outfile:
      data = {'dict_cnt': ifc0.dict_cnt}
      json.dump(data, outfile, indent=2, sort_keys=True)
    with open(self.log_folder + fname + '-1.json', 'w') as outfile:
      data = {'dict_cnt': ifc1.dict_cnt}
      json.dump(data, outfile, indent=2, sort_keys=True)

  def log_models(self, ifc0, ifc1, fname):
    pathlib.Path(self.log_folder).mkdir(parents=True, exist_ok=True)
    with open(self.log_folder + fname +'-0.json', 'w') as outfile:
      json.dump(ifc0.getObj(), outfile, indent=2, sort_keys=True)
    with open(self.log_folder + fname +'-1.json', 'w') as outfile:
      json.dump(ifc1.getObj(), outfile, indent=2, sort_keys=True)

  def log_singlefile_models(self, ifc0, fname):
    pathlib.Path(self.log_folder).mkdir(parents=True, exist_ok=True)
    with open(self.log_folder + fname +'.json', 'w') as outfile:
      json.dump(ifc0.getObj(), outfile, indent=2, sort_keys=True)

  def addDup_sdt(self, sdt, hashDic, hashDic_rev, objectDic, friendHashDic, friendHashDic_rev, friendObjectDic) -> dict:
    for key in sdt['data_type']:
      diff_val = sdt['data_type'][key]
      if isinstance(diff_val, list) and len(diff_val) == 2:
        #print(str(diff_val[0]))
        for k in list(diff_val[0]):
          if len(hashDic_rev[hashDic[k]]) > 1:
            for j in range(1, len(hashDic_rev[hashDic[k]])-1):
              print("The hashDic[k] is " + hashDic[k])
              print("The reverse hash is " + hashDic_rev[hashDic[k]][j])
              diff_val[0][hashDic_rev[hashDic[k]][j]] = objectDic[hashDic[k]][0]
        for k in list(diff_val[1]):
          if len(friendHashDic_rev[friendHashDic[k]]) > 1:
            for j in range(1, len(friendHashDic_rev[friendHashDic[k]])-1):
              diff_val[1][friendHashDic_rev[friendHashDic[k]][j]] = friendObjectDic[friendHashDic[k]][0]
    return sdt

  def clear_dictionary(self, ifc: IfcSemantics):
    ifc.dict_hash.clear()
    ifc.dict_hash_rev.clear()
    ifc.dict_hash_cnt.clear()
    ifc.dict_obj_trim.clear()

  def log_addDup_sdt(self, sdt, fname):
    pathlib.Path(self.log_folder).mkdir(parents=True, exist_ok=True)
    with open(self.log_folder + fname + '.json', 'w') as outfile:
      json.dump(sdt, outfile, indent=2, sort_keys=True)

  def restore_sdt(self, ifcjson_filename: str, sdt_t1: str, hashDic: str, friendHashDic: str, objectDic: str, friendObjectDic: str) -> dict:
    t_file_start = time.time()
    # load IFC json
    ifc0 = IfcSemantics()
    ifc0.loadjson(ifcjson_filename)
    sdt = SdtIO.base85file_to_dict(sdt_t1)
    print("The Object dictionary is " + objectDic)
    # restore duplicated objects in sdt
    with open(hashDic, 'r') as loadHashDic:
      hashDic = json.load(loadHashDic)
    with open(friendHashDic, 'r') as loadFhashDic:
      friendHashDic = json.load(loadFhashDic)
    with open(objectDic, 'r') as loadObjDic:
      objectDic = json.load(loadObjDic)
    with open(friendObjectDic, 'r') as loadfObjDic:
      friendObjectDic = json.load(loadfObjDic)
    dupSDT = self.addDup_sdt(sdt, hashDic['hash_dict'], hashDic['hash_dict_rev'], objectDic['obj_dict'], friendHashDic['hash_dict'], friendHashDic['hash_dict_rev'], friendObjectDic['obj_dict'])
    if self.Verbose:
      print('>SDT restored in ' + str(round(time.time()-t_file_start, 3)) + 's.\n')
      self.log_addDup_sdt(dupSDT, '9-restored-sdt')
    #print(sdt)
    if self.Verbose:
      print('>IFC files converted and loaded in ' + str(round(time.time() - t_file_start, 3))+ 's.\n')
    
    starttime = time.time()
    ifc0.apply_sdt(sdt, self.Verbose)
    self.time_elapsed = time.time() - starttime
    
    if self.Verbose:
      with open(self.log_folder + '10-restored.json', 'w') as outfile:
        json.dump(ifc0.data, outfile, indent=2)
    
    return ifc0.data


  def remove_minor_dup(self, ifc_file: str) -> IfcSemantics:
    t_file_start = time.time()
    if ifc_file[-4:].lower() == '.ifc':
      if self.Verbose:
        print('>Start handling .ifc files ...')
        print('Loading ' + ifc_file + ' ...')
      fileName = ifc_file.split("-v")[1].lower().replace(".", "_")
      ifc0, idDict0, groupObj= self.load_ifc(ifc_file, fileName + '.ifcjson')
    elif ifc_file[-8:].lower() == '.ifcjson':
      if self.Verbose:
        print('>Start handling ifcJSON files ...')
        print('Loading ' + ifc_file + ' ...')
      ifc0 = self.load_ifcjson(ifc_file)
    else:
      if self.Verbose:
        print('>Start handling .ifcxml files ...')
        print('Loading ' + ifc_file + ' ...')
      fileName = ifc_file[-5:].lower().replace(".", "_")
      ifc0 = self.load_ifcxml(ifc_file, fileName + '.ifcjson')
    if self.Verbose:
      print('>IFC files converted and loaded in ' + str(round(time.time() - t_file_start, 3)) + 's.\n')


    # step 1: hash GUIDs and create the hash dictionary
    starttime = time.time()
    # loading initial objects and add Rvt entities into the dict
    ifc0.loadHashedObj(ifc0.data)
    # Adding unique entities
    ifc0.loadUniqueHashType(ifc0.data)
    # Hashing GUIDs
    ifc0.uniqueHashGUID()
    """
        if self.Verbose:
      self.log_object_dicts(ifc0, ifc_file[-5], '0.5-Fully-Hashed-Objects')
    """


    # Step 2: remove the duplicated properties, relationships and replace the reference
    ifc0.removeDup()
    if self.Verbose:
      self.log_hash_dicts(ifc0, ifc_file.split("-v")[1].lower().replace(".ifc",""), '1-hash-GUID')
    ifc0.finalize2(ifc0.dict_hash_rev)

    if self.Verbose:
      self.log_object_dicts(ifc0, ifc_file.split("-v")[1].lower().replace(".ifc",""), '1-Final-Trimmed-Objects')

    # Record time
    self.time_elapsed = time.time() - starttime

    return ifc0, idDict0, groupObj

  def compute_diff(self, ifc0: IfcSemantics, ifc1: IfcSemantics) -> dict:
    
    # Step 1: Adding the hashed guid to dict
    ifc0.load(ifc0.data)
    ifc1.load(ifc1.data)
    """
        if self.Verbose:
      self.log_ifc_data(ifc0, ifc1, '1.5-loaded-ifc-data')
    """
    # Remove the same-Ids objects according to the hash GUID dict generated in the RemoveDup proces
    
    ifc0.loadUniqueType(ifc0.data)
    ifc1.loadUniqueType(ifc1.data)
    ifc0.addIdentical(ifc1)
    ifc1.addIdentical(ifc0)
    ifc0.hashGUID()
    ifc1.hashGUID()
    ifc0.addIdentical(ifc1)
    ifc1.addIdentical(ifc0)

    # Step 2: removal of duplicated subtrees
    dict0 = ifc0.getDictObj()
    dict1 = ifc1.getDictObj()
    for k in dict0:
      if k in dict1:
        if len(dict0[k]) == 1 and len(dict1[k]) == 1:
          s1 = json.dumps(dict0[k][0], indent=None, sort_keys=True)
          s2 = json.dumps(dict1[k][0], indent=None, sort_keys=True)
          if s1 == s2:
            dict0[k][0].clear()
            dict1[k][0].clear()
        elif len(dict0[k]) == len(dict1[k]):
          for i in range(len(dict0[k])):
            s1 = json.dumps(dict0[k][i], indent=None, sort_keys=True)
            s2 = json.dumps(dict1[k][i], indent=None, sort_keys=True)
            if s1 == s2:
              dict0[k][i].clear()
              dict1[k][i].clear()
    ifc0.hash_final()
    ifc1.hash_final()
    ifc0.addIdentical(ifc1)
    ifc1.addIdentical(ifc0)
    if self.Verbose:
      print("Start computing difference of two IFC files ...")
    starttime = time.time()
    dict0 = ifc0.getDictObj()
    dict1 = ifc1.getDictObj()
    for k in dict0:
      if k in dict1:
        if len(dict0[k]) == 1 and len(dict1[k]) == 1:
          s1 = json.dumps(dict0[k][0], indent=None, sort_keys=True)
          s2 = json.dumps(dict1[k][0], indent=None, sort_keys=True)
          if s1 == s2:
            dict0[k][0].clear()
            dict1[k][0].clear()
        elif len(dict0[k]) == len(dict1[k]):
          for i in range(len(dict0[k])):
            if 'globalId' in dict0[k][i] and dict0[k][i]['globalId'] == dict1[k][i]['globalId']:
              dict0[k][i].clear()
              dict1[k][i].clear()
            else:
              s1 = json.dumps(dict0[k][i], indent=None, sort_keys=True)
              s2 = json.dumps(dict1[k][i], indent=None, sort_keys=True)
              if s1 == s2:
                dict0[k][i].clear()
                dict1[k][i].clear()
    """
        if self.Verbose:
      self.log_models(ifc0, ifc1, '2.2-selected-diff-instances')
      #self.log_dict_cnt(ifc0, ifc1, '2.2-hashed-type-cnt')
      self.log_model_dicts(ifc0, ifc1, '2.2-diff-GUID')
    """
    # Step 3: completion, compute diff
    ifc0.finalize(ifc0.dict_rev, ifc1.dict_rev)
    ifc1.finalize(ifc0.dict_rev, ifc1.dict_rev)
    """
        if self.Verbose:
      self.log_models(ifc0, ifc1, '3-instances-to-compare')
    """
    result = diff(ifc0.getObj(), ifc1.getObj(), syntax='symmetric', marshal=True)

    # record time
    self.time_elapsed = time.time() - starttime
    if self.Verbose:
      print('>IFC files compute in ' + str(round(self.time_elapsed,2)) + 's.\n')
    self.current_sdt = result
    if self.Verbose:
      with open(self.log_folder + '2-diff-unzipped.json', 'w') as outfile:
        json.dump(result, outfile, indent=2)
    return result















