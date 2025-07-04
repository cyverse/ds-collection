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
    temporaryStorage.repl_replicate = 'REPL_FORCED_REPL_RESC';

    *err = errormsg(
      msiDataObjRepl(*objPath, 'backupRescName=*RescName++++verifyChksum=', *status), *msg);

    temporaryStorage.repl_replicate = '';

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
      foreach (*rec in SELECT DATA_RESC_HIER, RESC_NAME WHERE DATA_ID = '*Object') {
        *rescHier = *rec.DATA_RESC_HIER;
        *rescName = *rec.RESC_NAME;

        if (!(*rescHier like regex '^(*ingestName|*replName)(;.*)?$')) {
          if (errorcode(msiDataObjTrim(*dataPath, *rescName, 'null', '1', 'null', *status)) < 0) {
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
    foreach (*rec in SELECT DATA_RESC_HIER, RESC_NAME WHERE DATA_ID = '*Object') {
      *rescHier = *rec.DATA_RESC_HIER;
      *rescName = *rec.RESC_NAME;

      if (!(*rescHier like regex '^(*IngestName|*ReplName)(;.*)?$')) {
        if (errorcode(msiDataObjTrim(*dataPath, *rescName, 'null', '1', 'null', *status)) < 0) {
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
# XXX - Replica updating is broken for large files in 4.2.8. See
#       https://github.com/irods/irods/issues/5160. This is fixed in 4.2.9.
#   foreach (*rec in SELECT COLL_NAME, DATA_NAME WHERE DATA_ID = '*Object') {
#     *dataPath = *rec.COLL_NAME ++ '/' ++ *rec.DATA_NAME;
#   }
#
#   if (*dataPath == '') {
#     _repl_logMsg('data object *Object no longer exists');
#   } else {
#     *err = errormsg(
#       msiDataObjRepl(*dataPath, 'all=++++updateRepl=++++verifyChksum=', *status), *msg);
#
#     if (*err < 0 && *err != -808000) {
#       _repl_logMsg('failed to sync replicas of data object *Object trying again in 8 hours');
#       _repl_logMsg(*msg);
#       *err;
#     } else {
#       _repl_logMsg('synced replicas of data object *Object');
#     }
#   }
  foreach (*rec in
    SELECT COLL_NAME, DATA_NAME, DATA_SIZE, order_asc(DATA_REPL_NUM)
    WHERE DATA_ID = '*Object' AND DATA_REPL_STATUS = '1'
  ) {
    *dataPath = *rec.COLL_NAME ++ '/' ++ *rec.DATA_NAME;
    *dataSize = double(*rec.DATA_SIZE);
    *replNum = int(*rec.DATA_REPL_NUM);
    break;
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
      if (*dataSize > 1048576) {  # 1 MiB
        *idArg = execCmdArg(*Object);
        *replNumArg = execCmdArg(str(*replNum));
        *sizeArg = execCmdArg(trimr(str(*dataSize), "."));
        *argv = "*idArg *replNumArg *sizeArg";
        *err = errormsg(msiExecCmd('correct-size', *argv, "", "", "", *out), *msg);

        if (*err < 0) {
          misGetStderrInExecCmdOut(*out, *details);
          _repl_logMsg('Failed to correct size of *dataPath replica *replNum');
          _repl_logMsg(*msg);
          _repl_logMsg(*details);
        }
      }

      _repl_logMsg('synced replicas of data object *Object');
    }
  }
# XXX - ^^^
}


# SUPPORTING FUNCTIONS AND RULES

_defaultIngestResc : string * boolean
_defaultIngestResc = (cyverse_DEFAULT_RESC, true)


_defaultReplResc : string * boolean
_defaultReplResc = (cyverse_DEFAULT_REPL_RESC, true)


_delayTime : int
_delayTime =
  let *_ = if (errorcode(temporaryStorage.repl_delayTime) < 0) {
      temporaryStorage.repl_delayTime = str(cyverse_INIT_REPL_DELAY);
    } in
  int(temporaryStorage.repl_delayTime);


_incDelayTime {
  temporaryStorage.repl_delayTime = str(1 + int(temporaryStorage.repl_delayTime));
}


_repl_logMsg(*Msg) {
  writeLine('serverLog', 'DS: *Msg');
}


# DEPRECATED
# XXX - As of 4.2.10, Booleans and tuples are not supported by packing instructions. The resource
#       description tuple must be expanded, and the second term needs to be converted to a string.
#       See https://github.com/irods/irods/issues/3634 for Boolean support.
_scheduleMv(*Object, *IngestName, *IngestOptionalStr, *ReplName, *ReplOptionalStr) {
# XXX - The rule engine plugin must be specified. This is fixed in iRODS 4.2.9. See
#       https://github.com/irods/irods/issues/5413.
#     - REPEAT not honored for rodsuser. This is fixed in iRODS 4.2.9. See
#       https://github.com/irods/irods/issues/5257
#     - PLUSET doesn't understand h unit. This is fixed in iRODS 4.2.9. See
#       https://github.com/irods/irods/issues/4055
#   delay('<PLUSET>' ++ str(_delayTime) ++ 's</PLUSET><EF>8h REPEAT UNTIL SUCCESS</EF>')
#   {_mvReplicas(*Object, (*IngestName, bool(*IngestOptionalStr)), (*ReplName, bool(*ReplOptionalStr)));}
#
#   _incDelayTime;
# }
  delay(
    ' <INST_NAME>irods_rule_engine_plugin-irods_rule_language-instance</INST_NAME>
      <PLUSET>' ++ str(_delayTime) ++ 's</PLUSET>
      <EF>0s REPEAT 0 TIMES</EF> ' )
  {#_mvReplicas
    _mvReplicas_workaround(*Object, *IngestName, *IngestOptionalStr, *ReplName, *ReplOptionalStr);
  }

  _incDelayTime;
}
_mvReplicas_workaround(*Object, *IngestName, *IngestOptionalStr, *ReplName, *ReplOptionalStr) {
  *err = errorcode(
    _mvReplicas(
      *Object,
      (*IngestName, bool(*IngestOptionalStr)),
      (*ReplName, bool(*ReplOptionalStr)) ) );

  if (*err < 0) {
    delay(
      ' <INST_NAME>irods_rule_engine_plugin-irods_rule_language-instance</INST_NAME>
        <PLUSET>28800s</PLUSET>
        <EF>0s REPEAT 0 TIMES</EF> ' )
    {#_mvReplicas
      _mvReplicas_workaround(*Object, *IngestName, *IngestOptionalStr, *ReplName, *ReplOptionalStr);
    }
  }
}
# XXX - ^^^


_repl_scheduleMv(*Object, *IngestName, *ReplName) {
# XXX - The rule engine plugin must be specified. This is fixed in iRODS 4.2.9. See
#       https://github.com/irods/irods/issues/5413.
#     - REPEAT not honored for rodsuser. This is fixed in iRODS 4.2.9. See
#       https://github.com/irods/irods/issues/5257
#     - PLUSET doesn't understand h unit. This is fixed in iRODS 4.2.9. See
#       https://github.com/irods/irods/issues/4055
#   delay('<PLUSET>' ++ str(_delayTime) ++ 's</PLUSET><EF>8h REPEAT UNTIL SUCCESS</EF>')
#   {_repl_mvReplicas(*Object, *IngestName, *ReplName);}
#
#   _incDelayTime;
# }
  delay(
    ' <INST_NAME>irods_rule_engine_plugin-irods_rule_language-instance</INST_NAME>
      <PLUSET>' ++ str(_delayTime) ++ 's</PLUSET>
      <EF>0s REPEAT 0 TIMES</EF> ' )
  {#_repl_mvReplicas
    _repl_mvReplicas_workaround(*Object, *IngestName, *ReplName);
  }

  _incDelayTime;
}
_repl_mvReplicas_workaround(*Object, *IngestName, *ReplName) {
  if (errorcode(_repl_mvReplicas(*Object, *IngestName, *ReplName)) < 0) {
    delay(
      ' <INST_NAME>irods_rule_engine_plugin-irods_rule_language-instance</INST_NAME>
        <PLUSET>28800s</PLUSET>
        <EF>0s REPEAT 0 TIMES</EF> ' )
    {#_repl_mvReplicas
      _repl__mvReplicas_workaround(*Object, *IngestName, *ReplName);
    }
  }
}
# XXX - ^^^


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


_repl_scheduleMoves(*Entity, *IngestName, *ReplName) {
  *entity = str(*Entity);
  *type = cyverse_getEntityType(*entity);

  if (cyverse_isColl(*type)) {
    # if the entity is a collection
    foreach (*collPat in list(*entity, *entity ++ '/%')) {
      foreach (*rec in SELECT DATA_ID WHERE COLL_NAME LIKE '*collPat') {
        *dataId = *rec.DATA_ID;
        _repl_scheduleMv(*dataId, *IngestName, *ReplName);
      }
    }
  } else if (cyverse_isDataObj(*type)) {
    # if the entity is a data object
    msiSplitPath(*entity, *collPath, *dataName);

    foreach (*rec in SELECT DATA_ID WHERE COLL_NAME = '*collPath' AND DATA_NAME = '*dataName') {
      *dataId = *rec.DATA_ID;
      _repl_scheduleMv(*dataId, *IngestName, *ReplName);
    }
  }
}


_repl_scheduleRepl(*Object, *RescName) {
# XXX - The rule engine plugin must be specified. This is fixed in iRODS 4.2.9. See
#       https://github.com/irods/irods/issues/5413.
#     - REPEAT not honored for rodsuser. This is fixed in iRODS 4.2.9. See
#       https://github.com/irods/irods/issues/5257
#     - PLUSET doesn't understand h unit. This is fixed in iRODS 4.2.9. See
#       https://github.com/irods/irods/issues/4055
#   delay('<PLUSET>' ++ str(_delayTime) ++ 's</PLUSET><EF>8h REPEAT UNTIL SUCCESS</EF>')
#   {_repl_replicate(*Object, *RescName);}
#
#   _incDelayTime;
# }
  delay(
    ' <INST_NAME>irods_rule_engine_plugin-irods_rule_language-instance</INST_NAME>
      <PLUSET>' ++ str(_delayTime) ++ 's</PLUSET>
      <EF>0s REPEAT 0 TIMES</EF> ' )
  {#_repl_replicate
    _repl_replicate_workaround(*Object, *RescName);
  }

  _incDelayTime;
}
_repl_replicate_workaround(*Object, *RescName) {
  if (errorcode(_repl_replicate(*Object, *RescName)) < 0) {
    delay(
      ' <INST_NAME>irods_rule_engine_plugin-irods_rule_language-instance</INST_NAME>
        <PLUSET>28800s</PLUSET>
        <EF>0s REPEAT 0 TIMES</EF> ' )
    {#_repl_replicate
      _repl__replicate_workaround(*Object, *RescName);
    }
  }
}
# XXX - ^^^


_repl_scheduleSyncReplicas(*Object) {
# XXX - There is a bug in iRODS 4.2.8 that prevents a general query that doesn't explicitly use
#       r_coll_main from working when authorization is controlled by a ticket on a collection.
#   foreach (*rec in SELECT COUNT(DATA_REPL_NUM) WHERE DATA_ID = '*Object' AND DATA_REPL_STATUS = '0')
#   {
  foreach ( *rec in
    SELECT COUNT(DATA_REPL_NUM), COLL_ID WHERE DATA_ID = '*Object' AND DATA_REPL_STATUS = '0'
  ) {
# XXX - ^^^
    if (int(*rec.DATA_REPL_NUM) > 0) {
# XXX - The rule engine plugin must be specified. This is fixed in iRODS 4.2.9. See
#       https://github.com/irods/irods/issues/5413.
#     - REPEAT not honored for rodsuser. This is fixed in iRODS 4.2.9. See
#       https://github.com/irods/irods/issues/5257
#     - PLUSET doesn't understand h unit. This is fixed in iRODS 4.2.9. See
#       https://github.com/irods/irods/issues/4055
#       delay('<PLUSET>' ++ str(_delayTime) ++ 's</PLUSET><EF>8h REPEAT UNTIL SUCCESS</EF>')
#       {_repl_syncReplicas(*Object)}
#
#       _incDelayTime;
#     }
#   }
# }
      delay(
        ' <INST_NAME>irods_rule_engine_plugin-irods_rule_language-instance</INST_NAME>
          <PLUSET>' ++ str(_delayTime) ++ 's</PLUSET>
          <EF>0s REPEAT 0 TIMES</EF> ' )
      {#_repl_syncReplicas
        _repl_syncReplicas_workaround(*Object);
      }

      _incDelayTime;
    }
  }
}
_repl_syncReplicas_workaround(*Object) {
  if (errorcode(_repl_syncReplicas(*Object)) < 0) {
    delay(
      ' <INST_NAME>irods_rule_engine_plugin-irods_rule_language-instance</INST_NAME>
        <PLUSET>28800s</PLUSET>
        <EF>0s REPEAT 0 TIMES</EF> ' )
    {#_repl_syncReplicas
      _repl__syncReplicas_workaround(*Object);
    }
  }
}
# XXX - ^^^


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


# Given an absolute path to a collection, this rule determines the resource
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
  *repl = cyverse_DEFAULT_REPL_RESC;
  *residency = 'preferred';

  foreach (*record in SELECT META_RESC_ATTR_VALUE, META_RESC_ATTR_UNITS
                      WHERE RESC_NAME = *Resc AND META_RESC_ATTR_NAME = 'ipc::replica-resource') {
    *repl = *record.META_RESC_ATTR_VALUE;
    *residency = *record.META_RESC_ATTR_UNITS;
  }

  *result =(*repl, *residency);
  *result;
}


# REPLICATION RULES

# This rule updates the replicas if needed after a collection or data object has
# been moved
#
# Parameters:
#  SourceObject  (path) the absolute path to the collection or data object
#                before it was moved
#  DestObject    (path) the absolute path after it was moved

# DEPRECATED
_old_replEntityRename(*SourceObject, *DestObject) {
  on (pire_replBelongsTo(/*DestObject)) {
    if (!pire_replBelongsTo(/*SourceObject)) {
      _scheduleMoves(*DestObject, pire_replIngestResc, pire_replReplResc);
    }
  }
}
_old_replEntityRename(*SourceObject, *DestObject) {
  on (pire_replBelongsTo(/*SourceObject)) {
    _scheduleMoves(*DestObject, _defaultIngestResc, _defaultReplResc);
  }
}
# DEPRECATION NOTE: When the conditional versions are ready to be deleted, merge this into
#                   replEntityRename.
_old_replEntityRename(*SourceObject, *DestObject) {
  (*srcResc, *_) = _repl_findResc(*SourceObject);

  if (*srcResc != cyverse_DEFAULT_RESC) {
    _repl_scheduleMoves(*DestObject, cyverse_DEFAULT_RESC, cyverse_DEFAULT_REPL_RESC);
  }
}

replEntityRename(*SourceObject, *DestObject) {
  (*destResc, *_) = _repl_findResc(*DestObject);

  if (*destResc != cyverse_DEFAULT_RESC) {
    (*srcResc, *_) = _repl_findResc(*SourceObject);

    if (*srcResc != *destResc) {
      (*destRepl, *_) = _repl_findReplResc(*destResc);
      _repl_scheduleMoves(*DestObject, *destResc, *destRepl);
    }
  } else {
    _old_replEntityRename(*SourceObject, *DestObject);
  }
}


# This rule ensures that the correct resource is chosen for first replica of a
# newly created data object.
#
# Parameters:
#  DataPath  (path) the path to the data object being created

# DEPRECATED
_ipcRepl_acSetRescSchemeForCreate(*DataPath) {
  on (pire_replBelongsTo(*DataPath)) {
    _setDefaultResc(pire_replIngestResc);
  }
}
_ipcRepl_acSetRescSchemeForCreate(*DataPath) {
  _setDefaultResc(_defaultIngestResc);
}

ipcRepl_acSetRescSchemeForCreate(*DataPath) {
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
  on (pire_replBelongsTo(*DataPath)) {
    _setDefaultResc(pire_replReplResc);
  }
}
_ipcRepl_acSetRescSchemeForRepl(*DataPath) {
  _setDefaultResc(_defaultReplResc);
}

ipcRepl_acSetRescSchemeForRepl(*DataPath) {
  if (
    if errorcode(temporaryStorage.repl_replicate) < 0 then true
    else temporaryStorage.repl_replicate != 'REPL_FORCED_REPL_RESC'
  ) {
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

# DEPRECATED
_ipcRepl_put_old(*ObjPath, *DestResc, *New) {
  on (pire_replBelongsTo(/*ObjPath)) {}
}
_ipcRepl_put_old(*ObjPath, *DestResc, *New) {
  _ipcRepl_createOrOverwrite_old(*ObjPath, *DestResc, *New, _defaultIngestResc, _defaultReplResc);
}

_ipcRepl_put(*ObjPath, *DestResc, *New) {
  (*ingestResc, *_) = _repl_findResc(*ObjPath);

  if (*ingestResc != cyverse_DEFAULT_RESC) {
    (*replResc, *_) = _repl_findReplResc(*ingestResc);
    _ipcRepl_createOrOverwrite(*ObjPath, *DestResc, *New, *ingestResc, *replResc);
  } else {
    _ipcRepl_put_old(*ObjPath, *DestResc, *New);
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
ipcRepl_dataObjCreated(*User, *Zone, *DATA_OBJ_INFO) {
  _ipcRepl_put(*DATA_OBJ_INFO.logical_path, hd(split(*DATA_OBJ_INFO.resc_hier, ';')), true);
}


# This rule ensures that modifications to a file are synced to all replicas.
#
# Parameters:
#  User           (string) unused
#  Zone           (string) unused
#  DATA_OBJ_INFO  (`KeyValuePair_PI`) information related to the created data
#                 object
#
ipcRepl_dataObjModified(*User, *Zone, *DATA_OBJ_INFO) {
  _ipcRepl_put(*DATA_OBJ_INFO.logical_path, hd(split(*DATA_OBJ_INFO.resc_hier, ';')), false);
}


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
#  repl_replicate  this value is read to see if replication is forced to a
#                  specific resource
#
pep_resource_resolve_hierarchy_pre(*INSTANCE, *CONTEXT, *OUT, *OPERATION, *HOST, *PARSER, *VOTE) {
  on (
    if errorcode(temporaryStorage.repl_replicate) == 0
    then temporaryStorage.repl_replicate == 'REPL_FORCED_REPL_RESC'
    else false
  ) {}
}
