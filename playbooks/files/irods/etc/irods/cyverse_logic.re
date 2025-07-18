# The general Data Store rule independent of environment specific rule
# customizations.
#
#
#### AMQP MESSAGE PUBLISHING
#
# For a select set of user events described below, iRODS is configured to
# publish messages defined as JSON documents to an AMQP topic exchange. The name
# of the exchange is configured in the iRODS rule constant
# `cyverse_AMQP_EXCHANGE`.
#
### Shared JSON Object Definitions
#
# This section describes the JSON objects that are common to multiple messages.
#
## AVU
#
# All AVUs mentioned in the AMQP messages will be an object with the following
# form.
#
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/avu",
#  "title": "AVU",
#  "description": "an iRODS AVU",
#  "type": "object",
#  "properties" {
#   "attribute": {
#    "description": "the name of the AVU",
#    "type": "string"
#   },
#   "value": {
#    "description": "the value of the AVU",
#    "type": "string"
#   },
#   "unit": {
#    "description": "the units of the value",
#    "string"
#   }
#  },
#  "required": [ "attribute", "value" ]
# }
#
## User Id
#
# All users mentioned in the AMQP messages be be an object with the following
# form.
#
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/user-id",
#  "title": "User Identity",
#  "description": "An object uniquely identifying an iRODS user",
#  "type": "object",
#  "properties": {
#   "name": {
#    "description": "The username of the user",
#    "type": "string"
#   },
#   "zone": {
#    "description": "The authentication zone of the user",
#    "type": "string"
#   }
#  },
#  "required": [ "name", "zone" ]
# }
#
## Simple AVU Change
#
# All AMQP messages involving a single collection or data object and a single
# AVU will have the following form.
#
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/avu/simple-change",
#  "title": "Simple AVU Change",
#  "description": "An object describing a simple AVU change event",
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the AVU event happened ",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description":
#     "The UUID of the collection or data object receiving the AVU change",
#    "type": "string"
#   },
#   "metadatum": {
#    "description": "the AVU",
#    "$ref": "/avu"
#   }
#  },
#  "required": [ "author", "entity", "metadatum" ]
# }
#
### Types of Messages Published
#
# Here are the definitions of all of the messages that are published to the
# topic exchange.
#
## Collection Created
#
# Whenever a collection is created, the following message is published.
#
# topic: collection.add
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/collection/add",
#  "title": "collection.add",
#  "description": "The message published whenever a collection is created",
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the collection was created",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description": "The UUID of the newly created collection",
#    "type": "string"
#   },
#   "path": {
#    "description": "The absolute logical path to the collection",
#    "type": "string"
#   }
#  },
#  "required": [ "author", "entity", "path" ]
# }
#
## Collection Moved
#
# Whenever a collection is moved or renamed, the following message is published.
#
# topic: collection.mv
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/collection/mv",
#  "title": "collection.mv",
#  "description":
#   "The message published whenever a collection is moved or renamed",
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the collection was moved",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description": "The UUID of the collection",
#    "type": "string"
#   },
#   "old-path": {
#    "description": "The collection's previous absolute logical path",
#    "type": "string"
#   },
#   "new-path": {
#    "description": "The collection's current absolute logical path",
#    "type": "string"
#   }
#  },
#  "required": [ "author", "entity", "old-path", "new-path" ]
# }
#
## Collection Removed
#
# Whenever a collection is removed, the following message is published.
#
# topic: collection.rm
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/collection/rm",
#  "title": "collection.rm",
#  "description": "The message published whenever a collection is removed",
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the collection was deleted",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description": "The UUID of the collection",
#    "type": "string"
#   },
#   "path": {
#    "description": "The collection's previous absolute logical path",
#    "type": "string"
#   }
#  },
#  "required": [ "author", "entity", "path" ]
# }
#
## Collection ACL Change
#
# Whenever a collection's ACL is changed, i.e., a permission is added, modified,
# or removed, or inheritance is changed, the following message is published.
#
# topic: collection.acl.mod
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/collection/acl/mod",
#  "title": "collection.acl.mod",
#  "description":
#   "The message published whenever a collection's ACL is changed, or ACL inheritance is changed"
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the ACL was modified",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description": "The UUID of the collection",
#    "type": "string"
#   },
#   "recursive": {
#    "description":
#     "whether or not the change was recursively applied to all member collections and data objects",
#    "type": "boolean"
#   },
#   "permission": {
#    "description":
#     "The permission level being set, one of: 'null', 'read', 'write', or 'own'",
#    "type": "string"
#   },
#   "user": {
#    "description": "The user receiving the permission",
#    "$ref": "/user-id"
#   },
#   "inherit": {
#    "description": "inheritance is being set (true) or removed (false)",
#    "type": "boolean"
#   }
#  },
#  "required": [ "author", "entity", "recursive" ]
# }
#
## Collection AVU Added
#
# Whenever an AVU is added to a collection, the following message is published.
#
# topic: collection.metadata.add
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/collection/metadata/add",
#  "title": "collection.metadata.add",
#  "description":
#   "The message published whenever an AVU is added to a collection"
#  "$ref": "/avu/simple-change"
# }
#
## Collection AVU Administratively Added
#
# Whenever an AVU is added to a collection administratively, the following
# message is published.
#
# topic: collection.metadata.adda
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/collection/metadata/adda",
#  "title": "collection.metadata.adda",
#  "description":
#   "The message published whenever an AVU is administratively added to a collection"
#  "$ref": "/avu/simple-change"
# }
#
## Collection AVU Copied
#
# Whenever an AVU is copied to a collection, the following message is published.
#
# topic: collection.metadata.cp
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/collection/metadata/cp",
#  "title": "collection.metadata.cp",
#  "description":
#   "The message published whenever an AVU is copied to a collection".
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the AVU were copied",
#    "$ref": "/user-id"
#   },
#   "source": {
#    "description": "The name or path of the source providing the AVUs",
#    "type": "string"
#   },
#   "source-type": {
#    "description":
#     "the type of the source: collection, data-object, resource, or user",
#    "type": "string"
#   },
#   "destination": {
#    "description": "The logical path to the collection receiving the AVUs",
#    "type": "string"
#   }
#  },
#  "required": [ "author", "source", "source-type", "destination" ]
# }
#
## Collection AVU Modified
#
# Whenever a collection's AVU is modified, the following message is published.
#
# topic: collection.metadata.mod
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/collection/metadata/mod",
#  "title": "collection.metadata.mod",
#  "description":
#   "The message published whenever a collection's AVU is modified".
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the AVU was modified",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description": "The UUID of the collection",
#    "type": "string"
#   },
#   "old-metadatum": {
#    "description": "the AVU before it was modified",
#    "$ref": "/avu"
#   },
#   "new-metadatum": {
#    "description": "the AVU after it was modified",
#    "$ref": "/avu"
#   }
#  },
#  "required": [ "author", "entity", "old-metadatum", "new-metadatum" ]
# }
#
## Collection AVU Removed
#
# Whenever a collection's AVU is removed, the following message is published.
#
# topic: collection.metadata.rm
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/collection/metadata/rm",
#  "title": "collection.metadata.rm",
#  "description":
#   "The message published whenever a collection's AVU is removed"
#  "$ref": "/avu/simple-change"
# }
#
## Collection AVUs Removed by Wildcard
#
# Whenever a collection's AVUs are removed by wildcard, the following message is
# published.
#
# topic: collection.metadata.rmw
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/collection/metadata/rmw",
#  "title": "collection.metadata.rmw",
#  "description":
#   "The message published whenever a collection's AVUs are removed by wildcard"
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the AVUs were removed",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description": "The UUID of the collection",
#    "type": "string"
#   },
#   "attribute-pattern": {
#    "description": "the wildcard pattern that matched the attributes",
#    "type": "string"
#   },
#   "value-pattern": {
#    "description": "the wildcard pattern that matched the values",
#    "type": "string"
#   },
#   "unit-pattern": {
#    "description": "the wildcard pattern that matched the units",
#    "type": "string"
#   }
#  },
#  "required": [ "author", "entity" ]
# }
#
## Collection AVU Set
#
# Whenever an AVU is set on a collection, the following message is published.
#
# topic: collection.metadata.adda
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/collection/metadata/set",
#  "title": "collection.metadata.set",
#  "description":
#   "The message published whenever an AVU is set on a collection"
#  "$ref": "/avu/simple-change"
# }
#
## Data Object Created
#
# Whenever a data object is created, the following message is published.
#
# topic: data-object.add
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/data-object/add",
#  "title": "data-object.add",
#  "description": "The message published whenever a data object is created",
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the data object was created",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description": "The UUID of the newly created collection",
#    "type": "string"
#   },
#   "path": {
#    "description": "The absolute logical path to the data object",
#    "type": "string"
#   },
#   "creator": {
#    "description": "The user assigned as the owner of the data object",
#    "$ref": "/user-id"
#   },
#   "size": {
#    "description": "The size in bytes of the data object",
#    "type", "integer"
#   },
#   "type": {
#    "description": "The file type of the data object",
#    "type": "string"
#   }
#  },
#  "required": [ "author", "entity", "path", "size" ]
# }
#
## Data Object Moved
#
# Whenever a data object is moved or renamed, the following message is
# published.
#
# topic: data-object.mv
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/data-object/mv",
#  "title": "data-object.mv",
#  "description":
#   "The message published whenever a data object is moved or renamed",
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the data object was moved",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description": "The UUID of the data object",
#    "type": "string"
#   },
#   "old-path": {
#    "description": "The data object's previous absolute logical path",
#    "type": "string"
#   },
#   "new-path": {
#    "description": "The data object's current absolute logical path",
#    "type": "string"
#   }
#  },
#  "required": [ "author", "entity", "old-path", "new-path" ]
# }
#
## Data Object Modified
#
# Whenever a data object is modified or overwritten (not its AVU metadata), the
# following message is published.
#
# topic: data-object.mod
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/data-object/mod",
#  "title": "data-object.mod",
#  "description": "The message published whenever a data object is modified",
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the data object was modified",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description": "The UUID of the data object",
#    "type": "string"
#   },
#   "creator": {
#    "description": "The user assigned as the owner of the data object",
#    "$ref": "/user-id"
#   },
#   "size": {
#    "description": "The size in bytes of the data object",
#    "type", "integer"
#   },
#   "type": {
#    "description": "The file type of the data object",
#    "type": "string"
#   }
#  },
#  "required": [ "author", "entity", "path", "size" ]
# }
#
## Data Object Opened
#
# Whenever a data object is opened for either reading or writing, the following
# message is published.
#
# topic: data-object.open
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/data-object/open",
#  "title": "data-object.open",
#  "description": "The message published whenever a data object is opened",
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the data object was modified",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description": "The UUID of the data object",
#    "type": "string"
#   },
#   "path": {
#    "description": "The absolute logical path to the data object",
#    "type": "string"
#   },
#   "size": {
#    "description": "The size in bytes of the data object",
#    "type", "integer"
#   },
#   "timestamp": {
#    "description": "The time the data object was opened in the form YYYY-MM-DD.hh:mm:ss",
#    "type": "string"
#   }
#  },
#  "required": [ "author", "entity", "path", "size", "timestamp" ]
# }
#
## Data Object Removed
#
# Whenever a data object is removed, the following message is published.
#
# topic: data-object.rm
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/data-object/rm",
#  "title": "data-object.rm",
#  "description": "The message published whenever a data object is removed",
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the data object was deleted",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description": "The UUID of the data object",
#    "type": "string"
#   },
#   "path": {
#    "description": "The data object's previous absolute logical path",
#    "type": "string"
#   }
#  },
#  "required": [ "author", "entity", "path" ]
# }
#
## Data Object ACL Change
#
# Whenever a data object's ACL is changed, i.e., a permission is added,
# modified, or removed, the following message is published.
#
# topic: data-object.acl.mod
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/data-object/acl/mod",
#  "title": "data-object.acl.mod",
#  "description":
#   "The message published whenever a data object's ACL is changed"
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the ACL was modified",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description": "The UUID of the data object",
#    "type": "string"
#   },
#   "permission": {
#    "description":
#     "The permission level being set, one of: 'null', 'read', 'write', or 'own'",
#    "type": "string"
#   },
#   "user": {
#    "description": "The user receiving the permission",
#    "$ref": "/user-id"
#   }
#  },
#  "required": [ "author", "entity", "permission", "user" ]
# }
#
## Data Object AVU Added
#
# Whenever an AVU is added to a data object, the following message is published.
#
# topic: data-object.metadata.add
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/data-object/metadata/add",
#  "title": "data-object.metadata.add",
#  "description":
#   "The message published whenever an AVU is added to a data object"
#  "$ref": "/avu/simple-change"
# }
#
## Data Object AVU Administratively Added
#
# Whenever an AVU is added to a data object administratively, the following
# message is published.
#
# topic: data-object.metadata.adda
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/data-object/metadata/adda",
#  "title": "data-object.metadata.adda",
#  "description":
#   "The message published whenever an AVU is administratively added to a data object"
#  "$ref": "/avu/simple-change"
# }
#
## Data Object AVU Added by Wildcard
#
# Whenever an AVU is added to multiple data objects whose names match a wildcard
# pattern, the following message is published.
#
# topic: data-object.metadata.addw
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/data-object/metadata/addw",
#  "title": "data-object.metadata.addw",
#  "description":
#   "The message published when an AVU is added to one or more iRODS data objects using a wildcard matching their names",
#  "type": object,
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the AVU was added",
#    "$ref": "/user-id"
#   },
#   "pattern": {
#    "description":
#     "The PostgreSQL wildcard pattern used to match the names of the data objects receiving the AVU",
#    "type": "string"
#   },
#   "metadatum: {
#    "description": "The AVU",
#    "$ref": "/avu"
#   }
#  },
#  "required": [ "author", "pattern", "metadatum" ]
# }
#
## Data Object AVU Copied
#
# Whenever an AVU is copied to a data object, the following message is
# published.
#
# topic: data object.metadata.cp
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/data-object/metadata/cp",
#  "title": "data-object.metadata.cp",
#  "description":
#   "The message published whenever an AVU is copied to a data-object".
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the AVUs were copied",
#    "$ref": "/user-id"
#   },
#   "source": {
#    "description": "The name or path of the source providing the AVUs",
#    "type": "string"
#   },
#   "source-type": {
#    "description":
#     "the type of the source: collection, data-object, resource, or user",
#    "type": "string"
#   },
#   "destination": {
#    "description": "The logical path to the data object receiving the AVUs",
#    "type": "string"
#   }
#  },
#  "required": [ "author", "source", "source-type", "destination" ]
# }
#
## Data Object AVU Modified
#
# Whenever a data object's AVU is modified, the following message is published.
#
# topic: data-object.metadata.mod
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/data-object/metadata/mod",
#  "title": "data-object.metadata.mod",
#  "description":
#   "The message published whenever a data object's AVU is modified".
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the AVU was modified",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description": "The UUID of the data object",
#    "type": "string"
#   },
#   "old-metadatum": {
#    "description": "the AVU before it was modified",
#    "$ref": "/avu"
#   },
#   "new-metadatum": {
#    "description": "the AVU after it was modified",
#    "$ref": "/avu"
#   }
#  },
#  "required": [ "author", "entity", "old-metadatum", "new-metadatum" ]
# }
#
## Data Object AVU Removed
#
# Whenever a data object's AVU is removed, the following message is published.
#
# topic: data-object.metadata.rm
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/data-object/metadata/rm",
#  "title": "data-object.metadata.rm",
#  "description":
#   "The message published whenever a data object's AVU is removed"
#  "$ref": "/avu/simple-change"
# }
#
## Data Object AVUs Removed by Wildcard
#
# Whenever a data object's AVUs are removed by wildcard, the following message
# is published.
#
# topic: data-object.metadata.rmw
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/data-object/metadata/rmw",
#  "title": "data-object.metadata.rmw",
#  "description":
#   "The message published whenever a data-object's AVUs are removed by wildcard"
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the AVUs were removed",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description": "The UUID of the data object",
#    "type": "string"
#   },
#   "attribute-pattern": {
#    "description": "the wildcard pattern that matched the attributes",
#    "type": "string"
#   },
#   "value-pattern": {
#    "description": "the wildcard pattern that matched the values",
#    "type": "string"
#   },
#   "unit-pattern": {
#    "description": "the wildcard pattern that matched the units",
#    "type": "string"
#   }
#  },
#  "required": [ "author", "entity" ]
# }
#
## Data Object AVU Set
#
# Whenever an AVU is set on a data object, the following message is published.
#
# topic: data object.metadata.adda
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/data-object/metadata/set",
#  "title": "data-object.metadata.set",
#  "description":
#   "The message published whenever an AVU is set on a data object"
#  "$ref": "/avu/simple-change"
# }
#
## Data Object System Metadata Modified
#
# Whenever a data object's system metadata is modified, the following message is
# published.
#
# topic: data object.sys-metadata.mod
# body:
# {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "$id": "/data-object/sys-metadata/mod",
#  "title": "data-object.sys-metadata.mod",
#  "description":
#   "The message published whenever a data object's system metadata is modified"
#  "type": "object",
#  "properties": {
#   "author": {
#    "description":
#     "The user authenticated the session where the metadata is modified",
#    "$ref": "/user-id"
#   },
#   "entity": {
#    "description": "The UUID of the data object",
#    "type": "string"
#   }
#  },
#  "required": [ "author", "entity" ]
# }
#
#
#### CHECKSUM
#
# Every data object receives an MD5 checksum on upload. This happens
# asynchronously.
#
#
#### NUMBER OF RULE ENGINE PROCESSES
#
# The number of rule engine processes is configured using the rule base constant
# `cyverse_MAX_NUM_RE_PROCS`.
#
#
#### PROTECTED AVUS
#
# Any AVU attribute that begins with `ipc` can only be modified by rodsadmin
# users.
#
#
#### RESOURCE SERVER STORAGE TRACKING
#
# Available storage on a unixfilesystem resource is updated in the following
# cases.
#
#    * whenever a replica is added to it using parallel transfer
#    * whenever a replica is created by a copy operation
#
#
#### RODSADMIN GROUP
#
# The `rodsadmin` group receives own permission on all collections and data
# objects.
#
#
#### TLS POLICY
#
# Connections are not allowed to use TLS.
#
#
#### UUID
#
# Whenever a collection or data object is created, it receives a type 1 UUID.
#
#
# © 2021 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

