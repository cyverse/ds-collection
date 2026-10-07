# This rule base contains workarounds CVEs.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.


# Bug in the parsing of input to msiSendMail
# - https://www.cve.org/CVERecord?id=CVE-2024-38462
# - https://github.com/irods/irods/issues/7651
# - https://github.com/irods/irods/issues/7562
# - authenticated user can escalate to service account (admin) and execute remote code
#
# This can be removed after upgrading to 4.3.2
#
msiSendMail(*_1, *_2, *_3) {
	writeLine('serverLog', 'intercepted msiSendMail call');
}

# Bug in the parsing of input to irodsServerMonPerf perl script
# - https://www.cve.org/CVERecord?id=CVE-2024-38461
# - https://github.com/irods/irods/issues/7652
# - authenticated user can escalate to service account (admin) and execute remote code
#
# This can be removed after upgrading to 4.3.3.
#
msiServerMonPerf(*_1, *_2) {
	writeLine('serverLog', 'intercepted msiServerMonPerf call');
}

# Prevent tar slip security hole. It prevents the microservice
# `msiTarFileExtract` from executing.
#
# This can be removed after upgrading to 5.1.0
#
# Parameters:
#  LogicalPath  (string) the absolute path to the tar file to extract
#  TargetColl   (string) unused
#  DestResc     (string) unused
#  STATUS       (int) unused
#
# Session Variables:
#  userNameClient
#  rodsZoneClient
#
# Error Codes:
#  -169000 (SYS_NOT_ALLOWED)
#
msiTarFileExtract(*LogicalPath, *TargetColl, *DestResc, *STATUS) {
	*clientUser = $userNameClient;
	*clientZone = $rodsZoneClient;

	writeLine(
		'serverLog',
		'msiTarFileExtract: prevented *clientUser#*clientZone from extracting *LogicalPath' );

	failmsg(-169000, 'msiTarFileExtract is not allowed');
}

# The legacy `auth_response` API is vulnerable to custom payloads which can
# masquerade the authenticating user as a different account. This prevents
# mismatched startup user vs authenticating user via AUTH_RESPONSE_AN 704.
#
# This can be removed after upgrading to 5.1.0.
#
# Parameters:
#  Instance  (string) unused
#  Comm      (`KeyValuePair_PI`) information related to the session
#  Resp      (`KeyValuePair_PI`) Information related to the response?
#
# Error Codes:
#  -169000 (SYS_NOT_ALLOWED)
#
pep_api_auth_response_pre(*Instance, *Comm, *Resp) {
	*startupProxyUser = *Comm.proxy_user_name ++ '#' ++ *Comm.proxy_rods_zone;
	*authUser = *Resp.username;

	if (*startupProxyUser != *authUser) {
		*msg = 'pep_api_auth_response_pre: startup_proxy[*startupProxyUser] does not match'
			++ ' auth_user[*authUser] - DENIED (AN 704)';

		writeLine('serverLog', *msg);
		failmsg(-169000, 'startup_proxy must match authenticating user');
	}
}

# The `authentication` API is vulnerable to custom payloads which can masquerade
# the authenticating user as a different account. This prevents mismatched
# startup user vs authenticating user via AUTHENTICATION_APN 110000.
#
# This can be removed after upgrading to 5.1.0.
#
# Parameters:
#  Instance  (string) unused
#  Comm      (`KeyValuePair_PI`) information related to the session
#  Req       (`KeyValuePair_PI`) information related to the auth request?
#  Resp      (`KeyValuePair_PI`) information related to the auth response?
#
# Error Codes:
#  -169000 (SYS_NOT_ALLOWED)
#
pep_api_authenticate_pre(*Instance, *Comm, *Req, *Resp) {
	*startupProxyUser = *Comm.proxy_user_name;
	*startupProxyZone = *Comm.proxy_rods_zone;
	*reqBuf = *Req.buf;
	msiStrlen(*reqBuf, *bufLen);
	msi_json_parse(*reqBuf, int(*bufLen), *handle);
	msi_json_value(*handle, "/user_name", *authUser);
	msi_json_value(*handle, "/zone_name", *authZone);
	msi_json_free(*handle);

	if (*startupProxyUser != *authUser || *startupProxyZone != *authZone) {
		*msg = 'pep_api_authenticate_pre: startup_proxy[*startupProxyUser#*startupProxyZone] does not'
			++ ' match auth_user[*authUser#*authZone] - DENIED (AN 110000)';

		writeLine('serverLog', *msg);
		failmsg(-169000, 'startup_proxy must match authenticating user');
	}
}

