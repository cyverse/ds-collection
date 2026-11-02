# This rule base contains the PEPs of cyverse_core.re that depend on the iRODS
# release. This version is for iRODS 4.3.4.
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.


# DATA_OBJ_PUT

# This is the pre processing logic for when an attempt is made to upload a data
# object through the API using a DATA_OBJ_PUT request.
#
# Parameters:
#  Instance        (string) unknown
#  Comm            (`KeyValuePair_PI`) user connection and auth information
#  DataObjInp      (`KeyValuePair_PI`) information related to the data object
#  DataObjInpBBuf  (unknown) may contain the contents of the file being uploaded
#  PORTAL_OPR_OUT  unknown
#
pep_api_data_obj_put_pre(*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PORTAL_OPR_OUT) {
	cyverse_encryption_api_data_obj_put_pre(*Instance, *Comm, *DataObjInp);
}

# This is the post processing logic for when a data object is uploaded through
# the API using a DATA_OBJ_PUT request.
#
# Parameters:
#  Instance        (string) unknown
#  Comm            (`KeyValuePair_PI`) user connection and auth information
#  DataObjInp      (`KeyValuePair_PI`) information related to the data object
#  DataObjInpBBuf  (unknown) may contain the contents of the file being uploaded
#  PORTAL_OPR      unknown
#
pep_api_data_obj_put_post(*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PORTAL_OPR) {
	_cyverse_core_apiDataObjPutPost(*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PORTAL_OPR);
}
