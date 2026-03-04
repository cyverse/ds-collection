# A stub implementation of cyverse_logic.re used for unit testing. All rules
# write a message to the server log saying they were called.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

cyverse_logic_chksumRepl(*DataObjId, *ReplNum) {
	writeLine('serverLog', "cyverse_logic_chksumRepl(*DataObjId, *ReplNum) called");
}

cyverse_logic_acPreProcForModifyAccessControl(*RecurseFlag, *Perm, *Username, *Zone, *Path) {
	writeLine(
		'serverLog',
		"cyverse_logic_acPreProcForModifyAccessControl(*RecurseFlag, *Perm, *Username, *Zone, *Path)"
			++ " called" );
}

cyverse_logic_acPostProcForModifyAccessControl(
	*RecurseFlag, *Perm, *Username, *UserZone, *Path, *ClientUsername, *ClientZone
) {
	writeLine(
		'serverLog',
		"cyverse_logic_acPostProcForModifyAccessControl(*RecurseFlag, *Perm, *Username, *UserZone, *Path, *ClientUsername, *ClientZone)"
			++ " called" );
}

cyverse_logic_acPreProcForModifyAVUMetadata(
	*Opt, *EntityType, *EntityName, *Attr, *Val, *Unit, *ClientUsername, *ClientZone
) {
	writeLine(
		'serverLog',
		"cyverse_logic_acPreProcForModifyAVUMetadata(*Opt, *EntityType, *EntityName, *Attr, *Val, *Unit, *ClientUsername, *ClientZone)"
			++ " called" );
}

cyverse_logic_acPreProcForModifyAVUMetadata(
	*Opt,
	*EntityType,
	*EntityName,
	*Attr,
	*Val,
	*Unit,
	*New1,
	*New2,
	*New3,
	*ClientUsername,
	*ClientZone
) {
	writeLine(
		'serverLog',
		"cyverse_logic_acPreProcForModifyAVUMetadata(*Opt, *EntityType, *EntityName, *Attr, *Val, *Unit, *New1, *New2, *New3, *ClientUsername, *ClientZone)"
			++ " called" );
}

cyverse_logic_acPreProcForModifyAVUMetadata(
	*Opt, *SrcType, *TgtType, *SrcName, *TgtName, *ClientUsername, *ClientZone
) {
	writeLine(
		'serverLog',
		"cyverse_logic_acPreProcForModifyAVUMetadata(*Opt, *SrcType, *TgtType, *SrcName, *TgtName, *ClientUsername, *ClientZone)"
			++ " called" );
}

cyverse_logic_acPostProcForModifyAVUMetadata(
	*Opt, *EntityType, *EntityName, *Attr, *Val, *Unit, *ClientUsername, *ClientZone
) {
	writeLine(
		'serverLog',
		"cyverse_logic_acPostProcForModifyAVUMetadata(*Opt, *EntityType, *EntityName, *Attr, *Val, *Unit, *ClientUsername, *ClientZone)"
			++ " called" );
}

cyverse_logic_acPostProcForModifyAVUMetadata(
	*Opt,
	*EntityType,
	*EntityName,
	*Attr,
	*Val,
	*Unit,
	*New1,
	*New2,
	*New3,
	*ClientUsername,
	*ClientZone
) {
	writeLine(
		'serverLog',
		"cyverse_logic_acPostProcForModifyAVUMetadata(*Opt, *EntityType, *EntityName, *Attr, *Val, *Unit, *New1, *New2, *New3, *ClientUsername, *ClientZone)"
			++ " called");
}

cyverse_logic_acPostProcForModifyAVUMetadata(
	*Opt, *SrcType, *TgtType, *SrcName, *TgtName, *ClientUsername, *ClientZone
) {
	writeLine(
		'serverLog',
		"cyverse_logic_acPostProcForModifyAVUMetadata(*Opt, *SrcType, *TgtType, *SrcName, *TgtName, *ClientUsername, *ClientZone)"
			++ " called" );
}

cyverse_logic_acCreateCollByAdmin(*ParCollPath, *CollName, *ClientUsername, *ClientZone) {
	writeLine(
		'serverLog',
		"cyverse_logic_acCreateCollByAdmin(*ParCollPath, *CollName, *ClientUsername, *ClientZone)"
			++ " called" );
}

cyverse_logic_acPostProcForCollCreate(*CollPath, *ClientUsername, *ClientZone) {
	writeLine(
		'serverLog',
		"cyverse_logic_acPostProcForCollCreate(*CollPath, *ClientUsername, *ClientZone) called" );
}

cyverse_logic_acDeleteCollByAdmin(*ParCollPath, *CollName, *ClientUsername, *ClientZone) {
	writeLine(
		'serverLog',
		"cyverse_logic_acDeleteCollByAdmin(*ParCollPath, *CollName, *ClientUsername, *ClientZone)"
			++ " called" );
}

cyverse_logic_acDeleteCollByAdminIfPresent(*ParCollPath, *CollName, *ClientUsername, *ClientZone) {
	writeLine(
		'serverLog',
		"cyverse_logic_acDeleteCollByAdminIfPresent(*ParCollPath, *CollName, *ClientUsername, *ClientZone)"
			++ " called" );
}

cyverse_logic_acPreprocForRmColl(*CollPath) {
	writeLine('serverLog', "cyverse_logic_acPreprocForRmColl(*CollPath) called");
}

cyverse_logic_acPostProcForRmColl(*CollPath, *ClientUsername, *ClientZone) {
	writeLine(
		'serverLog',
		"cyverse_logic_acPostProcForRmColl(*CollPath, *ClientUsername, *ClientZone) called" );
}

cyverse_logic_acPreConnect(*OUT) {
	writeLine('serverLog', "cyverse_logic_acPreConnect(OUT) called");
	*OUT = 'CS_NEG_REFUSE';
}