@include 'cyverse_json'

#
# LISTS
#

_cyverse_logic_contains(*Item, *List) =
	if size(*List) == 0 then false
	else if *Item == hd(*List) then true
	else _cyverse_logic_contains(*Item, tl(*List))


#
# ICAT IDS
#

_cyverse_logic_getCollId(*Path) =
	let *id = -1 in
	let *path = str(*Path) in
	let *_ = foreach (*rec in SELECT COLL_ID WHERE COLL_NAME = *path) { *id = int(*rec.COLL_ID) } in
	*id

_cyverse_logic_getDataObjId(*Path) =
	let *collPath = '' in
	let *dataObjName = '' in
	let *_ = msiSplitPath(str(*Path), *collPath, *dataObjName) in
	let *id = -1 in
	let *_ = foreach ( *rec in
			SELECT DATA_ID WHERE COLL_NAME = *collPath AND DATA_NAME = *dataObjName
		) { *id = int(*rec.DATA_ID) } in
	*id

_cyverse_logic_getId(*Path) =
	if cyverse_isColl(cyverse_getEntityType(*Path)) then _cyverse_logic_getCollId(*Path)
	else _cyverse_logic_getDataObjId(*Path)


#
# USER INFO
#

_cyverse_logic_isAdm(*Username, *UserZone) =
	let *admin = false in
	let *_ = foreach ( *rec in
			SELECT USER_ID
			WHERE USER_NAME = *Username AND USER_ZONE = *UserZone AND USER_TYPE = 'rodsadmin'
		) { *admin = true } in
	*admin


#
# AVUS
#

# Gets the new AVU setting from a list of candidates. New AVU settings are
# passed in an arbitrary order and the type of AVU setting is identified by a
# prefix. This function looks for values matching the given prefix. If multiple
# matching values are found then the last one wins.
#
_cyverse_logic_getNewAVUSetting(*Orig, *Prefix, *Candidates) =
	if size(*Candidates) == 0 then *Orig
	else
		let *candidate = hd(*Candidates) in
		if cyverse_startsWith(*candidate, *Prefix)
		then substr(*candidate, 2, strlen(*candidate))
		else _cyverse_logic_getNewAVUSetting(*Orig, *Prefix, tl(*Candidates))


#
# CHECKSUMS
#

# This compute the checksum of of a given replica of a given data object. This
# rule doesn't fail if the replica to checksum no longer exists.
#
# Parameters:
#  DataObjId  the DB Id of the data object of interest
#  ReplNum    the replica number that will be check summed
#
cyverse_logic_chksumRepl(*DataObjId, *ReplNum) {
	*dataObjPath = '';
	foreach (*rec in
		SELECT COLL_NAME, DATA_NAME WHERE DATA_ID = '*DataObjId' AND DATA_REPL_NUM = '*ReplNum'
	) {
		*dataObjPath = *rec.COLL_NAME ++ '/' ++ *rec.DATA_NAME;
	}

	if (*dataObjPath != '') {
		msiAddKeyValToMspStr('forceChksum', '', *opts);
		msiAddKeyValToMspStr('replNum', str(*ReplNum), *opts);
		msiDataObjChksum(*dataObjPath, *opts, *_);
	}
}

# Using an API PEP's data object operation input map, it determines if data
# object(s) will need a checksum.
#
#_cyverse_logic_needsChecksum : `KeyValPair_PI` -> boolean
_cyverse_logic_needsChecksum(*DataObjOpInp) =
	!cyverse_hasKey(*DataObjOpInp, 'regChksum') && !cyverse_hasKey(*DataObjOpInp, 'verifyChksum')

# Schedule a task for computing the checksum of a given replica of a given data object
_cyverse_logic_schedChksumRepl(*DataObjPath, *ReplNum) {
	*dataObjId = _cyverse_logic_getDataObjId(*DataObjPath)

	delay(
		'<INST_NAME>irods_rule_engine_plugin-irods_rule_language-instance</INST_NAME>' ++
		'<PLUSET>0s</PLUSET>' ++
		'<EF>0s REPEAT 0 TIMES</EF>'
	) {cyverse_logic_chksumRepl(*dataObjId, *ReplNum)}
}

# Ensures that the replica of a given data object on a given storage resource
# has a checksum
#
# Parameters:
#  *DataPath  (string) the absolute path to the data object
#  *RescHier  (string) the resource hierarchy of the storage resource
#
_cyverse_logic_ensureReplicaChecksum(*DataPath, *RescHier) {
	msiSplitPath(*DataPath, *collPath, *dataName);

	foreach ( *rec in
		SELECT DATA_REPL_NUM
		WHERE COLL_NAME == *collPath AND DATA_NAME == *dataName AND DATA_RESC_HIER == *RescHier
	) {
		_cyverse_logic_schedChksumRepl(*DataPath, *rec.DATA_REPL_NUM);
	}
}


#
# UUIDS
#

_cyverse_logic_UUID_ATTR = 'ipc_UUID'

# Assign a UUID to a given collection or data object.
_cyverse_logic_assignUUID(*EntityType, *EntityPath, *Uuid, *ClientName, *ClientZone) {
	*status = 0;

	if (_cyverse_logic_isAdm(*ClientName, *ClientZone)) {
		*path = str(*EntityPath);
		*status = errormsg(
			msiModAVUMetadata(*EntityType, *path, 'set', _cyverse_logic_UUID_ATTR, *Uuid, ''), *msg );

		if (*status != 0) {
			writeLine('serverLog', "DS: Failed to assign UUID to *path (*msg)");
			fail;
		}
	} else {
		cyverse_setProtectedAVU(*EntityPath, _cyverse_logic_UUID_ATTR, *Uuid, '');
	}
}

