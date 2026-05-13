# Replication logic
#
# All data objects belong to at least on resource. The resource a data object's
# primary replica belongs to depends on the data object's parent collection. The
# resource residency policy for a given collection is either assigned to the
# collection by an AVU or to one of its ancestral collections, with the policy
# attached to its most recent ancestor taking precedent. Depending on the policy
# attached to the parent collection, a user may force the primary replica to be
# stored on a specific resource. By default, the primary replica is stored on
# CyVerseRes.
#
# A data object may be replicated to a second resource. This may automatically
# happen asynchronously, or a user may manually replicate the object
# synchronously. Whether or not replication is allowed, and whether or not it
# happens automatically depend on policy attached to the resource where its
# primary replica is stored. All data stored on the CyVerseRes are automatically
# asynchronously replicated to taccRes.
#
# All policy controlling replica residency and replication are controlled by the
# following AVUs.
#
# ipc::hosted-collection COLL (forced|preferred)
#  When attached to a resource RESC, this AVU indicates that data objects that
#  belong to the collection COLL are to have their primary replica stored on
#  RESC. When the unit is 'preferred', the user may override this. COLL is the
#  absolute path to the base collection. If a resource is determined by both the
#  iRODS server a client connects to and an ipc::hosted-collection AVU, the AVU
#  takes precedence. If two or more AVUs match, the resource whose COLL has the
#  specific match is used.
#
# ipc::replica-resource REPL-RESC (forced|preferred)
#  When attached to a resource RESC, this AVU indicates that the resource
#  REPL-RESC is to asynchronously replicate the contents of RESC. When the unit
#  is 'preferred', the user may override this.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.


# DEFERRED FUNCTIONS AND RULES

_repl_replicate(*Object, *RescName) {
  _repl_logMsg('replicating data object *Object to *RescName');

  *objPath = cyverse_getDataPath(*Object);

  if (*objPath == '') {
    _repl_logMsg('data object *Object no longer exists');
  } else {
    temporaryStorage.cyverse_repl_replicate = 'REPL_FORCED_REPL_RESC';

# XXX - As of iRODS 4.3.3, ticket information doesn't get sent to deferred rules.
#     msiAddKeyValToMspStr('backupRescName', *RescName, *opts);
#     msiAddKeyValToMspStr('verifyChksum', '', *opts);
#     *status = errormsg(msiDataObjRepl(*objPath, *opts, *_), *err);
    *admArg = execCmdArg('-M');
    *backupArg = execCmdArg('-B');
    *destRescFlgArg = execCmdArg('-R');
    *destRescArg = execCmdArg(*RescName);
    *dataArg = execCmdArg(*objPath);
    *args = '*admArg *backupArg *destRescFlgArg *destRescArg *dataArg';
    *status = errormsg(msiExecCmd('irepl-exec', *args, '', '', '', *resp), *err);
    msiGetStderrInExecCmdOut(*resp, *msg);
    *err = *err ++ ' (' ++ *msg ++ ')';
# XXX - ^^^

    temporaryStorage.cyverse_repl_replicate = '';

    if (*status < 0) {
      if (*status == -808000 || *status == -817000) {
        _repl_logMsg(
          'failed to replicate data object *Object (*objPath), data no longer exists: *err' );
      } else if (*status == -314000) {
        _repl_logMsg(
          'failed to replicate data object *Object (*objPath) due to checksum error: *err' );
      } else {
        _repl_logMsg('failed to replicate data object *Object (*objPath), retry in 8 hours: *err');
        *status;
      }
    } else {
      _repl_logMsg('replicated data object *Object (*objPath)');
    }
  }
}


