# Prepare Sandboxes
Python scripts which uses Simple Salesforce to create, refresh, and delete sandboxes.

Scripts require a Production User Email, Password, and Security Token (https://help.salesforce.com/s/articleView?id=sf.user_security_token.htm&type=5).

```
python ./create_sandbox.py --user "$PROD_USER" --password "$PROD_PASSWORD" --token "$PROD_TOKEN" --sandbox "$SANDBOX"
python ./query_sandbox.py --user "$PROD_USER" --password "$PROD_PASSWORD" --token "$PROD_TOKEN" --sandbox "$SANDBOX"
python ./delete_sandbox.py --user "$PROD_USER" --password "$PROD_PASSWORD" --token "$PROD_TOKEN" --sandbox "$SANDBOX"
```

The sample GitLab CI/CD config file can be used to run these scripts from the `web` pipeline source. The `SANDBOX` variable with the intended sandbox name should be set up when running a web pipeline.

Deploy the Apex Classes to your production org after updating the Profile ID and Public Group ID in the files.

Update the `create_sandbox.py` script with your org's Apex Class ID and Public Group ID.
