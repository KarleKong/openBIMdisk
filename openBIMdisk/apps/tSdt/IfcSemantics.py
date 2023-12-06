import hashlib
import json



class IfcSemantics:
  def __init__(self):
    self.data = {}
    self.dict = {}
    self.dict_hash = {}
    self.dict_rev = {}
    self.dict_hash_rev = {}
    self.dict_obj = {}
    self.dict_obj_trim = {}
    self.dict_cnt = {}
    self.dict_hash_cnt = {}
    self.tmp_GUID_obj = {}
    self.tmp_GUID_obj_trim = {}
    self.type_cnt = {}
    self.hashed_type_cnt = {}
    self.conf_unordered_list = {'hasProperties', 'cfsFaces'}
    self.comp_use_name = {'IfcDistributionPort', 'IfcRelConnectsPortToElement'}
    self.hash_final_types = {'IfcShapeRepresentation', 'IfcRelDefinesByProperties', 'IfcRelAssociatesMaterial'}
    self.ignore_parent_ref = {'contextOfItems': None, 'parentContext': None, 'ofProductRepresentation': None, 'propertyDefinitionOf': None, 'relatedOpeningElement': None, 'isDefinedBy': None, 'hasAssociations': None, 'hasFillings': None}
    self.ignore_self_ref = {'representationMap': None, 'representationsInContext': None}
  
  def put(self, key, val):
    self.dict[key] = val
  
  def get(self, key):
    return self.dict[key]
  
  def remove(self, key):
    self.dict.pop(key, None)
  
  def contains(self, key):
    return key in self.dict
  
  def loadjson(self, fname):
    with open(fname) as json_file:
      self.data = json.load(json_file)
      self.sortdata()

  """
   def loadxml(self, fname):
      with open(fname) as xml_file:
        self.data = xmltodict.parse(xml_file)
        self.sortdata()
  """


  def setjson(self, jsonData):
    jsonStr = json.dumps(jsonData, sort_keys=True, indent=None, separators=(',', ':'))   #serialize an obj to a Json formatted str
    self.data = json.loads(jsonStr)
    self.sortdata()
  
  def sortdata(self):
    to_pop = []
    self.data['data_type'] = {}
    for i in range(len(self.data['data'])):
      if 'type' in self.data['data'][i]:
        key = self.data['data'][i]['type']
        if key in self.data['data_type']:
          self.data['data_type'][key].append(self.data['data'][i])
        else:
          self.data['data_type'][key] = [self.data['data'][i]]
        to_pop.insert(0, i)
    for i in to_pop:
      self.data['data'].pop(i)
    if len(self.data['data']) == 0:
      self.data.pop('data', None)
  
  def adddict(self, old_id, new_id, obj):
    # ensure unique
    if new_id in self.dict_cnt:
      self.dict_cnt[new_id] += 1
      self.dict_obj[new_id].append(obj)
      new_id += '#' + str(self.dict_cnt[new_id])
    else:
      self.dict_cnt[new_id] = 1
      self.dict_obj[new_id] = [obj]
    # add to dicts
    true_old_id = old_id
    if old_id in self.dict_rev:
      true_old_id = self.dict_rev[old_id]
      self.dict_rev.pop(old_id, None)
      k_old_id = old_id
      if '#' not in old_id and self.dict_cnt[old_id] == 1:
        self.dict_obj.pop(old_id, None)
    self.dict[true_old_id] = new_id
    self.dict[old_id] = new_id
    self.dict_rev[new_id] = true_old_id
    obj['globalId'] = new_id

  # put the hashed ids and old ids into the hash_dict
  def addhashdict(self, old_id, new_id, obj):
    # ensure unique for 'tagged' instances
    if new_id[:4] == 'Rvt-':
      if new_id in self.dict_hash_cnt:
        self.dict_hash_cnt[new_id] += 1
        self.dict_obj_trim[new_id].append(obj)
        new_id += '#' + str(self.dict_hash_cnt[new_id])
      else:
        self.dict_hash_cnt[new_id] = 1
        self.dict_obj_trim[new_id] = [obj]
    else:
      if new_id in self.dict_hash_cnt:
        self.dict_hash_cnt[new_id] += 1
        self.dict_obj_trim[new_id].append(obj)
      else:
        self.dict_hash_cnt[new_id] = 1
        self.dict_obj_trim[new_id] = [obj]
    # add to hash dicts and its reverse dicts
    true_old_id = old_id
    if old_id in self.dict_hash_rev:
      true_old_id = self.dict_hash_rev[old_id][int(self.dict_hash_cnt[old_id]-1)]
      self.dict_hash_rev.pop(old_id, None)
      if '#' not in old_id and self.dict_hash_cnt[old_id] == 1:
        self.dict_obj_trim.pop(old_id, None)
      #self.dict_hash_rev[new_id] = [true_old_id]

    self.dict_hash[true_old_id] = new_id
    self.dict_hash[old_id] = new_id
    if new_id in self.dict_hash_rev and true_old_id not in self.dict_hash_rev.values():
      self.dict_hash_rev[new_id].append(old_id)
    else:
      self.dict_hash_rev[new_id] = [true_old_id]
    obj['globalId'] = new_id

  def removeDup(self):
    for k in self.dict_obj_trim:
      if len(self.dict_obj_trim[k]) > 1:
        for i in range(len(self.dict_obj_trim[k])):
          if i != 0:
            self.dict_obj_trim[k][i].clear()

  def getUniqueObjKey(self, obj):
    ukey = ''
    if 'type' in obj:
      ukey = obj['type']
    if 'contextIdentifier' in obj:
      ukey += '-' + obj['contextIdentifier']
    return ukey
  
  def sort_list_by_value(self, obj, k):
    hashed = {}
    for i in range(len(obj[k])):
      hashed[i] = self.hashcode(obj[k][i])
    
    obj[k] = hashed

  def load(self, obj):
    # print(type(obj), obj)
    if isinstance(obj, list):
      for i in range(len(obj)):
        if isinstance(obj[i], dict) or isinstance(obj[i], list):
          self.load(obj[i])
        if isinstance(obj[i], float):
          obj[i] = round(obj[i], 6)
    elif isinstance(obj, dict):
      if 'globalId' in obj:
        old_id = obj['globalId']
        if 'type' in obj and 'tag' in obj:
          new_id = 'Rvt-' + obj['type'] + '-' + obj['tag']
          self.adddict(old_id, new_id, obj)
        elif 'type' in obj and 'name' in obj and obj['type'] in self.comp_use_name:
          truename = obj['name']
          if '|' in truename:
            truename = truename[:truename.index('|')]
            obj['name'] = truename
          new_id = 'Rvt-' + obj['type'] + '-' + truename
          self.adddict(old_id, new_id, obj)
        else:
          self.dict[obj['globalId']] = None
          self.tmp_GUID_obj[obj['globalId']] = obj
        if 'type' in obj:
          ukey = self.getUniqueObjKey(obj)
          if ukey in self.hashed_type_cnt:
            self.hashed_type_cnt[ukey] += 1
          else:
            self.hashed_type_cnt[ukey] = 1
      for k in obj:
        v = obj[k]
        if isinstance(v, dict) or isinstance(v, list):
          self.load(v)
        if isinstance(v, float):
          obj[k] = round(v, 6)
        if isinstance(obj[k], list) and k in self.conf_unordered_list:
          obj[k].sort(key=lambda x: self.hashcode(x), reverse=False)

  def loadHashedObj(self, obj):
    #print(type(obj), obj)
    if isinstance(obj, list):
      for i in range(len(obj)):
        if isinstance(obj[i], dict) or isinstance(obj[i], list):
          self.loadHashedObj(obj[i])
        if isinstance(obj[i], float):
          obj[i] = round(obj[i], 6) #round the float to 6 decimal digits
    elif isinstance(obj, dict):
      if 'globalId' in obj:
        old_id = obj['globalId']
        if 'type' in obj and 'tag' in obj:
          new_id = 'Rvt-' + obj['type'] + '-' + obj['tag']
          self.addhashdict(old_id, new_id, obj) # add the mapping between old_id and new_id
        elif 'type' in obj and 'name' in obj and obj['type'] in self.comp_use_name:
          truename = obj['name']
          if '|' in truename:
            truename = truename[:truename.index('|')]
            obj['name'] = truename
          new_id = 'Rvt-' + obj['type'] + '-' + truename
          self.addhashdict(old_id, new_id, obj)
        else:
          self.dict_hash[obj['globalId']] = None
          self.tmp_GUID_obj_trim[obj['globalId']] = obj
        # Count the instances number of different type, e.g. IfcPropertySet etc.
        if 'type' in obj:
          ukey = self.getUniqueObjKey(obj)
          if ukey in self.type_cnt:
            self.type_cnt[ukey] += 1
          else:
            self.type_cnt[ukey] = 1
      for k in obj:
        v = obj[k]
        if isinstance(v, dict) or isinstance(v, list):
          self.loadHashedObj(v)
        if isinstance(v, float):
          obj[k] = round(v, 6)
        if isinstance(obj[k], list) and k in self.conf_unordered_list:
          obj[k].sort(key=lambda x: self.hashcode(x), reverse=False)
  
  def loadUniqueType(self, obj):
    if isinstance(obj, list):
      for v in obj:
        if isinstance(v, dict) or isinstance(v, list):
          self.loadUniqueType(v)
    elif isinstance(obj, dict):
      if 'globalId' in obj:
        old_id = obj['globalId']
        ukey = self.getUniqueObjKey(obj)
        if ukey in self.hashed_type_cnt and self.hashed_type_cnt[ukey] == 1:
          new_id = ukey + '#1'
          self.adddict(old_id, new_id, obj)
          #self.addhashdict(old_id, new_id, obj)
      for k in obj:
        v = obj[k]
        if isinstance(v, dict) or isinstance(v, list):
          self.loadUniqueType(v)

  def loadUniqueHashType(self, obj):
    if isinstance(obj, list):
      for v in obj:
        if isinstance(v, dict) or isinstance(v, list):
          self.loadUniqueHashType(v)
    elif isinstance(obj, dict):
      if 'globalId' in obj:
        old_id = obj['globalId']
        ukey = self.getUniqueObjKey(obj)
        if ukey in self.type_cnt and self.type_cnt[ukey] == 1:
          new_id = ukey + '#1'
          self.addhashdict(old_id, new_id, obj)
      for k in obj:
        v = obj[k]
        if isinstance(v, dict) or isinstance(v, list):
          self.loadUniqueHashType(v)

  def resetRef(self, obj):
    #top_level = False
    if obj is None:
      obj = self.data
      #top_level = True
    if isinstance(obj, list):
      for v in obj:
        if isinstance(v, dict) or isinstance(v, list):
          self.resetRef(v)
    elif isinstance(obj, dict):
      if 'globalId' in obj:
        if obj['globalId'] in self.dict and self.dict[obj['globalId']] is not None:
          obj['globalId'] = self.dict[obj['globalId']]
      if 'ref' in obj:
        if obj['ref'] in self.dict and self.dict[obj['ref']] is not None:
          obj['ref'] = self.dict[obj['ref']]
      for k in obj:
        v = obj[k]
        if isinstance(v, dict) or isinstance(v, list):
          self.resetRef(v)
  
  def restoreRef(self, dictionary, dictionary2, obj):
    #top_level = False
    if obj is None:
      obj = self.data
    if isinstance(obj, list):
      for v in obj:
        if isinstance(v, dict) or isinstance(v, list):
          self.restoreRef(dictionary, dictionary2, v)
    elif isinstance(obj, dict):
      if 'globalId' in obj:
        if obj['globalId'] in dictionary and dictionary[obj['globalId']] is not None:
          obj['globalId'] = dictionary[obj['globalId']]
        elif obj['globalId'] in dictionary2 and dictionary2[obj['globalId']] is not None:
          obj['globalId'] = dictionary2[obj['globalId']]
      if 'ref' in obj:
        if obj['ref'] in dictionary and dictionary[obj['ref']] is not None:
          obj['ref'] = dictionary[obj['ref']]
        elif obj['ref'] in dictionary2 and dictionary2[obj['ref']] is not None:
          obj['ref'] = dictionary2[obj['ref']]
      for k in obj:
        v = obj[k]
        if isinstance(v, dict) or isinstance(v, list):
          self.restoreRef(dictionary, dictionary2, v)

  def restoreRef2(self, dictionary, obj):
    if obj is None:
      obj = self.data
    if isinstance(obj, list):
      for v in obj:
        if isinstance(v, dict) or isinstance(v, list):
          self.restoreRef2(dictionary, v)
    elif isinstance(obj, dict):
      if 'globalId' in obj:
        if obj['globalId'] in dictionary and dictionary[obj['globalId']][0] is not None:
          obj['globalId'] = dictionary[obj['globalId']][0]
      if 'ref' in obj:
        if '#' not in obj['ref']:
          if obj['ref'] in dictionary and dictionary[obj['ref']][0] is not None:
            obj['ref'] = dictionary[obj['ref']][0]
        elif "Rvt" not in obj['ref']:
          if obj['ref'] in dictionary and dictionary[obj['ref']][0] is not None:
            obj['ref'] = dictionary[obj['ref']][0]
        else:
          old_id = obj['ref']
          new_id = old_id[:old_id.index('#')]
          obj['ref'] = dictionary[new_id][0]

      for k in obj:
        v = obj[k]
        if isinstance(v, dict) or isinstance(v, list):
          self.restoreRef2(dictionary, v)
  
  def clearInvalidRef(self, obj):
    #top_level = False
    if obj is None:
      obj = self.data
      #top_level = True
    if isinstance(obj, list):
      for v in obj:
        if isinstance(v, dict) or isinstance(v, list):
          self.clearInvalidRef(v)
    elif isinstance(obj, dict):
      if 'ref' in obj:
        if obj['ref'] in self.dict and '#' in obj['ref']:
          ref_old = obj['ref']
          ref_org = ref_old[:ref_old.index('#')]
          print("the ref_org is " + ref_org)
          if ref_old in self.dict_obj and len(self.dict_obj[ref_old]) == 0:
            if ref_org in self.dict_obj and len(self.dict_obj[ref_org]) == 0:
              obj['ref'] = ref_org
      for k in obj:
        v = obj[k]
        if isinstance(v, dict) or isinstance(v, list):
          self.clearInvalidRef(v)

  def clearInvalidRef2(self, obj):
    if obj is None:
      obj = self.data
      # top_level = True
    if isinstance(obj, list):
      for v in obj:
        if isinstance(v, dict) or isinstance(v, list):
          self.clearInvalidRef(v)
    elif isinstance(obj, dict):
      if 'ref' in obj:
        if obj['ref'] in self.dict_hash and '#' in obj['ref']:
          ref_old = obj['ref']
          ref_org = ref_old[:ref_old.index('#')]
          print("the ref_org is " + ref_org)
          if ref_old in self.dict_obj_trim and len(self.dict_obj_trim[ref_old]) == 0:
            if ref_org in self.dict_obj_trim and len(self.dict_obj_trim[ref_org]) == 0:
              obj['ref'] = ref_org
      for k in obj:
        v = obj[k]
        if isinstance(v, dict) or isinstance(v, list):
          self.clearInvalidRef(v)
  
  def hashcode(self, obj):
    s = json.dumps(obj, sort_keys=True, indent=0)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()
  
  def replaceRef(self, obj, str1, str2):
    if isinstance(obj, list):
      for v in obj:
        if isinstance(v, dict) or isinstance(v, list):
          self.replaceRef(v, str1, str2)
    elif isinstance(obj, dict):
      if 'ref' in obj:
        if obj['ref'] == str1:
          obj['ref'] = str2
      for k in obj:
        v = obj[k]
        if isinstance(v, dict) or isinstance(v, list):
          self.replaceRef(v, str1, str2)
  
  def hashGUID(self):
    while True:
      v1 = self.countNone()
      self.hash(None)
      v2 = self.countNone()
      #print(v1, '-->', v2)
      if v2 == 0 or v1 == v2:
        break

  # hash function generates new GUID according to the str of object,
  # by ignoring the globalId (set as '')
  # different obj results to different new globalId
  def hash(self, obj):
    top_level = False
    if obj is None:
      obj = self.data
      top_level = True
    if isinstance(obj, list):
      for v in obj:
        if isinstance(v, dict) or isinstance(v, list):
          self.hash(v)
    elif isinstance(obj, dict):
      if 'globalId' in obj:
        if obj['globalId'] in self.dict and self.dict[obj['globalId']] is None and obj['globalId'][:4] != 'Rvt-':
          old_id = obj['globalId']
          # (1) ignore REF entries
          for e in self.ignore_parent_ref:
            if e in obj:
              self.ignore_parent_ref[e] = obj[e]
              obj[e] = None
          # (2) ignore self-citation
          for e in self.ignore_self_ref:
            if e in obj:
              self.replaceRef(obj[e], old_id, None)
          if not self.hasRandRef(obj):
            obj['globalId'] = ''
            new_id = obj['type'] + '-' + self.hashcode(obj)
            if len(old_id) >= len(new_id) and old_id[:len(new_id)] == new_id:
              obj['globalId'] = old_id
              #self.adddict(old_id, new_id, obj)
            else:
              self.adddict(old_id, new_id, obj)
            #obj['globalId'] = new_id
          # resotre (1)
          for e in self.ignore_parent_ref:
            if e in obj:
              obj[e] = self.ignore_parent_ref[e]
          #  resotre (2)
          for e in self.ignore_self_ref:
            if e in obj:
              self.replaceRef(obj[e], None, old_id)
      for k in obj:
        v = obj[k]
        if isinstance(v, dict) or isinstance(v, list):
          self.hash(v)
    if top_level:
      self.resetRef(None)
    #  print(obj)
  
  def hash_final_item(self, key: str):
    lst = self.data['data_type'][key]
    cnt = 0
    if isinstance(lst, list):
      for obj in lst:
        if isinstance(obj, dict) and 'globalId' in obj:
          old_id = obj['globalId']
          if old_id[:4] == 'Rvt-':
            continue
          obj['globalId'] = ''
          new_id = obj['type'] + '-' + self.hashcode(obj)
          if len(old_id) >= len(new_id) and old_id[:len(new_id)] == new_id:
            obj['globalId'] = old_id
          else:
            self.adddict(old_id, new_id, obj)
            cnt += 1
    # print ('hash_plain :', key, 'changed =', cnt, 'out of', len(lst))
    self.resetRef(None)
  
  def hash_final(self):
    for t in self.hash_final_types:
      self.hash_final_item(t)
    self.resetRef(None)
    self.clearInvalidRef(None)
  
  def finalize(self, dictionary, dictionary2):
    self.toplevelNonempty()
    self.restoreRef(dictionary, dictionary2, None)
    self.toplevel2dict()

  def finalize2(self, dictionary):
    self.toplevelNonempty()
    self.restoreRef2(dictionary, None)
    self.clearInvalidRef2(None)
  
  def hasRandRef(self, obj):
    if isinstance(obj, list):
      for v in obj:
        if isinstance(v, dict) or isinstance(v, list):
          if self.hasRandRef(v):
            return True
    elif isinstance(obj, dict):
      if 'ref' in obj and obj['ref'] is not None:
        if obj['ref'] in self.dict and self.dict[obj['ref']] is None:
          return True
      for k in obj:
        v = obj[k]
        if isinstance(v, dict) or isinstance(v, list):
          if self.hasRandRef(v):
            return True
    return False

  def hasRandRef2(self, obj):
    if isinstance(obj, list):
      for v in obj:
        if isinstance(v, dict) or isinstance(v, list):
          if self.hasRandRef2(v):
            return True
    elif isinstance(obj, dict):
      if 'ref' in obj and obj['ref'] is not None:
        if obj['ref'] in self.dict_hash and self.dict_hash[obj['ref']] is None:
          return True
      for k in obj:
        v = obj[k]
        if isinstance(v, dict) or isinstance(v, list):
          if self.hasRandRef2(v):
            return True
    return False

  # 如果ifc0文件的字典中新的globalId为空(但是有old_id)，同时ifc1文件中有同样Id的instance,则在ifc0文件的字典中添加该instance的old_id,所以在最终的字典中，如果key和value的字段值一致，则说明该instance在两个文件中完全一致
  def addIdentical(self, friendDict):
    for k in self.dict:
      if self.dict[k] is None and friendDict.contains(k):
        self.adddict(k, k, self.tmp_GUID_obj[k])
        self.tmp_GUID_obj.pop(k, None)
    self.resetRef(None)

  def countNone(self):
    ret = 0
    for k in self.dict:
      if self.dict[k] is None:
        #print(k)
        ret += 1
    return ret

  def countHashNone(self):
    ret = 0
    for k in self.dict_hash:
      if self.dict_hash[k] is None:
        ret += 1
    return ret
  
  def countIdentical(self):
    ret = 0
    for k in self.dict:
      if self.dict[k] == k:
        ret += 1
    return ret
  
  def countIntersect(self, foreign):
    ret = 0
    for k in self.dict:
      if foreign.contains(k) and self.dict[k] == foreign.get(k):
        ret += 1
    return ret
  
  def countMapped(self):
    return len(self.dict_rev)
  
  def countRevitID(self):
    ret = 0
    for k in self.dict:
      if self.dict[k] is not None and self.dict[k][:7] == 'RevitID':
        ret += 1
    return ret
  
  def toplevel2dict(self):
    for i in self.data['data_type']:
      if isinstance(self.data['data_type'][i], list):
        lst = self.data['data_type'][i]
        d = {}
        for j in range(len(lst)):
          if isinstance(lst[j], dict) and 'globalId' in lst[j]:
            key = lst[j]['globalId']
          else:
            key = self.hashcode(lst[j])
          #if key in dictionary:
          #  key = dictionary[key]
          #  if 'globalId' in lst[j]:
          #    lst[j]['globalId'] = key
          d[key] = lst[j]
        self.data['data_type'][i] = d
  
  def toplevelNonempty(self):
    for i in self.data['data_type']:
      if isinstance(self.data['data_type'][i], list):
        lst = self.data['data_type'][i]
        to_del = []
        for j in range(len(lst)):
          obj = lst[j]
          if isinstance(obj, dict) and len(obj) == 0:
            to_del.append(j)
        for j in range(len(to_del), 0, -1):
          del lst[to_del[j-1]]
        #print(i, len(to_del) + len(lst), '==>', len(lst))
  
  def apply_sdt(self, sdt, verbose = False):
    for key in sdt['data_type']:
      me = self.data['data_type'][key]
      diff = sdt['data_type'][key]
      # delete [{k: v, k: v}, {}]
      # insert [{}, {k: v, k: v}]
      # del + ins [{k: v, k: v}, {k: v, k: v}]
      # change {'key': [v1, v2]}
      #   delete with change {..., '$delete': {}}
      #   insert with change {..., '$insert': {}}
      if isinstance(diff, list) and len(diff) == 2:
        if len(diff[0]) > 0:
          # del
          for k in diff[0]:
            if verbose:
              print('deleting', k, 'from', key)
            self.delete_globalid_by_sdt(me, k)
        if len(diff[1]) > 0:
          # insert
          for k in diff[1]:
            if verbose:
              print('inserting', k, 'to', key)
            self.add_obj_by_sdt(me, k, diff[1][k])
      elif isinstance(diff, dict):
        if '$delete' in diff:
          # delete
          if isinstance(me, list):
            if isinstance(diff['$delete'], list):
              for i in range(len(diff['$delete'])):
                tar = diff['$delete'][i][0]
                if verbose:
                  print('deleting', tar, 'from', key)
                me.pop(tar)
            elif isinstance(diff['$delete'], dict):
              for k1 in diff['$delete']:
                if verbose:
                  print('deleting', k1, 'from', key)
                #print(me, k1, 'del')
                self.delete_globalid_by_sdt(me, k1)
          elif isinstance(me, dict):
            for k1 in diff['$delete']:
              if verbose:
                print('deleting', k1, 'from', key)
              self.delete_globalid_by_sdt(me, k1)
        if '$insert' in diff:
          # insert
          if isinstance(me, list):
            if isinstance(diff['$insert'], list):
              for i in range(len(diff['$insert'])):
                tar = diff['$insert'][i][0]
                if verbose:
                  print('top-inserting', tar, 'to', key)
                me.insert(tar, diff['$insert'][i][1])
            elif isinstance(diff['$insert'], dict):
              for k in diff['$insert']:
                if verbose:
                  print('top-inserting', k, 'to', key)
                me.append(diff['$insert'][k])
          elif isinstance(me, dict):
            for k1 in diff['$insert']:
              if verbose:
                print('top-inserting', k1, 'to', key)
              self.add_obj_by_sdt(me, k1, diff['$insert'][k1])
        for k in diff:
          if k == '$insert' or k == '$delete':
            continue
          # change
          id = -1
          for i in range(len(me)):
            if 'globalId' in me[i] and me[i]['globalId'] == k:
              id = i
              break
          if id >= 0:
            if verbose:
              print('changing', diff[k], 'at', k)
            self.change_by_sdt(me[id], diff[k], verbose)
    self.types_to_data()

  def addDup_sdt(self, sdt, hashDic, hashDic_rev, objectDic, friendHashDic, friendHashDic_rev, friendObjectDic) -> dict:
    for key in sdt['data_type']:
      diff_val = sdt['data_type'][key]
      if isinstance(diff_val, list) and len(diff_val) == 2:
        for k in diff_val[0]:
          if len(hashDic_rev[hashDic[k]]) > 1:
            for j in range(0, len(hashDic_rev[hashDic[k]])-1):
              diff_val[0].append(objectDic[hashDic_rev[hashDic[k]][j]])
        for k in diff_val[1]:
          if len(friendHashDic_rev[friendHashDic[k]]) > 1:
            for j in range(0, len(friendHashDic_rev[friendHashDic[k]])-1):
              diff_val[0].append(friendObjectDic[friendHashDic_rev[friendHashDic[k]][j]])
    return sdt.data

  def delete_globalid_by_sdt(self, obj_list, gid_to_del):
    if isinstance(obj_list, list):
      id = -1
      for i in range(len(obj_list)):
        if 'globalId' in obj_list[i] and obj_list[i]['globalId'] == gid_to_del:
          id = i
          break
      if id >= 0:
        obj_list.pop(id)
    elif isinstance(obj_list, dict):
      obj_list.pop(gid_to_del, None)
  
  def add_obj_by_sdt(self, obj, key, val):
    if isinstance(obj, dict):
      obj[key] = val
    elif isinstance(obj, list):
      obj.append(val)
  
  def change_by_sdt(self, obj, diff, verbose=False, parent_dict = None, key = None):
    #print(obj, diff)
    if isinstance(diff, list) and len(diff) == 2 and key != None:
      if parent_dict is not None and key is not None:
        parent_dict[key] = diff[1]
    elif isinstance(diff, dict) and len(diff) >0:
      if '$delete' in diff:
        if isinstance(obj, list):
          for i in range(len(diff['$delete'])):
            tar = diff['$delete'][i][0]
            if verbose:
              print('call-deleting', tar, 'from', key)
            obj.pop(tar)
        elif isinstance(obj, dict):
          for i in diff['$delete']:
            if verbose:
              print('call-deleting', i, 'from', key)
            self.delete_globalid_by_sdt(obj, i)
      if '$insert' in diff:
        if isinstance(obj, list):
          for i in range(len(diff['$insert'])):
            if verbose:
              print('call-inserting', diff['$insert'][i][1], 'to', key, 'at', diff['$insert'][i][0])
            obj.insert(diff['$insert'][i][0], diff['$insert'][i][1])
        elif isinstance(obj, dict):
          for k1 in diff['$insert']:
            if verbose:
              print('call-inserting', k1, 'to', key)
            self.add_obj_by_sdt(obj, k1, diff['$insert'][k1])
      if key is not None and isinstance(obj, list):
        for k in diff:
          if k == '$insert' or k == '$delete':
            continue
          tar = int(k)
          self.change_by_sdt(obj[tar], diff[k], verbose)
      for k in diff:
        if k in obj:
          self.change_by_sdt(obj[k], diff[k], verbose, obj, k)
  
  def types_to_data(self):
    self.data['data'] = []
    for t in self.data['data_type']:
      for obj in self.data['data_type'][t]:
        self.data['data'].append(obj)
    self.data['data_type'].clear()
    self.data.pop('data_type', None)
  
  def printObj(self):
    print(self.data)
  
  def getObj(self):
    return self.data
  
  def getDictObj(self):
    return self.dict_obj

  def uniqueHashGUID(self):
    while True:
      v1 = self.countHashNone()
      self.hashObject(None)
      v2 = self.countHashNone()
      # print(v1, '-->', v2)
      if v2 == 0 or v1 == v2:
        break

  def hashObject(self, obj):
    top_level = False
    if obj is None:
      obj = self.data
      top_level = True
    if isinstance(obj, list):
      for v in obj:
        if isinstance(v, dict) or isinstance(v, list):
          self.hashObject(v)
    elif isinstance(obj, dict):
      if 'globalId' in obj:
        if obj['globalId'] in self.dict_hash and self.dict_hash[obj['globalId']] is None and obj['globalId'][:4] != 'Rvt-':
          old_id = obj['globalId']
          # (1) ignore REF entries
          for e in self.ignore_parent_ref:
            if e in obj:
              self.ignore_parent_ref[e] = obj[e]
              obj[e] = None
          # (2) ignore self-citation
          for e in self.ignore_self_ref:
            if e in obj:
              self.replaceRef(obj[e], old_id, None)
          if not self.hasRandRef2(obj):
            obj['globalId'] = ''
            new_id = obj['type'] + '-' + self.hashcode(obj)
            if len(old_id) >= len(new_id) and old_id[:len(new_id)] == new_id:
              obj['globalId'] = old_id
            else:
              self.addhashdict(old_id, new_id, obj)
          # resotre (1)
          for e in self.ignore_parent_ref:
            if e in obj:
              obj[e] = self.ignore_parent_ref[e]
          #  resotre (2)
          for e in self.ignore_self_ref:
            if e in obj:
              self.replaceRef(obj[e], None, old_id)
      for k in obj:
        v = obj[k]
        if isinstance(v, dict) or isinstance(v, list):
          self.hashObject(v)
    if top_level:
      self.resetHashRef(None)

  def resetHashRef(self, obj):
    #top_level = False
    if obj is None:
      obj = self.data
      #top_level = True
    if isinstance(obj, list):
      for v in obj:
        if isinstance(v, dict) or isinstance(v, list):
          self.resetHashRef(v)
    elif isinstance(obj, dict):
      if 'globalId' in obj:
        if obj['globalId'] in self.dict_hash and self.dict_hash[obj['globalId']] is not None:
          obj['globalId'] = self.dict_hash[obj['globalId']]
      if 'ref' in obj:
        if obj['ref'] in self.dict_hash and self.dict_hash[obj['ref']] is not None:
          obj['ref'] = self.dict_hash[obj['ref']]
      for k in obj:
        v = obj[k]
        if isinstance(v, dict) or isinstance(v, list):
          self.resetHashRef(v)