_repl_mvReplicas(*Object, *IngestName, *ReplName) {
  _repl_logMsg('moving replicas of data object *Object');

  *dataPath = cyverse_getDataPath(*Object);

  if (*dataPath != '') {
    *replFail = false;

    if (_repl_replicate(*Object, *IngestName) < 0) {
      *replFail = true;
    }

    if (*ReplName != *IngestName) {
      if (_repl_replicate(*Object, *ReplName) < 0) {
        *replFail = true;
      }
    }

    if (*replFail) {
      fail;
    }

    # Once a replica exists on all the project's resource, remove the other replicas
    foreach (*rec in SELECT DATA_RESC_HIER, DATA_REPL_NUM WHERE DATA_ID = '*Object') {
      *rescHier = *rec.DATA_RESC_HIER;
      *replNum = *rec.DATA_REPL_NUM;

      if (!(*rescHier like regex '^(*IngestName|*ReplName)(;.*)?$')) {
        if (errorcode(msiDataObjTrim(*dataPath, 'null', *replNum, '1', 'null', *status)) < 0) {
          _repl_logMsg('failed to trim replica of *Object on *rescHier (*status)');
          *replFail = true;
        }
      }
    }

    if (*replFail) {
      _repl_logMsg('failed to completely move replicas of data object *Object');
      fail;
    }
  }

  _repl_logMsg('moved replicas of data object *Object');
}


_repl_syncReplicas(*Object) {
  _repl_logMsg('syncing replicas of data object *Object');

  *dataPath = cyverse_getDataPath(*Object);

  if (*dataPath == '') {
    _repl_logMsg('data object *Object no longer exists');
  } else {
# XXX - As of iRODS 4.3.3, ticket information doesn't get sent to deferred rules.
#     msiAddKeyValToMspStr('all', '', *opts);
#     msiAddKeyValToMspStr('irodsAdmin', '', *opts);
#     msiAddKeyValToMspStr('updateRepl', '', *opts);
#     msiAddKeyValToMspStr('verifyChksum', '', *opts);
#     *status = errormsg(msiDataObjRepl(*dataPath, *opts, *status), *err);
    *admArg = execCmdArg('-M');
    *allArg = execCmdArg('-a');
    *updateArg = execCmdArg('-U');
    *dataArg = execCmdArg(*dataPath);
    *args = '*admArg *allArg *updateArg *dataArg';
    *status = errormsg(msiExecCmd('irepl-exec', *args, '', '', '', *_), *err);
# XXX - ^^^

    if (*status < 0 && *status != -808000) {
      _repl_logMsg(
        'failed to sync replicas of data object *Object (*dataPath) trying again in 8 hours:'
        ++ ' *err' );

      *status;
    } else {
      _repl_logMsg('synced replicas of data object *Object (*dataPath)');
    }
  }
}


# SUPPORTING FUNCTIONS AND RULES

_delayTime : int
_delayTime =
  let *_ = if (!cyverse_hasKey(temporaryStorage, 'cyverse_repl_delayTime')) {
      temporaryStorage.cyverse_repl_delayTime = str(cyverse_INIT_REPL_DELAY);
    } in
  int(temporaryStorage.cyverse_repl_delayTime);


_incDelayTime {
  temporaryStorage.cyverse_repl_delayTime = str(1 + int(temporaryStorage.cyverse_repl_delayTime));
}


_repl_logMsg(*Msg) {
  writeLine('serverLog', 'DS: *Msg');
}


_repl_scheduleMv(*Object, *IngestName, *ReplName) {
  delay('<PLUSET>' ++ str(_delayTime) ++ 's</PLUSET><EF>8h REPEAT UNTIL SUCCESS</EF>')
  {_repl_mvReplicas(*Object, *IngestName, *ReplName);}

  _incDelayTime;
}


_repl_scheduleRepl(*Object, *RescName) {
  delay('<PLUSET>' ++ str(_delayTime) ++ 's</PLUSET><EF>8h REPEAT UNTIL SUCCESS</EF>')
  {_repl_replicate(*Object, *RescName);}

  _incDelayTime;
}


_repl_scheduleSyncReplicas(*Object) {
# XXX - There is a bug in iRODS 4.3.3 that prevents a general query that doesn't
#       explicitly use r_coll_main from working when authorization is controlled
#       by a ticket on a collection.
#   foreach ( *rec in
#     SELECT COUNT(DATA_REPL_NUM) WHERE DATA_ID = '*Object' AND DATA_REPL_STATUS = '0'
#   ) {
  foreach ( *rec in
    SELECT COUNT(DATA_REPL_NUM), COLL_ID WHERE DATA_ID = '*Object' AND DATA_REPL_STATUS = '0'
  ) {
# XXX - ^^^
    if (int(*rec.DATA_REPL_NUM) > 0) {
      delay('<PLUSET>' ++ str(_delayTime) ++ 's</PLUSET><EF>8h REPEAT UNTIL SUCCESS</EF>')
      {_repl_syncReplicas(*Object)}

      _incDelayTime;
    }
  }
}


