# Trash timestamp management policy
#
# The logic here ensures that the any collection or data object that is put into
# trash receives metadata indicating the time it was put into trash. It also
# removes this metadata from anything moved out of trash. When a collection is
# put into trash, only the collection receives the metadata, not its contents.
# The AVU metadata attribute used is `ipc::trash_timestamp` with value being the
# 11 digit number of seconds since the POSIX epoch, the standard way iRODS
# stores time stamps.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

# generates a unique variable name for a data object or collection based on its
# absolute path, the variable name is prefixed with "trash_timestamp_".
#
# Parameters:
#  *Path:  the absolute path to the data object or collection
#
# Return:
#  the variable name to be used in temporaryStorage to store a timestamp value
#
_ipcTrash_mkTimestampVar: path -> string
_ipcTrash_mkTimestampVar(*Path) = 'trash_timestamp_' ++ str(*Path)

# generates a unique variable name for a data object based on its absolute path,
# the variable name is prefixed with "data_id_".
#
# Parameters:
#  *Path:  the absolute path to the data object
#
# Return:
#  the variable name to be used in temporaryStorage to store a DATA_ID
#
_ipcTrash_mkObjDataIdVar: path -> string
_ipcTrash_mkObjDataIdVar(*Path) = 'data_id_' ++ str(*Path)

_ipcTrash_manageTimeAVU(*Action, *Type, *Path, *Val) {
	*actionArg = execCmdArg(*Action);
	*typeArg = execCmdArg(*Type);
	*pathArg = execCmdArg(str(*Path));
	*valArg = execCmdArg(*Val);
	*avuName = execCmdArg("ipc::trash_timestamp");
	*argv = "*actionArg *typeArg *pathArg *avuName *valArg";
	*err = errormsg(msiExecCmd('imeta-exec', *argv, "", "", "", *out), *msg);

	if (*err < 0) {
		msiGetStderrInExecCmdOut(*out, *resp);
		writeLine('serverLog', 'imeta-exec stderr: *resp');
		writeLine('serverLog', '_ipcTrash_manageTimeAVU: *msg');
		*err;
	}
}


