# Prepare Sandboxes
Python scripts which uses Simple Salesforce to create, refresh, and delete sandboxes.

Scripts require a Production User Email, Password, and Security Token (https://help.salesforce.com/s/articleView?id=sf.user_security_token.htm&type=5).


## Create and Refresh Sandboxes
```
python ./create_sandbox.py --user "$PROD_USER" --password "$PROD_PASSWORD" --token "$PROD_TOKEN" --sandbox "$SANDBOX"
```

The above script either creates a new sandbox or refreshes an existing sandbox. Sandbox refreshes will auto-activate, so you will not be able to revert the sandbox once this script runs.

List protected sandboxes here if you wish to prevent a sandbox from being refreshed this way.
``` python
DO_NOT_REFRESH = ['FullQA', 'dev']
```

The `sandbox_data` dictionary below is similar to a Sandbox Definition File:
- LicenseType = License for the sandbox (Developer, Developer Pro, Full Copy)
- ActivationUserGroupId = ID of the Public Group (https://help.salesforce.com/s/articleView?id=sf.ls_create_public_groups.htm&type=5)
- ApexClassId = ID of the Apex Class to run in the sandbox post activation

``` python
    # Update Public Group and Apex Class ID for your org
    sandbox_data = {
        'LicenseType': 'DEVELOPER',
        'SandboxName': sandbox_name,
        'ActivationUserGroupId': '00G5a000003ji0R',
        'ApexClassId': '01p5a000007t7Yx'
    }
```

### Apex Class

To use the Apex Class in sandbox creations and refreshes, the class must first be deployed to your Production org.

The `PrepareMySandbox` apex class will update all users in the Public Group to the desired profile and reset their passwords. 

Update the Profile ID and public group ID in the class and test class before deploying to your org. Also update the test class users' email for your org.

All users in the public group will receive a password reset email once the sandbox is ready.

If you don't want to use this Apex Class, remove the `ApexClassId` line from `create_sandbox.py`.

## Delete Sandboxes
```
python ./delete_sandbox.py --user "$PROD_USER" --password "$PROD_PASSWORD" --token "$PROD_TOKEN" --sandbox "$SANDBOX"
```

This script will delete sandboxes assuming the sandbox meets deletion criteria (cannot be created or refreshes within the past day).

List protected sandboxes here if you wish to prevent a sandbox from being deleted this way:
``` python
DO_NOT_DELETE = ['FullQA', 'dev']
```

## Query Sandboxes
```
python ./query_sandbox.py --user "$PROD_USER" --password "$PROD_PASSWORD" --token "$PROD_TOKEN" --sandbox "$SANDBOX"
```

This script can be used to check the current sandbox status. 

When the sandbox is ready for use, the status will be `Completed`.

## CI/CD Example

A sample GitLab CI/CD config file has been included. For other CI/CD platforms, please ensure the container used contains Python and the simple salesforce library. The scripts themselves require no updates for other platforms.

For GitLab, the pipeline source is `web` (CI/CD → Pipelines, click 'Run Pipeline' button). Add the `SANDBOX` variable with the sandbox name, then press `Run pipeline`. The create/refresh job will run automatically. The query and delete jobs will be manually triggered.