# Given an absolute path to a data object, this rule determines the resource
# where member data objects have their primary replicas stored. It returns a
# two-tuple with the first is element is the name of the resource, and the
# second is the value 'forced' or 'preferred'. 'forced' means that the user
# cannot override this choice, and 'preferred' means they can.
_repl_findResc(*DataPath) {
  msiSplitPath(*DataPath, *collPath, *dataName);
  *resc = cyverse_DEFAULT_RESC;
  *residency = 'preferred';
  *bestColl = '/';

  foreach (*record in SELECT META_RESC_ATTR_VALUE, META_RESC_ATTR_UNITS, RESC_NAME
                      WHERE META_RESC_ATTR_NAME = 'ipc::hosted-collection') {
    if (*collPath ++ '/' like *record.META_RESC_ATTR_VALUE ++ '/*') {
      if (strlen(*record.META_RESC_ATTR_VALUE) > strlen(*bestColl)) {
        *bestColl = *record.META_RESC_ATTR_VALUE;
        *residency = *record.META_RESC_ATTR_UNITS;
        *resc = *record.RESC_NAME;
      }
    }
  }

  *result = (*resc, *residency);
  *result;
}


# Given a resource, this rule determines the list of resources that
# asynchronously replicate its replicas.
_repl_findReplResc(*Resc) {
  *residency = 'preferred';

  if (*Resc == cyverse_DEFAULT_RESC) {
    *repl = cyverse_DEFAULT_REPL_RESC;
  } else {
    *repl = *Resc;

    foreach ( *rec in
      SELECT META_RESC_ATTR_VALUE, META_RESC_ATTR_UNITS
      WHERE RESC_NAME = *Resc AND META_RESC_ATTR_NAME = 'ipc::replica-resource'
    ) {
      *repl = *rec.META_RESC_ATTR_VALUE;
      *residency = *rec.META_RESC_ATTR_UNITS;
    }
  }

  *result = (*repl, *residency);
  *result;
}


_ipcRepl_createOrOverwrite(*DataPath, *DestRescHier, *New) {
  *dataId = cyverse_getDataId(*DataPath);
  (*ingestResc, *_) = _repl_findResc(*DataPath);
  (*replResc, *_) = _repl_findReplResc(*ingestResc);

  if (*New) {
    _repl_scheduleRepl(
      *dataId, if hd(split(*DestRescHier, ';')) == *replResc then *ingestResc else *replResc );
  } else {
    _repl_scheduleSyncReplicas(*dataId);
  }
}


# REPLICATION RULES

# This rule ensures that the correct resource is chosen for first replica of a
# newly created data object.
#
# Parameters:
#  DataPath  (path) the path to the data object being created
#
cyverse_repl_acSetRescSchemeForCreate(*DataPath) {
  (*resc, *residency) = _repl_findResc(*DataPath);
  msiSetDefaultResc(*resc, *residency);
}


# This rule ensures that the correct resource is chosen for the second and
# subsequent replicas of a data object.
#
# Parameters:
#  DataPath  (path) the path to the data object being replicated
#
cyverse_repl_acSetRescSchemeForRepl(*DataPath) {
  if (cyverse_getValue(temporaryStorage, 'cyverse_repl_replicate') != 'REPL_FORCED_REPL_RESC') {
    (*resc, *_) = _repl_findResc(*DataPath);
    (*repl, *residency) = _repl_findReplResc(*resc);
    msiSetDefaultResc(*repl, *residency);
  }
}


# This rule ensures that uploaded files are replicated.
#
# Parameters:
#  User           (string) unused
#  Zone           (string) unused
#  DATA_OBJ_INFO  (`KeyValuePair_PI`) information related to the created data
#                 object
#
cyverse_repl_dataObjCreated(*User, *Zone, *DATA_OBJ_INFO) {
  _ipcRepl_createOrOverwrite(
    cyverse_getValue(*DATA_OBJ_INFO, 'logical_path'),
    cyverse_getValue(*DATA_OBJ_INFO, 'resc_hier'),
    true );
}