# If a data object is being moved to trash, this sets the trash_timestamp avu on
# the object, and records the object's Id for later use in the session.
#
# Parameters:
#   Instance          (string) unused
#   Comm              (`KeyValuePair_PI`) unused
#   DataObjUnlinkInp  (`KeyValuePair_PI`) information about the data object
#                     being deleted
#
# temporaryStorage:
#  data_id_<PATH>          records the ID of the data object with absolute path
#                          PATH
#  trash_timestamp_<PATH>  records the timestamp when the data object with
#                          absolute path PATH is moved to trash
#
cyverse_trash_api_data_obj_unlink_pre(*Instance, *Comm, *DataObjUnlinkInp) {
	if (errorcode(*DataObjUnlinkInp.forceFlag) != 0) {
		msiGetSystemTime(*timestamp, "");
		*dataObjPath = *DataObjUnlinkInp.obj_path;
		*timestampVar = _ipcTrash_mkTimestampVar(/*dataObjPath);
		temporaryStorage.'*timestampVar' = *timestamp;
		_ipcTrash_manageTimeAVU("set", cyverse_DATA_OBJ, *dataObjPath, *timestamp);
		msiSplitPath(*dataObjPath, *coll, *file);

		foreach(*row in SELECT DATA_ID WHERE COLL_NAME = '*coll' AND DATA_NAME = '*file') {
			*dataIdVar = _ipcTrash_mkObjDataIdVar(/*dataObjPath);
			temporaryStorage.'*dataIdVar' = *row.DATA_ID;
		}
	}
}


# If a data object was moved to trash, this sets the trash timestamp on any newly
# created collections in trash.
#
# Parameters:
#  Instance          (string) unused
#  Comm              (`KeyValuePair_PI`) unused
#  DataObjUnlinkInp  (`KeyValuePair_PI`) information about the data object being
#                    deleted
#
# temporaryStorage:
#  data_id_<PATH>          provides the ID of the data object with absolute
#                          path PATH
#  trash_timestamp_<PATH>  provides the timestamp when the data object with
#                          absolute path PATH is moved to trash
#
cyverse_trash_api_data_obj_unlink_post(*Instance, *Comm, *DataObjUnlinkInp) {
	*dataObjPath = *DataObjUnlinkInp.obj_path;
	*timestampVar = _ipcTrash_mkTimestampVar(/*dataObjPath);

	if (errorcode(temporaryStorage.'*timestampVar') == 0) {
		temporaryStorage.'*timestampVar' = "";
	}

	*dataIdVar = _ipcTrash_mkObjDataIdVar(/*dataObjPath);

	if (errorcode(temporaryStorage.'*dataIdVar') == 0) {
		*dataIdVarTemp = temporaryStorage.'*dataIdVar';

		foreach(*row in SELECT COLL_NAME WHERE DATA_ID = '*dataIdVarTemp') {
			*collNameList = split(*row.COLL_NAME, '/');

			if (size(*collNameList) >= 5) {
				*parentCollPath = "";

				for (*i = 0; *i < 5; *i = *i + 1) {
					*parentCollPath = *parentCollPath ++ "/" ++ elem(*collNameList, *i);
				}

				_ipcTrash_manageTimeAVU("set", cyverse_COLL, *parentCollPath, *timestamp);
			}
		}
	}
}


# If an error occurs while moving a data object to trash, any trash timestamp
# AVUs created during is deleted.
#
# Parameters:
#  Instance          (string) unused
#  Comm              (`KeyValuePair_PI`) unused
#  DataObjUnlinkInp  (`KeyValuePair_PI`) information about the data object being
#                    deleted
#
# temporaryStorage:
#  trash_timestamp_<PATH>  provides the timestamp for object with path PATH to
#                          be removed
#
cyverse_trash_api_data_obj_unlink_except(*Instance, *Comm, *DataObjUnlinkInp) {
	*dataObjPath = *DataObjUnlinkInp.obj_path;
	*timestampVar = _ipcTrash_mkTimestampVar(/*dataObjPath);

	if (errorcode(temporaryStorage.'*timestampVar') == 0) {
		if (temporaryStorage.'*timestampVar' != "") {
			_ipcTrash_manageTimeAVU(
				"rm", cyverse_DATA_OBJ, *dataObjPath, temporaryStorage.'*timestampVar' );
		}
	}
}


# If a data object was uploaded to trash, this sets its trash trash timestamp.
# created collections in trash.
#
# Parameters:
#  Instance        (string) unused
#  Comm            (`KeyValuePair_PI`) unused
#  DataObjInp      (`KeyValuePair_PI`) information related to the data object
#  DataObjInpBBuf  (unknown) unused
#  PORTAL_OPR_OUT  (unknown) unused
#
cyverse_trash_api_data_obj_put_post(
	*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PORTAL_OPR_OUT
) {
	*zone = cyverse_ZONE;

	if (*DataObjInp.obj_path like '/*zone/trash/*') {
		msiGetSystemTime(*timestamp, "");
		_ipcTrash_manageTimeAVU("set", cyverse_DATA_OBJ, *DataObjInp.obj_path, *timestamp);
	}
}


# When a collection is being moved to trash, this sets a trash timestamp on the
# collection.
#
# Parameters:
#  Instance     (string) unused
#  Comm         (`KeyValuePair_PI`) unused
#  RmCollInp    (`KeyValuePair_PI`) information about the collection being
#               deleted
#  CollOprStat  (unknown) unused
#
# temporaryStorage:
#  trash_timestamp_<PATH>  records the timestamp when the collection with
#                          absolute path PATH is moved to trash
#
cyverse_trash_api_rm_coll_pre(*Instance, *Comm, *RmCollInp, *CollOprStat) {
	if (errorcode(*RmCollInp.forceFlag) != 0) {
		msiGetSystemTime(*timestamp, "");
		*collNamePath = *RmCollInp.coll_name;
		*timestampVar = _ipcTrash_mkTimestampVar(/*collNamePath);
		temporaryStorage.'*timestampVar' = *timestamp;
		_ipcTrash_manageTimeAVU("set", cyverse_COLL, *collNamePath, *timestamp);
	}
}


# If moving a collection to trash fails, this removes the trash timestamp.
#
# Parameters:
#  Instance     (string) unused
#  Comm         (`KeyValuePair_PI`) unused
#  RmCollInp    (`KeyValuePair_PI`) information about the collection being
#               deleted
#  CollOprStat  (unknown) unused
#
# temporaryStorage:
#  trash_timestamp_<PATH>  records the timestamp when the collection with
#                          absolute path PATH is moved to trash
#
cyverse_trash_api_rm_coll_except(*Instance, *Comm, *RmCollInp, *CollOprStat) {
	*collNamePath = *RmCollInp.coll_name;
	*timestampVar = _ipcTrash_mkTimestampVar(/*collNamePath);

	if (errorcode(temporaryStorage.'*timestampVar') == 0) {
		_ipcTrash_manageTimeAVU("rm", cyverse_COLL, *collNamePath, temporaryStorage.'*timestampVar');
	}
}

# When a collection is created in trash, this sets a trash timestamp on it.
#
# Parameters:
#  Instance       (string) unused
#  Comm           (`KeyValuePair_PI`) unused
#  CollCreateInp  (`KeyValuePair_PI`) information related to the new collection
#
cyverse_trash_api_coll_create_post(*Instance, *Comm, *CollCreateInp) {
	*zone = cyverse_ZONE;
	*collNamePath = *CollCreateInp.coll_name;

	if (*collNamePath like '/*zone/trash/*') {
		msiGetSystemTime(*timestamp, "");
		_ipcTrash_manageTimeAVU("set", cyverse_COLL, *collNamePath, *timestamp);
	}
}


# When a collection or data object is being moved to trash, this records a trash
# timestamp for it, and if it is a collection, recursively for everything in it.
#
# Parameters:
#  Instance          (string) unused
#  Comm              (`KeyValuePair_PI`) unused
#  DataObjRenameInp  (`KeyValuePair_PI`) information about the data object and
#                    its new path
#
# temporaryStorage:
#  trash_timestamp_<PATH*>  records the timestamp for the collection or data
#                           object with absolute path PATH is moved to trash,
#                           there is one for each deleted collection or data
#                           object
#
cyverse_trash_api_data_obj_rename_pre(*Instance, *Comm, *DataObjRenameInp) {
	*zone = cyverse_ZONE;
	if (
		*DataObjRenameInp.src_obj_path like '/*zone/trash/*'
		&& *DataObjRenameInp.dst_obj_path not like '/*zone/trash/*'
	) {
		*srcObjPath = *DataObjRenameInp.src_obj_path;
		*timestampVar = _ipcTrash_mkTimestampVar(/*srcObjPath);
		msiGetObjType(*srcObjPath, *type);

		if (cyverse_isColl(*type)) {
			foreach( *row in
				SELECT META_COLL_ATTR_VALUE
				WHERE COLL_NAME like '*srcObjPath' AND META_COLL_ATTR_NAME = 'ipc::trash_timestamp'
			) {
				temporaryStorage.'*timestampVar' = *row.META_COLL_ATTR_VALUE;
			}
		} else if (cyverse_isDataObj(*type)) {
			msiSplitPath(*srcObjPath, *coll, *obj);

			foreach( *row in
				SELECT META_DATA_ATTR_VALUE
				WHERE COLL_NAME like '*coll'
					AND DATA_NAME like '*obj'
					AND META_DATA_ATTR_NAME = 'ipc::trash_timestamp'
			) {
				temporaryStorage.'*timestampVar' = *row.META_DATA_ATTR_VALUE;
			}
		}
	}
}


# After a collection or data object is moved to trash, this sets a trash
# timestamp on it. If is a collection, it recursively sets a trash timestamp on
# everything in it.
#
# Parameters:
#  Instance          (string) unused
#  Comm              (`KeyValuePair_PI`) unused
#  DataObjRenameInp  (`KeyValuePair_PI`) information about the data object and
#                    its old path
#
# temporaryStorage:
#  trash_timestamp_<PATH*>  records the timestamp for the collection or data
#                           object with absolute path PATH is moved to trash,
#                           there is one for each deleted collection or data
#                           object
#
cyverse_trash_api_data_obj_rename_post(*Instance, *Comm, *DataObjRenameInp) {
	*zone = cyverse_ZONE;
	*destObjPath = *DataObjRenameInp.dst_obj_path;

	if (*destObjPath like '/*zone/trash/*') {
		msiGetSystemTime(*timestamp, "");
		_ipcTrash_manageTimeAVU("set", cyverse_getEntityType(*destObjPath), *destObjPath, *timestamp);
	}
	else if (
		*DataObjRenameInp.src_obj_path like '/*zone/trash/*'
		&& *DataObjRenameInp.dst_obj_path not like '/*zone/trash/*'
	) {
		*srcObjPath = *DataObjRenameInp.src_obj_path;
		*timestampVar = _ipcTrash_mkTimestampVar(/*srcObjPath);

		if (errorcode(temporaryStorage.'*timestampVar') == 0) {
			_ipcTrash_manageTimeAVU(
				"rm",
				cyverse_getEntityType(*destObjPath),
				*destObjPath,
				temporaryStorage.'*timestampVar' );
		}
	}
}


# If a data object is copied into trash this sets a trash timestamp on it.
#
# Parameters:
#  Instance        (string) unused
#  Comm            (`KeyValuePair_PI`) unused
#  DataObjCopyInp  (`KeyValuePair_PI`) information related to copy operation
#  TransStat       (unknown) unused
#
cyverse_trash_api_data_obj_copy_post(*Instance, *Comm, *DataObjCopyInp, *TransStat) {
	*zone = cyverse_ZONE;
	*destObjPath = *DataObjCopyInp.dst_obj_path;

	if (*destObjPath like '/*zone/trash/*') {
		msiGetSystemTime(*timestamp, "");
		_ipcTrash_manageTimeAVU("set", cyverse_DATA_OBJ, *destObjPath, *timestamp);
	}
}


# When a data object is created in trash, this sets a trash timestamp on it.
#
# Parameters:
#  Instance    (string) unused
#  Comm        (`KeyValuePair_PI`) unused
#  DataObjInp  (`KeyValuePair_PI`) information related to the created data
#              object
#
cyverse_trash_api_data_obj_create_post(*Instance, *Comm, *DataObjInp) {
	*zone = cyverse_ZONE;
	*objPath = *DataObjInp.obj_path;

	if (*objPath like '/*zone/trash/*') {
		msiGetSystemTime(*timestamp, "");
		_ipcTrash_manageTimeAVU("set", cyverse_DATA_OBJ, *objPath, *timestamp);
	}
}
