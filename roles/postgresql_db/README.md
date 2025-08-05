# cyverse.ds.postgresql_db

This role ensures a database exists within a PostgreSQL DBMS. The role assumes the database has an
admin user.

## Requirements

None

## Role Variables

Variable                       | Required | Default                             | Choices | Comment
------------------------------ | -------- | ----------------------------------- | ------- | -------
`postgresql_db_dbms_pg_hba`    | no       | /etc/postgresql/12/main/pg_hba.conf |         | the absolute path to the service's pg_hba.conf file
`postgresql_db_dbms_port`      | no       | 5432                                |         | the TCP the DBMS is listening on
`postgresql_db_name`           | no       | postgres                            |         | the name of the database
`postgresql_db_admin_username` | no       | postgres                            |         | the account name of the database admin
`postgresql_db_admin_password` | yes      |                                     |         | the password used to authenticate the database's admin user
`postgresql_db_client_hosts`   | no       | []                                  |         | the host names or IP addresses for the services that connect to the given DB as the given admin user

## Dependencies

None

## Example Playbook

```yaml
- hosts: dbms
  roles:
    - role: postgresql_db
      vars:
        postgresql_db_name: ICAT
        postgresql_db_admin_username: irods
        postgresql_db_admin_password: testpassword
```