_cyverse_logic_genUUID() =
	let *uuid = '' in
	let *_ = if (errorcode(msiExecCmd('generate-uuid', '', '', '', '', *genResp)) == 0) {
			msiGetStdoutInExecCmdOut(*genResp, *uuid);
			*uuid = trimr(*uuid, "\n");
		} in
	*uuid

# Looks up the UUID of a collection from its path.
_cyverse_logic_getCollUUID(*CollPath) =
	let *coll = str(*CollPath) in
	let *uuid = '' in
	let *attr = _cyverse_logic_UUID_ATTR in
	let *_ = foreach ( *record in
			SELECT META_COLL_ATTR_VALUE WHERE COLL_NAME == *coll AND META_COLL_ATTR_NAME == *attr
		) { *uuid = *record.META_COLL_ATTR_VALUE; } in
	*uuid

# Looks up the UUID of a data object from its path.
_cyverse_logic_getDataObjUUID(*DataObjPath) =
	let *parentColl = '' in
	let *dataName = '' in
	let *_ = msiSplitPath(str(*DataObjPath), *parentColl, *dataName) in
	let *uuid = '' in
	let *attr = _cyverse_logic_UUID_ATTR in
	let *_ = foreach ( *record in
			SELECT META_DATA_ATTR_VALUE
			WHERE COLL_NAME == *parentColl AND DATA_NAME == *dataName AND META_DATA_ATTR_NAME == *attr
		) { *uuid = *record.META_DATA_ATTR_VALUE; } in
	*uuid

# Looks up the UUID for a given type of entity (collection or data object)
_cyverse_logic_getUUID(*EntityType, *EntityPath) =
	if cyverse_isColl(*EntityType) then _cyverse_logic_getCollUUID(*EntityPath)
	else if cyverse_isDataObj(*EntityType) then _cyverse_logic_getDataObjUUID(*EntityPath)
	else ''

_cyverse_logic_ensureUUID(*EntityType, *EntityPath, *ClientName, *ClientZone, *UUID) {
	*uuid = _cyverse_logic_getUUID(*EntityType, *EntityPath);
	if (*uuid == '') {
		*uuid = _cyverse_logic_genUUID();
		if (*uuid == '') {
			writeLine('serverLog', 'Failed to generate UUID for ' ++ str(*EntityPath));
			fail;
		}
		_cyverse_logic_assignUUID(*EntityType, *EntityPath, *uuid, *ClientName, *ClientZone);
	}
	*UUID = *uuid;
}


#
# ACTION TRACKING
#

_cyverse_logic_mkActionKey(*EntityId) = str(*EntityId) ++ '-ROOT_ACTION'

_cyverse_logic_isCurrentAction(*EntityId, *Action) =
	let *key = _cyverse_logic_mkActionKey(*EntityId) in
	if errorcode(temporaryStorage."*key") != 0 then false else temporaryStorage."*key" == *Action

_cyverse_logic_registerAction(*EntityId, *Action) {
	*key = _cyverse_logic_mkActionKey(*EntityId);
	if (if errorcode(temporaryStorage."*key") != 0 then true else temporaryStorage."*key" == '') {
		temporaryStorage."*key" = *Action;
	}
}

_cyverse_logic_unregisterAction(*EntityId, *Action) {
	*key = _cyverse_logic_mkActionKey(*EntityId);
	if (
		if errorcode(temporaryStorage."*key") != 0 then false else temporaryStorage."*key" == *Action
	) {
		temporaryStorage."*key" = '';
	}
}


#
# AMQP MESSAGE PUBLISHING
#

_cyverse_logic_COLL_MSG_TYPE = 'collection'
_cyverse_logic_DATA_OBJ_MSG_TYPE = 'data-object'
_cyverse_logic_RESC_MSG_TYPE = 'resource'
_cyverse_logic_USER_MSG_TYPE = 'user'

_cyverse_logic_getMsgType(*EntityType) =
	if cyverse_isColl(*EntityType) then _cyverse_logic_COLL_MSG_TYPE
	else if cyverse_isDataObj(*EntityType) then _cyverse_logic_DATA_OBJ_MSG_TYPE
	else if cyverse_isResc(*EntityType) then _cyverse_logic_RESC_MSG_TYPE
	else if cyverse_isUser(*EntityType) then _cyverse_logic_USER_MSG_TYPE
	else ''

_cyverse_logic_mkAVUObj(*Attr, *Val, *Unit) =
	cyverse_json_obj(list(
		('attribute', cyverse_json_str(*Attr)),
		('value', cyverse_json_str(*Val)),
		('unit', cyverse_json_str(*Unit)) ))

_cyverse_logic_mkUserObj: string * string -> cyverse_json_val
_cyverse_logic_mkUserObj(*Name, *Zone) =
	cyverse_json_obj(list(('name', cyverse_json_str(*Name)), ('zone', cyverse_json_str(*Zone))))

_cyverse_logic_mkAuthorField: string * string -> (string * cyverse_json_val)
_cyverse_logic_mkAuthorField(*Name, *Zone) = ('author', _cyverse_logic_mkUserObj(*Name, *Zone))

_cyverse_logic_mkEntityField(*Uuid) = ('entity', cyverse_json_str(*Uuid))

_cyverse_logic_mkPathField(*Path) = ('path', cyverse_json_str(str(*Path)))

_cyverse_logic_resolveMsgEntityId(*EntityType, *EntityName, *ClientName, *ClientZone, *ID) {
	if (cyverse_isFSType(*EntityType)) {
		_cyverse_logic_ensureUUID(*EntityType, str(*EntityName), *ClientName, *ClientZone, *ID);
	} else {
		*ID = *EntityName;
	}
}

# sends a message to a given AMQP topic exchange
#
# Parameters:
# *Topic (string) the topic of the message
# *Msg (string) the message to send
#
# Remote Execution:
# It executes the amqp-topic-send command script on the rule engine host
#
_cyverse_logic_sendMsg(*Topic, *Msg) {
	*exchangeArg = execCmdArg(cyverse_AMQP_EXCHANGE);
	*topicArg = execCmdArg(*Topic);
	*msgArg = execCmdArg(cyverse_json_serialize(*Msg));
	*argStr = '*exchangeArg *topicArg *msgArg';

	*status = errormsg(msiExecCmd('amqp-topic-send', *argStr, cyverse_RE_HOST, '', 0, *out), *msg);

	if (*status < 0) {
		msiGetStderrInExecCmdOut(*out, *err);
		writeLine("serverLog", "Failed to send AMQP message: *msg");
		writeLine("serverLog", *err);
	}

	0;
}

_cyverse_logic_sendAVUAddWildcard(
	*DataObjPattern, *AttrName, *AttrVal, *AttrUnit, *AuthorName, *AuthorZone
) {
	*msg = cyverse_json_obj(list(
		_cyverse_logic_mkAuthorField(*AuthorName, *AuthorZone),
		('pattern', cyverse_json_str(*DataObjPattern)),
		('metadatum', _cyverse_logic_mkAVUObj(*AttrName, *AttrVal, *AttrUnit)) ));

	_cyverse_logic_sendMsg(_cyverse_logic_DATA_OBJ_MSG_TYPE ++ '.metadata.addw', *msg);
}

_cyverse_logic_sendAVUCp(*SrcType, *Src, *TgtType, *Tgt, *AuthorName, *AuthorZone) {
	*msg = cyverse_json_obj(list(
		_cyverse_logic_mkAuthorField(*AuthorName, *AuthorZone),
		('source', cyverse_json_str(*Src)),
		('source-type', cyverse_json_str(_cyverse_logic_getMsgType(*SrcType))),
		('destination', cyverse_json_str(*Tgt)) ));

	_cyverse_logic_sendMsg(_cyverse_logic_getMsgType(*TgtType) ++ '.metadata.cp', *msg);
}

_cyverse_logic_sendAVUMod(
	*EntityType,
	*Entity,
	*OldName,
	*OldVal,
	*OldUnit,
	*NewName,
	*NewVal,
	*NewUnit,
	*AuthorName,
	*AuthorZone
) {
	*msg = cyverse_json_obj(list(
		_cyverse_logic_mkAuthorField(*AuthorName, *AuthorZone),
		_cyverse_logic_mkEntityField(*Entity),
		('old-metadatum', _cyverse_logic_mkAVUObj(*OldName, *OldVal, *OldUnit)),
		('new-metadatum', _cyverse_logic_mkAVUObj(*NewName, *NewVal, *NewUnit)) ) );

	_cyverse_logic_sendMsg(_cyverse_logic_getMsgType(*EntityType) ++ '.metadata.mod', *msg);
}

_cyverse_logic_sendAVURmWildcard(
	*EntityType, *Entity, *AttrPat, *ValPat, *UnitPat, *AuthorName, *AuthorZone
) {
	*msg = cyverse_json_obj(list(
		_cyverse_logic_mkAuthorField(*AuthorName, *AuthorZone),
		_cyverse_logic_mkEntityField(*Entity),
		('attribute-pattern', cyverse_json_str(*AttrPat)),
		('value-pattern', cyverse_json_str(*ValPat)),
		('unit-pattern', cyverse_json_str(*UnitPat)) ));

	_cyverse_logic_sendMsg(_cyverse_logic_getMsgType(*EntityType) ++ '.metadata.rmw', *msg);
}

_cyverse_logic_sendAVUOp(
	*Op, *EntityType, *Entity, *AttrName, *AttrVal, *AttrUnit, *AuthorName, *AuthorZone
) {
	*msg = cyverse_json_obj(list(
		_cyverse_logic_mkAuthorField(*AuthorName, *AuthorZone),
		_cyverse_logic_mkEntityField(*Entity),
		('metadatum', _cyverse_logic_mkAVUObj(*AttrName, *AttrVal, *AttrUnit)) ));

	_cyverse_logic_sendMsg(_cyverse_logic_getMsgType(*EntityType) ++ '.metadata.' ++ *Op, *msg);
}

_cyverse_logic_sendCollACLMod(
	*Coll, *AccessLvl, *Username, *UserZone, *Recurse, *AuthorName, *AuthorZone
) {
	*msg = cyverse_json_obj(list(
		_cyverse_logic_mkAuthorField(*AuthorName, *AuthorZone),
		_cyverse_logic_mkEntityField(*Coll),
		('recursive', cyverse_json_bool(*Recurse)),
		('permission', cyverse_json_str(*AccessLvl)),
		('user', _cyverse_logic_mkUserObj(*Username, *UserZone)) ));

	_cyverse_logic_sendMsg(_cyverse_logic_COLL_MSG_TYPE ++ '.acl.mod', *msg);
}

_cyverse_logic_sendCollInheritMod(*Coll, *Inherit, *Recurse, *AuthorName, *AuthorZone) {
	*msg = cyverse_json_obj(list(
		_cyverse_logic_mkAuthorField(*AuthorName, *AuthorZone),
		_cyverse_logic_mkEntityField(*Coll),
		('recursive', cyverse_json_bool(*Recurse)),
		('inherit', cyverse_json_bool(*Inherit)) ));

	_cyverse_logic_sendMsg(_cyverse_logic_COLL_MSG_TYPE ++ '.acl.mod', *msg);
}

_cyverse_logic_sendCollAccessMod(
	*Coll, *AccessLvl, *Username, *UserZone, *Recurse, *AuthorName, *AuthorZone
) {
	if (*AccessLvl == 'inherit') {
		_cyverse_logic_sendCollInheritMod(*Coll, true, *Recurse, *AuthorName, *AuthorZone);
	}
	else if (*AccessLvl == 'noinherit') {
		_cyverse_logic_sendCollInheritMod(*Coll, false, *Recurse, *AuthorName, *AuthorZone);
	}
	else {
		_cyverse_logic_sendCollACLMod(
			*Coll, *AccessLvl, *Username, *UserZone, *Recurse, *AuthorName, *AuthorZone );
	}
}

_cyverse_logic_sendCollAdd(*Id, *Path, *AuthorName, *AuthorZone) {
	*msg = cyverse_json_obj(list(
		_cyverse_logic_mkAuthorField(*AuthorName, *AuthorZone),
		_cyverse_logic_mkEntityField(*Id),
		_cyverse_logic_mkPathField(*Path) ));

	_cyverse_logic_sendMsg(_cyverse_logic_COLL_MSG_TYPE ++ '.add', *msg);
}

