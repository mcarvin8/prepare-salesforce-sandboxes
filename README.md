# Prepare Sandboxes
Python scripts which uses Simple Salesforce to create, refresh, and delete sandboxes.

The environment requires Python 3 and the Salesforce CLI (`sf`).

## Authenticate to Production using the Salesforce CLI

You must first authenticate to your production org using the Salesforce CLI.

The below sandbox Python scripts require the Production Alias used when authenticating.

You can use the provided SFDX authenticate script with the Force Auth URL and the desired alias.

```
USAGE
  $ python ./authenticate_sfdx.py --alias "PRODUCTION" --url $PRODUCTION_AUTH_URL

FLAGS
  -a, --alias=<value> Production Alias used when authenticating with the Salesforce CLI.
  -u, --url=<value>  Production Force Auth URL.

```

## Create and Refresh Sandboxes

```
USAGE
  $ python ./create_sandbox.py --alias "PRODUCTION" --sandbox "$SANDBOX" --license {Developer,Developer_Pro,Partial,Full} [-c CLASS_VALUE] [-g GROUP]

FLAGS
  -a, --alias=<value> Production Alias used when authenticating with the Salesforce CLI.
  -s, --sandbox=<value>  Name of the sandbox to create or refresh.
  -l, --license=<value>  License type to create/refresh the sandbox as. Valid options are {Developer,Developer_Pro,Partial,Full}.
  -c, --class=<value>  [OPTIONAL] Apex Class ID to run post sandbox activation.
  -g, --group=<value>  [OPTIONAL] Public Group ID (aka Activation User Group ID) to provide sandbox acess.

```


The above script either creates a new sandbox or refreshes an existing sandbox. Sandbox refreshes will auto-activate, so you will not be able to revert the sandbox once this script runs.

Update the script to list protected branches here if you wish to prevent a sandbox from being refreshed this way.
``` python
DO_NOT_REFRESH = ['FullQA', 'dev']
```

### Apex Class

The `force-app\main\default\classes\PrepareMySandbox.cls` apex class in this project will update all users in the Public Group to the desired profile and reset their passwords. 

To use this Apex Class in sandbox creations and refreshes, the class must first be deployed to your Production org.

Update the Profile ID and public group ID in the class and test class before deploying to your org. Also update the test class users' email for your org.

All users in the public group will receive a password reset email once the sandbox is ready.

If you don't want to use this Apex Class, remove the `ApexClassId` line from `create_sandbox.py`.

## Delete Sandboxes

```
USAGE
  $ python ./delete_sandbox.py --alias "PRODUCTION" --sandbox "$SANDBOX"

FLAGS
  -a, --alias=<value> Production Alias used when authenticating with the Salesforce CLI.
  -s, --sandbox=<value>  Name of the sandbox to delete.

```

This script will delete sandboxes assuming the sandbox meets deletion criteria.

List protected sandboxes here if you wish to prevent a sandbox from being deleted this way:
``` python
DO_NOT_DELETE = ['FullQA', 'dev']
```

## Query Sandboxes

```
USAGE
  $ python ./query_sandbox.py --alias "PRODUCTION" --sandbox "$SANDBOX"

FLAGS
  -a, --alias=<value> Production Alias used when authenticating with the Salesforce CLI.
  -s, --sandbox=<value>  Name of the sandbox to query.

```

This script can be used to check the current sandbox status. 

When the sandbox is ready for use, the status will be `Completed`.

## CI/CD Example

A sample GitLab CI/CD config file has been included. For other CI/CD platforms, please ensure the container used contains Python and the simple salesforce library. The scripts themselves require no updates for other platforms.

For GitLab, the pipeline source is `web` (CI/CD → Pipelines, click 'Run Pipeline' button). Add the `SANDBOX` variable with the sandbox name, then press `Run pipeline`. The create/refresh job will run automatically. The query and delete jobs will be manually triggered.
