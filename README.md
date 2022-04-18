# bp-feats
A little project as the first step to automate backporting for Suricata.
Configurable variables are present in `config.toml` per section.

In order to use the project,

```
pip3 -r requirements.txt
```
Save your Redmine API key in a file named `api.keys`.

## init.py
Run the script

```
python init.py
```

to see what tickets are ready for backports and which are missing a backport ticket.

## backport.sh
Script to automate backporting for clean commits. An error report named `bp_error.log`
is recorded for commits that were not cleanly backported in the directory where the
script is run from.

Run the script from the suricata directory where you want to apply the backported
commits. Requires a file with list of commit hashes to be applied one on a line.
This files shall be picked up from the directory where this script resides.
```
../backport.sh hashes.txt
```

This will backport each commit one by one and based on error status, log the info in
the error file and rollback to a previous stage. It will check whether a commit was
cleanly applied, passed build and unittests.

### Future Plan
The script that applies that commits and that finds the issues ready for backporting
is not supposed to be so disconnected in the future and be a part of a pipeline to
achieve better automation.
