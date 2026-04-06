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
# DEPRECATED FUNCTIONALITY
#
# Unlike the logic in cyverse_logic.re, the replication logic doesn't apply
# globally. Different projects may have different replication policies.
#
# THIRD PARTY REPLICATION LOGIC
#
# Third party replication logic goes in its own file, and the file should be
# included in cyverse_core.re. Third party logic should be implement a set of
# functions prefixed by the containing file name.
#
# Here's the list of functions that need to be provided by in the replication
# logic file.
#
# <file_name>_replBelongsTo(*Entity)
#  Determines if the provided collection or data object belongs to the project
#
#  Parameters:
#   Entity  the absolute iRODS path to the collection or data object
#
#  Returns:
#   a Boolean indicating whether or not the collection or data object belongs to
#   the project
#
#  Example:
#   project_replBelongsTo : path -> boolean
#   project_replBelongsTo(*Entity) =
#      str(*Entity) like '/' ++ cyverse_ZONE ++ '/home/shared/project/*'
#
# <file_name>_replIngestResc
#  Returns the resource where newly ingested files for the project should be
#  stored.
#
#  Returns:
#   a tuple where the first value is the name of the resource and the second is
#   a flag indicating whether or not this resource choice may be overridden by
#   the user.
#
#  Example:
#   project_replIngestResc : string * boolean
#   project_replIngestResc = ('projectIngestRes', true)
#
# <file_name>_replReplResc
#  Returns the resource where a replica of a data object should be stored.
#
#  Return:
#   a tuple where the first value is the name of the resource and the second is
#   a flag indicating whether or not this resource choice may be overridden by
#   the user.
#
#  Examples:
#   project_replReplResc : string * boolean
#   project_replReplResc = ('projectReplRes', false)
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.


# DEFERRED FUNCTIONS AND RULES

_repl_replicate(*Object, *RescName) {
  _repl_logMsg('replicating data object *Object to *RescName');

  *objPath = '';
  foreach (*rec in SELECT COLL_NAME, DATA_NAME WHERE DATA_ID = '*Object') {
    *objPath = *rec.COLL_NAME ++ '/' ++ *rec.DATA_NAME;
  }

  if (*objPath == '') {
    _repl_logMsg('data object *Object no longer exists');
  } else {
    temporaryStorage.cyverse_repl_replicate = 'REPL_FORCED_REPL_RESC';

    *err = errormsg(
      msiDataObjRepl(*objPath, 'backupRescName=*RescName++++verifyChksum=', *status), *msg);

    temporaryStorage.cyverse_repl_replicate = '';

    if (*err < 0){
      if (*err == -808000 || *err == -817000) {
        _repl_logMsg('failed to replicate data object *Object, data no longer exists');
        _repl_logMsg(*msg);
        0
      } else if (*err == -314000) {
        _repl_logMsg('failed to replicate data object *Object due to checksum error');
        _repl_logMsg(*msg);
        0
        # the exit status is 0 to indicate that replication should not be retried
      } else {
        _repl_logMsg('failed to replicate data object *Object, retry in 8 hours');
        _repl_logMsg(*msg);
        *err;
      }
    } else {
      _repl_logMsg('replicated data object *Object');
    }
  }
}


