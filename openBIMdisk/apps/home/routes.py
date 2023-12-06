from apps.home import blueprint
from jinja2 import TemplateNotFound
import sqlite3
import os
from flask import  render_template, redirect, request, url_for, session, send_from_directory, g, flash, jsonify
from flask_login import (
    current_user,
    login_required,
)
from werkzeug.utils import secure_filename
import argparse
from apps.tSdt.IfcSdt import *
from apps.tSdt.io import *
# from apps.tSdt.third_party import json2ifc
# from flask_bootstrap import Bootstrap
import time
from hfc.fabric import Client
import sys,asyncio
from apps import config
# from pyecharts.charts import Bar, Timeline
import json

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
database_dir = os.path.join(basedir, 'db.sqlite3')
allowed_extension = config.Config.ALLOWED_EXTENSIONS
upload_folder = config.Config.UPLOAD_FOLDER
output_diff = config.Config.OUTPUT_FOLDER_DIFF
output_restore = config.Config.OUTPUT_FOLDER_RESTORE
log_folder = config.Config.LOG_FOLDER
sqlDB =config.Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
fabric_folder = config.Config.FABRIC_FOLDER
project = "WCH"

def allowed_file_type(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extension

def file_exists(filename):
    return os.path.exists(os.path.join(upload_folder, filename))

@blueprint.route('/index')
@login_required
def index():
    conn = sqlite3.connect(database_dir)
    cursor = conn.cursor()
    currentUser = current_user.username
    cursor.execute("SELECT username, role, orgName FROM Users where username != '" + currentUser + "'")
    userList = cursor.fetchall()
    conn.close()
    return render_template('home/index.html', segment='index', userList=userList)


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500

# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
    
    # function route

@blueprint.route('/to_tsdt', methods=['POST','GET'])
@login_required
def to_tsdt():
    if request.method == 'GET':
        return redirect(url_for('home_blueprint.uploaded_file'))

@blueprint.route('/file', methods=['POST'])
@login_required
def file():
    if request.method == 'POST':
        to_upload_files = request.files.getlist("file")
        for file in to_upload_files:
            if file and allowed_file_type(file.filename) and not file_exists(file.filename):
                filename = secure_filename(file.filename)
                upload_path = os.path.join(upload_folder, filename).replace('\\','/')
                file.save(upload_path)
            elif file and allowed_file_type(file.filename):
                flash('File with the same name already exists')
    return jsonify({'fileNames': file.filename})

@blueprint.route('/uploaded_file', methods=['GET','POST']) 
def uploaded_file():
    logFolders= []
    for dirname in os.listdir(os.path.join(log_folder, "WCH")):
        logFolders.append(dirname)
    return render_template('home/tSDT_computing.html', logFolders=logFolders)

@blueprint.route('/download/<filename>', methods=['GET'])
def download(filename):
    if request.method == 'GET':
        path = os.path.isfile(os.path.join(upload_folder,filename))
        if path:
            return send_from_directory(upload_folder, filename, as_attachment=True)


@blueprint.route('/tsdt_function', methods = ['POST'])
def tsdt_function():
    if request.method == 'POST':
        data = request.json
        files = data.get('fileNames', [])
        fileName1 = files[0]
        fileName2 = files[1]
        file_pth_1 = os.path.join(upload_folder,fileName1)
        file_pth_2 = os.path.join(upload_folder,fileName2)
        result_filePath, result_changeData, module_data = my_sdt_route(file_pth_1, file_pth_2, project)
        # upload to blockchain network
        user_name = "org1.example.com"
        user_authority = "Admin"
        channel_name = "bscchannel"
        tx_id = "WCH" + fileName1.split('.')[0] + '-' + fileName2.split('.')[0]
        activity = 'sdt'
        if 'v' in fileName1 and 'v' in fileName2:
            baseversion = 'V' + fileName1.split('.')[0].split('v')[1]
            targetversion = 'V' + fileName2.split('.')[0].split('v')[1]
        else:
            baseversion = 'V' + fileName1.split('.')[0]
            targetversion = 'V' + fileName2.split('.')[0]
        filePath = result_filePath
        result_fileName = os.path.basename(filePath)
        trans_time = time.ctime(os.path.getctime(filePath))
        fileType = 'sdt_file'
        fileSize = str(round(float(os.path.getsize(filePath)),2)) + 'KB'
        args = [tx_id,activity,baseversion,targetversion,filePath,fileType,fileSize]
        database = getattr(g, 'db', None)
        if database is None:
            database = g.db = sqlite3.connect(sqlDB)
        transID = invoke_transaction(user_name, user_authority, channel_name, args)
        result_changeDetail = result_changeData
        for i in range(0,len(result_changeDetail)):
            item = result_changeDetail[i]
            for key in item:
                component_type = key
                if "Rel" in key or "OwnerHistory" in key or "Property" in key:
                    isRVTobj = 0
                else:
                    isRVTobj = 1
                guid_ll = len(item[key]) # length of 
                for i in range (0,guid_ll):
                    item_data = item[key][i].replace("(","").replace(")","").split(",")
                    guid = item_data[0]
                    changeType = item_data[1]
                    file_ver = item_data[2]
                    ifcID = item_data[3]
                    if changeType != "modify":
                        isTarget = 1
                        isBase = 0
                    elif file_ver == "baseVer":
                        isBase = 1
                        isTarget = 0
                    elif file_ver == "targetVer":
                        isBase = 0
                        isTarget = 1
                    elif file_ver == "baseVer-targetVer":
                        isBase = 1
                        isTarget = 1
                    cursor = database.cursor()
                    cursor.execute("INSERT OR REPLACE INTO bsc_info (transID, GUID, ifcID, ifcType, isRVTobj, changeType, isBase, isTarget) values (?,?,?,?,?,?,?,?)", (transID, guid, ifcID, component_type, isRVTobj, changeType, isBase, isTarget ))
                    database.commit()
        
        for j in range(0,len(module_data)):
            item = module_data[j]
            for key in item:
                module_guid = key
                module_item_data = item[key].replace("(", "").replace(")", "").split(";")
                module_name = module_item_data[0]
                related_obj_guid = module_item_data[2]
                group_level = module_item_data[3]
                related_rel_guid = module_item_data[4]
                cursor = database.cursor()
                cursor.execute("INSERT OR REPLACE INTO module (moduleID, GUID, relatedObj, level, relatedRel) values (?,?,?,?,?)", (module_name, module_guid, related_obj_guid, group_level, related_rel_guid))
                database.commit
        # Upload result to the local sqlite3 database
        cursor = database.cursor()
        cursor.execute("INSERT OR REPLACE INTO blockchainTrans (baseVersion, targetVersion,transID,tsdtName,transTime) values (?,?,?,?,?)", (baseversion, targetversion,transID, result_fileName, trans_time))
        database.commit()
        database.close()
    return redirect(url_for('home_blueprint.computeResult', filename=result_fileName))

def my_sdt_route(file1,file2, projName):
    parser = argparse.ArgumentParser(description='Compute SDT of two IFC SPF files (as JSON).')
    #parser = reqparse.RequestParser()
    parser.add_argument('-a', '--ifc1', type=str, help='input ifc file path #A')
    parser.add_argument('-b', '--ifc2', type=str, help='input ifc file path #B')
    parser.add_argument('-o', '--output', type=str, help='output json file path')
    parser.add_argument('-v', '--verbose', action='store_true', help='logging verbose details to log_folder')
    args,unknown = parser.parse_known_args()
    args.ifc1 = file1
    args.ifc2 = file2
    args.output = output_diff + projName + '/'
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    # generate the log file name accordingly
    if "v" in file1 and "v" in file2:
        subfile1 = file1.split("v")[1].split(".")[0]
        subfile2 = file2.split("v")[1].split(".")[0]
        filename = 'v' + subfile1 + '-v' + subfile2 + '.sdt'
    else:
        filename = 'v' + file1[-5:-4] + '-v' + file2[-5:-4] + '.sdt' 
    IfcSdt.log_folder = LOG_FOLDER_PROJ(file1, file2, projName) + "/"
    args.verbose = 'verbose'
    sdt = IfcSdt()
    sdt.Verbose = args.verbose
    ifc1, idDict1, groupObj1 = sdt.remove_minor_dup(args.ifc1)
    ifc2, idDict2, groupObj2 = sdt.remove_minor_dup(args.ifc2)
    result = sdt.compute_diff(ifc1,ifc2)
    # upload the detailed difference to the database and blockchain 
    changed_item_type_list =[]
    changed_item = []
    group = []
    group_item = []
    for key in result["data_type"]:
        changed_type = key
        guid_list = []
        changed_item_type_list.append(key)
        diff_item = result["data_type"][key]
        if isinstance(diff_item, list) and len(diff_item) == 2:
            for key in diff_item[0]:
                if key in idDict1:
                    guid_list.append("("+ key + ",modify,baseVer," + idDict1[key] + ")")
            for key in diff_item[1]:
                if key in idDict2:
                    guid_list.append("("+ key + ",modify,targetVer," + idDict2[key] + ")")
        elif isinstance(diff_item, dict):
            for key in diff_item:
                if key == "$insert":
                    for key in diff_item["$insert"]:
                        if key in idDict2:
                            guid_list.append("(" + key + ",insert,targetVer," + idDict2[key] + ")")
                elif key == "$delete":
                    for key in diff_item["$delete"]:
                       if key in idDict1:
                        guid_list.append("(" + key + ",delete,baseVer," + idDict1[key] + ")")
                else:
                    guid_list.append("("+ key + ",modify,baseVer-targetVer," + idDict1[key] + ")")        
        changed_item_guid = guid_list
        changed_item_by_type = {changed_type : changed_item_guid}
        changed_item.append(changed_item_by_type)
    for key in groupObj1 and groupObj2:
        objList = []
        relList = []
        group_name_1 = groupObj1[key][0].split(":")[1]
        group_name_2 = groupObj2[key][0].split(":")[1]
        group_guid = key
        group_level = groupObj1[key][2].split(" ")[1].replace("')", "")
        if group_name_1 == group_name_2 and len(groupObj1[key][1]) == len(groupObj2[key][1]):
            if len(groupObj1[key][3]) == len(groupObj2[key][3]):
                group_name = group_name_1
                for k in range(0,len(groupObj1[key][1])-1):
                    item = groupObj1[key][1][k]
                    related_obj_guid = list(item.values())[0]
                    objList.append(related_obj_guid) 
                for j in range(0,len(groupObj1[key][3])-1):
                    item = groupObj1[key][3][j]
                    relList.append(item)
                group_item = "(" + group_name + ";" + group_guid + ";" + str(objList) + ";" + str(group_level) + ";" + str(relList) + ";baseVer)"
                group_item_by_guid = {group_guid:group_item}
            else:
                group_name = group_name_1
                for k in range(0,len(groupObj1[key][1])-1):
                    item = groupObj1[key][1][k]
                    related_obj_guid = list(item.values())[0]
                    objList.append(related_obj_guid)
                for j in range(0,len(groupObj1[key][3])-1):
                    item = groupObj1[key][3][j]
                    relList.append(item)
                group_item = "(" + group_name + ";" + group_guid + ";" + str(objList) + ";" + str(group_level) + ";" + str(relList) + ";baseVer)"
                for j in range(0,len(groupObj2[key][3])-1):
                    item = groupObj2[key][3][j]
                    relList.append(item)
                group_item = "(" + group_name + ";" + group_guid + ";" + str(objList) + ";" + str(group_level) + ";" + str(relList) + ";targetVer)"  
                group_item_by_guid = {group_guid:group_item}
            
        elif group_name_1 == group_name_2 and len(groupObj1[key][1]) != len(groupObj2[key][1]):
            group_name = group_name_2
            for k in range(0,len(groupObj1[key][1])-1):
                item = groupObj1[key][1][k]
                related_obj_guid_1 = list(item.values())[0]
                objList.append(related_obj_guid_1)
            group_item.append("(" + group_name + ";" + group_guid + ";" + str(objList) + ";" + "baseVer)")
            for k in range(0,len(groupObj2[key][1])-1):
                item = groupObj2[key][1][k]
                related_obj_guid_2 = list(item.values())[0]
                objList.append(related_obj_guid_2)
            group_item.append("(" + group_name + ";" + group_guid + ";" + str(objList) + ";" + "targetVer)")
            group_item_by_guid = {group_guid:group_item}
        group.append(group_item_by_guid)
    filePath = SdtIO.dict_to_base85file(args.output + filename, result)

    return filePath, changed_item, group

def invoke_transaction(user_name, user_authority, channel_name, args):
    if sys.platform == "win32" and (3, 8, 0) <= sys.version_info < (3, 9, 0):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()
    test_netwrok_path = os.path.join(fabric_folder, "test/fixtures/test-network.json")
    cli = Client(net_profile=test_netwrok_path)
    # get the user
    org1_admin = cli.get_user(user_name, user_authority)
    # invoke a chaincode to upload the data
    # make the client know there is a channel in the network
    cli.new_channel(channel_name)
    # An example args = ['WCH-PY-User04', 'sdt', 'v0', 'v1', '147.8.133.147:5000/download/case-v35.ifc', 'ifc', '138591.23KB']
    response = loop.run_until_complete(cli.chaincode_invoke(requestor=org1_admin,
                                                            channel_name='bscchannel',
                                                            peers=['peer0.org1.example.com', 'peer0.org2.example.com'],
                                                            args=args,
                                                            cc_name='basic',
                                                            wait_for_event=True,
                                                            fcn='CreateAsset'
                                                            ))
    # first get the hash by calling 'query-info'
    response = loop.run_until_complete(cli.query_info(
        requestor=org1_admin,
        channel_name='bscchannel',
        peers=['peer0.org1.example.com', 'peer0.org2.example.com'],
        decode=True
    ))
    current_hash = response.currentBlockHash
    response = loop.run_until_complete(cli.query_block_by_hash(
        requestor=org1_admin,
        channel_name='bscchannel',
        peers=['peer0.org1.example.com', 'peer0.org2.example.com'],
        block_hash=current_hash,
        decode=True
    ))
    transID = str(response.get('data').get('data')[0].get('payload').get('header').get('channel_header').get('tx_id'))
    return transID

def LOG_FOLDER_PROJ(file1,file2,projName):
    folder_name = projName
    if "v" in file1 and "v" in file2:
        subfile1 = file1.split("v")[1].split(".")[0]
        subfile2 = file2.split("v")[1].split(".")[0]
        filename = 'v' + subfile1 + '-v' + subfile2
    else:
        filename = 'v' + file1[-5:-4] + '-v' + file2[-5:-4]
    folder_path = os.path.join(log_folder, folder_name, filename)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    config.Config.LOG_FOLDER = folder_path
    return folder_path

@blueprint.route('/computeResult/<filename>', methods=['GET','POST'])
def computeResult(filename):
    if request.method == 'POST':
        data = request.json
        filename = data.get('resultFileName', [])
        output_diff_folder = os.path.join(output_diff, project)
        file = send_from_directory(output_diff_folder, filename, as_attachment=True)
        response = jsonify({'URL': output_diff_folder})
        return render_template('home/diff_result.html', result = file)
    elif request.method == 'GET':
        output_diff_folder = os.path.join(output_diff, project)
        file = send_from_directory(output_diff_folder, filename, as_attachment=True)
        return render_template('home/diff_result.html', result = filename, projName = project, blob=file)

@blueprint.route('/restoreResult/<filename>', methods=['GET','POST'])
def restoreResult(filename):
    if request.method == 'POST':
        data = request.json
        filename = data.get('resultFileName', [])
        output_diff_folder = os.path.join(output_diff, project)
        file = send_from_directory(output_diff_folder, filename, as_attachment=True)
        response = jsonify({'URL': output_diff_folder})
        return render_template('home/restore_result.html', result = file)
    elif request.method == 'GET':
        output_diff_folder = os.path.join(output_diff, project)
        file = send_from_directory(output_diff_folder, filename, as_attachment=True)
        return render_template('home/restore_result.html', result = filename, projName = project, blob=file)

@blueprint.route('/diff/<projName>/<filename>', methods=['GET','POST'])
def diff(projName,filename):
    if request.method == 'GET':
        path=os.path.isfile(os.path.join(output_diff,projName,filename))
        if path:
            return send_from_directory(os.path.join(output_diff,projName), filename, as_attachment=True)
        
# this defines the Semantic Tracing Page
@blueprint.route('/to_tracing', methods=['GET', 'POST'])
def to_tracing():
    if request.method == 'GET':
        return redirect(url_for('home_blueprint.tSDT_tracing'))
    
@blueprint.route('/tSDT_tracing', methods = ['GET', 'POST'])
def tSDT_tracing():
     # query data from the cached database
    database = getattr(g, 'db', None)
    if database is None:
        database = g.db = sqlite3.connect(sqlDB)
    cursor1 = database.cursor()
    cursor1.execute('SELECT version, timestamp from BIMversion order by timestamp DESC')
    data = cursor1.fetchall()
    cursor1.close()
    cursor2 = database.cursor()
    cursor2.execute("SELECT count(version), strftime('%m', timestamp) from BIMversion group by strftime('%Y,%m', timestamp)")
    monthly_sum = cursor2.fetchall()
    database.close()
    result_file_info = []
    result_files = []
    logFolders = []
    for dirname in os.listdir(output_diff):
        for filename in os.listdir(os.path.join(output_diff, dirname)):
            result = filename
            filePath = os.path.join(output_diff, dirname, filename).replace('\\','/')
            projName = dirname
            previous_Ver = filename.split("-")[0]
            latest_ver_o = filename.split("-")[1]
            latest_Ver = latest_ver_o.replace(".sdt","")
            compute_time = time.ctime(os.path.getctime(filePath))
            result_size = round(float(os.path.getsize(filePath)/1024) ,2)
            result_file_info.append((result, filePath, projName, previous_Ver, latest_Ver, compute_time, result_size))
            result_files.append(result_file_info)
    for dirname in os.listdir(os.path.join(log_folder, "WCH")):
        logFolders.append(dirname)

    restore_files = []
    for dirname in os.listdir(output_restore):
        for filename in os.listdir(os.path.join(output_restore, dirname)):
            if ".ifcjson" in filename:
                restore_result = filename
                filePath = os.path.join(output_restore, dirname, filename)
                projName = dirname
                versionNumList = filename.split(".")[0].split("-")
                restore_Ver = versionNumList[0]
                previous_Ver = versionNumList[1]
                restore_time = time.ctime(os.path.getctime(filePath))
                result_size = round(float(os.path.getsize(filePath)/1024) ,2)
                restore_files.append((restore_result, filePath, projName, restore_Ver, previous_Ver, restore_time, result_size))
    return render_template('home/tSDT_tracing.html', events=monthly_sum, results=result_files, restore_files=restore_files, logFolders=logFolders)

@blueprint.route('/tsdt_restore', methods=['GET','POST'])
def tsdt_restore():
    if request.method == 'POST':
        data = request.get_json()
        baseVersion = data['baseVersion']
        targetVersion = data['targetVersion']
        projName = data['Project']
        # session['folderName'] = restore_route(baseVersion, targetVersion, projName)
        session['data'] = restore_route(baseVersion, targetVersion, projName)
    return redirect(url_for('home_blueprint.restore_result'))

def LOG_FOLDER_RESTORE(baseVersion, targetVersion, projName):
    folder_name = projName
    sdt_folder = baseVersion + "-" + targetVersion
    folder_path = os.path.join(log_folder, folder_name, sdt_folder)
    if not os.path.exists(folder_path):
        real_sdt_folder = targetVersion + "-" + baseVersion
        folder_path = os.path.join(log_folder, folder_name, real_sdt_folder)
        if not os.path.exists(folder_path):
            folder_path = "null"
    return folder_path

def restore_route(baseVersion, targetVersion, projName):
    parser = argparse.ArgumentParser(description='Restore IFC from SDT (as ifcJSON).')
    parser.add_argument('-a', '--ifcjson', type=str, help='input ifc file path #A')
    parser.add_argument('-b', '--sdt', type=str, help='input SDT file path #B')
    parser.add_argument('-o', '--output', type=str, help='output ifcjson file path')
    parser.add_argument('-v', '--verbose', action='store_true', help='logging verbose details to restore_log_folder')
    args,unknown = parser.parse_known_args()
    sdtfile = baseVersion + "-" + targetVersion
    IfcSdt.log_folder = LOG_FOLDER_RESTORE(baseVersion, targetVersion, projName)
    ifcjsonName = "0-" + baseVersion.replace("v","") +"_ifc.ifcjson"
    targetJsonName = sdtfile+ ".ifcjson"
    targetIfcName = targetVersion + ".ifc"
    log_folder_name = sdtfile
    hashDict_name = "1-hash-GUID-" + baseVersion.replace("v","") + ".json"
    friend_hashDict_name = "1-hash-GUID-" + targetVersion.replace("v","") + ".json"
    objDict_name = "1-Final-Trimmed-Objects-" + baseVersion.replace("v","") + ".json"
    friend_objDict_name = "1-Final-Trimmed-Objects-" + targetVersion.replace("v","") + ".json"
    # print(hashDict_name, friend_hashDict_name, objDict_name, friend_objDict_name)
    args.ifcjson = os.path.join(log_folder, projName, log_folder_name,ifcjsonName)
    args.sdt_t1 = sdtfile
    sdtResultFile = sdtfile + ".sdt"
    args.sdt = os.path.join(output_diff,projName,sdtResultFile)
    args.hashDic = os.path.join(log_folder,projName,log_folder_name,hashDict_name)
    args.friendHashDic = os.path.join(log_folder,projName,log_folder_name,friend_hashDict_name)
    args.objectDic = os.path.join(log_folder,projName,log_folder_name,objDict_name)
    args.friendObjectDic = os.path.join(log_folder,projName,log_folder_name,friend_objDict_name)
    args.output = os.path.join(output_restore, projName) + "/"
    args.output_ifc = os.path.join(output_restore, projName, targetIfcName)
    if not os.path.exists(os.path.join(output_restore, projName)):
        os.makedirs(os.path.join(output_restore, projName))
    args.verbose = 'verbose'
    sdt = IfcSdt()
    sdt.Verbose = args.verbose
    r = sdt.restore_sdt(args.ifcjson, args.sdt, args.hashDic, args.friendHashDic, args.objectDic, args.friendObjectDic)
    print('SDT: ifcJSON restored in ' + str(round(sdt.time_elapsed, 3)) + 's')
    print('IFC restored in ' + str(round(sdt.time_elapsed, 3)) + 's')
    with open(args.output + targetJsonName, 'w') as outfile:
        json.dump(r, outfile, sort_keys=True, indent=2)
    return log_folder_name, targetJsonName

@blueprint.route('/restore_result')
def restore_result():
    # list all the restored files
    data = session.get('data','')
    logFolder = data[0]
    restoreResult = data[1]
    return render_template('home/restore_result.html', logFolder=logFolder, restoreResult = restoreResult)

@blueprint.route('/restore/<projName>/<filename>', methods=['GET','POST'])
def restore(projName,filename):
    if request.method == 'GET':
        path=os.path.isfile(os.path.join(output_restore,projName,filename))
        if path:
            return send_from_directory(os.path.join(output_restore,projName), filename, as_attachment=True)
        
@blueprint.route('/query', methods=['GET','POST'] )
def query():
   if request.method == 'POST':
        moduleID = request.form.get('selectedModuleName')
        module_orientation = moduleID.split("-")[2]
        module_tower = moduleID.split("-")[0]
        module_seriesNo = moduleID.split("-")[3]
        if module_tower == "A":
            if module_orientation == "N" and int(module_seriesNo) < 9:
                module_no_real = module_seriesNo
            elif module_orientation == "N" and int(module_seriesNo) >= 9:
                module_no_dict = {"9":"14", "10":"13", "11":"12", "12":"11", "13":"10", "14":"9"}
                module_no_real = module_no_dict[module_seriesNo]
            elif module_orientation == "S":
                module_no_real = str(int(module_seriesNo) + 14)
        elif module_orientation == "N":
            module_no_dict = {"14":"27", "13":"28", "12":"26", "11":"25", "10":"24", "9":"23", "8":"16", "7":"17", "6":"15", "5":"18", "4":"19", "3":"20", "2":"22", "1":"21"}
            module_no_real = module_no_dict[module_seriesNo]
        elif module_orientation == "S":
            module_no_dict = {"1":"7", "2":"8", "3":"6", "4":"5", "5":"4", "6":"1", "7":"3", "8":"2", "9":"9", "10":"10", "11":"11", "12":"12", "13":"13", "14":"14"}
            module_no_real = module_no_dict[module_seriesNo]
        mapped_moduleName = "module-" + module_tower + "-" + module_no_real
        level = moduleID.split("-")[1] + "/F"
        database = getattr(g, 'db', None)
        if database is None:
            database = g.db = sqlite3.connect(sqlDB)
        cursor = database.cursor()
        cursor.execute("SELECT relatedObj FROM module where moduleID=? and level=?", (mapped_moduleName, level))
        module_info = cursor.fetchall()
        if module_info != None:
            relatedObjList = module_info[0][0].replace("[", "").replace("]", "").split(",")
            refined_relatedObjList = []
            for j in range(0, len(relatedObjList)):
                relatedObj = relatedObjList[j].replace(" '", "").replace("'", "")
                refined_relatedObjList.append(relatedObj)
            cursor.execute("SELECT relatedRel FROM module where moduleID=? and level=?", (mapped_moduleName, level))
            rel_info = cursor.fetchall()
            relatedRelList = rel_info[0][0].replace("[", "").replace("]", "").split(",")
            # to modify the relationship
            refined_relatedRelList = []
            for k in range(0, len(relatedRelList)):
                relatedRel = relatedRelList[k].replace(" '", "").replace("'", "")
                refined_relatedRelList.append(relatedRel)
            cursor.execute("SELECT ifcID FROM bsc_info where ifcID is not Null")
            changed_item_id = cursor.fetchall()
            for i in range(0, len(changed_item_id)):
                changed_item = changed_item_id[i][0]
                if changed_item in refined_relatedObjList:
                    cursor.execute("SELECT transID, ifcType, changeType from bsc_info where ifcID=?", (changed_item,))
                    bsc_item = cursor.fetchall()
                elif changed_item in refined_relatedRelList:
                    cursor.execute("SELECT b.transID, b.ifcType, b.changeType, t.transTime, t.tsdtName from bsc_info as b INNER JOIN blockchainTrans as t where ifcID=? and b.transID = t.transID ", (changed_item,))
            bsc_item = cursor.fetchall()
            table_html=''
            for item in bsc_item:
                transID = item[0]
                ifcEntity = item[1]
                changeType = item[2]
                transTime = item[3]
                tsdtName = item[4]
                table_html += '<tr class="table-info"><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(transID, ifcEntity, changeType,transTime,tsdtName)
        else:
            session['bsc_data'] = "No inspection records!"
        return table_html
    
@blueprint.route('/blockchain')
def blockchain():
   return render_template('home/blockchain.html')




