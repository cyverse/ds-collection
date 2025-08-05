# PIRE project policy
#
# Any data object put in the BH-PIRE or EHT project collection will be stored on
# the BH-PIRE resource server. No other data objects may be stored there.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

@include 'pire-env'


_pire_isForPire(*Path) =
	let *answer = false in
	let *pireRes = pire_RESC in
	let *_ = foreach( *rec in
			SELECT META_RESC_ATTR_VALUE
			WHERE RESC_NAME = *pireRes AND META_RESC_ATTR_NAME = 'ipc::hosted-collection'
		) { *answer = *answer || (str(*Path) like *rec.META_RESC_ATTR_VALUE ++ '/*'); } in
	*answer


### DYNAMIC PEPS ###

## RESOURCE ##

# RESOLVE HIERARCHY

# Restrict the PIRE resource to files in the PIRE collection
#
# Parameters:
#  Instance  (string) unused
#  Context   (`KeyValuePair_PI`) the resource plugin Context
#  OUT       (`KeyValuePair_PI`) unused
#  Op        (string) unused
#  Host      (string) unused
#  PARSER    (`KeyValuePair_PI`) unused
#  VOTE      (float) unused
#
# XXX - Because of https://github.com/irods/irods/issues/6463
# # Error Codes:
# #  -32000 (SYS_INVALID_RESC_INPUT)  this is returned when an error occurred in
# #                                   one of the on branches of this rule
# temporaryStorage:
#  resource_resolve_hierarchy_err  this is used to store an error message when an attempt is made to
#                                  to store a replica on the AVRA resource that should be.
# XXX - ^^^
#
pep_resource_resolve_hierarchy_pre(*Instance, *Context, *OUT, *Op, *Host, *PARSER, *VOTE) {
	on (
		pire_RESC != cyverse_DEFAULT_RESC
		&& *Context.resc_hier == pire_RESC
		&& !_pire_isForPire(*Context.logical_path)
	) {
		*msg = 'CYVERSE ERROR: ' ++ pire_RESC ++ ' usage is limited to the collections '
			++ str(pire_PUBLIC_BASE_COLL) ++ ' and ' ++ str(pire_PROJECT_BASE_COLL) ++ '.';
# XXX - Because of https://github.com/irods/irods/issues/6463, an error
# happening in an `ON` condition needs to be captured and sent in the catch-all.
# 		cut;
# 		failmsg(-32000, *msg);
		temporaryStorage.resource_resolve_hierarchy_err = *msg;
		fail;
# XXX - ^^^
	}
}
