# PIRE project policy
#
# Any data object put in the BH-PIRE or EHT project collection will be stored on
# the BH-PIRE resource server. No other data objects may be stored there.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

@include 'pire-env'


_pire_isForPire(*Path) =
	let *strPath = str(*Path)
	in *strPath like str(pire_PROJECT_BASE_COLL) ++ '/*' ||
		*strPath like str(pire_PUBLIC_BASE_COLL) ++ '/*'


# Determines if the provided collection or data object belongs to the PIRE
# project
#
# Parameters:
#  Entity  the absolute path to the collection or data object
#
# Return:
#  true if the collection or data object belongs to the project, otherwise false
#
pire_replBelongsTo : path -> boolean
pire_replBelongsTo(*Entity) = _pire_isForPire(*Entity)


# Returns the resource where newly ingested files will be stored
#
# Return:
#  a tuple where the first value is the name of the resource and the second is a
#  flag indicating whether or not this resource choice may be overridden by the
#  user.
#
pire_replIngestResc : string * boolean
pire_replIngestResc = (pire_RESC, false)


# Returns the resource where the second and subsequent replicas of a file will
# be stored
#
# Return:
#  a tuple where the first value is the name of the resource and the second is a
#  flag indicating whether or not this resource choice may be overridden by the
#  user.
#
pire_replReplResc : string * boolean
pire_replReplResc = pire_replIngestResc


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
# Error Codes:
#  -32000 (SYS_INVALID_RESC_INPUT)  this is returned when an attempt is made to
#                                   store an unauthorized file on the PIRE
#                                   resource.
#
pep_resource_resolve_hierarchy_pre(*Instance, *Context, *OUT, *Op, *Host, *PARSER, *VOTE) {
	on (
		pire_RESC != cyverse_DEFAULT_RESC
		&& *Context.resc_hier == pire_RESC
		&& !_pire_isForPire(*Context.logical_path)
	) {
		*msg = 'CYVERSE ERROR: ' ++ pire_RESC ++ ' usage is limited to the EHT collection, '
			++ str(pire_PUBLIC_BASE_COLL);

		cut;
		failmsg(-32000, *msg);
	}
}