# The `rcBulkDataObjReg` API is vulnerable to raw packstruct payloads that can
# register files anywhere already on the iRODS Server. The implementation blocks
# this API call.
#
# This can be removed after upgrading to 5.1.0
#
# Parameters:
#  Instance               (string) unused
#  Comm                   (`KeyValuePair_PI`) information related to the session
#  BultDataObjRegInp      (`KeyValuePair_PI`) unused
#  BULK_DATA_OBJ_REG_OUT  (unknown) unused
#
# Error Codes:
#  -31000 (SYS_INVALID_FILE_PATH)
#
pep_api_bulk_data_obj_reg_pre(*Instance, *Comm, *BultDataObjRegInp, *BULK_DATA_OBJ_REG_OUT) {
	*msg = 'pep_api_bulk_data_obj_reg_pre: prevented'
		++ ' [' ++ *Comm.user_user_name ++ '#' ++ *Comm.user_rods_zone ++ '] from bulk registering'
		++ ' files';

	writeLine('serverLog', *msg);
	failmsg(-169000, 'rcBulkDataObjReg is not allowed');
}

# There is a security hole in `icp -p` that allows an overwrite to escape the
# iRODS access control and overwrite a file not accessible to the user. This
# prevents `icp -p` from being able to write to client-submitted physical paths.
#
# This can be removed after upgrading to 4.3.5
#
# Parameters:
#  Instance        (string) unused
#  Comm            (`KeyValuePair_PI`) unused
#  DataObjCopyInp  (`KeyValuePair_PI`) information related to copy operation
#  TransStat       (unknown) unused
#
# Error Codes:
#  -31000 (SYS_INVALID_FILE_PATH)
#
pep_api_data_obj_copy_pre(*Instance, *Comm, *DataObjCopyInp, *TransStat) {
	on (errorcode(*DataObjCopyInp.dst_filePath) == 0) {
		cut;
		failmsg(-31000, 'CYVERSE ERROR: no physical path allowed');
	}
}

# There is a security hole in `iput -p` that allows an overwrite to escape the
# iRODS access control and overwrite a file not accessible to the user. This
# prevents `iput -p` from being able to write to client-submitted physical paths.
#
# This can be removed after upgrading to 4.3.5
#
# Parameters:
#  Instance        (string) unused
#  Comm            (`KeyValuePair_PI`) unused
#  DataObjInp      (`KeyValuePair_PI`) information related to the data object
#  DataObjInpBBuf  (unknown) unused
#  PORTAL_OPR_OUT  (unknown) unused
#
# Error Codes:
#  -31000 (SYS_INVALID_FILE_PATH)
#
# XXX: This PEP has a huge memory leak:
#      https://github.com/irods/irods/issues/8106. Fixed in 4.3.4. There is no
#      workaround.
# pep_api_data_obj_put_pre(*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PORTAL_OPR_OUT) {
# 	on (errorcode(*DataObjInp.filePath) == 0) {
# 		cut;
# 		failmsg(-31000, 'CYVERSE ERROR: no physical path allowed');
# 	}
# }

