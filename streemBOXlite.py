#!/usb/bin/env python3
# -*- coding: utf-8 -*-

# Author: twitter: @b00010111

import sqlite3
from datetime import datetime
import getopt,sys,os
import glob
from sys import platform
import csv,json,pprint
import copy

version = '0.0051'
s_path = u_path = ''
s_path_local_cache = ''
s_path_user = "%SYSTEMDRIVE%\\Users\$REPLACE$\\"
s_path_box_data = 'AppData/Local/Box/Box/data/'
s_path_box_data_w = "AppData\Local\Box\Box\data\\"
s_path_box_cache = 'AppData/Local/Box/Box/cache/'
s_path_box_cache_w = "AppData\Local\Box\Box\cache\\"
s_file_streemfs = 'streemfs.db'

userprofile = "%USERPROFILE%\\"
systemdrive_replace = ''

os_linux = True
users = b_json = b_csv = quiet = verbose = short = False
output_dir = ''


#
# Function to check if system script is running on is Windows or not. function sets global os_linux variable to False if Windows, otherwise
# os_linux will be True
#
def checkos ():
	global os_linux
	if platform == "win32":
		os_linux = False

#Parameter: s_path Path to the folder containing the streemfs.db file to parse
#Parameter: s_path_local_cache local path to the cache folder in which cacheDataIds can be found, give emtpy string if unknown
#Return: entries dictionary containing the parsed streemfs.db entries and the enritchment fields added
def parseDB(s_path,s_path_local_cache):
	global os_linux
	global userprofile
	if os_linux:
		db = s_path + '/' + s_file_streemfs
	else:
		db = s_path + "\\" + s_file_streemfs
	entries = {}
	if os.path.isfile(db) == False:
		if verbose:
			print("Unable to find database file: " + db)
		return entries
	conn = sqlite3.connect(db)
	if verbose:
		print("database connected\ndatabase path:")
		print(db)
	#rows are tuples
	cursor = conn.execute("select fsnodes.inodeId, fsnodes.name, fsnodes.isFile, fsnodes.createdAtTimestamp, fsnodes.modifiedAtTimestamp, fsnodes.accessedAtTimestamp, cachefiles.cacheDataId,cachefiles.inodeId,cachefiles.dirtyData,cachefiles.size, cachefiles.sizeAtLastConsistentState,fsnodes.parentInodeId from fsnodes left join cachefiles on fsnodes.inodeId=cachefiles.inodeId;")
	for row in cursor:
		#print(row)
		InodeId = row[0]
		if InodeId in entries:
			continue
		else:
			#entries[InodeId] = row
			entries[InodeId] = {'fsnodes.inodeId':row[0], 'fsnodes.name':row[1], 'fsnodes.isFile':row[2], 'fsnodes.createdAtTimestamp':row[3], 'fsnodes.modifiedAtTimestamp':row[4], 'fsnodes.accessedAtTimestamp':row[5], 'cachefiles.cacheDataId':row[6],'cachefiles.inodeId':row[7], 'cachefiles.dirtyData':row[8],'cachefiles.size':row[9], 'cachefiles.sizeAtLastConsistentState':row[10], 'fsnodes.parentInodeId':row[11]}

	#rows are tuples
	cursor = conn.execute("select fsnodes.inodeId, fsnodes.name, fsnodes.isFile, fsnodes.createdAtTimestamp, fsnodes.modifiedAtTimestamp, fsnodes.accessedAtTimestamp,cachefiles.cacheDataId, cachefiles.inodeId,cachefiles.dirtyData,cachefiles.size, cachefiles.sizeAtLastConsistentState,fsnodes.parentInodeId from cachefiles left join fsnodes on fsnodes.inodeId=cachefiles.inodeId;")
	for row in cursor:
		#print(row)
		# we check on chacefiles.inodeID this time in order not showing if an entry is in cachefiles but not in fsnodes. This should not happen as known today, but if so, the result is not missed! 
		InodeId = row[7]
		if InodeId in entries:
			continue
		else:
			entries[InodeId] = {'fsnodes.inodeId':row[0], 'fsnodes.name':row[1], 'fsnodes.isFile':row[2], 'fsnodes.createdAtTimestamp':row[3], 'fsnodes.modifiedAtTimestamp':row[4], 'fsnodes.accessedAtTimestamp':row[5], 'cachefiles.cacheDataId':row[6],'cachefiles.inodeId':row[7], 'cachefiles.dirtyData':row[8],'cachefiles.size':row[9], 'cachefiles.sizeAtLastConsistentState':row[10], 'fsnodes.parentInodeId':row[11]}

	for k,row in entries.items():
		#print(row)
		### add fields to dict like parsed timestamps, enriched path, later we either print dict, or csv dict, or json output  depending on output choosen ###
		# fsnodes.isFile ==1 isFile True, else False
		file_verbose = row.get('fsnodes.isFile','Error')
		if file_verbose == 1:
			row['File'] = 'True'
		elif file_verbose == 'Error':
			row['File'] = 'Error'
		else:
			row['File'] = 'False'	
		# cachfiles.dirtyData ==1 looks like data not beeing synced, in terms of beeing an exception
		# size from chache files in bytes
		row['size_unit'] = 'byte'
		# Dealing with timestamps
		row['timezone'] = 'UTC'
		if row.get('fsnodes.createdAtTimestamp',None) != None:
			dt_object = datetime.utcfromtimestamp(row.get('fsnodes.createdAtTimestamp',None))
			row['Date_Creation'] = dt_object.strftime('%Y-%m-%d')	
			row['Time_Creation'] = dt_object.strftime('%H:%M:%S')
		else:
			row['Date_Creation'] = ''
			row['Time_Creation'] = ''
		if row.get('fsnodes.modifiedAtTimestamp',None) != None:
			dt_object = datetime.utcfromtimestamp(row.get('fsnodes.modifiedAtTimestamp',None))
			row['Date_Modification'] = dt_object.strftime('%Y-%m-%d')	
			row['Time_Modification'] = dt_object.strftime('%H:%M:%S')
		else:
			row['Date_Modification'] = ''
			row['Time_Modification'] = ''
		if row.get('fsnodes.accessedAtTimestamp',None) != None:
			dt_object = datetime.utcfromtimestamp(row.get('fsnodes.accessedAtTimestamp',None))
			row['Date_Access'] = dt_object.strftime('%Y-%m-%d')	
			row['Time_Access'] = dt_object.strftime('%H:%M:%S')
		else:
			row['Date_Access'] = ''
			row['Time_Access'] = ''
	
		cacheDataId = row.get('cachefiles.cacheDataId',None)
		if cacheDataId == None:
			cacheDataPath_w = "None"
		else:
			cacheDataPath_w = userprofile + s_path_box_cache_w + cacheDataId
		row['WindowsPathToCacheFile'] = cacheDataPath_w
		if len(s_path_local_cache) > 0 and cacheDataId != None:
			if os_linux:
				if s_path_local_cache.endswith("/"):
					row['CacheFileLocalPath'] = s_path_local_cache + cacheDataId
				else:
					row['CacheFileLocalPath'] = s_path_local_cache + '/' + cacheDataId
			else:
				if s_path_local_cache.endswith("\\"):
					row['CacheFileLocalPath'] = s_path_local_cache + cacheDataId
				else:
					row['CacheFileLocalPath'] = s_path_local_cache + '\\' + cacheDataId
			# if the file does not exist, add UNVALIDATED as prefix
			if os.path.isfile(row['CacheFileLocalPath']) == False:
				row['CacheFileLocalPath'] = 'UNVALIDATED ' + row.get('CacheFileLocalPath')
		else:
			row['CacheFileLocalPath'] = 'None'
	return entries	

