# This rule base contains the workarounds in cve.re that depend on the iRODS
# release. This version is for iRODS 4.3.4.
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

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
pep_api_data_obj_put_pre(*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PORTAL_OPR_OUT) {
	on (errorcode(*DataObjInp.filePath) == 0) {
		cut;
		failmsg(-31000, 'CYVERSE ERROR: no physical path allowed');
	}
}
