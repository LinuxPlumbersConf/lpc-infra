# Syncronizing cvent and LDAP

## First run
* Login into cvent registration list:
  https://web.cvent.com/p/243819c8-57d2-4894-a798-255b6329d0f4/reporting/799f92aa-929f-4190-98f5-ba5d3d8ad640/RUN/
* Sort the registrants list by last registration date so that newest registrations will be at the bottom. The exported CSV will contain data exactly the same way it is presented on the website.
* Click three dots just above the registrants list and export the list as CSV, say as `Registrants.0.csv`
* Run the `csv2ldap.py` to import CSV data to the LDAP server

```
python csv2ldap.py -c Registrants.0.csv
```

Note: this step overrides admin and moderator permissions. The admin and moderator rights shold be restored with

```
python csv2ldap.py --admins <file with admin emails>
python csv2ldap.py --moderators <file with moderator emails>
```

## Incremental updates
* Login into cvent registration list
* Sort the registrants list by last registration date so that newest registrations will be at the bottom
* Export the registrants list as CSV. Choose a different name that the initial export, e.g. `Registrants.1.csv`
* Create an (almost) empty CSV

```
head -1 Registrants.0.csv > regs.csv
```

* Add new and updated registrations to the CSV

```
diff -u Registrants.0.csv  Registrants.1.csv  | grep ^+  | grep -v ^+++ | \
	sed 's/^+//'  >> regs.csv
```

* Run `csv2ldap`

```
python csv2ldap.py -c regs.csv
```