cyverse_logic_acPostProcForDataCopyReceived(*StoreResc) {
	writeLine('serverLog', "cyverse_logic_acPostProcForDataCopyReceived(*StoreResc) called");
}

cyverse_logic_acDataDeletePolicy(*DataPath) {
	writeLine('serverLog', "cyverse_logic_acDataDeletePolicy(*DataPath) called");
}

cyverse_logic_acPostProcForDelete(*DataPath, *ClientUsername, *ClientZone) {
	writeLine(
		'serverLog',
		"cyverse_logic_acPostProcForDelete(*DataPath, *ClientUsername, *ClientZone) called" );
}

cyverse_logic_acPostProcForOpen(*DataPath, *DataSize, *ClientUsername, *ClientZone) {
	writeLine(
		'serverLog',
		"cyverse_logic_acPostProcForOpen(*DataPath, *DataSize, *ClientUsername, *ClientZone)"
			++ " called" );
}

cyverse_logic_acPostProcForObjRename(*SrcEntity, *DestEntity, *ClientUsername, *ClientZone) {
	writeLine(
		'serverLog',
		"cyverse_logic_acPostProcForObjRename(*SrcEntity, *DestEntity, *ClientUsername, *ClientZone)"
			++ " called" );
}

cyverse_logic_acPostProcForParallelTransferReceived(*StoreResc) {
	writeLine('serverLog', "cyverse_logic_acPostProcForParallelTransferReceived(*StoreResc) called");
}

cyverse_logic_dataObjCreated(*Username, *Zone, *DataObjInfo, *Step) {
	writeLine(
		'serverLog', "cyverse_logic_dataObjCreated(*Username, *Zone, DataObjInfo, *Step) called" );
}

cyverse_logic_dataObjMetaMod(*Username, *Zone, *Path) {
	writeLine('serverLog', "cyverse_logic_dataObjMetaMod(*Username, *Zone, *Path) called");
}

cyverse_logic_api_bulk_data_obj_put_post(*Instance, *Comm, *BulkOpInp, *BulkOpInpBBuf) {
	writeLine(
		'serverLog',
		"cyverse_logic_api_bulk_data_obj_put_post(*Instance, *Comm, *BulkOpInp, *BulkOpInpBBuf)"
			++ " called" );
}

cyverse_logic_api_bulk_data_obj_reg_post(
	*Instance, *Comm, *BulkDataObjRegInp, *BULK_DATA_OBJ_REG_OUT
) {
	writeLine(
		'serverLog',
		"cyverse_logic_api_bulk_data_obj_reg_post(*Instance, *Comm, *BulkDataObjRegInp, BULK_DATA_OBJ_REG_OUT)"
			++ " called" );
}

cyverse_logic_api_data_obj_copy_post(*Instance, *Comm, *DataObjCopyInp, *TransStat) {
	writeLine(
		'serverLog',
		"cyverse_logic_api_data_obj_copy_post(*Instance, *Comm, *DataObjCopyInp, *TransStat)"
			++ " called" );
}

cyverse_logic_api_data_obj_create_post(*Instance, *Comm, *DataObjInp) {
	writeLine(
		'serverLog', "cyverse_logic_api_data_obj_create_post(*Instance, *Comm, *DataObjInp) called" );
}

cyverse_logic_api_data_obj_create_and_stat_post(*Instance, *Comm, *DataObjInp, *OpenStat) {
	writeLine(
		'serverLog',
		"cyverse_logic_api_data_obj_create_and_stat_post(*Instance, *Comm, *DataObjInp, *OpenStat)"
			++ " called" );
}

cyverse_logic_api_data_obj_open_post(*Instance, *Comm, *DataObjInp) {
	writeLine(
		'serverLog', "cyverse_logic_api_data_obj_open_post(*Instance, *Comm, *DataObjInp) called" );
}

cyverse_logic_api_data_obj_write_post(*Instance, *Comm, *DataObjWriteInp, *DataObjWriteInpBBuf) {
	writeLine(
		'serverLog',
		"cyverse_logic_api_data_obj_write_post(*Instance, *Comm, *DataObjWriteInp, *DataObjWriteInpBBuf)"
			++ " called" );
}

cyverse_logic_api_data_obj_close_post(*Instance, *Comm, *DataObjCloseInp) {
	writeLine(
		'serverLog',
		"cyverse_logic_api_data_obj_close_post(*Instance, *Comm, *DataObjCloseInp) called" );
}

cyverse_logic_api_data_obj_put_post(
	*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PORTAL_OPR_OUT
) {
	writeLine(
		'serverLog',
		"cyverse_logic_api_data_obj_put_post(*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, PORTAL_OPR_OUT)"
			++ " called" );
}

cyverse_logic_api_phy_path_reg_post(*Instance, *Comm, *PhyPathRegInp) {
	writeLine(
		'serverLog', "cyverse_logic_api_phy_path_reg_post(*Instance, *Comm, *PhyPathRegInp) called" );
}

cyverse_logic_api_replica_open_post(*Instance, *Comm, *DataObjInp, *JSON_OUTPUT) {
	writeLine(
		'serverLog',
		"cyverse_logic_api_replica_open_post(*Instance, *Comm, *DataObjInp, JSON_OUTPUT) called" );
}

cyverse_logic_api_replica_close_post(*Instance, *Comm, *JsonInput) {
	writeLine(
		'serverLog', "cyverse_logic_api_replica_close_post(*Instance, *Comm, *JsonInput) called" );
}

cyverse_logic_api_touch_post(*Instance, *Comm, *JsonInput) {
	writeLine('serverLog', "cyverse_logic_api_touch_post(*Instance, *Comm, *JsonInput) called" );
}
