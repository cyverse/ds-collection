# This rule base contains the PEPs of cyverse_core.re that depend on the iRODS
# release. This version is for iRODS 4.3.1.
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.


# DATA_OBJ_PUT

# pep_api_data_obj_put_pre and pep_api_data_obj_put_post have a huge memory leak
# before 4.3.4: https://github.com/irods/irods/issues/8106. There is no
# workaround for pep_api_data_obj_put_pre, so cyverse_encryption.re can't
# reject an upload, and acPostProcForPut does the post processing instead.

# This is the post processing logic for when a data object is uploaded through
# the API using a DATA_OBJ_PUT request. It builds the arguments
# pep_api_data_obj_put_post would have been given from the session variables.
#
acPostProcForPut {
	*Instance = '';

	*Comm.user_rods_zone = $rodsZoneClient;
	*Comm.user_user_name = $userNameClient;

	*DataObjInpBBuf = '';

	*DataObjInp.obj_path = $objPath;
	*DataObjInp.data_size = str($dataSize);

	msiSplitPath($objPath, *collPath, *dataName);

	foreach( *rec in
		SELECT DATA_RESC_HIER
		WHERE COLL_NAME = *collPath AND DATA_NAME = *dataName AND DATA_RESC_NAME = $rescName
	) {
		*DataObjInp.resc_hier = *rec.DATA_RESC_HIER;
	}

	_cyverse_core_apiDataObjPutPost(*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PORTAL_OPR);
}
