# Encryption enforcement policy
#
# This rule base implements CyVerse's encryption enforcement policy. A user may
# choose to require that any file uploaded to a collection be encrypted. To do
# this, the user must set the AVU attribute `encryption::required` with value
# `true` on a collection. Afterwards, any file uploaded to this collection or
# one under it, must have the file extension `.enc`. This is the extension used
# by GoCommands when it encrypts a file.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.


# Checks if encryption is required for the collection entity
_cyverse_encryption_required(*Coll) =
	let *coll = str(*Coll) in
	let *isRequired = false in
	let *_ = foreach ( *rec in
			SELECT META_COLL_ATTR_VALUE
			WHERE COLL_NAME == *coll AND META_COLL_ATTR_NAME == 'encryption::required'
		) { *isRequired = bool(*rec.META_COLL_ATTR_VALUE) } in
	*isRequired


# This rule checks if encryption is required and reject creating collections
# containing non-encrypted files
_cyverse_encryption_checkRequiredColl(*SrcColl, *DstColl) {
	msiSplitPath(str(*DstColl), *dstParent, *_);

	# check if parent coll has encryption::required avu
	if (_cyverse_encryption_required(*dstParent)) {
		*srcColl = str(*SrcColl);

		# check if src coll has non-encrypted data objects
		foreach (*rec in SELECT DATA_NAME WHERE COLL_NAME == *srcColl || LIKE '*srcColl/%') {
			# all encrypted files will have ".enc" extension
			if (!cyverse_endsWith(*rec.DATA_NAME, ".enc")) {

				# fail to prevent iRODS from creating the file without encryption
				writeLine(
					'serverLog', "Failed to create data object, encryption is required under *srcColl" );

				cut;
				failmsg(-815000, 'CYVERSE ERROR:  attempt to create unencrypted data object');
			}
		}
	}
}


# This rule checks if encryption is required and reject creating non-encrypted files
_cyverse_encryption_checkRequiredDataObj(*Path) {
	msiSplitPath(str(*Path), *parentColl, *objName);

	# check if parent coll has encryption::required avu
	if (_cyverse_encryption_required(*parentColl)) {
		# all encrypted files will have ".enc" extension
		if (!cyverse_endsWith(*objName, ".enc")) {
			# fail to prevent iRODS from creating the file without encryption
			writeLine(
				'serverLog', "Failed to create data object, encryption is required under *parentColl");
			cut;
			failmsg(-815000, 'CYVERSE ERROR:  attempt to create unencrypted data object');
		}
	}
}


_cyverse_encryption_copyParentAvu(*Path) {
	*path = str(*Path);
	msiSplitPath(*path, *parentColl, *collName);

	if (_cyverse_encryption_required(*parentColl)) {
		*mode = ''

		foreach ( *rec in
			SELECT META_COLL_ATTR_VALUE
			WHERE COLL_NAME == *parentColl AND META_COLL_ATTR_NAME == 'encryption::mode'
		) {
			*mode = *rec.META_COLL_ATTR_VALUE;
			break;
		}

		foreach (*rec in SELECT COLL_NAME WHERE COLL_NAME == *path || LIKE '*path/%') {

			# Add encryption require meta to the sub coll
			*err = errormsg(
				msiModAVUMetadata(cyverse_COLL, *rec.COLL_NAME, 'set', 'encryption::required', "true", ''),
				*msg );

			if (*err < 0) { writeLine('serverLog', *msg); }

			if (*mode != '') {
				*err = errormsg(
					msiModAVUMetadata(cyverse_COLL, *rec.COLL_NAME, 'set', 'encryption::mode', *mode, ''),
					*msg );

				if (*err < 0) { writeLine('serverLog', *msg); }
			}
		}
	}
}


_cyverse_encryption_rejectBulkRegIfRequired(*Coll) {
	msiSplitPath(str(*Coll), *parentColl, *collName);

	if (_cyverse_encryption_required(*parentColl)) {

		# we don't allow bulk registering files
		writeLine(
			'serverLog',
			"Failed to bulk register data objects in encryption required collection *parentColl" );

		cut;

		*errMsg =
			'CYVERSE ERROR: attempt to bulk registering data objects in encryption required'
			++ ' collection';

		failmsg(-815000, *errMsg);
	}
}


# If a subcollection is created in a collection that requires encryption, this
# ensures that the subcollection also requires encryption.
#
#  Instance       (string) unknown
#  Comm           (`KeyValuePair_PI`) user connection and auth information
#  CollCreateInp  (`KeyValuePair_PI`) information related to the new collection
#
cyverse_encryption_api_coll_create_post(*Instance, *Comm, *CollCreateInp) {
	_cyverse_encryption_copyParentAvu(*CollCreateInp.coll_name);
}


# This verifies that an object is encrypted if it is being created and stat'ed
# in a collection that requires encryption.
#
#  Instance    (string) unknown
#  Comm        (`KeyValuePair_PI`) user connection and auth information
#  DataObjInp  (`KeyValuePair_PI`) information related to the created data
#              object
#  OpenStat    unknown
#
cyverse_encryption_api_data_obj_create_and_stat_pre(*Instance, *Comm, *DataObjInp, *OpenStat) {
	_cyverse_encryption_checkRequiredDataObj(*DataObjInp.obj_path);
}