_cyverse_logic_sendDataObjACLMod(
	*DataObj, *AccessLvl, *Username, *UserZone, *AuthorName, *AuthorZone
) {
	*msg = cyverse_json_obj(list(
		_cyverse_logic_mkAuthorField(*AuthorName, *AuthorZone),
		_cyverse_logic_mkEntityField(*DataObj),
		('permission', cyverse_json_str(*AccessLvl)),
		('user', _cyverse_logic_mkUserObj(*Username, *UserZone)) ));

	_cyverse_logic_sendMsg(_cyverse_logic_DATA_OBJ_MSG_TYPE ++ '.acl.mod', *msg);
}

_cyverse_logic_sendDataObjAdd(
	*Id, *Path, *OwnerName, *OwnerZone, *Size, *Type, *AuthorName, *AuthorZone
) {
	*msg = cyverse_json_obj(list(
		_cyverse_logic_mkAuthorField(*AuthorName, *AuthorZone),
		_cyverse_logic_mkEntityField(*Id),
		_cyverse_logic_mkPathField(*Path),
		('creator', _cyverse_logic_mkUserObj(*OwnerName, *OwnerZone)),
		('size', cyverse_json_num(*Size)),
		('type', cyverse_json_str(*Type)) ));

	_cyverse_logic_sendMsg(_cyverse_logic_DATA_OBJ_MSG_TYPE ++ '.add', *msg);
}

# Publish a data-object.sys-metadata.mod message to AMQP exchange
_cyverse_logic_sendDataObjMetadataMod(*Id, *AuthorName, *AuthorZone) {
	*msg = cyverse_json_obj(list(
		_cyverse_logic_mkAuthorField(*AuthorName, *AuthorZone),
		_cyverse_logic_mkEntityField(*Id) ));

	_cyverse_logic_sendMsg(_cyverse_logic_DATA_OBJ_MSG_TYPE ++ '.sys-metadata.mod', *msg);
}

# Publish a data-object.mod message to AMQP exchange
_cyverse_logic_sendDataObjMod(
	*Id, *Path, *OwnerName, *OwnerZone, *Size, *Type, *AuthorName, *AuthorZone
) {
	*msg = cyverse_json_obj(list(
		_cyverse_logic_mkAuthorField(*AuthorName, *AuthorZone),
		_cyverse_logic_mkEntityField(*Id),
		('creator', _cyverse_logic_mkUserObj(*OwnerName, *OwnerZone)),
		('size', cyverse_json_num(*Size)),
		('type', cyverse_json_str(*Type)) ));

	_cyverse_logic_sendMsg(_cyverse_logic_DATA_OBJ_MSG_TYPE ++ '.mod', *msg);
}

_cyverse_logic_sendDataObjOpen(*Id, *Path, *Size, *AuthorName, *AuthorZone) {
	msiGetSystemTime(*timestamp, 'human');

	*msg = cyverse_json_obj(list(
		_cyverse_logic_mkAuthorField(*AuthorName, *AuthorZone),
		_cyverse_logic_mkEntityField(*Id),
		_cyverse_logic_mkPathField(*Path),
		('size', cyverse_json_num(*Size)),
		('timestamp', cyverse_json_str(*timestamp)) ));

	_cyverse_logic_sendMsg(_cyverse_logic_DATA_OBJ_MSG_TYPE ++ '.open', *msg);
}

_cyverse_logic_sendEntityMv(*Type, *Id, *OldPath, *NewPath, *AuthorName, *AuthorZone) {
	*msgType = _cyverse_logic_getMsgType(*Type);

	if (*msgType == '') {
		writeLine('serverLog', 'Failed to determine message type for entity type "*Type"');
		-1105000;  # INVALID_OBJECT_TYPE
	} else {
		*msg = cyverse_json_obj(list(
			_cyverse_logic_mkAuthorField(*AuthorName, *AuthorZone),
			_cyverse_logic_mkEntityField(*Id),
			('old-path', cyverse_json_str(str(*OldPath))),
			('new-path', cyverse_json_str(str(*NewPath))) ));

		_cyverse_logic_sendMsg(*msgType ++ '.mv', *msg);
	}
}

_cyverse_logic_sendEntityRm(*Type, *Id, *Path, *AuthorName, *AuthorZone) {
	*msg = cyverse_json_obj(list(
		_cyverse_logic_mkAuthorField(*AuthorName, *AuthorZone),
		_cyverse_logic_mkEntityField(*Id),
		_cyverse_logic_mkPathField(*Path) ));

	_cyverse_logic_sendMsg(_cyverse_logic_getMsgType(*Type) ++ '.rm', *msg);
}

# Determine the size and type of a data object, and owner
#
# _cyverse_logic_retrieveDataInfo : string -> `KeyValPair_PI`
_cyverse_logic_retrieveDataInfo(*Path) =
	let *info.'size' = '-1' in
	let *info.'type' = '' in
	let *info.ownerName = '' in
	let *info.ownerZone = '' in
	let *collPath = '' in
	let *dataName = '' in
	let *_ = msiSplitPath(*Path, *collPath, *dataName) in
	let *_ = foreach( *rec in
			SELECT DATA_SIZE, DATA_TYPE_NAME, DATA_OWNER_NAME, DATA_OWNER_ZONE
			WHERE COLL_NAME == *collPath AND DATA_NAME == *dataName AND DATA_REPL_STATUS == '1'
		) {
			*info.'size' = *rec.DATA_SIZE;
			*info.'type' = *rec.DATA_TYPE_NAME;
			*info.ownerName = *rec.DATA_OWNER_NAME;
			*info.ownerZone = *rec.DATA_OWNER_ZONE;
		} in
	*info

# Publishes a message indicating that a data object was created.
#
_cyverse_logic_notifyDataObjCreated(*Path, *AuthorName, *AuthorZone) {
	*id = _cyverse_logic_getUUID(cyverse_DATA_OBJ, *Path);

	if (*id != '') {
		*info = _cyverse_logic_retrieveDataInfo(*Path);

		_cyverse_logic_sendDataObjAdd(
			*id,
			*Path,
			*info.ownerName,
			*info.ownerZone,
			double(*info.'size'),
			*info.'type',
			*AuthorName,
			*AuthorZone );
	}
}

# Publishes a message indicating that a data object was created.
#
# _cyverse_logic_notifyDataObjMod : string * string * string -> void
_cyverse_logic_notifyDataObjMod(*Path, *AuthorName, *AuthorZone) {
	*id = _cyverse_logic_getUUID(cyverse_DATA_OBJ, *Path);

	if (*id != '') {
		*info = _cyverse_logic_retrieveDataInfo(*Path);

		_cyverse_logic_sendDataObjMod(
			*AuthorName,
			*AuthorZone,
			*id,
			*Path,
			*info.ownerName,
			*info.ownerZone,
			double(*info.'size'),
			*info.'type' );
	}
}


#
# PROTECTED AVUS
#

# Indicates whether or not an AVU is protected
_cyverse_logic_isAVUProtected(*Attr) = cyverse_startsWith(*Attr, 'ipc')

# Indicates whether the protected AVU is ipc_UUID, which has some additional safeguards
_cyverse_logic_isAVUProtectedUUID(*Attr) = *Attr == _cyverse_logic_UUID_ATTR

# Verifies that an attribute can be modified. If it can't it fails and sends an
# error message to the caller.
_cyverse_logic_ensureAVUEditable(*EditorName, *EditorZone, *Attr, *Val, *Unit) {
	if (_cyverse_logic_isAVUProtected(*Attr) && !_cyverse_logic_isAdm(*EditorName, *EditorZone)) {
		cut;
		failmsg(-830000, 'CYVERSE ERROR: attempt to alter protected AVU <*Attr, *Val, *Unit>');
	}
}

# If an AVU is allowed, it sets the AVU to the given item
_cyverse_logic_setAVUToCopy(*EntityType, *EntityName, *Attr, *Val, *Unit, *UserName, *RodsZone) {
	if (
		!_cyverse_logic_isAVUProtected(*Attr)
		|| (_cyverse_logic_isAdm(*UserName, *RodsZone) && !_cyverse_logic_isAVUProtectedUUID(*Attr))
	) {
		msiModAVUMetadata(*EntityType, *EntityName, 'set', *Attr, *Val, *Unit);
	} else {
		*msg = 'CYVERSE NOTIFICATION: Cannot copy AVU <*Attr, *Val, *Unit>, either not having admin'
			++ ' permissions or it is a protected UUID';

		writeLine('stdout', *msg);
	}
}

# Copies the AVUs from a given collection to the given item.
_cyverse_logic_cpCollAVUs(*CollPath, *TargetType, *TargetName, *UserName, *RodsZone) {
	*path = str(*CollPath);
	foreach (*avu in
		SELECT META_COLL_ATTR_NAME, META_COLL_ATTR_VALUE, META_COLL_ATTR_UNITS
		WHERE COLL_NAME == *path
	) {
		_cyverse_logic_setAVUToCopy(
			*TargetType,
			*TargetName,
			*avu.META_COLL_ATTR_NAME,
			*avu.META_COLL_ATTR_VALUE,
			*avu.META_COLL_ATTR_UNITS,
			*UserName,
			*RodsZone );
	}
}

# Copies the AVUs from a given data object to the given item.
_cyverse_logic_cpDataObjAVUs(*DataObjPath, *TargetType, *TargetName, *UserName, *RodsZone) {
	msiSplitPath(str(*DataObjPath), *collPath, *dataObjName);

	foreach (*avu in
		SELECT META_DATA_ATTR_NAME, META_DATA_ATTR_VALUE, META_DATA_ATTR_UNITS
		WHERE COLL_NAME == *collPath AND DATA_NAME == *dataObjName
	) {
		_cyverse_logic_setAVUToCopy(
			*TargetType,
			*TargetName,
			*avu.META_DATA_ATTR_NAME,
			*avu.META_DATA_ATTR_VALUE,
			*avu.META_DATA_ATTR_UNITS,
			*UserName,
			*RodsZone );
	}
}

# Copies the AVUs from a given resource to the given item.
_cyverse_logic_cpRescAVUs(*RescName, *TargetType, *TargetName, *UserName, *RodsZone) {
	foreach (*avu in
		SELECT META_RESC_ATTR_NAME, META_RESC_ATTR_VALUE, META_RESC_ATTR_UNITS
		WHERE RESC_NAME == *RescName
	) {
		_cyverse_logic_setAVUToCopy(
			*TargetType,
			*TargetName,
			*avu.META_RESC_ATTR_NAME,
			*avu.META_RESC_ATTR_VALUE,
			*avu.META_RESC_ATTR_UNITS,
			*UserName,
			*RodsZone );
	}
}

# Copies the AVUs from a given user to the given item.
_cyverse_logic_cpUserAVUs(*Username, *TargetType, *TargetName, *UserName, *RodsZone) {
	*nameParts = split(*Username, '#');
	*query =
		if size(*nameParts) == 2 then
		   # A zone was provided.
			let *name = elem(*nameParts, 0) in
			let *zone = elem(*nameParts, 1) in
			SELECT META_USER_ATTR_NAME, META_USER_ATTR_VALUE, META_USER_ATTR_UNITS
			WHERE USER_NAME == *name AND USER_ZONE == *zone
		else
			SELECT META_USER_ATTR_NAME, META_USER_ATTR_VALUE, META_USER_ATTR_UNITS
			WHERE USER_NAME == *Username;
	foreach (*avu in *query) {
		_cyverse_logic_setAVUToCopy(
			*TargetType,
			*TargetName,
			*avu.META_USER_ATTR_NAME,
			*avu.META_USER_ATTR_VALUE,
			*avu.META_USER_ATTR_UNITS,
			*UserName,
			*RodsZone );
	}
}


#
# RODSADMIN GROUP PERMISSIONS
#

_cyverse_logic_resolveAdmPerm(*Path) =
	if str(*Path) like regex '/' ++ cyverse_ZONE ++ '(/trash)?/home/.*' then 'own' else 'write'