# BULK_DATA_OBJ_PUT

# This ensures that a bulk uploaded data object is replicated.
#
# Parameters:
#  Instance       (string) unknown
#  Comm           (`KeyValuePair_PI`) user connection and auth information
#  BulkOpInp      (`KeyValuePair_PI`) information related to the bulk upload
#  BulkOpInpBBuf  (unknown) may contain the contents of the uploaded files
#
cyverse_repl_api_bulk_data_obj_put_post(*Instance, *Comm, *BulkOpInp, *BulkOpInpBBuf) {
  *rescHier = cyverse_getValue(*BulkOpInp, 'resc_hier');

  foreach (*key in *BulkOpInp) {
    if (*key like 'logical_path_*') {
      _ipcRepl_createOrOverwrite(cyverse_getValue(*BulkOpInp, *key), *rescHier, true);
    }
  }
}


# DATA_OBJ_COPY

# This ensures that a copy of a data object is replicated, if a data object is

# overwritten, the other replicas are synced.
#
# Parameters:
#  Instance        (string) unknown
#  Comm            (`KeyValuePair_PI`) user connection and auth information
#  DataObjCopyInp  (`KeyValuePair_PI`) information related to copy operation
#  TransStat       unknown
#
cyverse_repl_api_data_obj_copy_post(*Instance, *Comm, *DataObjCopyInp, *TransStat) {
  _ipcRepl_createOrOverwrite(
    cyverse_getValue(*DataObjCopyInp, 'dst_obj_path'),
    cyverse_getValue(*DataObjCopyInp, 'dst_resc_hier'),
    cyverse_getValue(*DataObjCopyInp, 'dst_openType') == cyverse_FILE_CREATE );
}


# DATA_OBJ_PUT

# This ensures that an uploaded data object is replicated, if a data object is
# overwritten, the other replicas are synced.
#
# Parameters:
#  Instance        (string) unknown
#  Comm            (`KeyValuePair_PI`) user connection and auth information
#  DataObjInp      (`KeyValuePair_PI`) information related to the data object
#  DataObjInpBBuf  (unknown) may contain the contents of the file being uploaded
#  PORTAL_OPR_OUT  unknown
#
cyverse_repl_api_data_obj_put_post(
  *Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PORTAL_OPR_OUT
) {
  _ipcRepl_createOrOverwrite(
    cyverse_getValue(*DataObjInp, 'obj_path'),
    cyverse_getValue(*DataObjInp, 'resc_hier'),
    cyverse_getValue(*DataObjInp, 'openType') == cyverse_FILE_CREATE );
}


# DATA_OBJ_RENAME

# This ensures that when a data object is moved, if required, the replicas are
# moved to appropriate resources.
#
# Parameters:
#  Instance          (string) unknown
#  Comm              (`KeyValuePair_PI`) user connection and auth information
#  DataObjRenameInp  (`KeyValuePair_PI`) information about the data object and
#                    its old path
#
cyverse_repl_api_data_obj_rename_post(*Instance, *Comm, *DataObjRenameInp) {
  *dstPath = cyverse_getValue(*DataObjRenameInp, 'dst_obj_path');
  (*dstResc, *_) = _repl_findResc(*dstPath);
  (*srcResc, *_) = _repl_findResc(cyverse_getValue(*DataObjRenameInp, 'src_obj_path'));

  if (*dstResc != cyverse_DEFAULT_RESC) {
    if (*srcResc != *dstResc) {
      (*dstRepl, *_) = _repl_findReplResc(*dstResc);
    }
  } else {
    if (*srcResc != cyverse_DEFAULT_RESC) {
      *dstRepl = cyverse_DEFAULT_REPL_RESC;
    }
  }

  if (*dstResc != *srcResc) {
    *srcType = int(cyverse_getValue(*DataObjRenameInp, 'src_opr_type'));

    if (*srcType == 11) {  # data object
      _repl_scheduleMv(cyverse_getDataId(*dstPath), *dstResc, *dstRepl);
    } else {  # collection
      foreach (*rec in SELECT DATA_ID WHERE COLL_NAME = *dstPath || LIKE '*dstPath/%') {
        _repl_scheduleMv(int(*rec.DATA_ID), *dstResc, *dstRepl);
      }
    }
  }
}


