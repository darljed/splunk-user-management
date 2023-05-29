# splunk-user-management
Simple script to automate Splunk user's bulk creation, update and delete.

# Usage
Run the script using this command.

`python3 user-management.py <path/to/file.csv>`

example:

```bash
python user-management.py template.csv
```

## How to setup template
Create a valid csv file with the following fields: `action,id,roles,temp_pass,default_app`

- `action`: Values can be: `add,create,update,update_add_roles,delete`

- `id`: username

- `roles`: comma separated list of roles

- `temp_pass`: (optional) sets new temporary password and forces to update password upon login. Applicable only for add, create and update. if blank, user password won't be updated. 

- `default_app`: (optional) default application of the user


Example: `new_users.csv`
| action | id | roles | temp_pass | default_app |
| --- | --- | ----| --- | --- |
| add | user1 | "user,power" | changeme | search |
| update | "admin" | "admin,can_delete"| changeme | search |
| update | "user2" | "user"|  | my_app |
| delete | "user3" | | | |
