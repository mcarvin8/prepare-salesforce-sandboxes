""""
    Create and refresh sandboxes using the Tooling API.
"""
import argparse
import logging
import sys

import sandbox_functions

# Format logging message
logging.basicConfig(format='%(message)s', level=logging.DEBUG)

# List sandboxes that shouldn't be refreshed this way
DO_NOT_REFRESH = ['FullQA', 'dev']


def parse_args():
    """
    Function to pass required arguments.
    """
    parser = argparse.ArgumentParser(description='A script to create or refresh a sandbox.')
    parser.add_argument('-u', '--user')
    parser.add_argument('-p', '--password')
    parser.add_argument('-t', '--token')
    parser.add_argument('-s', '--sandbox', help='Name of the sandbox to create or refresh')
    args = parser.parse_args()
    return args


def create_sandbox(sandbox_name, sandbox_data, salesforce_connection):
    """
        Create a sandbox
    """
    logging.info('Creating a new sandbox %s', sandbox_name)
    salesforce_connection.toolingexecute("sobjects/SandboxInfo",'POST', sandbox_data)
    logging.info('Sandbox creation has been initiated.')


def refresh_sandbox(sandbox_id, sandbox_data, salesforce_connection):
    """
        Refresh a sandbox
    """
    logging.info('Refreshing an existing sandbox')
    salesforce_connection.toolingexecute(f'sobjects/SandboxInfo/{sandbox_id}', 'PATCH', sandbox_data)
    logging.info('Sandbox refresh has been initiated.')


def main(user_name, user_password, user_token, sandbox_name):
    """
    Main function
    """
    if sandbox_name in DO_NOT_REFRESH:
        logging.info('ERROR: The sandbox `%s` is in the DO NOT REFRESH list', sandbox_name)
        sys.exit(1)

    sf = sandbox_functions.get_salesforce_connection(user_name, user_password, user_token)

    # Update Public Group and Apex Class ID for your org
    sandbox_data = {
        'LicenseType': 'DEVELOPER',
        'SandboxName': sandbox_name,
        'ActivationUserGroupId': '00G5a000003ji0R',
        'ApexClassId': '01p5a000007t7Yx'
    }

    # Check if the provided sandbox name exists
    query_data = sf.toolingexecute(f"query?q=SELECT+StartDate,SandboxName,SandboxInfoId,Status+FROM+SandboxProcess+WHERE+SandboxName+=+'{sandbox_name}'",'GET')
    records = query_data['records']

    # Create sandbox if sandbox records exist, but the sandbox was deleted in the org
    if all(record.get('Status') in {'Deleted', 'Deleting'} for record in records):
        create_sandbox(sandbox_name, sandbox_data, sf)
        return

    # Refresh the sandbox if records exist
    if records:
        sandbox_id, elgible_sandbox_info = sandbox_functions.find_eligible_sandbox(records)
        if elgible_sandbox_info:
            activate = {
                'AutoActivate': True
            }
            sandbox_data.update(activate)
            refresh_sandbox(sandbox_id, sandbox_data, sf)
        else:
            logging.info('ERROR: Sandbox %s is not eligible for a sandbox refresh', sandbox_name)
            logging.info('The sandbox was created or refreshed within the past day.')
            sys.exit(1)
    else:
        create_sandbox(sandbox_name, sandbox_data, sf)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.user, inputs.password, inputs.token, inputs.sandbox)