#Function to write one instance of parsed and enritched streemfs.db
#Parameter: entries dict containing on parsed and enritched streemfs.db 
#Parameter: outputdir file will be written to this dir, if this parameter is empty the file will be written in current working directory
#Parameter: filename output file name
#Parameter: l_short Boolean, if true the short output csv header will be written
def writeCSV(entries,outputdir,filename,l_short):
	if len(outputdir) > 0:
		# test if dir exists
		if os.path.isdir(outputdir) == False:
			print("Output directory does not exist, exiting")
			exit(1)
		else:
			#check if outputdir as trailing slash, if so do no add it, do so for win and posix path
			if os_linux:
				if outputdir.endswith("/"):
					csvfile = open(outputdir+filename,'w')
				else:
					csvfile = open(outputdir+'/'+filename,'w')
			else:
				if outputdir.endswith("\\"):
					csvfile = open(outputdir+filename,'w')
				else:
					csvfile = open(outputdir+"\\"+filename,'w')
			
	else:
		csvfile = open(filename,'w')
	if verbose:
		print("Writing csv resultfile to:")
		print(os.path.abspath(csvfile.name))
	if l_short:
		csvHeaderlist = ['fsnodes.name', 'cachefiles.cacheDataId', 'File', 'Date_Creation', 'Time_Creation', 'Date_Modification', 'Time_Modification']
	else:
		csvHeaderlist = ['fsnodes.name', 'cachefiles.cacheDataId', 'File', 'CacheFileLocalPath', 'WindowsPathToCacheFile', 'fsnodes.parentInodeId','cachefiles.size', 'cachefiles.sizeAtLastConsistentState', 'size_unit', 'Date_Creation', 'Time_Creation', 'Date_Modification', 'Time_Modification', 'Date_Access', 'Time_Access', 'timezone', 'cachefiles.dirtyData', 'cachefiles.inodeId', 'fsnodes.isFile', 'fsnodes.inodeId', 'fsnodes.createdAtTimestamp', 'fsnodes.modifiedAtTimestamp', 'fsnodes.accessedAtTimestamp']
	csvwriter = csv.DictWriter(csvfile, delimiter=',', quotechar='\"', fieldnames=csvHeaderlist)
	csvwriter.writeheader()
	for k,v in entries.items():
		csvwriter.writerow(v)
	csvfile.close()
	