# This verifies that an object is encrypted if it is being created in a
# collection that requires encryption.
#
#  Instance	(string) unknown
#  Comm		(`KeyValuePair_PI`) user connection and auth information
#  DataObjInp  (`KeyValuePair_PI`) information related to the created data
#			  object
#
cyverse_encryption_api_data_obj_create_pre(*Instance, *Comm, *DataObjInp) {
	_cyverse_encryption_checkRequiredDataObj(*DataObjInp.obj_path);
}


# This verifies that an object is encrypted if it is being opened for
# modification in a collection that requires encryption.
#
#  Instance    (string) unknown
#  Comm        (`KeyValuePair_PI`) user connection and auth information
#  DataObjInp  (`KeyValuePair_PI`) information related to the data object
#  OpenStat    unknown
#
cyverse_encryption_api_data_obj_open_and_stat_pre(*Instance, *Comm, *DataObjInp, *OpenStat) {
	_cyverse_encryption_checkRequiredDataObj(*DataObjInp.obj_path);
}


# This verifies that an object is encrypted if it is being opened for
# modification in a collection that requires encryption.
#
#  Instance    (string) unused
#  Comm        (`KeyValuePair_PI`) unused
#  DataObjInp  (`KeyValuePair_PI`) information related to the data object
#
cyverse_encryption_api_data_obj_open_pre(*Instance, *Comm, *DataObjInp) {
	_cyverse_encryption_checkRequiredDataObj(*DataObjInp.obj_path);
}


# This verifies that an object is encrypted if it is being uploaded into a
# collection that requires encryption.
#
#  Instance        (string) unknown
#  Comm            (`KeyValuePair_PI`) user connection and auth information
#  DataObjInp      (`KeyValuePair_PI`) information related to the data object
#  DataObjInpBBuf  (unknown) may contain the contents of the file being uploaded
#  PORTAL_OPR_OUT  unknown
#
cyverse_encryption_api_data_obj_put_pre(*Instance, *Comm, *DataObjInp) {
	_cyverse_encryption_checkRequiredDataObj(*DataObjInp.obj_path);
}


# This verifies that an object is encrypted if it is being copied into a
# collection that requires encryption.
#
#  Instance        (string) unknown
#  Comm            (`KeyValuePair_PI`) user connection and auth information
#  DataObjCopyInp  (`KeyValuePair_PI`) information related to copy operation
#  TransStat       unknown
#
cyverse_encryption_api_data_obj_copy_pre(*Instance, *Comm, *DataObjCopyInp, *TransStat) {
	_cyverse_encryption_checkRequiredDataObj(*DataObjCopyInp.dst_obj_path);
}


# This verifies that an object is encrypted if it is being moved into a
# collection that requires encryption. If `DataObjRenameInp` refers to a
# collection, then it verifies that every object in the collection is encrypted.
#
#  Instance          (string) unknown
#  Comm              (`KeyValuePair_PI`) user connection and auth information
#  DataObjRenameInp  (`KeyValuePair_PI`) information about the collection or
#                    data object and its new path
#
cyverse_encryption_api_data_obj_rename_pre(*Instance, *Comm, *DataObjRenameInp) {
	if (int(*DataObjRenameInp.src_opr_type) == 11) {  # data object
		_cyverse_encryption_checkRequiredDataObj(*DataObjRenameInp.dst_obj_path);
	} else if (int(*DataObjRenameInp.src_opr_type) == 12) {  # collection
		_cyverse_encryption_checkRequiredColl(
			*DataObjRenameInp.src_obj_path, *DataObjRenameInp.dst_obj_path );
	}
}


# This ensures that a collection that is moved into a collection that requires
# encryption will also require encryption.
#
#  Instance          (string) unknown
#  Comm              (`KeyValuePair_PI`) user connection and auth information
#  DataObjRenameInp  (`KeyValuePair_PI`) information about the collection or
#                    data object and its old path
#
cyverse_encryption_api_data_obj_rename_post(*Instance, *Comm, *DataObjRenameInp) {
	if (int(*DataObjRenameInp.src_opr_type) == 12) {  # collection
		_cyverse_encryption_copyParentAvu(*DataObjRenameInp.dst_obj_path);
	}
}


# This verifies that when a bundle file is unbundled in a collection that
# requires encryption, that every file in the bundle is encrypted.
#
#  Instance                (string) unknown
#  Comm                    (`KeyValuePair_PI`) user connection and auth
#                          information
#  StructFileExtAndRegInp  (`KeyValuePair_PI`) information about the struct file
#
cyverse_encryption_api_struct_file_ext_and_reg_pre(*Instance, *Comm, *StructFileExtAndRegInp) {
	_cyverse_encryption_rejectBulkRegIfRequired(*StructFileExtAndRegInp.collection_path);
}
