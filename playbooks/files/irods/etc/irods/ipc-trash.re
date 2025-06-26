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

_ipcTrash_manageTimeAVU(*action, *type, *path, *avuValue) {
  *actionArg = execCmdArg(*action);
  *typeArg = execCmdArg(*type);
  *pathArg = execCmdArg(*path);
  *avuValueArg = execCmdArg(*avuValue);
  *avuName = execCmdArg("ipc::trash_timestamp");
  *argv = "*actionArg *typeArg *pathArg *avuName *avuValueArg";
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
#   INSTANCE          (string) unused
#   COMM              (`KeyValuePair_PI`) unused
#   DATAOBJUNLINKINP  (`KeyValuePair_PI`) information about the data object
#                     being deleted
#
# temporaryStorage:
#  data_id_<PATH>          records the ID of the data object with absolute path
#                          PATH
#  trash_timestamp_<PATH>  records the timestamp when the data object with
#                          absolute path PATH is moved to trash
#
ipcTrash_api_data_obj_unlink_pre(*INSTANCE, *COMM, *DATAOBJUNLINKINP) {
  if (errorcode(*DATAOBJUNLINKINP.forceFlag) != 0) {
    msiGetSystemTime(*timestamp, "");
    *dataObjPath = *DATAOBJUNLINKINP.obj_path;
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
#  INSTANCE          (string) unused
#  COMM              (`KeyValuePair_PI`) unused
#  DATAOBJUNLINKINP  (`KeyValuePair_PI`) information about the data object being
#                    deleted
#
# temporaryStorage:
#  data_id_<PATH>          provides the ID of the data object with absolute
#                          path PATH
#  trash_timestamp_<PATH>  provides the timestamp when the data object with
#                          absolute path PATH is moved to trash
#
ipcTrash_api_data_obj_unlink_post(*INSTANCE, *COMM, *DATAOBJUNLINKINP) {
  *dataObjPath = *DATAOBJUNLINKINP.obj_path;
  *timestampVar = _ipcTrash_mkTimestampVar(/*dataObjPath);
  if (errorcode(temporaryStorage.'*timestampVar') == 0) {
    temporaryStorage.'*timestampVar' = "";
  }
  *dataIdVar = _ipcTrash_mkObjDataIdVar(/*dataObjPath);
  if (errorcode(temporaryStorage.'*dataIdVar') == 0) {
    *dataIdVarTemp = temporaryStorage.'*dataIdVar';
    foreach(*Row in SELECT COLL_NAME WHERE DATA_ID = '*dataIdVarTemp') {
      *collNameList = split(*Row.COLL_NAME, '/');
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
#  INSTANCE          (string) unused
#  COMM              (`KeyValuePair_PI`) unused
#  DATAOBJUNLINKINP  (`KeyValuePair_PI`) information about the data object being
#                    deleted
#
# temporaryStorage:
#  trash_timestamp_<PATH>  provides the timestamp for object with path PATH to
#                          be removed
#
ipcTrash_api_data_obj_unlink_except(*INSTANCE, *COMM, *DATAOBJUNLINKINP) {
  *dataObjPath = *DATAOBJUNLINKINP.obj_path;
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
#  INSTANCE        (string) unused
#  COMM            (`KeyValuePair_PI`) unused
#  DATAOBJINP      (`KeyValuePair_PI`) information related to the data object
#  DATAOBJINPBBUF  (unknown) unused
#  PORTAL_OPR_OUT  (unknown) unused
#
ipcTrash_api_data_obj_put_post(*INSTANCE, *COMM, *DATAOBJINP, *DATAOBJINPBBUF, *PORTALOPROUT) {
  *zone = cyverse_ZONE;
  if (*DATAOBJINP.obj_path like '/*zone/trash/*') {
    msiGetSystemTime(*timestamp, "");
    _ipcTrash_manageTimeAVU("set", cyverse_DATA_OBJ, *DATAOBJINP.obj_path, *timestamp);
  }
}


# When a collection is being moved to trash, this sets a trash timestamp on the
# collection.
#
# Parameters:
#  INSTANCE     (string) unused
#  COMM         (`KeyValuePair_PI`) unused
#  RMCOLLINP    (`KeyValuePair_PI`) information about the collection being
#               deleted
#  COLLOPRSTAT  (unknown) unused
#
# temporaryStorage:
#  trash_timestamp_<PATH>  records the timestamp when the collection with
#                          absolute path PATH is moved to trash
#
ipcTrash_api_rm_coll_pre(*INSTANCE, *COMM, *RMCOLLINP, *COLLOPRSTAT) {
  if (errorcode(*RMCOLLINP.forceFlag) != 0) {
    msiGetSystemTime(*timestamp, "");
    *collNamePath = *RMCOLLINP.coll_name;
    *timestampVar = _ipcTrash_mkTimestampVar(/*collNamePath);
    temporaryStorage.'*timestampVar' = *timestamp;
    _ipcTrash_manageTimeAVU("set", cyverse_COLL, *collNamePath, *timestamp);
  }
}


# If moving a collection to trash fails, this removes the trash timestamp.
#
# Parameters:
#  INSTANCE     (string) unused
#  COMM         (`KeyValuePair_PI`) unused
#  RMCOLLINP    (`KeyValuePair_PI`) information about the collection being
#               deleted
#  COLLOPRSTAT  (unknown) unused
#
# temporaryStorage:
#  trash_timestamp_<PATH>  records the timestamp when the collection with
#                          absolute path PATH is moved to trash
#
ipcTrash_api_rm_coll_except(*INSTANCE, *COMM, *RMCOLLINP, *COLLOPRSTAT) {
  *collNamePath = *RMCOLLINP.coll_name;
  *timestampVar = _ipcTrash_mkTimestampVar(/*collNamePath);
  if (errorcode(temporaryStorage.'*timestampVar') == 0) {
    _ipcTrash_manageTimeAVU(
      "rm", cyverse_COLL, *collNamePath, temporaryStorage.'*timestampVar' );
  }
}

# When a collection is created in trash, this sets a trash timestamp on it.
#
# Parameters:
#  INSTANCE       (string) unused
#  COMM           (`KeyValuePair_PI`) unused
#  COLLCREATEINP  (`KeyValuePair_PI`) information related to the new collection
#
ipcTrash_api_coll_create_post(*INSTANCE, *COMM, *COLLCREATEINP) {
  *zone = cyverse_ZONE;
  *collNamePath = *COLLCREATEINP.coll_name;
  if (*collNamePath like '/*zone/trash/*') {
    msiGetSystemTime(*timestamp, "");
    _ipcTrash_manageTimeAVU("set", cyverse_COLL, *collNamePath, *timestamp);
  }
}


# When a collection or data object is being moved to trash, this records a trash
# timestamp for it, and if it is a collection, recursively for everything in it.
#
# Parameters:
#  INSTANCE          (string) unused
#  COMM              (`KeyValuePair_PI`) unused
#  DATAOBJRENAMEINP  (`KeyValuePair_PI`) information about the data object and
#                    its new path
#
# temporaryStorage:
#  trash_timestamp_<PATH*>  records the timestamp for the collection or data
#                           object with absolute path PATH is moved to trash,
#                           there is one for each deleted collection or data
#                           object
#
ipcTrash_api_data_obj_rename_pre(*INSTANCE, *COMM, *DATAOBJRENAMEINP) {
  *zone = cyverse_ZONE;
  if (
    (*DATAOBJRENAMEINP.src_obj_path like '/*zone/trash/*')
    && (*DATAOBJRENAMEINP.dst_obj_path not like '/*zone/trash/*')
  ) {
    *srcObjPath = *DATAOBJRENAMEINP.src_obj_path;
    *timestampVar = _ipcTrash_mkTimestampVar(/*srcObjPath);
    msiGetObjType(*srcObjPath, *Type);
    if (cyverse_isColl(*Type)) {
      foreach(*Row in SELECT META_COLL_ATTR_VALUE
                        WHERE COLL_NAME like '*srcObjPath'
                          AND META_COLL_ATTR_NAME = 'ipc::trash_timestamp') {
                            temporaryStorage.'*timestampVar' = *Row.META_COLL_ATTR_VALUE;
      }
    }
    else if (cyverse_isDataObj(*Type)) {
      msiSplitPath(*srcObjPath, *Coll, *File);
      foreach(*Row in SELECT META_DATA_ATTR_VALUE
                        WHERE COLL_NAME like '*Coll'
                          AND DATA_NAME like '*File'
                            AND META_DATA_ATTR_NAME = 'ipc::trash_timestamp') {
                              temporaryStorage.'*timestampVar' = *Row.META_DATA_ATTR_VALUE;
      }
    }
  }
}


# After a collection or data object is moved to trash, this sets a trash
# timestamp on it. If is a collection, it recursively sets a trash timestamp on
# everything in it.
#
# Parameters:
#  INSTANCE          (string) unused
#  COMM              (`KeyValuePair_PI`) unused
#  DATAOBJRENAMEINP  (`KeyValuePair_PI`) information about the data object and
#                    its old path
#
# temporaryStorage:
#  trash_timestamp_<PATH*>  records the timestamp for the collection or data
#                           object with absolute path PATH is moved to trash,
#                           there is one for each deleted collection or data
#                           object
#
ipcTrash_api_data_obj_rename_post(*INSTANCE, *COMM, *DATAOBJRENAMEINP) {
  *zone = cyverse_ZONE;
  *destObjPath = *DATAOBJRENAMEINP.dst_obj_path;
  if (*destObjPath like '/*zone/trash/*') {
    msiGetSystemTime(*timestamp, "");
    _ipcTrash_manageTimeAVU("set", cyverse_getEntityType(*destObjPath), *destObjPath, *timestamp);
  }
  else if (
    (*DATAOBJRENAMEINP.src_obj_path like '/*zone/trash/*')
    && (*DATAOBJRENAMEINP.dst_obj_path not like '/*zone/trash/*')
  ) {
    *srcObjPath = *DATAOBJRENAMEINP.src_obj_path;
    *timestampVar = _ipcTrash_mkTimestampVar(/*srcObjPath);
    if (errorcode(temporaryStorage.'*timestampVar') == 0) {
      _ipcTrash_manageTimeAVU(
        "rm", cyverse_getEntityType(*destObjPath), *destObjPath, temporaryStorage.'*timestampVar' );
    }
  }
}


# If a data object is copied into trash this sets a trash timestamp on it.
#
# Parameters:
#  INSTANCE        (string) unused
#  COMM            (`KeyValuePair_PI`) unused
#  DATAOBJCOPYINP  (`KeyValuePair_PI`) information related to copy operation
#  TRANSSTAT       (unknown) unused
#
ipcTrash_api_data_obj_copy_post(*INSTANCE, *COMM, *DATAOBJCOPYINP, *TRANSSTAT) {
  *zone = cyverse_ZONE;
  *destObjPath = *DATAOBJCOPYINP.dst_obj_path;
  if (*destObjPath like '/*zone/trash/*') {
    msiGetSystemTime(*timestamp, "");
    _ipcTrash_manageTimeAVU("set", cyverse_DATA_OBJ, *destObjPath, *timestamp);
  }
}


# When a data object is created in trash, this sets a trash timestamp on it.
#
# Parameters:
#  INSTANCE    (string) unused
#  COMM        (`KeyValuePair_PI`) unused
#  DATAOBJINP  (`KeyValuePair_PI`) information related to the created data
#              object
#
ipcTrash_api_data_obj_create_post(*INSTANCE, *COMM, *DATAOBJINP) {
  *zone = cyverse_ZONE;
  *objPath = *DATAOBJINP.obj_path;
  if (*objPath like '/*zone/trash/*') {
    msiGetSystemTime(*timestamp, "");
    _ipcTrash_manageTimeAVU("set", cyverse_DATA_OBJ, *objPath, *timestamp);
  }
}
