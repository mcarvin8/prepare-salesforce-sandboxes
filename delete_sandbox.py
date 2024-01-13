""""
    Delete sandboxes using the Tooling API.
"""
import argparse
import logging
import sys

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
    parser.add_argument('-a', '--alias')
    parser.add_argument('-s', '--sandbox', help='Name of the sandbox to delete')
    args = parser.parse_args()
    return args


def delete_sandbox(sandbox_id, salesforce_connection):
    """
        Delete a sandbox
    """
    logging.info('Deleting the existing sandbox')
    salesforce_connection.toolingexecute(f'sobjects/SandboxInfo/{sandbox_id}', 'DELETE')
    logging.info('Sandbox deletion has been initiated.')


def main(alias, sandbox_name):
    """
    Main function
    """
    if sandbox_name in DO_NOT_DELETE:
        logging.info('ERROR: The sandbox `%s` is in the DO NOT DELETE list', sandbox_name)
        sys.exit(1)

    sf = sandbox_functions.get_salesforce_connection(alias)

    # Check if the provided sandbox name exists
    query_data = sf.toolingexecute(f"query?q=SELECT+StartDate,SandboxName,SandboxInfoId,Status+FROM+SandboxProcess+WHERE+SandboxName+=+'{sandbox_name}'",'GET')
    records = query_data['records']

    # Exit if sandbox records exist, but the sandbox is already deleted in the org
    if all(record.get('Status') in {'Deleted', 'Deleting'} for record in records):
        logging.info('ERROR: The sandbox has already been deleted in the Org.')
        sys.exit(1)

    if records:
        sandbox_id, elgible_sandbox_info = sandbox_functions.find_eligible_sandbox(records)
        if elgible_sandbox_info:
            delete_sandbox(sandbox_id, sf)
        else:
            logging.info('ERROR: Sandbox %s is not eligible for a sandbox deletion.', sandbox_name)
            logging.info('The sandbox was recently refreshed or created within the past day.')
            sys.exit(1)
    else:
        logging.info('ERROR: A sandbox with the name `%s` could not be found in the Org.', sandbox_name)
        sys.exit(1)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.alias, inputs.sandbox)