#Function to write one instance of parsed and enritched streemfs.db
#Parameter: entries dict containing on parsed and enritched streemfs.db 
#Parameter: outputdir file will be written to this dir, if this parameter is empty the file will be written in current working directory
#Parameter: filename output file name
#FIXME: does not work with -outputdir
def writeJSON(entries,outputdir,filename):
	if len(outputdir) > 0:
		# test if dir exists
		if os.path.isdir(outputdir) == False:
			print("Output directory does not exist, exiting")
			exit(1)
		else:
			#check if outputdir as trailing slash, if so do no add it, do so for win and posix path
			if os_linux:
				if outputdir.endswith("/"):
					jsonfile = open(outputdir+filename,'w')
				else:
					jsonfile = open(outputdir+'/'+filename,'w')
			else:
				if outputdir.endswith("\\"):
					jsonfile = open(outputdir+filename,'w')
				else:
					jsonfile = open(outputdir+"\\"+filename,'w')
			
	else:
		jsonfile = open(filename,'w')
	if verbose:
		print("Writing json resultfile to:")
		print(os.path.abspath(jsonfile.name))
	for k,v in entries.items():
		json.dump(v, jsonfile)
#	with open(filename, "w") as outfile:
#		for k,v in entries.items():
#			json.dump(v, outfile)
	

#function creats the dict representing the sort output format
#short format: filename, cacheId, 'Date_Creation', 'Time_Creation', 'Date_Modification', 'Time_Modification'
def create_short_format(l_entries):
	l_shortdict = {}
	for k,v in l_entries.items():
		temp_e = {}
		temp_e['fsnodes.name'] = v.get('fsnodes.name','')
		temp_e['cachefiles.cacheDataId'] = v.get('cachefiles.cacheDataId','')
		temp_e['Date_Creation'] = v.get('Date_Creation','')
		temp_e['Time_Creation'] = v.get('Time_Creation','')
		temp_e['Date_Modification'] = v.get('Date_Modification','')
		temp_e['Time_Modification'] = v.get('Time_Modification','')
		temp_e['File'] = v.get('File','')
		# we need to do a deepcopy of the object, which will be added to the dirct, otherwise it is just a reference to the new_row object. Which will represent the last status of the new_row object for all keys.
		l_shortdict[k] = copy.deepcopy(temp_e)
	return copy.deepcopy(l_shortdict)
	