# DEPRECATED
_mvReplicas(*Object, *IngestResc, *ReplResc) {
  _repl_logMsg('moving replicas of data object *Object');

  *dataPath = '';
  foreach (*rec in SELECT COLL_NAME, DATA_NAME WHERE DATA_ID = '*Object') {
    *dataPath = *rec.COLL_NAME ++ '/' ++ *rec.DATA_NAME;
  }

  if (*dataPath != '') {
    *replFail = false;
    (*ingestName, *ingestOptional) = *IngestResc;
    (*replName, *replOptional) = *ReplResc;

    if (_repl_replicate(*Object, *ingestName) < 0) {
      *replFail = true;
    }

    if (*replName != *ingestName) {
      if (_repl_replicate(*Object, *replName) < 0) {
        *replFail = true;
      }
    }

    if (!*replFail) {
      # Once a replica exists on all the project's resource, remove the other replicas
      foreach (*rec in SELECT DATA_RESC_HIER, DATA_REPL_NUM WHERE DATA_ID = '*Object') {
        *rescHier = *rec.DATA_RESC_HIER;
        *replNum = *rec.DATA_REPL_NUM;

        if (!(*rescHier like regex '^(*ingestName|*replName)(;.*)?$')) {
          if (errorcode(msiDataObjTrim(*dataPath, 'null', *replNum, '1', 'null', *status)) < 0) {
            _repl_logMsg('failed to trim replica of *Object on *rescHier (*status)');
            *replFail = true;
          }
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


_repl_mvReplicas(*Object, *IngestName, *ReplName) {
  _repl_logMsg('moving replicas of data object *Object');

  *dataPath = '';
  foreach (*rec in SELECT COLL_NAME, DATA_NAME WHERE DATA_ID = '*Object') {
    *dataPath = *rec.COLL_NAME ++ '/' ++ *rec.DATA_NAME;
  }

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

  *dataPath = '';
  foreach (*rec in SELECT COLL_NAME, DATA_NAME WHERE DATA_ID = '*Object') {
    *dataPath = *rec.COLL_NAME ++ '/' ++ *rec.DATA_NAME;
  }

  if (*dataPath == '') {
    _repl_logMsg('data object *Object no longer exists');
  } else {
    *err = errormsg(
      msiDataObjRepl(*dataPath, 'all=++++updateRepl=++++verifyChksum=', *status), *msg );

    if (*err < 0 && *err != -808000) {
      _repl_logMsg('failed to sync replicas of data object *Object trying again in 8 hours');
      _repl_logMsg(*msg);
      *err;
    } else {
      _repl_logMsg('synced replicas of data object *Object');
    }
  }
}


# SUPPORTING FUNCTIONS AND RULES

_defaultIngestResc : string * boolean
_defaultIngestResc = (cyverse_DEFAULT_RESC, true)


_defaultReplResc : string * boolean
_defaultReplResc = (cyverse_DEFAULT_REPL_RESC, true)


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


# DEPRECATED
# XXX - As of 4.3.1, Booleans and tuples are not supported by packing
#       instructions. The resource description tuple must be expanded, and the
#       second term needs to be converted to a string. See
#       https://github.com/irods/irods/issues/3634 for Boolean support.
_scheduleMv(*Object, *IngestName, *IngestOptStr, *ReplName, *ReplOptStr) {
  delay('<PLUSET>' ++ str(_delayTime) ++ 's</PLUSET><EF>8h REPEAT UNTIL SUCCESS</EF>')
  {_mvReplicas(*Object, (*IngestName, bool(*IngestOptStr)), (*ReplName, bool(*ReplOptStr)))}

  _incDelayTime;
}

_repl_scheduleMv(*Object, *IngestName, *ReplName) {
  delay('<PLUSET>' ++ str(_delayTime) ++ 's</PLUSET><EF>8h REPEAT UNTIL SUCCESS</EF>')
  {_repl_mvReplicas(*Object, *IngestName, *ReplName);}

  _incDelayTime;
}


# DEPRECATED
_scheduleMoves(*Entity, *IngestResc, *ReplResc) {
  *entity = str(*Entity);
  (*ingestName, *ingestOptional) = *IngestResc;
  (*replName, *replOptional) = *ReplResc;
  *type = cyverse_getEntityType(*entity);

  if (cyverse_isColl(*type)) {
    # if the entity is a collection
    foreach (*collPat in list(*entity, *entity ++ '/%')) {
      foreach (*rec in SELECT DATA_ID WHERE COLL_NAME LIKE '*collPat') {
        *dataId = *rec.DATA_ID;
        _scheduleMv(*dataId, *ingestName, str(*ingestOptional), *replName, str(*replOptional));
      }
    }
  } else if (cyverse_isDataObj(*type)) {
    # if the entity is a data object
    msiSplitPath(*entity, *collPath, *dataName);

    foreach (*rec in SELECT DATA_ID WHERE COLL_NAME = '*collPath' AND DATA_NAME = '*dataName') {
      *dataId = *rec.DATA_ID;
      _scheduleMv(*dataId, *ingestName, str(*ingestOptional), *replName, str(*replOptional));
    }
  }
}


_cyverse_repl_scheduleCollMove(*Coll, *IngestName, *ReplName) {
  *coll = str(*Coll);

  foreach (*rec in SELECT DATA_ID WHERE COLL_NAME = *coll || LIKE '*coll/%') {
    *dataId = *rec.DATA_ID;
    _repl_scheduleMv(*dataId, *IngestName, *ReplName);
  }
}


_cyverse_repl_scheduleDataMove(*Data, *IngestName, *ReplName) {
  msiSplitPath(str(*Data), *collPath, *dataName);

  foreach (*rec in SELECT DATA_ID WHERE COLL_NAME = '*collPath' AND DATA_NAME = '*dataName') {
    _repl_scheduleMv(*rec.DATA_ID, *IngestName, *ReplName);
  }
}


_repl_scheduleMoves(*Entity, *IngestName, *ReplName) {
  *type = cyverse_getEntityType(*Entity);

  if (cyverse_isColl(*type)) {
    _cyverse_repl_scheduleCollMove(*Entity, *IngestName, *ReplName);
  } else if (cyverse_isDataObj(*type)) {
    _cyverse_repl_scheduleDataMove(*Entity, *IngestName, *ReplName);
  }
}


_repl_scheduleRepl(*Object, *RescName) {
  delay('<PLUSET>' ++ str(_delayTime) ++ 's</PLUSET><EF>8h REPEAT UNTIL SUCCESS</EF>')
  {_repl_replicate(*Object, *RescName);}

  _incDelayTime;
}


_repl_scheduleSyncReplicas(*Object) {
# XXX - There is a bug in iRODS 4.3.1 that prevents a general query that doesn't
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


# DEPRECATED
_ipcRepl_createOrOverwrite_old(*DataPath, *DestResc, *New, *IngestResc, *ReplResc) {
  msiSplitPath(*DataPath, *collName, *dataName);

  foreach (*rec in SELECT DATA_ID WHERE COLL_NAME = '*collName' AND DATA_NAME = '*dataName') {
    *dataId = *rec.DATA_ID;

    if (*New) {
      (*ingestName, *optional) = *IngestResc;
      (*replName, *optional) = *ReplResc;
      _repl_scheduleRepl(*dataId, if *DestResc == *replName then *ingestName else *replName);
    } else {
      _repl_scheduleSyncReplicas(*dataId);
    }
  }
}


_ipcRepl_createOrOverwrite(*DataPath, *DestResc, *New, *IngestResc, *ReplResc) {
  msiSplitPath(*DataPath, *collName, *dataName);

  foreach (*rec in SELECT DATA_ID WHERE COLL_NAME = '*collName' AND DATA_NAME = '*dataName') {
    *dataId = *rec.DATA_ID;

    if (*New) {
      _repl_scheduleRepl(*dataId, if *DestResc == *ReplResc then *IngestResc else *ReplResc);
    } else {
      _repl_scheduleSyncReplicas(*dataId);
    }
  }
}


_setDefaultResc(*Resource) {
  (*name, *optional) = *Resource;
  msiSetDefaultResc(*name, if *optional then 'preferred' else 'forced');
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
  if (*Resc == cyverse_DEFAULT_RESC) {
    (*repl, *opt) = _defaultReplResc;
    *residency = if *opt then 'preferred' else 'forced';
  } else {
    *repl = *Resc;
    *residency = 'preferred';

    foreach (*record in SELECT META_RESC_ATTR_VALUE, META_RESC_ATTR_UNITS
                        WHERE RESC_NAME = *Resc AND META_RESC_ATTR_NAME = 'ipc::replica-resource') {
      *repl = *record.META_RESC_ATTR_VALUE;
      *residency = *record.META_RESC_ATTR_UNITS;
    }
  }

  *result = (*repl, *residency);
  *result;
}


# DEPRECATED
_ipcRepl_put_old(*ObjPath, *DestResc, *New) {
  _ipcRepl_createOrOverwrite_old(*ObjPath, *DestResc, *New, _defaultIngestResc, _defaultReplResc);
}

_ipcRepl_put(*ObjPath, *DestRescHier, *New) {
  (*ingestResc, *_) = _repl_findResc(*ObjPath);
  *destResc = hd(split(*DestRescHier, ';'));

  if (*ingestResc != cyverse_DEFAULT_RESC) {
    (*replResc, *_) = _repl_findReplResc(*ingestResc);
    _ipcRepl_createOrOverwrite(*ObjPath, *destResc, *New, *ingestResc, *replResc);
  } else {
    _ipcRepl_put_old(*ObjPath, *destResc, *New);
  }
}


# REPLICATION RULES

# This rule updates the replicas if needed after a collection or data object has
# been moved
#
# Parameters:
#  SourceObject  (path) the absolute path to the collection or data object
#                before it was moved
#  DestObject    (path) the absolute path after it was moved
#
replEntityRename(*SourceObject, *DestObject) {
  (*destResc, *_) = _repl_findResc(*DestObject);
  (*srcResc, *_) = _repl_findResc(*SourceObject);

  if (*destResc != cyverse_DEFAULT_RESC) {
    if (*srcResc != *destResc) {
      (*destRepl, *_) = _repl_findReplResc(*destResc);
      _repl_scheduleMoves(*DestObject, *destResc, *destRepl);
    }
  } else {
    if (*srcResc != cyverse_DEFAULT_RESC) {
      _repl_scheduleMoves(*DestObject, cyverse_DEFAULT_RESC, cyverse_DEFAULT_REPL_RESC);
    }
  }
}


# This rule ensures that the correct resource is chosen for first replica of a
# newly created data object.
#
# Parameters:
#  DataPath  (path) the path to the data object being created

# DEPRECATED
_ipcRepl_acSetRescSchemeForCreate(*DataPath) {
  _setDefaultResc(_defaultIngestResc);
}

cyverse_repl_acSetRescSchemeForCreate(*DataPath) {
  (*resc, *residency) = _repl_findResc(*DataPath);

  if (*resc != cyverse_DEFAULT_RESC) {
    msiSetDefaultResc(*resc, *residency);
  } else {
    _ipcRepl_acSetRescSchemeForCreate(*DataPath);
  }
}


# This rule ensures that the correct resource is chosen for the second and
# subsequent replicas of a data object.
#
# Parameters:
#  DataPath  (path) the path to the data object being replicated

# DEPRECATED
_ipcRepl_acSetRescSchemeForRepl(*DataPath) {
  _setDefaultResc(_defaultReplResc);
}

cyverse_repl_acSetRescSchemeForRepl(*DataPath) {
  if (cyverse_getValue(temporaryStorage, 'cyverse_repl_replicate') != 'REPL_FORCED_REPL_RESC') {
    (*resc, *_) = _repl_findResc(*DataPath);

    if (*resc != cyverse_DEFAULT_RESC) {
      (*repl, *residency) = _repl_findReplResc(*resc);
      msiSetDefaultResc(*repl, *residency);
    } else {
      _ipcRepl_acSetRescSchemeForRepl(*DataPath);
    }
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
  _ipcRepl_put(*DATA_OBJ_INFO.logical_path, hd(split(*DATA_OBJ_INFO.resc_hier, ';')), true);
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
      _ipcRepl_put(cyverse_getValue(*BulkOpInp, *key), *rescHier, true);
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
  _ipcRepl_put(
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
  _ipcRepl_put(
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
      _repl_scheduleDataMove(*dstPath, *dstResc, *dstRepl);
    } else if (*srcType == 12) {  # collection
      _repl_scheduleCollMove(*dstPath, *dstResc, *dstRepl);
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
  _ipcRepl_put(
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
# XXX - As of iRODS 4.3.1, *JsonInput buffer ends with a serialized NUL, i.e., the string '\x00'
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
        _ipcRepl_put(*dataPath, *rec.DATA_RESC_HIER, true);
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
      _ipcRepl_put(*path, *destResc, *new);
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
    _ipcRepl_put(*path, *destResc, *openType == cyverse_FILE_CREATE);
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
