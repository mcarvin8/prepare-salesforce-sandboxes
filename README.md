# Prepare Salesforce Sandboxes
Python scripts which uses Simple Salesforce to create, refresh, and delete sandboxes.

The environment requires Python 3 and the Salesforce CLI (`sf`).

> This [Salesforce issue](https://issues.salesforce.com/issue/a028c00000x9ZiUAAU/release-of-selective-sandbox-access-delayed) with Public Groups in sandboxes has been resolved with API version 61. The simple salesforce connection must be established at API version 61 in order for `ActivationUserGroupId` to be present in the Tooling API. The scripts should connect to your Production org at the latest API version supported.

## Authenticate to Production using the Salesforce CLI

You can authenticate to your Production org in 1 of 2 ways using the Salesforce CLI.

1. Authenticate using an existing alias
2. Authenticate using a Force Auth URL

> Please ensure you only use one of the 2 flags for authentication. If you provide both, it will default to alias first.

### Using an Alias

To authenticate with an existing alias, you must provide the sandbox script with the `--alias` flag.

### Using a Force Auth URL

To authenticate directly with a Force Auth URL, you must at least have Salesforce CLI 2.24.4 or newer installed.

You must provide the sandbox script with the `--url` flag.

## Protected Sandboxes JSON file

The create/refresh sandbox script and the delete sandbox script will process a JSON file containg protected sandboxes if the file is found. If a user attempts to refresh or delete a sandbox in the JSON file, the script will end with a failure.

By default, the scripts will look for a JSON file named `.protectedsandboxes.json` in the running directory that follows this format:

```json
{
    "do_not_refresh": ["FullQA", "dev"]
}
```

## Create and Refresh Sandboxes

```
USAGE
  $ python ./scripts/python/create_sandbox.py --alias "PRODUCTION" --sandbox "$SANDBOX" --license {Developer,Developer_Pro,Partial,Full} [-c CLASS_VALUE] [-g GROUP] [--url $FORCE_AUTH_URL] [--json ".protectedsandboxes.json"]

FLAGS
  -a, --alias=<value> Production Alias used when authenticating with the Salesforce CLI. Do not provide this if you are using the --url flag.
  -s, --sandbox=<value>  Name of the sandbox to create or refresh.
  -l, --license=<value>  License type to create/refresh the sandbox as. Valid options are {Developer,Developer_Pro,Partial,Full}.
  -c, --class=<value>  [OPTIONAL] Apex Class ID to run post sandbox activation.
  -g, --group=<value>  [OPTIONAL] Public Group ID (aka Activation User Group ID) to provide sandbox access.
  -u, --url=<value> Production Force Auth URL to use when authenticating with the Salesforce CLI. Do not provide this if you are using the --alias flag.
  -j, --json=<value> Path to the JSON file containing the protected sandboxes to not refresh. Default is ".protectedsandboxes.json".
```

The above script either creates a new sandbox or refreshes an existing sandbox. Sandbox refreshes will auto-activate, so you will not be able to revert the sandbox once this script runs.

### Apex Class

The `force-app/main/default/classes/PrepareMySandbox.cls` apex class in this project is designed to run post sandbox refresh and do the following operations:
1. Set all active users in the public group named 'FullTime Developers' to the 'Admin-SoD-PreProd-Delivery' profile
2. Assign all active users in the public group named 'FullTime Developers' the "Author_Apex" permission set provided in this repo
3. Assign all active users in the public group named 'FullTime Developers' the Administrator role provided in this repo
4. Reset passwords for all active users in the public group named 'FullTime Developers'

To use this Apex Class in sandbox creations and refreshes, the class must be deployed to your Production org. Update the class and test class with your public group name and the desired profile/permission set/role if you want to use ones you already have. Update the test class to set the `oldProfile` to a different profile to confirm the class is working as intended. Update the test class to create different test users (emails).

If you'd like, you can deploy the `Author_Apex` permission set, the `Admin-SoD-PreProd-Delivery` and `Admin-SoD-Prod-Delivery` profiles, the `FullTime Developers` public group, and `Administrator` role provided in this repo and referenced in the Apex classes to your production org if you'd like to use them.

## Delete Sandboxes

```
USAGE
  $ python ./scripts/python/delete_sandbox.py --alias "PRODUCTION" --sandbox "$SANDBOX" [--url $FORCE_AUTH_URL] [--json ".protectedsandboxes.json"]

FLAGS
  -a, --alias=<value> Production Alias used when authenticating with the Salesforce CLI. Do not provide this if you are using the --url flag.
  -s, --sandbox=<value>  Name of the sandbox to delete.
  -u, --url=<value> Production Force Auth URL to use when authenticating with the Salesforce CLI. Do not provide this if you are using the --alias flag.
  -j, --json=<value> Path to the JSON file containing the protected sandboxes to not refresh. Default is ".protectedsandboxes.json".
```

This script will delete sandboxes assuming the sandbox meets deletion criteria.

## Query Sandboxes

```
USAGE
  $ python ./scripts/python/query_sandbox.py --alias "PRODUCTION" --sandbox "$SANDBOX" [--url $FORCE_AUTH_URL]

FLAGS
  -a, --alias=<value> Production Alias used when authenticating with the Salesforce CLI. Do not provide this if you are using the --url flag.
  -s, --sandbox=<value>  Name of the sandbox to query.
  -u, --url=<value> Production Force Auth URL to use when authenticating with the Salesforce CLI. Do not provide this if you are using the --alias flag.
```

This script can be used to check the current sandbox status. 

When the sandbox is ready for use, the status will be `Completed`.

## CI/CD Examples

Sample CI/CD workflows for GitHub and GitLab have been included. For other CI/CD platforms, please ensure the container used contains Python and the simple salesforce library. The scripts themselves require no updates for other platforms.

For GitLab (`.gitlab-ci.yml`):
- Add the `PRODUCTION_AUTH_URL` variable in your repo CI/CD variables.
- The pipeline source is web. Go to CI/CD → Pipelines and click the 'Run Pipeline' button.
    - Add the `SANDBOX` variable with the sandbox name.
    - Add the `LICENSE` variable with one of the valid license types (Developer,Developer_Pro,Partial,Full).
    - Optionally, add the `CLASS` variable with the Apex Class ID.
    - Optionally, add the `GROUP` variable with the Public Group ID.
    - Press `Run pipeline`. The create/refresh job will run automatically. The query and delete jobs will be manually triggered.

For GitHub:
- All workflows will be manually triggered via workflow dispatch.
- All workflows require the `PRODUCTION_AUTH_URL` defined in your repo secrets.
- The `Create/Refresh Sandbox`, `Delete Sandbox`, and `Check Sandbox Status` requires a `sandbox` input with the name of the sandbox.
- The `Create/Refresh Sandbox` must include 1 of the available options for the license type input.
- The `Create/Refresh Sandbox` workflow optionally can include string inputs for the Apex Class ID and Public Group ID.
