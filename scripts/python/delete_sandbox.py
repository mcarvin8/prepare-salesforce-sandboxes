""""
    Delete sandboxes using the Tooling API.
"""
import argparse
import logging
import sys

import get_salesforce_connection
import sandbox_functions

# Format logging message
logging.basicConfig(format='%(message)s', level=logging.DEBUG)

# List sandboxes that shouldn't be deleted this way
DO_NOT_DELETE = ['FullQA', 'dev']


def parse_args():
    """
    Function to pass required arguments.
    """
    parser = argparse.ArgumentParser(description='A script to delete a sandbox.')
    parser.add_argument('-a', '--alias', help='Production alias used for authentication', required=False)
    parser.add_argument('-s', '--sandbox', help='Name of the sandbox to delete', required=True)
    parser.add_argument('-u', '--url', help='Force Auth URL for your production org.', required=False)
    parser.add_argument('-j', '--json', help='Path to the JSON file containing protected sandboxes.', default='.protectedsandboxes.json')
    args = parser.parse_args()
    return args


def delete_sandbox(sandbox_name, sandbox_id, salesforce_connection):
    """
        Delete a sandbox
    """
    logging.info('Deleting the existing sandbox: %s', sandbox_name)
    salesforce_connection.toolingexecute(f'sobjects/SandboxInfo/{sandbox_id}', 'DELETE')
    logging.info('Sandbox deletion has been initiated.')


def main(alias, sandbox_name, url, protected_sandboxes_file):
    """
    Main function
    """
    protected_sandboxes_list = sandbox_functions.load_protected_sandboxes_json(protected_sandboxes_file)
    if protected_sandboxes_list and (sandbox_name in protected_sandboxes_list):
        logging.error('The sandbox is in the Protected Sandboxes JSON file: %s', sandbox_name)
        sys.exit(1)

    if alias:
        sf = get_salesforce_connection.get_salesforce_connection_alias(alias)
    elif url:
        sf = get_salesforce_connection.get_salesforce_connection_url(url)
    else:
        logging.error('ERROR: The Salesforce Production alias or URL was not provided for authentication.')
        logging.error('Please provide `--alias` or `--url` flag and try again.')
        sys.exit(1)

    # Check if the provided sandbox name exists
    query_data = sf.toolingexecute(f"query?q=SELECT+StartDate,SandboxName,SandboxInfoId,Status+FROM+SandboxProcess+WHERE+SandboxName+=+'{sandbox_name}'",'GET')
    records = query_data['records']

    # Exit if sandbox records exist, but the sandbox is already deleted in the org
    if all(record.get('Status') in {'Deleted', 'Deleting'} for record in records):
        logging.error('ERROR: The sandbox has already been deleted in the Org: %s', sandbox_name)
        sys.exit(1)

    if records:
        sandbox_id, elgible_sandbox_info = sandbox_functions.find_eligible_sandbox(records)
        if elgible_sandbox_info:
            delete_sandbox(sandbox_name, sandbox_id, sf)
        else:
            logging.error('ERROR: Sandbox %s is not eligible for a sandbox deletion.', sandbox_name)
            logging.error('The sandbox was recently refreshed or created within the past day.')
            sys.exit(1)
    else:
        logging.info('ERROR: A sandbox with the name `%s` could not be found in the Org.', sandbox_name)
        sys.exit(1)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.alias, inputs.sandbox, inputs.url,
         inputs.json)