# PHY_PATH_REG

# This ensures that when a data object is created via registration of a replica,
# that is properly replicated. If a replica was added to an existing data
# object, it ensures the other replicas are synced.
#
# Parameters:
#  Instance       (string) unknown
#  Comm           (`KeyValuePair_PI`) user connection and auth information
#  PhyPathRegInp  (`KeyValuePair_PI`) information related to the physical path
#                 registration
#
cyverse_repl_api_phy_path_reg_post(*Instance, *Comm, *PhyPathRegInp) {
  _ipcRepl_createOrOverwrite(
    cyverse_getValue(*PhyPathRegInp, 'obj_path'),
    cyverse_getValue(*PhyPathRegInp, 'resc_hier'),
    !cyverse_hasKey(*PhyPathRegInp, 'regRepl') );
}


# TOUCH

# This ensures that a data object created by itouch, that is replicated.
#
# Parameters:
#  Instance   (string) unknown
#  Comm       (`KeyValuePair_PI`) user connection and auth information
#  JsonInput  (string) a JSON-serialized description of the touch request
#
cyverse_repl_api_touch_post(*Instance, *Comm, *JsonInput) {
# XXX - As of iRODS 4.3.3, *JsonInput buffer ends with a serialized NUL, i.e., the string '\x00'
#   (*input, *_) = match cyverse_json_deserialize(*JsonInput.buf) with
#     | cyverse_json_deserialize_val(*v, *_) => (*v, "")
  (*input, *_) = match cyverse_json_deserialize(trimr(*JsonInput.buf, '\\x00')) with
    | cyverse_json_deserialize_val(*v, *_) => (*v, "");
# XXX - ^^^

  *dataPath = match cyverse_json_getValue(*input, 'logical_path') with
    | cyverse_json_empty => ''
    | cyverse_json_str(*s) => *s;

  if (*dataPath != '') {
    *options = cyverse_json_getValue(*input, 'options');

    *noCreate = match cyverse_json_getValue(*options, 'no_create') with
      | cyverse_json_empty => false
      | cyverse_json_bool(*b) => *b;

    *replNumSet = match cyverse_json_getValue(*options, 'replica_number') with
      | cyverse_json_empty => false
      | cyverse_json_num(*n) => true;

    *rescNameSet = match cyverse_json_getValue(*options, 'leaf_resource_name') with
      | cyverse_json_empty => false
      | cyverse_json_str(*_) => true;

    if (!*noCreate && !*replNumSet && !*rescNameSet) {
      msiSplitPath(*dataPath, *collPath, *dataName);

      foreach(*rec in SELECT DATA_RESC_HIER WHERE COLL_NAME = *collPath AND DATA_NAME = *dataName) {
        _ipcRepl_createOrOverwrite(*dataPath, *rec.DATA_RESC_HIER, true);
      }
    }
  }
}


# DATA_OBJ_CREATE
#
# NB: This PEP is used together with DATA_OBJ_CLOSE

# When a data object is created using a DATA_OBJ_CREATE request, ensure that it
# is replicated. This stores the data object path in temporaryStorage using the
# key `cyverse_repl_dataObjClose_objPath`. The selected resource hierarchy for
# its replica using the key `cyverse_repl_dataObjClose_selectedHierarchy`. The
# key `cyverse_repl_dataObjClose_created` is set to 'created'. The replication
# logic will be triggered in the DATA_OBJ_CLOSE PEP.
#
# Parameters:
#  Instance    (string) unknown
#  Comm        (`KeyValuePair_PI`) user connection and auth information
#  DataObjInp  (`KeyValuePair_PI`) information related to the created data
#              object
#
cyverse_repl_api_data_obj_create_post(*Instance, *Comm, *DataObjInp) {
  temporaryStorage.cyverse_repl_dataObjClose_objPath = cyverse_getValue(*DataObjInp, 'obj_path');
  temporaryStorage.cyverse_repl_dataObjClose_rescHier = cyverse_getValue(
    *DataObjInp, 'selected_hierarchy' );
  temporaryStorage.cyverse_repl_dataObjClose_created = 'created';
}