# There is a security hole in irm -f that allows a user with read permission on
# a data object to silently delete the underlying physical files. See
# https://github.com/irods/irods/issues/8441 for more information. This rule
# prevents this from happening.
#
# This can be removed after upgrading to 4.3.5
#
# Parameters:
#  Instance          (string) unused
#  Comm              (`KeyValuePair_PI`) information related to the session
#  DataObjUnlinkInp  (`KeyValuePair_PI`) information to the data object being
#                    deleted
#
# Error Codes:
#  -818000 (CAT_NO_ACCESS_PERMISSION)
#
_cve_DEL_VAL = 1130
_cve_delete_allowed(*ClientUser, *ClientZone, *DataPath) =
	let *permSufficient = false in
	let *collPath = '' in
	let *dataName = '' in
	let *_ = msiSplitPath(str(*DataPath), *collPath, *dataName) in
	let *_ = foreach (*groupRec in
			select USER_GROUP_NAME where USER_NAME = '*ClientUser' and USER_ZONE = '*ClientZone'
		) {
			*group = *groupRec.USER_GROUP_NAME;
			foreach (*accessRec in
				select DATA_ACCESS_TYPE
				where USER_NAME = '*group' and COLL_NAME = '*collPath' and DATA_NAME = '*dataName'
			) {
				if (int(*accessRec.DATA_ACCESS_TYPE) >= _cve_DEL_VAL) {
					*permSufficient = true;
				}
			}
			if (*permSufficient) {
			 	break;
			}
		} in
	*permSufficient
pep_api_data_obj_unlink_pre(*Instance, *Comm, *DataObjUnlinkInp) {
	on (
		! _cve_delete_allowed(*Comm.user_user_name, *Comm.user_rods_zone, *DataObjUnlinkInp.obj_path)
	) {
		*msg = 'pep_api_data_obj_unlink_pre: prevented '
			++ *Comm.user_user_name ++ '#' ++ *Comm.user_rods_zone ++ ' from removing logical_path '
			++ *DataObjUnlinkInp.obj_path;

		writeLine('serverLog', *msg);
		cut;
		failmsg(-818000, 'delete_object or greater required');
	}
}

# The `rcExecRuleExpression` API is vulnerable to direct NATIVE_PROT client
# payloads of Python code to be run on the iRODS Server when the iRODS Python
# Rule Engine Plugin is installed. This rule prevents this.
#
# This can be removed after upgrading to iRODS 5.1.0.
#
# Parameters:
#  Instance  (string) unused
#  Comm      (`KeyValuePair_PI`) information related to the session
#  ExecRule  (unknown) unused
#
# Error Codes:
#  -169000 (SYS_NOT_ALLOWED)
#
pep_api_exec_rule_expression_pre(*Instance, *Comm, *ExecRule) {
	*proxyUser = *Comm.proxy_user_name
	*proxyZone = *Comm.proxy_rods_zone

	foreach(*row in SELECT USER_TYPE where USER_NAME = '*proxyUser' and USER_ZONE = '*proxyZone') {
		*userType = *row.USER_TYPE;
	}

	if ("rodsadmin" != *userType) {
		*msg = 'pep_api_exec_rule_expression_pre: prevented [*proxyUser#*proxyZone] from calling'
			++ ' rcExecRuleExpression (AN 1206)';

		writeLine('serverLog', *msg);
		failmsg(-169000, 'rcExecRuleExpression is not allowed');
	}
}

