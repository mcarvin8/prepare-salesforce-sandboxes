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
    parser.add_argument('-a', '--alias', help='Production alias used for authentication', required=True)
    parser.add_argument('-s', '--sandbox', help='Name of the sandbox to create or refresh', required=True)
    parser.add_argument('-l', '--license', help='Type of license for the sandbox (`Developer`, `Developer_Pro`, `Partial`, `Full`)',
                        choices=['Developer', 'Developer_Pro', 'Partial', 'Full'], required=True)
    parser.add_argument('-c', '--class',  dest='class_id', help='Apex Class ID to run post sandbox activation')
    parser.add_argument('-g', '--group', help='Public Group ID to provide access to sandbox')
    args = parser.parse_args()
    return args


def create_sandbox(sandbox_name, sandbox_definition, salesforce_connection):
    """
        Create a sandbox
    """
    logging.info('Creating a new sandbox: %s', sandbox_name)
    salesforce_connection.toolingexecute("sobjects/SandboxInfo",'POST', sandbox_definition)
    logging.info('Sandbox creation has been initiated.')


def refresh_sandbox(sandbox_name, sandbox_id, sandbox_definition, salesforce_connection):
    """
        Refresh a sandbox
    """
    logging.info('Refreshing an existing sandbox: %s', sandbox_name)
    salesforce_connection.toolingexecute(f'sobjects/SandboxInfo/{sandbox_id}', 'PATCH', sandbox_definition)
    logging.info('Sandbox refresh has been initiated.')


def main(alias, sandbox_name, license_type, class_id, group_id):
    """
    Main function
    """
    if sandbox_name in DO_NOT_REFRESH:
        logging.error('The sandbox is in the DO NOT REFRESH list: %s', sandbox_name)
        sys.exit(1)

    sf = sandbox_functions.get_salesforce_connection(alias)

    # Initialize the sandbox definition dictionary
    sandbox_definition = {
        'LicenseType': license_type,
        'SandboxName': sandbox_name,
        'AutoActivate': True
    }

    # Check if class_id is not None and add it to the dictionary
    if class_id is not None:
        sandbox_definition['ApexClassID'] = class_id

    # Check if group_id is not None and add it to the dictionary
    if group_id is not None:
        sandbox_definition['ActivationUserGroupId'] = group_id

    # Check if the provided sandbox name exists
    query_data = sf.toolingexecute(f"query?q=SELECT+StartDate,SandboxName,SandboxInfoId,Status+FROM+SandboxProcess+WHERE+SandboxName+=+'{sandbox_name}'",'GET')
    records = query_data['records']

    # Create sandbox if sandbox records exist, but the sandbox was deleted in the org
    if all(record.get('Status') in {'Deleted', 'Deleting'} for record in records):
        create_sandbox(sandbox_name, sandbox_definition, sf)
        return

    # Refresh the sandbox if records exist
    if records:
        sandbox_id, elgible_sandbox_info = sandbox_functions.find_eligible_sandbox(records)
        if elgible_sandbox_info:
            refresh_sandbox(sandbox_name, sandbox_id, sandbox_definition, sf)
        else:
            logging.error('ERROR: Sandbox %s is not eligible for a sandbox refresh', sandbox_name)
            logging.error('The sandbox was created or refreshed within the past day.')
            sys.exit(1)
    else:
        create_sandbox(sandbox_name, sandbox_definition, sf)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.alias, inputs.sandbox,
         inputs.license, inputs.class_id, inputs.group)
