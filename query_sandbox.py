""""
    Get current sandbox status with the Tooling API.
"""
import argparse
import logging
import sys

import get_salesforce_connection
import sandbox_functions

# Format logging message
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """
    Function to pass required arguments.
    """
    parser = argparse.ArgumentParser(description='A script to post the sandbox status.')
    parser.add_argument('-a', '--alias', help='Production alias used for authentication', required=False)
    parser.add_argument('-s', '--sandbox', help='Name of the sandbox to query', required=True)
    parser.add_argument('-u', '--url', help='Force Auth URL for your production org.', required=False)
    args = parser.parse_args()
    return args


def main(alias, sandbox_name, url):
    """
    Main function
    """
    if alias:
        sf = get_salesforce_connection.get_salesforce_connection_alias(alias)
    elif url:
        sf = get_salesforce_connection.get_salesforce_connection_url(url)
    else:
        logging.error('The Salesforce Production alias or URL was not provided for authentication.')
        logging.error('Please provide `--alias` or `--url` flag and try again.')
        sys.exit(1)

    # Check if the provided sandbox name exists
    query_data = sf.toolingexecute(f"query?q=SELECT+StartDate,SandboxName,Status+FROM+SandboxProcess+WHERE+SandboxName+=+'{sandbox_name}'",'GET')
    records = query_data['records']
    if records:
        elgible_sandbox_info = {}
        eligible_status = None
        newest_start_date = None
        for item in records:
            sandbox_name_str = item.get('SandboxName')
            sandbox_status = item.get('Status')
            start_date = item.get('StartDate')
            if (newest_start_date is None or start_date > newest_start_date) and sandbox_status not in {'Deleted', 'Deleting'}:
                elgible_sandbox_info[sandbox_name_str] = sandbox_name_str
                eligible_status = sandbox_status
                newest_start_date = start_date

        # only log status if it's not Deleting or Deleted
        if elgible_sandbox_info:
            logging.info('The sandbox `%s` has been found.', sandbox_name)
            logging.info('Current Status: %s', eligible_status)
        else:
            logging.info('ERROR: No Active Sandboxes named `%s` found in the org.', sandbox_name)
            sys.exit(1)
    else:
        logging.info('ERROR: A Sandbox with the name `%s` was not found in the org.', sandbox_name)
        sys.exit(1)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.alias, inputs.sandbox, inputs.url)