_cyverse_logic_setAdmPerm(*Path) {
	msiSetACL('default', _cyverse_logic_resolveAdmPerm(*Path), 'rodsadmin', str(*Path));
}


#
# STATIC PEPS
#

# This rule prevents the user from removing rodsadmin's ownership from an ACL
# unless the user is of type rodsadmin.
#
# Parameters:
#  RecurseFlag  (unused)
#  Perm         (string) the permission being granted to *Username, if the value
#               is "null", "read", "write", or "own", enable inheritance if the
#               value is "inherit", or disable inheritance if the value is
#               "noinherit". If the value is prefixed with "admin:", this is an
#               administrative ACL change.
#  Username     (string) the account or group being given *Perm, ignored if
#               *Perm is "inherit" or "noinherit"
#  Zone         (unused)
#  Path         (string) the path to the collection or data object whose ACL is
#               being altered
#
cyverse_logic_acPreProcForModifyAccessControl(*RecurseFlag, *Perm, *Username, *Zone, *Path) {
	if (*Username == 'rodsadmin') {
		if (!(*Perm like 'admin:*') && *Perm != _cyverse_logic_resolveAdmPerm(*Path)) {
			cut;
			failmsg(-830000, 'CYVERSE ERROR: attempt to alter admin user permission.');
		}
	}
}

# This sends a collection or data-object ACL modification message for the
# updated object.
#
# Parameters:
#  RecurseFlag     (string) indicates if the permission change applied
#                  recursively to the contents of a *Path, "1" indicates the
#                  flag was present, and "0" indicates the opposite.
#  Perm            (string) the permission granted to *Username, if the value
#                  was "null", "read", "write", or "own", enabled inheritance if
#                  the value was "inherit", or disabled inheritance if the value
#                  was "noinherit". If the value is prefixed with "admin:", this
#                  is an administrative ACL change.
#  Username        (string) the account or group given *Perm, ignored if *Perm
#                  was "inherit" or "noinherit"
#  UserZone        (string) the zone where *UserName belongs, ignored if *Perm
#                  is "inherit" or "noinherit"
#  Path            (string) the path to the collection or data object whose ACL
#                  was altered
#  ClientUsername  (string) the client user performing the modification
#  ClientZone      (string) the authentication zone for the client user
#
cyverse_logic_acPostProcForModifyAccessControl(
	*RecurseFlag, *Perm, *Username, *UserZone, *Path, *ClientUsername, *ClientZone
) {
	*me = 'cyverse_logic_acPostProcForModifyAccessControl';
	*entityId = _cyverse_logic_getId(*Path);

	if (*entityId >= 0) {
		_cyverse_logic_registerAction(*entityId, *me);

		if (_cyverse_logic_isCurrentAction(*entityId, *me)) {
			*lvl = cyverse_rmPrefix(*Perm, list('admin:'));
			*type = cyverse_getEntityType(*Path);
			*userZone = if *UserZone == '' then cyverse_ZONE else *UserZone;
			*uuid = '';
			_cyverse_logic_ensureUUID(*type, *Path, *ClientUsername, *ClientZone, *uuid);

			if (cyverse_isColl(*type)) {
				_cyverse_logic_sendCollAccessMod(
					*uuid,
					*lvl,
					*Username,
					*userZone,
					bool(*RecurseFlag),
					*ClientUsername,
					*ClientZone );
			} else if (cyverse_isDataObj(*type)) {
				_cyverse_logic_sendDataObjACLMod(
					*uuid, *lvl, *Username, *userZone, *ClientUsername, *ClientZone );
			}

			_cyverse_logic_unregisterAction(*entityId, *me);
		}
	}
}

# This rule checks that AVU being added, set or removed isn't a protected one.
# Only rodsadmin users are allowed to add, remove or update protected AVUs.
#
# Parameters:
#  Opt             (string) the subCommand, one of 'add', 'adda', 'addw', 'rm',
#                  'rmi', 'rmw', or 'set'
#  EntityType      (unused)
#  EntityName      (unused)
#  Attr            (string) the name of the attribute
#  Val             (string) the value of the attribute
#  Unit            (string) the unit of the attribute
#  ClientUsername  (string) the client user performing the modification
#  ClientZone      (string) the authentication zone for the client user
#
cyverse_logic_acPreProcForModifyAVUMetadata(
	*Opt, *EntityType, *EntityName, *Attr, *Val, *Unit, *ClientUsername, *ClientZone
) {
	if (*Opt != 'adda') {
		_cyverse_logic_ensureAVUEditable(*ClientUsername, *ClientZone, *Attr, *Val, *Unit);
	}
}

# This rule checks that AVU being modified isn't a protected one.
#
# Parameters:
#  Opt             (unused)
#  EntityType      (unused)
#  EntityName      (unused)
#  Attr            (string) the attribute name before modification
#  Val             (string) the attribute value before modification
#  Unit            (string) the attribute unit before modification
#  New1            (string) holds an update to the name, value, or unit prefixed
#                  by 'n:', 'v:', or 'u:', respectively
#  New2            (string) either empty or holds an update to the name, value,
#                  or unit prefixed by 'n:', 'v:', or 'u:', respectively
#  New3            (string) either empty or holds an update to the name, value,
#                  or unit prefixed by 'n:', 'v:', or 'u:', respectively
#  ClientUsername  (string) the client user performing the modification
#  ClientZone      (string) the authentication zone for the client user
#
# XXX: Due to a bug in iRODS 4.2.8, when a unitless AVU is modified to have a new attribute name,
#      value, and unit in a single call, the new unit is not passed in.
#
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
	*newArgs = list(*New1, *New2, *New3);

	# Determine the new AVU settings.
	*newAttr = _cyverse_logic_getNewAVUSetting(*Attr, 'n:', *newArgs);
	*newVal = _cyverse_logic_getNewAVUSetting(*Val, 'v:', *newArgs);
	*newUnit = _cyverse_logic_getNewAVUSetting(*Unit, 'u:', *newArgs);

	_cyverse_logic_ensureAVUEditable(*ClientUsername, *ClientZone, *Attr, *Val, *Unit);
	_cyverse_logic_ensureAVUEditable(*ClientUsername, *ClientZone, *newAttr, *newVal, *newUnit);
}

# This rule ensures that only the non-protected AVUs are copied from one item to
# another.
#
# Parameters:
#  Opt             (unused)
#  SrcType         (string) the type of entity whose AVUs are being copied, '-C'
#                  for collection, '-d' for data object, '-R' for resource, or
#                  '-u' for user
#  TgtType         (string) the type of entity receiving the AVUs, '-C' for
#                  collection, '-d' for data object, '-R' for resource, or '-u'
#                  for user
#  SrcName         (string) the name of the entity whose AVUs are being copied,
#                  for a collection or data object, this is the entity's
#                  absolute path
#  TgtName         (string) the name of the entity receiving the AVUs, for a
#                  collection or data object, this is the entity's absolute path
#  ClientUsername  (string) the client user performing the modification
#  ClientZone      (string) the authentication zone for the client user
#
cyverse_logic_acPreProcForModifyAVUMetadata(
	*Opt, *SrcType, *TgtType, *SrcName, *TgtName, *ClientUsername, *ClientZone
) {
	if (cyverse_isColl(*SrcType)) {
		_cyverse_logic_cpCollAVUs(*SrcName, *TgtType, *TgtName, *ClientUsername, *ClientZone);
	} else if (cyverse_isDataObj(*SrcType)) {
		_cyverse_logic_cpDataObjAVUs(*SrcName, *TgtType, *TgtName, *ClientUsername, *ClientZone);
	} else if (cyverse_isResc(*SrcType)) {
		_cyverse_logic_cpRescAVUs(*SrcName, *TgtType, *TgtName, *ClientUsername, *ClientZone);
	} else if (cyverse_isUser(*SrcType)) {
		_cyverse_logic_cpUserAVUs(*SrcName, *TgtType, *TgtName, *ClientUsername, *ClientZone);
	}

	# fail to prevent iRODS from also copying the protected metadata
	cut;
	failmsg(0, 'CYVERSE SUCCESS: Successfully copied the allowed metadata.');
}

# This rule sends one of the AVU metadata set messages, depending on which
# subcommand was used.
#
# Parameters:
#  Opt             (string) the subCommand, one of 'add', 'adda', 'addw', 'rm',
#                  'rmw', 'rmi', or 'set'
#  EntityType      (string) the type of entity whose AVU was modified, '-C' for
#                  collection, '-d' for data object, '-R' for resource, or '-u'
#                  for user
#  EntityName      (string) the name of the entity whose AVU was modified, this
#                  is an absolute path for a collection or data object
#  Attr            (string) the name of the attribute
#  Val             (string) the value of the attribute
#  Unit            (string) the unit of the attribute
#  ClientUsername  (string) the client user performing the modification
#  ClientZone      (string) the authentication zone for the client user
#
cyverse_logic_acPostProcForModifyAVUMetadata(
	*Opt, *EntityType, *EntityName, *Attr, *Val, *Unit, *ClientUsername, *ClientZone
) {
	if (cyverse_isFSType(*EntityType) && *Attr != _cyverse_logic_UUID_ATTR) {
		if (_cyverse_logic_contains(*Opt, list('add', 'adda', 'rm', 'set'))) {
			*uuid = '';
			_cyverse_logic_ensureUUID(*EntityType, *EntityName, *ClientUsername, *ClientZone, *uuid);

			_cyverse_logic_sendAVUOp(
				*Opt, *EntityType, *uuid, *Attr, *Val, *Unit, *ClientUsername, *ClientZone );
		} else if (*Opt == 'addw') {
			_cyverse_logic_sendAVUAddWildcard(
				*EntityName, *Attr, *Val, *Unit, *ClientUsername, *ClientZone );
		} else if (*Opt == 'rmw') {
			*uuid = '';
			_cyverse_logic_ensureUUID(*EntityType, *EntityName, *ClientUsername, *ClientZone, *uuid);

			_cyverse_logic_sendAVURmWildcard(
				*EntityType, *uuid, *Attr, *Val, *Unit, *ClientUsername, *ClientZone );
		}
	}
}

# For a collection or data object, this rule sends a message indicating that an AVU was modified.
#
# Parameters:
#  Opt             (unused)
#  EntityType      (string) the type of entity whose AVU was modified, '-C' for
#                  collection, '-d' for data object, '-R' for resource, or '-u'
#                  for user
#  EntityName      (string) the name of the entity whose AVU was modified, this
#                  is an absolute path for a collection or data object
#  Attr            (string) the attribute name before modification
#  Val             (string) the attribute value before modification
#  Unit            (string) the attribute unit before modification
#  New1            (string) holds the updated name, value, or unit prefixed by
#                  'n:', 'v:', or 'u:', respectively
#  New2            (string) either empty or holds the updated name, value, or
#                  unit prefixed by 'n:', 'v:', or 'u:', respectively
#  New3            (string) either empty or holds the updated name, value, or
#                  unit prefixed by 'n:', 'v:', or 'u:', respectively
#  ClientUsername  (string) the client user performing the modification
#  ClientZone      (string) the authentication zone for the client user
#
# XXX: Due to a bug in iRODS 4.2.8, when a unitless AVU is modified to have a new attribute name,
#      value, and unit in a single call, the new unit is not passed in.
#
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
	if (cyverse_isFSType(*EntityType)) {
		*newArgs = list(*New1, *New2, *New3);
		*uuid = '';
		_cyverse_logic_ensureUUID(*EntityType, *EntityName, *ClientUsername, *ClientZone, *uuid);

		# Determine the new AVU settings.
		*newAttr = _cyverse_logic_getNewAVUSetting(*Attr, 'n:', *newArgs);
		*newVal = _cyverse_logic_getNewAVUSetting(*Val, 'v:', *newArgs);
		*newUnit = _cyverse_logic_getNewAVUSetting(*Unit, 'u:', *newArgs);

		# Send AVU modified message.
		_cyverse_logic_sendAVUMod(
			*EntityType,
			*uuid,
			*Attr,
			*Val,
			*Unit,
			*newAttr,
			*newVal,
			*newUnit,
			*ClientUsername,
			*ClientZone );
	}
}