#function get streemfs_path
#Parameter l_user String Path to the directory for the user to find streemfs.db
#Return String containing the path to the streemfs Database, using correct \/
def get_streemfs_path(l_user):
	global os_linux
	global s_path_box_data
	global s_path_box_data_w
	global s_file_streemfs
	
	test_path = ''
	if os_linux:
		#test_path = l_user + s_path_box_data + '/' + s_file_streemfs
		test_path = l_user + s_path_box_data + s_file_streemfs
	else:
		test_path = l_user + s_path_box_data_w + s_file_streemfs
	#if os.path.isfile(l_user + s_path_box_data):
	if os.path.isfile(test_path):
		# test if default path exists
		#if yes retrun it
		if os_linux:
			return l_user + s_path_box_data
		else:
			return l_user + s_path_box_data_w
	else:
		#else try to find the file in the USER directory recusive
		if os_linux:
			pattern = l_user +'**/' + s_file_streemfs
		else:
			pattern = l_user +"**\\" + s_file_streemfs
		for fname in glob.glob(pattern, recursive=True):
			if os.path.isfile(fname):
				#if something is found uses this Path
				if verbose:
					print("Found non standard path for streemfs DB:" + fname)
				return fname
	#code is only reached if nothing is found; return ''
	#print("reached return nothing")
	return ''
		
#function get local_cache_path
#Parameter l_user String Path to the directory for the user to find streemfs.db
#Return String containing the path to the streemfs Database, using correct \/
#def get_streemfs_path(l_path,l_user):
def get_cache_path(l_user):
	global os_linux
	global s_path_box_cache
	global s_path_box_cache_w
	test_path = ''
	if os_linux:
		test_path = l_user + s_path_box_cache
	else:
		test_path = l_user + s_path_box_cache_w
	#if os.path.isfile(l_user + s_path_box_data):
	if os.path.isdir(test_path):
		# test if default path exists
		#if yes retrun it
		return test_path
	else:
		#else try to find the cache folder in the USER directory recusive
		if os_linux:
			#TEST OB DAS GEHT: pattern = l_user +'**/cache'
			#und nachher testen nach isdir
			pattern = l_user +'**/cache'
		else:
			pattern = l_user +"**\\cache"
		for fname in glob.glob(pattern, recursive=True):
			if os.path.isdir(fname):
				#if something is found uses this Path
				if verbose:
					print("Found non standard path for cache folder:" + fname)
				return fname
	#code is only reached if nothing is found; return ''
	#print("reached return nothing")
	return ''
	
# Function to print the usage info to stdout
def usage():
	print ("Usage: ")
	print("-p --path <PATH>\n\tPath to the folder containing the acquiered streemfs.db file, output will show cache file path Windows as %USERPROFILE% "+s_path_box_cache_w+" as Path unless -U is used to overwrite the default")
	print("-l --localcache <PATH>\n\tIf you acquiered the cache folder (%USEROROFILE%AppData\Local\Box\Box\cache) from the original system you can provide its local path. Only valid if -p option is used")
	print("-u --users <PATH>\n\tPath to the acquiered Users Folder, Output will show cache file path windows as %SYSTEMDRIVE%\\Users\$USERNAME\\"+s_path_box_cache_w+" as Path unless -S is used to overwrite the default\n\tstreemfs.db and cache folder are searched at default path, if not found at the default location, the given Users directory is searched recursivly for a "+s_file_streemfs+" file and a folder named cache. In both cases ONLY THE FIRST HIT will be processed.") 
	print("-U --USERPROFILE <VALUE>\n\toverride %USERPROFILE% in output of -p option")
	print("-S --SYSTEMDRIVE <VALUE>\n\toverride %SYSTEMDRIVE% in output of -u option")
	print("-c --csv \n\twrite outout as csv file")
	print("-j --json \n\twrite output to json file")
	print("-q --quiet \n\tdo not print results to stdout")
	print("-v --verbose \n\tprint out status messages like successful database access and writing output files to stdout")
	print("-s --short \n\tshort output option only giving file name, cache file name (aka cacheID), File or no File, and Create,Modified Date/Time")
	print("-o --output <PATH>\n\tpath to output directory")
	print("-h --help \n\tprint this usage information")
	print("------------------------------------------")
	print("If field \"CacheFileLocalPath\" contains \"UNVALIDATED\" as prefix the corresponding cache file could not be found at the shown path")
	print("")

#
try:
	opts, args = getopt.getopt(sys.argv[1:],"p:u:U:S:o:cjqhl:vs",["path=","users=","USERPROFILE=","SYSTEMDRIVE=","outputdir=","csv","json","quiet","help","localcache=","verbose","short"])
 
