""""
    Get current sandbox status with the Tooling API.
"""
import argparse
import logging
import sys

import sandbox_functions

# Format logging message
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """
    Function to pass required arguments.
    """
    parser = argparse.ArgumentParser(description='A script to post the sandbox status.')
    parser.add_argument('-u', '--user')
    parser.add_argument('-p', '--password')
    parser.add_argument('-t', '--token')
    parser.add_argument('-s', '--sandbox', help='Name of the sandbox to query')
    args = parser.parse_args()
    return args


def main(user_name, user_password, user_token, sandbox_name):
    """
    Main function
    """
    sf = sandbox_functions.get_salesforce_connection(user_name, user_password, user_token)

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
            logging.info('The sandbox %s has been found.', sandbox_name)
            logging.info('Current Status: %s', eligible_status)
        else:
            logging.info('No Active Sandboxes %s found in the org.', sandbox_name)
            sys.exit(1)
    else:
        logging.info('A Sandbox with the name %s not found in the org.', sandbox_name)
        sys.exit(1)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.user, inputs.password, inputs.token, inputs.sandbox)