# This rules sends an AVU metadata copy message when the source and the target are collections or
# data objects. If only the target is a collection or data object, it sends an AVU metadata add
# message for each AVU being copied.
#
# Parameters:
#  Opt             (unused)
#  SrcType         (string) the type of entity whose AVUs were copied, '-C' for
#                  collection, '-d' for data object, '-R' for resource, or '-u'
#                  for user
#  TgtType         (string) the type of entity that received the AVUs, '-C' for
#                  collection, '-d' for data object, '-R' for resource, or '-u'
#                  for user
#  SrcName         (string) the name of the entity whose AVUs were copied, for a
#                  collection or data object, this is the entity's absolute path
#  TgtName         (string) the name of the entity that received the AVUs, for a
#                  collection or data object, this is the entity's absolute path
#  ClientUsername  (string) the client user performing the modification
#  ClientZone      (string) the authentication zone for the client user
#
cyverse_logic_acPostProcForModifyAVUMetadata(
	*Opt, *SrcType, *TgtType, *SrcName, *TgtName, *ClientUsername, *ClientZone
) {
	if (cyverse_isFSType(*TgtType)) {
		*tgt = '';
		_cyverse_logic_resolveMsgEntityId(*TgtType, *TgtName, *ClientUsername, *ClientZone, *tgt);

		if (cyverse_isFSType(*SrcType)) {
			*src = '';
			_cyverse_logic_resolveMsgEntityId(*SrcType, *SrcName, *ClientUsername, *ClientZone, *src);
			_cyverse_logic_sendAVUCp(*SrcType, *src, *TgtType, *tgt, *ClientUsername, *ClientZone);
		} else {
			*uuidAttr = _cyverse_logic_UUID_ATTR;

			if (cyverse_isResc(*SrcType)) {
				foreach( *rec in
					SELECT META_RESC_ATTR_NAME, META_RESC_ATTR_VALUE, META_RESC_ATTR_UNITS
					WHERE RESC_NAME == *SrcName AND META_RESC_ATTR_NAME != *uuidAttr
				) {
					_cyverse_logic_sendAVUOp(
						'add',
						*TgtType,
						*tgt,
						*rec.META_RESC_ATTR_NAME,
						*rec.META_RESC_ATTR_VALUE,
						*rec.META_RESC_ATTR_UNITS,
						*ClientUsername,
						*ClientZone );
				}
			} else {
				foreach( *rec in
					SELECT META_USER_ATTR_NAME, META_USER_ATTR_VALUE, META_USER_ATTR_UNITS
					WHERE USER_NAME == *SrcName AND META_USER_ATTR_NAME != *uuidAttr
				) {
					_cyverse_logic_sendAVUOp(
						'add',
						*TgtType,
						*tgt,
						*rec.META_USER_ATTR_NAME,
						*rec.META_USER_ATTR_VALUE,
						*rec.META_USER_ATTR_UNITS,
						*ClientUsername,
						*ClientZone );
				}
			}
		}
	}
}

# This rule sets the rodsadmin group permission of a collection when a
# collection is created by an administrative means, i.e. iadmin mkuser. It also
# assigns a UUID and pushes a collection.add message into the irods exchange.
#
# Parameters:
#  ParCollPath     (string) the absolute path to the parent of the collection
#                  being created
#  CollName        (string) the name of the collection being created
#  ClientUsername  (string) the client user performing the modification
#  ClientZone      (string) the authentication zone for the client user
#
cyverse_logic_acCreateCollByAdmin(*ParCollPath, *CollName, *ClientUsername, *ClientZone) {
	*coll = *ParCollPath ++ '/' ++ *CollName;
	*perm = _cyverse_logic_resolveAdmPerm(*coll);

	*err = errormsg(msiSetACL('default', 'admin:*perm', 'rodsadmin', *coll), *msg);
	if (*err < 0) {
		writeLine('serverLog', *msg);
	}

	*uuid = '';
	_cyverse_logic_ensureUUID(cyverse_COLL, *coll, *ClientUsername, *ClientZone, *uuid);
	_cyverse_logic_sendCollAdd(*uuid, *coll, *ClientUsername, *ClientZone);
}

# This rule makes the admin owner of any created collection. It also assigns a
# UUID and publishes a collection.add message to the irods exchange. This rule
# is not applied to collections created when a TAR file is expanded. (i.e.
# ibun -x)
#
# Parameters:
#  CollPath        (string) the path to the collection that was created
#  ClientUsername  (string) the client user performing the modification
#  ClientZone      (string) the authentication zone for the client user
#
cyverse_logic_acPostProcForCollCreate(*CollPath, *ClientUsername, *ClientZone) {
	*err = errormsg(_cyverse_logic_setAdmPerm(*CollPath), *msg);
	if (*err < 0) {
		writeLine('serverLog', *msg);
	}

	*uuid = '';
	_cyverse_logic_ensureUUID(cyverse_COLL, *CollPath, *ClientUsername, *ClientZone, *uuid);
	_cyverse_logic_sendCollAdd(*uuid, *CollPath, *ClientUsername, *ClientZone);
}

# This rule pushes a collection.rm message into the irods exchange.
#
# Parameters:
#  ParCollPath     (string) the absolute path to the parent collection of the
#                  collection being deleted
#  CollName        (string) the name of collection being deleted
#  ClientUsername  (string) the client user performing the modification
#  ClientZone      (string) the authentication zone for the client user
#
cyverse_logic_acDeleteCollByAdmin(*ParCollPath, *CollName, *ClientUsername, *ClientZone) {
	*path = *ParCollPath ++ '/' ++ *CollName;
	*uuid = _cyverse_logic_getCollUUID(*path);

	if (*uuid != '') {
		_cyverse_logic_sendEntityRm(cyverse_COLL, *uuid, *path, *ClientUsername, *ClientZone);
	}
}

# This rule pushes a collection.rm message into the irods exchange.
#
# Parameters:
#  ParCollPath     (string) the absolute path to the parent collection of the
#                  collection being deleted
#  CollName        (string) the name of collection being deleted
#  ClientUsername  (string) the client user performing the modification
#  ClientZone      (string) the authentication zone for the client user
#
cyverse_logic_acDeleteCollByAdminIfPresent(*ParCollPath, *CollName, *ClientUsername, *ClientZone) {
	cyverse_logic_acDeleteCollByAdmin(*ParCollPath, *CollName, *ClientUsername, *ClientZone);
}

# This rule stores the name UUID of a collection that is about to be deleted for
# use by cyverse_logic_acPostProcForRmColl.
#
# Parameters:
#  *CollPath  (path) the path to the collection
#
# temporaryStorage:
#  '*CollPath'  writes the UUID here
#
cyverse_logic_acPreprocForRmColl(*CollPath) {
	temporaryStorage.'*CollPath' = _cyverse_logic_getCollUUID(*CollPath);
}

# This rule publishes a removal message for a collection.
#
# Parameters:
#  CollPath        (string) the path to the collection being deleted
#  ClientUsername  (string) the client user performing the modification
#  ClientZone      (string) the authentication zone for the client user
#
# temporaryStorage:
#  '*CollPath'  reads the UUID from here
#
cyverse_logic_acPostProcForRmColl(*CollPath, *ClientUsername, *ClientZone) {
	*uuid = temporaryStorage.'*CollPath';

	if (*uuid != '') {
		_cyverse_logic_sendEntityRm(cyverse_COLL, *uuid, *CollPath, *ClientUsername, *ClientZone);
	}
}

# Refuse SSL connections
#
# Parameters:
#  OUT  (string) "CS_NEG_REFUSE"
#
cyverse_logic_acPreConnect(*OUT) {
	*OUT = 'CS_NEG_REFUSE';
}

# This rule ensures that the storage resource free space is updated when a
# data object is replicated to it.
#
# Parameters:
#  StoreResc  (string) the name of the storage resource where the replica was
#             stored
#
cyverse_logic_acPostProcForDataCopyReceived(*StoreResc) {
	msi_update_unixfilesystem_resource_free_space(*StoreResc);
}

# This rule stores the UUID of a data object that is about to be deleted for use
# by cyverse_logic_acPostProcForDelete.
#
# Parameters:
#  DataPath  (path) the path to the data object being deleted
#
# temporaryStorage:
#  '*DataPath'  writes the UUID here
#
cyverse_logic_acDataDeletePolicy(*DataPath) {
	temporaryStorage.'*DataPath' = _cyverse_logic_getDataObjUUID(*DataPath);
}

# This rule publishes a removal message for a data object.
#
# Parameters:
#  DataPath        (path) the path to the data object being deleted
#  ClientUsername  (string) the client user performing the modification
#  ClientZone      (string) the authentication zone for the client user
#
# temporaryStorage:
#  '*DataPath' reads the UUID from here
#
cyverse_logic_acPostProcForDelete(*DataPath, *ClientUsername, *ClientZone) {
	*uuid = temporaryStorage.'*DataPath';

	if (*uuid != '') {
		_cyverse_logic_sendEntityRm(cyverse_DATA_OBJ, *uuid, *DataPath, *ClientUsername, *ClientZone);
	}
}

# This rule publishes a data object access message.
#
# Parameters:
#  DataPath        (path) the path to the data object being opened
#  DataSize        (double) the size of the data object in bytes
#  ClientUsername  (string) the client user performing the modification
#  ClientZone      (string) the authentication zone for the client user
#
cyverse_logic_acPostProcForOpen(*DataPath, *DataSize, *ClientUsername, *ClientZone) {
	*me = 'cyverse_logic_acPostProcForOpen';
	*id = _cyverse_logic_getDataObjId(*DataPath);

	if (*id >= 0) {
		_cyverse_logic_registerAction(*id, *me);

		if (_cyverse_logic_isCurrentAction(*id, *me)) {
			*uuid = '';

			_cyverse_logic_ensureUUID(
				cyverse_DATA_OBJ, *DataPath, *ClientUsername, *ClientZone, *uuid );

			_cyverse_logic_sendDataObjOpen(*uuid, *DataPath, *DataSize, *ClientUsername, *ClientZone);
			_cyverse_logic_unregisterAction(*id, *me);
		}
	}
}

# This rule schedules a rename entry job for the data object or collection being
# renamed.
#
# Parameters:
#  SrcEntity       (string) the path to the collection or data object prior to
#                  being moved or renamed.
#  DestEntity      (string) the new path
#  ClientUsername  (string) the client user performing the modification
#  ClientZone      (string) the authentication zone for the client user
#
# Error Codes:
#   -1105000 (INVALID_OBJECT_TYPE)  if the type of DestEntity cannot be determined
#
cyverse_logic_acPostProcForObjRename(*SrcEntity, *DestEntity, *ClientUsername, *ClientZone) {
	*type = cyverse_getEntityType(*DestEntity);
	if (*type == '') {
		writeLine('serverLog', 'Cannot determine the type of "*DestEntity"');
		-1105000;
	} else {
		*uuid = '';
		_cyverse_logic_ensureUUID(*type, *DestEntity, *ClientUsername, *ClientZone, *uuid);

		if (*uuid != '') {
			_cyverse_logic_sendEntityMv(
				*type, *uuid, *SrcEntity, *DestEntity, *ClientUsername, *ClientZone );
		}
	}
}

# Whenever a large file is uploaded, recheck the free space on the storage
# resource server where the file was written.
#
# Parameters:
#  StoreResc  (string) the name of the storage resource where the replica was
#             stored
#
cyverse_logic_acPostProcForParallelTransferReceived(*StoreResc) {
	msi_update_unixfilesystem_resource_free_space(*StoreResc);
}


#
# DYNAMIC PEPS
#

