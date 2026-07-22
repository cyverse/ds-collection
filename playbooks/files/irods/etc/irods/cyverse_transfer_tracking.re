# This rule base contains the iRODS transfer tracking logic prototype created by
# RENCI.
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

_cyverse_transfer_tracking_addTransfer(*User, *Zone, *Dir, *Vol) {
	foreach( *res in
		select USER_ID where USER_NAME = '*User' and USER_ZONE = '*Zone' and USER_TYPE = 'rodsuser'
	) {
		*userArg = execCmdArg(*res.USER_ID);
		*dirArg = execCmdArg(*Dir);
		*volArg = execCmdArg(*Vol);
		*args = "*userArg *dirArg *volArg";
		*ec = errormsg(msiExecCmd("add-transfer", *args, "null", "null", "null", *out), *msg);
		if (*ec != 0) {
			msiGetStderrInExecCmdOut(*out, *err);
			writeLine('serverLog', "add-transfer failed: *msg (*err)");
			failmsg(*ec, *err);
		}
	}
}

# When a set of data objects are bulk uploaded, record the total volume of the
# files being uploaded.
#
# Parameters:
#  Instance       (string) unused
#  Comm           (`KeyValuePair_PI`) user connection and auth information
#  BulkOpInp      (`KeyValuePair_PI`) information related to the bulk upload
#  BulkOpInpBBuf  (unknown) unused
#
cyverse_transfer_tracking_api_bulk_data_obj_put_post(
	*Instance, *Comm, *BulkOprInp, *BulkOpInpBBuf
) {
	# NB: iRODS int type has a max value of 2147483647. Adding 1 to this results
	#     in -2147483648. To prevent this, if a file has a value larger than 9
	#     digits, record the file as an individual transfer. Also, if the
	#     cummulative volume i	 parallel s in danger of exceeding the maximum int value,
	#     record the current cummulative volume as an individual transfer and
	#     reset the total.
	*maxDigits = 9;
	*maxInt = 2147483647;

	*user = *Comm.user_user_name;
	*zone = *Comm.user_rods_zone;

	# bulk can hold up to 50 files, with sizes in data_size_0 through
	# data_size_49. walk through and sum the sizes

	*totalVol = 0;

	foreach(*k in *BulkOprInp) {
		if (*k like "data_size_*") {
			*volStr = *BulkOprInp.*k;

			if (strlen(*volStr) > *maxDigits) {
				_cyverse_transfer_tracking_addTransfer(*user, *zone, 'in', *volStr);
			} else {
				*vol = int(*BulkOprInp.*k);

				if (*maxInt - *totalVol > *vol) {
					_cyverse_transfer_tracking_addTransfer(*user, *zone, 'in', *totalVol);
					*totalVol = 0;
				}

				*totalVol = *totalVol + *vol;
			}
		}
	}

	_cyverse_transfer_tracking_addTransfer(*user, *zone, 'in', *totalVol);
}

# When a data object is downloaded through the DATA_OBJ_GET API, the size of the
# download is recorded.
#
# Parameters:
#  Instance        (string) unused
#  Comm            (`KeyValuePair_PI`) user connection and auth information
#  DataObjInp      (`KeyValuePair_PI`) information related to the data object
#  PORTAL_OPR      (unknown) unused
#  DATA_OBJ_B_BUF  (unknown) unused
#
cyverse_transfer_tracking_api_data_obj_get_post(
	*Instance, *Comm, *DataObjInp, *PORTAL_OPR, *DATA_OBJ_B_BUF
) {
	_cyverse_transfer_tracking_addTransfer(
		*Comm.user_user_name, *Comm.user_rods_zone, 'out', *DataObjInp.data_size );
}

# When a data object is uploaded through the DATA_OBJ_PUT API, the size of the
# upload is recorded.
#
# Parameters:
#  Instance        (string) unused
#  Comm            (`KeyValuePair_PI`) user connection and auth information
#  DataObjInp      (`KeyValuePair_PI`) information related to the data object
#  DataObjInpBBuf  (unknown) unused
#  PORTAL_OPR      (unknown) unused
#
cyverse_transfer_tracking_api_data_obj_put_post(
	*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PORTAL_OPR
) {
	_cyverse_transfer_tracking_addTransfer(
		*Comm.user_user_name, *Comm.user_rods_zone, 'in', *DataObjInp.data_size );
}

# When a data object is read from using a DATA_OBJ_READ request, the volume of
# data read is recorded.
#
# Parameters:
#  Instance             (string) unknown
#  Comm                 (`KeyValuePair_PI`) user connection and auth information
#  DataObjReadInp       (`KeyValuePair_PI`) information about the read request
#  DATA_OBJ_READ_B_BUF  (unknown) the contents that were read from the object
#
cyverse_transfer_tracking_api_data_obj_read_post(
	*Instance, *Comm, *DataObjReadInp, *DATA_OBJ_READ_B_BUF
) {
	_cyverse_transfer_tracking_addTransfer(
		*Comm.user_user_name, *Comm.user_rods_zone, 'out', *DataObjReadInp.len );
}

# When a data object is written to using a DATA_OBJ_WRITE request, the volume of
# data written is recorded.
#
# Parameters:
#  Instance             (string) unused
#  Comm                 (`KeyValuePair_PI`) user connection and auth information
#  DataObjWriteInp      (`KeyValuePair_PI`) information about the write request
#  DataObjWriteInpBBuf  (unknown) unused
#
cyverse_transfer_tracking_api_data_obj_write_post(
	*Instance, *Comm, *DataObjWriteInp, *DataObjWriteInpBBuf
) {
	_cyverse_transfer_tracking_addTransfer(
		*Comm.user_user_name, *Comm.user_rods_zone, 'in', *DataObjWriteInp.len );
}

# When a data object replica is opened through the API using a REPLICA_OPEN
# request, this records the size of the replica for use by
# cyverse_transfer_tracking_api_replica_close_post.
#
# Parameters:
#  Instance     (string) unused
#  Comm         (`KeyValuePair_PI`) user connection and auth information
#  DataObjInp   (`KeyValuePair_PI`) information about the data object
#  JSON_OUTPUT  (unknown) unused
#
cyverse_logic_api_replica_open_post(*Instance, *Comm, *DataObjInp, *JSON_OUTPUT) {
	temporaryStorage.cyverse_transfer_tracking_replica_dataObjPath = cyverse_getValue(
		*DataObjInp, 'obj_path' );

	temporaryStorage.cyverse_transfer_tracking_replica_openFlag = cyverse_getValue(
		*DataObjInp, 'open_flag' );
}

# When a data object replica is closed through the API using a REPLICA_CLOSE
# request, this updates the upload or download count appropriately.
#
# Parameters:
#  Instance   (string) unused
#  Comm       (`KeyValuePair_PI`) user connection and auth information
#  JsonInput  (string) a JSON-serialized description of the replica change
#
cyverse_transfer_tracking_api_replica_close_post(*Instance, *Comm, *JsonInput) {
	*path = cyverse_getValue(temporaryStorage, 'cyverse_transfer_tracking_replica_dataObjPath');
	*openFlag = cyverse_getValue(temporaryStorage, 'cyverse_transfer_tracking_replica_openFlag');

	_cyverse_transfer_tracking_addTransfer(
		*Comm.user_user_name,
		*Comm.user_rods_zone,
		if *openFlag == cyverse_OPEN_FLAG_R then 'out' else 'in',
		cyverse_getValue(cyverse_getDataInfo(*path), 'size') );
}