# splunk-user-mgmt
Simple script to automate Splunk user's bulk creation, update, delete and collection.

# Usage
Run the script using this command.

```bash
python3 user-management.py <file> <action>
```

## Create
To bulk create users, create a csv file with the following fields: `id,roles,temp_pass,default_app`

Example: `new_users.csv`
| id | roles | temp_pass | default_app |
| --- | ----| --- | --- |
| user1 | "user,power" | changeme | search |
| user2 | "admin" | changeme | search |

Run the script using this command.

```bash
python3 user-management.py new_users.csv add
```