# DATA_OBJ_OPEN
#
# NB: This PEP is used together with DATA_OBJ_CLOSE and possibly DATA_OBJ_WRITE.

# When a data object is created using a DATA_OBJ_OPEN request, ensure that it
# is replicated. If an existing object is modified, ensure that its replicas are
# synced. This stores the data object path in temporaryStorage using the
# key `cyverse_repl_dataObjClose_objPath`. The selected resource hierarchy for
# its replica using the key `cyverse_repl_dataObjClose_selectedHierarchy`. The
# key `cyverse_repl_dataObjClose_created` is set to 'created' if the data object
# was created. The key `cyverse_repl_dataObjClose_modified` is set to `modified`
# if the data object was truncated. The replication logic will be triggered in
# the DATA_OBJ_CLOSE PEP.
#
# Parameters:
#  Instance    (string) unknown
#  Comm        (`KeyValuePair_PI`) user connection and auth information
#  DataObjInp  (`KeyValuePair_PI`) information related to the data object
#
cyverse_repl_api_data_obj_open_post(*Instance, *Comm, *DataObjInp) {
  *flags = cyverse_getValue(*DataObjInp, 'open_flags');

  if (*flags != cyverse_OPEN_FLAG_R) {
    temporaryStorage.cyverse_repl_dataObjClose_objPath = cyverse_getValue(*DataObjInp, 'obj_path');
    temporaryStorage.cyverse_repl_dataObjClose_rescHier = cyverse_getValue(
      *DataObjInp, 'selected_hierarchy' );
    if (cyverse_getValue(*DataObjInp, 'openType') == cyverse_FILE_CREATE) {
      temporaryStorage.cyverse_repl_dataObjClose_created = 'created';
    }
    if (cyverse_replTruncated(*flags)) {
      temporaryStorage.cyverse_repl_dataObjClose_modified = 'modified';
    }
  }
}


# DATA_OBJ_WRITE
#
# NB: This PEP is used together with either DATA_OBJ_OPEN and DATA_OBJ_CLOSE.

# When a data object is modified by a DATA_OBJ_WRITE request, the
# temporaryStorage key `cyverse_repl_dataObjClose_modified` is set to
# 'modified'.
#
# Parameters:
#  Instance             (string) unknown
#  Comm                 (`KeyValuePair_PI`) user connection and auth information
#  DataObjWriteInp      (`KeyValuePair_PI`) information about the write request
#  DataObjWriteInpBBuf  (unknown) the contents that were added to the object
#
cyverse_repl_api_data_obj_write_post(*Instance, *Comm, *DataObjWriteInp, *DataObjWriteInpBBuf) {
  temporaryStorage.cyverse_repl_dataObjClose_modified = 'modified';
}


# DATA_OBJ_CLOSE
#
# NB: This PEP is used together with one of DATA_OBJ_CREATE or DATA_OBJ_OPEN and
#     possibly DATA_OBJ_WRITE.

# This ensures that a data object created by a CREATE or OPEN is properly
# replicated. If a data object is modified by a OPEN+WRITE, it ensures all of
# the replicas are synced.
#
# Parameters:
#  Instance         (string) unknown
#  Comm             (`KeyValuePair_PI`) user connection and auth information
#  DataObjCloseInp  (`KeyValuePair_PI`) information related to the data object
#                   close request
#
cyverse_repl_api_data_obj_close_post(*Instance, *Comm, *DataObjCloseInp) {
  *path = cyverse_getValue(temporaryStorage, 'cyverse_repl_dataObjClose_objPath');

  if (*path != '') {
    *destResc = cyverse_getValue(temporaryStorage, 'cyverse_repl_dataObjClose_rescHier');

    *needsRepl = false;
    if (cyverse_getValue(temporaryStorage, 'cyverse_repl_dataObjClose_created') == 'created') {
      *new = true;
      *needsRepl = true;
    } else if (
      cyverse_getValue(temporaryStorage, 'cyverse_repl_dataObjClose_modified') == 'modified'
    ) {
      *new = false;
      *needsRepl = true;
    }

    if (*needsRepl) {
      _ipcRepl_createOrOverwrite(*path, *destResc, *new);
    }

    temporaryStorage.cyverse_repl_dataObjClose_objPath = '';
    temporaryStorage.cyverse_repl_dataObjClose_rescHier = '';
    temporaryStorage.cyverse_repl_dataObjClose_created = '';
    temporaryStorage.cyverse_repl_dataObjClose_modified = '';
  }
}


