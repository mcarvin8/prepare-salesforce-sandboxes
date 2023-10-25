# Salesforce Sandbox Tooling API Scripts
Python scripts which utilizes the Salesforce Tooling API via Simple Salesforce to create, refresh, delete, and query sandboxes in Salesforce.

Scripts require a Production User Email, Password, and Security Token (https://help.salesforce.com/s/articleView?id=sf.user_security_token.htm&type=5).

The sample GitLab CI/CD config file can be used to run these scripts from the `web` pipeline source. The `SANDBOX` variable with the intended sandbox name should be set up when running a web pipeline.

The Apex class and test class should be deployed to your Production org after making updates for your org (Public Group and Profile).

Update the `create_sandbox.py` script with your org's Apex Class ID and Public Group ID.