# This gives rodsadmin own permission, generates a UUID, publishes a data object
# create message and schedules a checksum computation for a data object.
#
# Parameters:
#  Username     (string) the iRODS account that created the data object
#  Zone         (string) the zone of the username who created the data object
#  DataObjInfo  (`KeyValuePair_PI`) the DATA_OBJ_INFO map for a data object
#               metadata modification or registration event
# XXX - Because of https://github.com/irods/irods/issues/5540
# #
# cyverse_logic_dataObjCreated(*Username, *Zone, *DataObjInfo) {
# 	*me = 'cyverse_logic_dataObjCreated';
# 	*id = int(*DataObjInfo.data_id);
# 	_cyverse_logic_registerAction(*id, *me);
# 	*err = errormsg(_cyverse_logic_setAdmPerm(*DataObjInfo.logical_path), *msg);
# 	if (*err < 0) { writeLine('serverLog', *msg); }
#
# 	*uuid = ''
# 	_cyverse_logic_ensureUUID(
# 		cyverse_DATA_OBJ,
# 		*DataObjInfo.logical_path,
# 		*DataObjInfo.data_owner_name,
# 		*DataObjInfo.data_owner_zone,
# 		*uuid );
# 	_cyverse_logic_unregisterAction(*id, *me);
# }
#  Step         (string) the current step in the transfer process, one of
#               'FULL', 'START', or 'FINISH'
#
cyverse_logic_dataObjCreated(*Username, *Zone, *DataObjInfo, *Step) {
	*me = 'cyverse_logic_dataObjCreated';
	*id = int(*DataObjInfo.data_id);
	_cyverse_logic_registerAction(*id, *me);

	*uuid = '';

	if (*Step != 'FINISH') {
		*err = errormsg(_cyverse_logic_setAdmPerm(*DataObjInfo.logical_path), *msg);
		if (*err < 0) { writeLine('serverLog', *msg); }

		_cyverse_logic_ensureUUID(
			cyverse_DATA_OBJ,
			*DataObjInfo.logical_path,
			*DataObjInfo.data_owner_name,
			*DataObjInfo.data_owner_zone,
			*uuid );
	}

	if (*Step != 'START') {
		if (_cyverse_logic_isCurrentAction(*id, *me)) {
			_cyverse_logic_unregisterAction(*id, *me);
		}
	}
}
# XXX - ^^^

# This ensures that a data object has a UUID and publishes a data object
# system metadata modification message.
#
# Parameters:
#  Username  (string) the iRODS account that modified the data object
#  Zone      (string) the zone of the username who modified the data object
#  Path      (path) the path to the modified data object
#
cyverse_logic_dataObjMetaMod(*Username, *Zone, *Path) {
	*me = 'cyverse_logic_dataObjMetadataMod';
	*id = _cyverse_logic_getDataObjId(*Path);

	if (*id >= 0) {
		_cyverse_logic_registerAction(*id, *me);

		if (_cyverse_logic_isCurrentAction(*id, *me)) {
			*uuid = '';
			_cyverse_logic_ensureUUID(cyverse_DATA_OBJ, *Path, *Username, *Zone, *uuid);
			_cyverse_logic_sendDataObjMetadataMod(*uuid, *Username, *Zone);
			_cyverse_logic_unregisterAction(*id, *me);
		}
	}
}


# BULK_DATA_OBJ_PUT

# CHKSUM ALGORITHM:
#
# If neither *BulkOpInp.regChksum nor *BulkOpInp.verifyChksum exist, calculate
# the checksum of replica on *BulkOpInp.resc_hier for each entry of
# *BulkOpInp.logical_path.
#
# DATA OBJ CREATE AND MOD MSG PUBLISHING ALGORITHM:
#
# If *BulkOpInp.forceFlag is not set, then all data objects are new, so publish
# a data object add message for each one of them. Otherwise, there is no
# difference in the contents of *BulkOpInp between when a data object is created
# and when it is modified. For each data object, if the create time is less than
# the modification time time, publish a data object modification message,
# otherwise publish a data object create message.
#
# *BulkOpInp:
#   https://docs.irods.org/4.2.10/doxygen/group__data__object.html#gafeecbd87f6ba164e8c1d189c42a8c93e
#
# N.B. This can be triggered by `iput -b -r`.
# N.B. `-k` adds `regChksum` to BulkOpInp.
# N.B. `-K` adds `verifyChksum` to BULKOPRINP.
# N.B. Overwriting a replica that has a checksum clears the checksum.
# N.B. `-X` handled transparently
# N.B. large files are not passed through rcBulkDataObjPut
#
cyverse_logic_api_bulk_data_obj_put_post(*Instance, *Comm, *BulkOpInp, *BulkOpInpBBuf) {

	# checksum policy
	if (_cyverse_logic_needsChecksum(*BulkOpInp)) {
		foreach (*key in *BulkOpInp) {
			if (*key like 'logical_path_*') {
				_cyverse_logic_ensureReplicaChecksum(
					cyverse_getValue(*BulkOpInp, *key), cyverse_getValue(*BulkOpInp, 'resc_hier') );
			}
		}
	}

	# data object creation and modification message publishing policy
	*authorName = cyverse_getValue(*Comm, 'user_user_name');
	*authorZone = cyverse_getValue(*Comm, 'user_rods_zone');
	*mayOverwrite = cyverse_hasKey(*BulkOpInp, 'forceFlag');
	foreach (*key in *BulkOpInp) {
		if (*key like 'logical_path_*') {
			*dataPath = cyverse_getValue(*BulkOpInp, *key);
			*idx = triml(*key, 'logical_path_');
			if (*mayOverwrite) {
				msiSplitPath(*dataPath, *collPath, *dataName);
				foreach ( *rec in
					SELECT DATA_CREATE_TIME, DATA_MODIFY_TIME
					WHERE COLL_NAME == *collPath AND DATA_NAME == *dataName
				) {
					if (*rec.DATA_CREATE_TIME == *rec.DATA_MODIFY_TIME) {
						_cyverse_logic_notifyDataObjCreated(*dataPath, *authorName, *authorZone);
					} else {
						_cyverse_logic_notifyDataObjMod(*dataPath, *authorName, *authorZone);
					}
				}
			} else {
				_cyverse_logic_notifyDataObjCreated(*dataPath, *authorName, *authorZone);
			}
		}
	}
}


# BULK_DATA_OBJ_REG

# N.B. This isn't used by iCommands or any official API as of iRODS 4.2.10, so
# let's not implement it.
#
cyverse_logic_api_bulk_data_obj_reg_post(
	*Instance, *Comm, *BulkDataObjRegInp, *BULK_DATA_OBJ_REG_OUT
) {
}


# CHKSUM ALGORITHM:
#
# If neither *DataObjCopyInp.regChksum nor *DataObjCopyInp.verifyChksum exist,
# calculate the checksum of *DataObjCopyInp.dst_obj_path on
# *DataObjCopyInp.dst_resc_hier.
#
# DATA OBJ CREATE AND MOD MSG PUBLISHING ALGORITHM:
#
# If *DataObjCopyInp.dst_openType == 1 (CREATE) then publish a data object
# create message, otherwise publish a data object mod message. openType of 3
# (OPEN FOR WRITE)
#
# *DataObjCopyInp:
#   https://docs.irods.org/4.2.10/doxygen/group__data__object.html#gaad62fbc609d67726e15e7330bbbdf98d
#
cyverse_logic_api_data_obj_copy_post(*Instance, *Comm, *DataObjCopyInp, *TransStat) {
	*destPath = cyverse_getValue(*DataObjCopyInp, 'dst_obj_path');

	if (*destPath == '') {
		failmsg(
			-1,
			'Could not determine path to created data object, (DataObjCopyInp = *DataObjCopyInp)' );
	} else {

		# checksum policy
		if (_cyverse_logic_needsChecksum(*DataObjCopyInp)) {
			_cyverse_logic_ensureReplicaChecksum(
				*destPath, cyverse_getValue(*DataObjCopyInp, 'dst_resc_hier') );
		}

		# data object creation and modification message publishing policy
		*authorName = cyverse_getValue(*Comm, 'user_user_name');
		*authorZone = cyverse_getValue(*Comm, 'user_rods_zone');
		if (cyverse_getValue(*DataObjCopyInp, 'dst_openType') == cyverse_FILE_CREATE) {
			_cyverse_logic_notifyDataObjCreated(*destPath, *authorName, *authorZone);
		} else {
			_cyverse_logic_notifyDataObjMod(*destPath, *authorName, *authorZone);
		}
	}
}


# data_obj_create and data_obj_close are used together
#
# CHKSUM ALGORITHM:
#
# Always compute checksum. Store the path to the data object and the selected
# resource hierarchy for its replica in temporaryStorage using the keys
# `dataObjClose_objPath` and `dataObjClose_selectedHierarchy`, respectively.
# Also, set the temporaryStorage key `dataObjClose_needsChecksum` to some value.
# `data_obj_close` will use the existence of this key and the other two values
# to compute the checksum of the indicated replica.
#
# DATA OBJ CREATE AND MOD MSG PUBLISHING ALGORITHM:
#
# Alway publish a data object create message. Store the path to the data object
# in temporaryStorage using the key `dataObjClose_objPath`. Also, set the
# temporaryStorage key `dataObjClose_created` to some value. `data_obj_close`
# will use the existence of this key and the other object's path to publish a
# data object create message.

# *DataObjInp:
#   https://docs.irods.org/4.2.10/doxygen/group__data__object.html#gab5b8db16a4951cf048e88c8538d8aa56
#
cyverse_logic_api_data_obj_create_post(*Instance, *Comm, *DataObjInp) {
	temporaryStorage.dataObjClose_objPath = cyverse_getValue(*DataObjInp, 'obj_path');

	# checksum policy
	temporaryStorage.dataObjClose_selectedHierarchy = cyverse_getValue(
		*DataObjInp, 'selected_hierarchy' );
	temporaryStorage.dataObjClose_needsChecksum = 'checksum';

	# data object creation message publishing policy
	temporaryStorage.dataObjClose_created = 'created';
}

# N.B. This isn't used by iCommands or any official API as of iRODS 4.2.10
#
cyverse_logic_api_data_obj_create_and_stat_post(*Instance, *Comm, *DataObjInp, *OpenStat) {
	cyverse_logic_api_data_obj_create_post(*Instance, *Comm, *DataObjInp);
}


# data_obj_open, data_obj_write, and data_obj_close are used together
#
# How *DataObjInp.open_flags maps to the open mode, and what this means when
# combined with the value of *DataObjInp.openType.
#
#    case open_flags)
#       'r': do nothing
#       'r+': a write is possible
#       'w':
#           no create: truncated
#           create:  created or truncated
#       'w+':
#           no create: truncated
#           create: created or truncated
#       'a':
#           no create: a write is possible
#           create: possibly created and a write is possible
#       'a+':
#           no create: indistinct from r+
#           create:  possibly created and a write is possible
#
# CHECKSUM ALGORITHM:
#
# A checksum can only be computed after the replica has been modified, so this
# needs to happen in data_obj_close. Only when a change occurs does a checksum
# need to be computed. A change won't occur if the open mode was 'r'. If the
# mode isn't 'r', store the data object's path and the resource holding its
# replica for use by data_obj_close. A change definitely occurred when a replica
# is created or truncated, so if this happens, store a flag to let
# `data_obj_close` know that it needs to perform a checksum. If a replica is
# written to, it has also been modified, so `data_obj_write` needs to store a
# flag to let `data_obj_close` know this has happened.
#
# DATA OBJ CREATE AND MOD MSG PUBLISHING ALGORITHM:
#
# The decision on whether or not to publish a message will occur in
# `data_obj_close`. Only when a change occurs does a message need to be
# published. A change won't occur if the open mode was 'r'. If the mode isn't
# 'r', store the data object's path and for use by `data_obj_close`. A change
# definitely occurred when a data object is created or truncated. If an object
# is created, store a flag indicating that a create message should be published.
# If an existing object was truncated, store a flag indicating that a modify
# message should be published. If an object is written to, it has also been
# modified, so `data_obj_write` needs to store the flag indicated a modify
# message should be published. `data_obj_close` will use the flags along with
# the path to publish the correct message.