# REPLICA_OPEN
#
# NB: This PEP is used together with REPLICA_CLOSE

# This is the post processing logic for when a data object replica is opened
# through the API using a REPLICA_OPEN request.
#
# Parameters:
#  Instance     (string) unknown
#  Comm         (`KeyValuePair_PI`) user connection and auth information
#  DataObjInp   (`KeyValuePair_PI`) information about the data object
#  JSON_OUTPUT  unknown
#
cyverse_repl_api_replica_open_post(*Instance, *Comm, *DataObjInp, *JSON_OUTPUT) {
  *path = cyverse_getValue(*DataObjInp, 'obj_path');

  if (*path != '') {
    temporaryStorage.cyverse_repl_replica_dataObjPath = *path;
    temporaryStorage.cyverse_repl_replica_rescHier = cyverse_getValue(*DataObjInp, 'resc_hier');
    temporaryStorage.cyverse_repl_replica_openType =
      if cyverse_hasKey(*DataObjInp, 'openType') then cyverse_getValue(*DataObjInp, 'openType')
      else cyverse_FILE_OPEN_WRITE;
  }
}


# REPLICA_CLOSE
#
# NB: This PEP is used together with REPLICA_OPEN

# This is ensures that a data object created by istream is properly replicated.
# If a data object is modified, it ensures all of the replicas are synced.
#
# Parameters:
#  Instance   (string) unknown
#  Comm       (`KeyValuePair_PI`) user connection and auth information
#  JsonInput  (string) a JSON-serialized description of the replica change
#
cyverse_repl_api_replica_close_post(*Instance, *Comm, *JsonInput) {
  *path = cyverse_getValue(temporaryStorage, 'cyverse_repl_replica_dataObjPath');

  if (*path != '') {
    *destResc = cyverse_getValue(temporaryStorage, 'cyverse_repl_replica_rescHier');
    *openType = cyverse_getValue(temporaryStorage, 'cyverse_repl_replica_openType');
    _ipcRepl_createOrOverwrite(*path, *destResc, *openType == cyverse_FILE_CREATE);
    temporaryStorage.cyverse_repl_replica_dataObjPath = '';
    temporaryStorage.cyverse_repl_replica_rescHier = '';
    temporaryStorage.cyverse_repl_replica_openType = '';
  }
}


# RESOURCE

# This rule is provides the preprocessing logic for determine which  storage
# resource to choose for a replica. It is meant for project specific
# implementations where a project implementation is within an `on` block that
# restricts the resource resolution to entities relevant to the project.post
#
# Parameters:
#  INSTANCE   (string) the resource being considered
#  CONTEXT    (`KeyValuePair_PI`) the resource plugin context
#  OUT        (`KeyValuePair_PI`) unused
#  OPERATION  (string) the operation that will be performed on the replica,
#             "CREATE" for creating the replica, "OPEN" for reading the replica,
#             and "WRITE" for overwriting an existing replica.
#  HOST       (string) the host executing this policy
#  PARSER     (`KeyValuePair_PI`) unused
#  VOTE       (float) unused
#
# temporaryStorage:
#  cyverse_repl_replicate  this value is read to see if replication is forced to
#                          a specific resource
#
pep_resource_resolve_hierarchy_pre(*INSTANCE, *CONTEXT, *OUT, *OPERATION, *HOST, *PARSER, *VOTE) {
  on (cyverse_getValue(temporaryStorage, 'cyverse_repl_replicate') == 'REPL_FORCED_REPL_RESC') {}
}