except getopt.GetoptError as err:
	print(err)
	usage()
	exit(1)
	
for opt, arg in opts:
	if opt in ("-p", "--path"):
		s_path = arg
	elif opt in ("-u", "--users"):
		u_path = arg
		users = True
	elif opt in ("-U","--USERPROFILE"):
		userprofile = arg
	elif opt in ("-S","--SYSTEMDRIVE"):
		systemdrive_replace = arg
	elif opt in ("-l","--localcache"):
		s_path_local_cache = arg
	elif opt in ("-o","--outputdir"):
		output_dir = arg
	elif opt in ("-c","--csv"):
		b_csv = True
	elif opt in ("-j","--json"):
		b_json = True
	elif opt in ("-q","--quiet"):
		quiet = True
	elif opt in ("-v","--verbose"):
		verbose = True
	elif opt in ("-s","--short"):
		short = True
	elif opt in ("-h","--help"):
		usage()
		exit(0)
	else:
		usage()
		assert False, "unknown option"

checkos()
if len(s_path)==0 and len(u_path)==0:
	print("You need to provide either -p PATH_TO_STREEMFS.DB or -u PATH_TO_USERS_FOLDER. Neither was given...")
	print("Exiting")
	exit(1)
if verbose:
	print("Version: " + version)

if users == True:
	# loop over each user folder parsing the database (arguments: -u Path,  username, systemdrive overwrite (if given)
	if os.path.isdir(u_path) == False:
		#not a dir, exiting
		print("Provided path is not a directory. Argument given: " + u_path)
		exit(1)
	t_dirs = os.listdir(u_path)
	dirs = {}
	for t_dir in t_dirs:
		if os_linux:
			if u_path.endswith("/"):
				u_path = u_path[:-1]
			td = u_path + '/' + t_dir +'/'
		else:
			if u_path.endswith("\\"):
				u_path = u_path[:-1]
			td = u_path + "\\" + t_dir + "\\"
		if os.path.isdir(td):
			dirs[t_dir] = td
	# dirs object contains all directories in u_path, these folders should be the useres
	for ku,user in dirs.items():
		#replace placeholder with username value stored in ku
		userprofile = s_path_user.replace("$REPLACE$",ku)
		if len(systemdrive_replace)>0:
			userprofile = userprofile.replace("%SYSTEMDRIVE%",systemdrive_replace)
		# call function get streemfs_path and local cache path
		user_path = get_streemfs_path(user)
		#if no streemfs.db file is found, jumd to next user
		if len(user_path) == 0:
			if verbose:
				print("No database found for user:" + ku)
			continue
		cache_path = get_cache_path(user)
		entry = parseDB(user_path,cache_path)
		if short:
			entry = create_short_format(entry)
		if quiet == False:
			for k,v in entry.items():
				pprint.pprint(v) 
		if b_csv:
			#call csv output method
			csv_filename =  datetime.now().strftime("%Y%m%d%I%M") + '_' + ku + '_result.csv'
			writeCSV(entry,output_dir,csv_filename,short)
		if b_json:
			#call json output method
			json_filename =  datetime.now().strftime("%Y%m%d%I%M") + '_' + ku + '_result.json'
			writeJSON(entry,output_dir,json_filename)

else:
	# else, direct parsing of db
	path_to_cache = userprofile + s_path_box_cache_w
	#correct path if user supplies path including filename s_file_streemfs
	if s_path.endswith(s_file_streemfs):
		if verbose:
			print("Path should not include " + s_file_streemfs + ". Removing filename.")
		s_path = s_path.replace(s_file_streemfs,"")
	entry = parseDB(s_path,s_path_local_cache)
	if short:
		entry = create_short_format(entry)
	if quiet == False:
		for k,v in entry.items():
			pprint.pprint(v) 
	if b_csv:
		#call csv output method
		csv_filename =  datetime.now().strftime("%Y%m%d%I%M") + '_result.csv'
		writeCSV(entry,output_dir,csv_filename,short)
	if b_json:
		#call json output method
		json_filename =  datetime.now().strftime("%Y%m%d%I%M") + '_result.json'
		writeJSON(entry,output_dir,json_filename)