# *DataObjInp:
#   https://docs.irods.org/4.2.10/doxygen/group__data__object.html#gab869f78a9d131b1e973d425cd1ebf1f2
#
cyverse_logic_api_data_obj_open_post(*Instance, *Comm, *DataObjInp) {
	*flags = cyverse_getValue(*DataObjInp, 'open_flags');

	if (*flags != cyverse_OPEN_FLAG_R) {
		temporaryStorage.dataObjClose_objPath = cyverse_getValue(*DataObjInp, 'obj_path');

		# checksum policy
		temporaryStorage.dataObjClose_selectedHierarchy = cyverse_getValue(
			*DataObjInp, 'selected_hierarchy' );
		if (cyverse_getValue(*DataObjInp, 'openType') == cyverse_FILE_CREATE) {
			temporaryStorage.dataObjClose_needsChecksum = 'checksum';
		} else if (cyverse_replTruncated(*flags)) {
			temporaryStorage.dataObjClose_needsChecksum = 'checksum';
		}

		# data object creation and modification message publishing policy
		if (cyverse_getValue(*DataObjInp, 'openType') == cyverse_FILE_CREATE) {
			temporaryStorage.dataObjClose_created = 'created';
		} else if (cyverse_replTruncated(*flags)) {
			temporaryStorage.dataObjClose_modified = 'modified';
		}
	}
}

# *DataObjWriteInp:
#   https://docs.irods.org/4.2.10/doxygen/group__data__object.html#gaaa88dd8ad00161d5c48115bebbe6866c
#
cyverse_logic_api_data_obj_write_post(*Instance, *Comm, *DataObjWriteInp, *DataObjWriteInpBBuf) {

	# checksum policy
	temporaryStorage.dataObjClose_needsChecksum = 'checksum';

	# data object creation and modification message publishing policy
	temporaryStorage.dataObjClose_modified = 'modified';
}


# *DataObjCloseInp:
#   https://docs.irods.org/4.2.10/doxygen/group__data__object.html#ga9dcea65009d7cc49ed0106f88540f431
#
cyverse_logic_api_data_obj_close_post(*Instance, *Comm, *DataObjCloseInp) {
	*path = cyverse_getValue(temporaryStorage, 'dataObjClose_objPath');

	if (*path != '') {

		# checksum policy
		if (cyverse_getValue(temporaryStorage, 'dataObjClose_needsChecksum') != '') {
			*resc = cyverse_getValue(temporaryStorage, 'dataObjClose_selectedHierarchy');
			_cyverse_logic_ensureReplicaChecksum(*path, *resc);
		}
		temporaryStorage.dataObjClose_selectedHierarchy = '';
		temporaryStorage.dataObjClose_needsChecksum = '';

		# data object creation and modification message publishing policy
		*authorName = cyverse_getValue(*Comm, 'user_user_name');
		*authorZone = cyverse_getValue(*Comm, 'user_rods_zone');
		if (cyverse_getValue(temporaryStorage, 'dataObjClose_created') != '') {
			_cyverse_logic_notifyDataObjCreated(*path, *authorName, *authorZone);
		} else if (cyverse_getValue(temporaryStorage, 'dataObjClose_modified') != '') {
			_cyverse_logic_notifyDataObjMod(*path, *authorName, *authorZone);
		}
		temporaryStorage.dataObjClose_created = '';
		temporaryStorage.dataObjClose_modified = '';

		temporaryStorage.dataObjClose_objPath = '';
	}
}


# CHKSUM ALGORITHM:
#
# If neither *DataObjInp.regChksum nor *DataObjInp.verifyChksum exist, calculate
# the checksum of *DataObjInp.obj_path on *DataObjInp.resc_hier.
#
# DATA OBJ CREATE AND MOD MSG PUBLISHING ALGORITHM:
#
# If *DataObjInp.openType == 1 (CREATE) then publish a data object create
# message, otherwise publish a data object mod message. openType of 3
# (OPEN FOR WRITE)
#
# *DataObjInp:
#   https://docs.irods.org/4.2.10/doxygen/group__data__object.html#ga1b1d0d95bd1cbc6f07860d6f8174371f
#
cyverse_logic_api_data_obj_put_post(*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PORTAL_OPR_OUT) {
	*path = cyverse_getValue(*DataObjInp, 'obj_path');

	if (*path == '') {
		failmsg(-1, 'Could not determine path to created data object, (DataObjInp = *DataObjInp)');
	} else {

		# checksum policy
		if (_cyverse_logic_needsChecksum(*DataObjInp)) {
			_cyverse_logic_ensureReplicaChecksum(*path, cyverse_getValue(*DataObjInp, 'resc_hier'));
		}

		# data object creation and modification message publishing policy
		*authorName = cyverse_getValue(*Comm, 'user_user_name');
		*authorZone = cyverse_getValue(*Comm, 'user_rods_zone');
		if (cyverse_getValue(*DataObjInp, 'openType') == cyverse_FILE_CREATE) {
			_cyverse_logic_notifyDataObjCreated(*path, *authorName, *authorZone);
		} else {
			_cyverse_logic_notifyDataObjMod(*path, *authorName, *authorZone);
		}
	}
}


# CHKSUM ALGORITHM:
#
# If none of PhyPathRegInp.regRepl, PhyPathRegInp.regChksum, or
# PhyPathRegInp.verifyChksum are set, calculate the checksum of replica of
# PhyPathRegInp.obj_path on PhyPathRegInp.resc_hier.
#
# DATA OBJ CREATE AND MOD MSG PUBLISHING ALGORITHM:
#
# If PhyPathRegInp.regRepl is set, publish a data object modified message,
# otherwise publish a data object created message.
#
cyverse_logic_api_phy_path_reg_post(*Instance, *Comm, *PhyPathRegInp) {

	# checksum policy
	if (!cyverse_hasKey(*PhyPathRegInp, 'regRepl') && _cyverse_logic_needsChecksum(*PhyPathRegInp)) {
		_cyverse_logic_ensureReplicaChecksum(
			cyverse_getValue(*PhyPathRegInp, 'obj_path'),
			cyverse_getValue(*PhyPathRegInp, 'resc_hier') );
	}

	# data object creation and message publishing policy
	*path = cyverse_getValue(*PhyPathRegInp, 'obj_path');
	*authorName = cyverse_getValue(*Comm, 'user_user_name');
	*authorZone = cyverse_getValue(*Comm, 'user_rods_zone');
	if (cyverse_hasKey(*PhyPathRegInp, 'regRepl')) {
		_cyverse_logic_notifyDataObjMod(*path, *authorName, *authorZone);
	} else {
		_cyverse_logic_notifyDataObjCreated(*path, *authorName, *authorZone);
	}
}


# replica_open and replica_close work together.
#
# CHKSUM ALGORITHM:
#
# When replica_open_post is called, if *DataObjInp.destRescName is defined, then
# store it and *DataObjInp.obj_path in temporaryStorage. When replica_close_post
# is called, if destRescName and obj_path are in temporaryStorage, and
# *JSON_INPUT.buf.compute_checksum != true, compute the checksum of obj_path.
#
# DATA OBJ CREATE AND MOD MSG PUBLISHING ALGORITHM:
#
# When replica_open_post is called, If DataObjInp.openType is defined, then
# store it in temporaryStorage. Otherwise store it with the value 3
# (OPEN FOR WRITE). When replica_close_post is called, read DataObjInp.openType
# from temporaryStorage. If it is 1 (CREATE), then publish a data object add
# message, otherwise publish a data object modified message.
#
# N.B. These can be triggered by istream.
# N.B. Only `istream write` needs to be considered.
# N.B. This can create new, overwrite existing, modify existing, and append to
#      existing data objects.
# N.B. This can target a specific resource, e.g., `istream write -R`, or
#      existing replica, e.g., `istream write -n`.
# N.B. This can create a checksum, e.g., `istream write -k`.
# N.B. When a data object with a checksum is overwritten, modified or append
#      to, the checksum is cleared.

# *DataObjInp: https://docs.irods.org/4.2.10/doxygen/structDataObjInp.html
#
cyverse_logic_api_replica_open_post(*Instance, *Comm, *DataObjInp, *JSON_OUTPUT) {
	*path = cyverse_getValue(*DataObjInp, 'obj_path');

	if (*path != '') {
		temporaryStorage.replica_dataObjPath = *path;

		# checksum policy
		temporaryStorage.replica_rescHier = cyverse_getValue(*DataObjInp, 'destRescName');

		# data object creation and modification message publishing policy
		temporaryStorage.replica_openType =
			if cyverse_hasKey(*DataObjInp, 'openType') then cyverse_getValue(*DataObjInp, 'openType')
			else cyverse_FILE_OPEN_WRITE;
	}
}

cyverse_logic_api_replica_close_post(*Instance, *Comm, *JsonInput) {
	*path = cyverse_getValue(temporaryStorage, 'replica_dataObjPath');

	if (*path != '') {

		# checksum policy
		*chksumComputed = match cyverse_json_deserialize(*JsonInput.buf) with
			| cyverse_json_deserialize_val(*input, *_) =>
				match cyverse_json_getValue(*input, 'compute_checksum') with
					| cyverse_json_empty => false
					| cyverse_json_bool(*v) => *v;
		if (!*chksumComputed) {
			_cyverse_logic_ensureReplicaChecksum(
				*path, cyverse_getValue(temporaryStorage, 'replica_rescHier') );
		}
		temporaryStorage.replica_rescHier = '';

		# data object creation and modification message publishing policy
		*authorName = cyverse_getValue(*Comm, 'user_user_name');
		*authorZone = cyverse_getValue(*Comm, 'user_rods_zone');
		if (cyverse_getValue(temporaryStorage, 'replica_openType') == cyverse_FILE_CREATE) {
			_cyverse_logic_notifyDataObjCreated(*path, *authorName, *authorZone);
		} else {
			_cyverse_logic_notifyDataObjMod(*path, *authorName, *authorZone);
		}
		temporaryStorage.replica_openType = '';

		temporaryStorage.replica_dataObjPath = '';
	}
}


# CHKSUM ALGORITHM:
#
# Check to see if JSON_INPUT.buf.options.no_create is false. If it is, check to
# see if neither options.replica_number nor options.leaf_resource_name is set.
# If that's the case, check to see if the data object's 0 replica has a
# checksum. If it doesn't compute its checksum.
#
# DATA OBJ CREATE AND MOD MSG PUBLISHING ALGORITHM:
#
# NB: Current PEPs will handle itouch on an existing collection or data object.
#
# Check to see if *JsonInput.buf.options.no_create is false. If it is, check to
# see if neither options.replica_number nor options.leaf_resource_name is set.
# If that's the case, publish a data object create message
#
cyverse_logic_api_touch_post(*Instance, *Comm, *JsonInput) {
	*input = match cyverse_json_deserialize(*JsonInput.buf) with
		| cyverse_json_deserialize_val(*v, *_) => *v;

	*dataPath = match json_getValue(*input, 'logical_path') with
		| cyverse_json_empty => ''
		| cyverse_json_str(*s) => *s;

	if (*dataPath != '') {
		*options = cyverse_json_getValue(*input, 'options');

		*noCreate = match json_getValue(*options, 'no_create') with
			| cyverse_json_empty => false
			| cyverse_json_bool(*b) => *b;

		*replNumSet = match json_getValue(*options, 'replica_number') with
			| cyverse_json_empty => false
			| cyverse_json_num(*n) => true;

		*rescNameSet = match json_getValue(*options, 'leaf_resource_name') with
			| cyverse_json_empty => false
			| cyverse_json_str(*_) => true;

		if (!*noCreate && !*replNumSet && !*rescNameSet) {

			# checksum policy
			msiSplitPath(*dataPath, *collPath, *dataName);
			foreach ( *rec in
				SELECT DATA_CHECKSUM, DATA_RESC_HIER
				WHERE COLL_NAME = *collPath AND DATA_NAME = *dataName
			) {
				if (*rec.DATA_CHECKSUM == '') {
					_cyverse_logic_ensureReplicaChecksum(*dataPath, *rec.DATA_RESC_HIER);
				}
			}

			# data object creation and modification message publishing policy
			_cyverse_logic_notifyDataObjCreated(
				*dataPath,
				cyverse_getValue(*Comm, 'user_user_name'),
				cyverse_getValue(*Comm, 'user_rods_zone') );
		}
	}
}
