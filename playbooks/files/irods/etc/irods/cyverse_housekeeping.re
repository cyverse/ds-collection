# This is a library of rules for periodic tasks like updating quota usage data.
#
## STORAGE FREE SPACE TRACKING
#
# Once a day, the amount of available storage for each storage resource is
# determined and cataloged.
#
# © 2023 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.


#
# SHARED RULES
#

_cyverse_housekeeping_schedulePeriodicPolicy(*RuleName, *Freq, *Desc) {
	writeLine('serverLog', 'DS: scheduling *Desc');
	eval(``delay('<PLUSET>0s</PLUSET><EF>*Freq</EF>') {`` ++ *RuleName ++ ``}`` );
}

_cyverse_housekeeping_reschedulePeriodicPolicy(*RuleName, *Freq, *Desc) {
	*scheduled = false;
	foreach(*row in SELECT RULE_EXEC_ID, RULE_EXEC_FREQUENCY WHERE RULE_EXEC_NAME = '*RuleName') {
		if (*scheduled || *row.RULE_EXEC_FREQUENCY != *Freq) {
			writeLine('serverLog', 'DS: unscheduling *Desc');
			*idArg = execCmdArg(*row.RULE_EXEC_ID);
			*status = errorcode(
				msiExecCmd('delete-scheduled-rule', *idArg, 'null', 'null', 'null', *out) );
			if (*status < 0) {
				msiGetStderrInExecCmdOut(*out, *resp);
				failmsg(*status, *resp);
			}
		} else {
			*scheduled = true;
		}
	}
	if (*scheduled) {
		writeLine('stdout', '*Desc already scheduled');
	} else {
		_cyverse_housekeeping_schedulePeriodicPolicy(*RuleName, *Freq, *Desc);
		writeLine('stdout', 'scheduled *Desc');
	}
}


#
# STORAGE FREE SPACE
#

# NOTE: This runs on the resource server hosting the resource whose free space
# is in question.
_cyverse_housekeeping_determineStorageFreeSpace(*Host, *RescName) {
	writeLine('serverLog', "DS: remotely determining free space on *Host for *RescName");
	remote(*Host, '') {
		writeLine('serverLog', "DS: locally determining free space for *RescName");
		if (0 == errormsg(msi_update_unixfilesystem_resource_free_space(*RescName), *msg)) {
			writeLine('serverLog', "DS: determined free space for *RescName");
		} else {
			writeLine('serverLog', "DS: failed to determine free space for *RescName: *msg");
		}
	}
}

# This rule updates the catalog information on the amount of free space exists
# in each resource. It is safe to be run asynchronously.
#
cyverse_housekeeping_determineAllStorageFreeSpace {
	writeLine('serverLog', 'DS: determining free space on resource servers');
	foreach(*record in
		SELECT RESC_LOC, RESC_NAME WHERE RESC_TYPE_NAME = 'unixfilesystem' AND RESC_STATUS = 'up'
	) {
		*host = *record.RESC_LOC;
		*resc = *record.RESC_NAME;
		if (0 > errormsg(_cyverse_housekeeping_determineStorageFreeSpace(*host, *resc), *msg)) {
			writeLine('serverLog', "DS: failed to determine free space on *host for *resc: *msg");
		}
	}
	writeLine('serverLog', 'DS: determined free space on resource servers');
}

# This rule schedules the daily determination of the available disk space for
# all Unix file system resources. If it reschedules the determination, it writes
# 'scheduled storage determination' to standard output. If it doesn't error out,
# but it doesn't reschedule the determination, it writes 'storage determination
# already scheduled'.
#
cyverse_housekeeping_rescheduleStorageFreeSpaceDetermination {
	_cyverse_housekeeping_reschedulePeriodicPolicy(
		``cyverse_housekeeping_determineAllStorageFreeSpace``,
		'1d REPEAT FOR EVER',
		'storage determination' );
}