# The `rcRegDataObj` API is vulnerable to raw packstruct payloads that can
# register files anywhere already on the iRODS Server. The implementation blocks
# this API call.
#
# This can be removed after upgrading to iRODS 5.1.0.
#
# Parameters:
#  Instance           (string) unused
#  Comm               (`KeyValuePair_PI`) information related to the session
#  DataObjInfo        (`KeyValuePair_PI`) information about the data object
#                     being registered
#  OUT_DATA_OBJ_INFO  (unknown) unused
#
# Error Codes:
#  -169000 (SYS_NOT_ALLOWED)
#
pep_api_reg_data_obj_pre(*Instance, *Comm, *DataObjInfo, *OUT_DATA_OBJ_INFO) {
	*proxyUser = *Comm.proxy_user_name;
	*proxyZone = *Comm.proxy_rods_zone;

	foreach(*row in SELECT USER_TYPE where USER_NAME = '*proxyUser' and USER_ZONE = '*proxyZone') {
		*userType = *row.USER_TYPE;
	}

	if (*userType != 'rodsadmin') {
		*msg = 'pep_api_reg_data_obj_pre: prevented'
			++ ' [' ++ *Comm.user_user_name ++ '#' ++ *Comm.user_rods_zone ++ '] from registering'
			++ ' logical_path[' ++ *DataObjInfo.logical_path ++ '] with'
			++ ' physical_path[' ++ *DataObjInfo.physical_path ++ ']';

		writeLine('serverLog', *msg);
		failmsg(-169000, 'rcRegDataObj is not allowed');
	}
}

# There is a security hole that allows a user to retrieve sensitive information
# from and iRODS server. This rule blocks downloading subfiles.
#
# This can be removed after upgrading to iRODS 5.1.0.
#
# Parameters:
#  Instance  (string) unused
#  Comm      (`KeyValuePair_PI`) information related to the session
#  Subfile   (unknown) unused
#  OUT_BUF   (unknown) unused
#
# Error Codes:
#  -169000 (SYS_NOT_ALLOWED)
#
pep_api_sub_struct_file_get_pre(*Instance, *Comm, *Subfile, *OUT_BUF) {
	*msg = 'pep_api_sub_struct_file_get_pre: prevented '
		++ '[' ++ *Comm.user_user_name ++ '#' ++ *Comm.user_rods_zone ++ '] from getting a subfile';

	writeLine('serverLog', *msg);
	failmsg(-169000, 'getting a subfile is not allowed');
}

# There is a security hole that allows a user to put a script in msiExecCmd_bin,
# which can then be executed as the service account. This rule blocks uploading
# subfiles.
#
# This can be removed after upgrading to iRODS 5.1.0.
#
# Parameters:
#  Instance  (string) unused
#  Comm      (`KeyValuePair_PI`) information related to the session
#  Subfile   (unknown) unused
#  OUT_BUF   (unknown) unused
#
# Error Codes:
#  -169000 (SYS_NOT_ALLOWED)
#
pep_api_sub_struct_file_put_pre(*Instance, *Comm, *Subfile, *OUT_BUF) {
	*msg = 'pep_api_sub_struct_file_put_pre: prevented '
		++ '[' ++ *Comm.user_user_name ++ '#' ++ *Comm.user_rods_zone ++ '] from putting a subfile';

	writeLine('serverLog', *msg);
	failmsg(-169000, 'putting a subfile is not allowed');
}

# The `userAdmin` API is vulnerable to custom payloads which can create a new
# rodsadmin account. This prevents custom groupadmin payload via USER_ADMIN_AN
# 714.
#
# This can be removed after upgrading to 5.1.0.
#
# Parameters:
#  Inst   (unknown) unused
#  Ctx    (`KeyValuePair_PI`) contains information about the API?
#  OUT    (unknown) unused
#  UInfo  (`KeyValuePair_PI`) contains information about the user being created
#
# Error Codes:
#  -169000 (SYS_NOT_ALLOWED)
#
pep_database_reg_user_re_pre(*Inst, *Ctx, *OUT, *UInfo) {
	if ( "714" == *Ctx.api_index && "rodsadmin" == *UInfo.user_type) {
		*msg = 'pep_database_reg_user_re_pre: api_index[' ++ *Ctx.api_index ++ '] user_type['
			++ *UInfo.user_type ++ '] DENIED (AN 714)';

		writeLine('serverLog', *msg);
		failmsg(-169000, 'groupadmin creating rodsadmin is not allowed');
	}
}