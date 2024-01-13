"""Required modules."""
import argparse
import logging
import os
import tempfile
import subprocess
import sys


# Format logging message
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """
        Function to pass required arguments.
        alias - alias to set
        url - sfdx authorization URL (do not store in quotes)
    """
    parser = argparse.ArgumentParser(description='A script to authenticate to salesforce.')
    parser.add_argument('-a', '--alias')
    parser.add_argument('-u', '--url')
    args = parser.parse_args()
    return args


def make_temp_file(url):
    """
        Function to create the temporary file with the URL
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    with open(temp_file.name, 'w', encoding='utf-8') as file:
        file.write(url)
    return temp_file.name


def run_command(cmd):
    """
        Function to run the command using the system's command shell
    """
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError:
        sys.exit(1)


def main(alias, url):
    """
        Main function to authorize to salesforce.
    """
    # Create temporary file to store the URL
    url_file = make_temp_file(url)

    # Set all commands
    # Do not expose the URL in the logs
    commands = []
    commands.append(f'sf org login sfdx-url -f {url_file} --set-default --alias {alias}')
    commands.append(f'sf config set target-org={alias}')
    commands.append(f'sf config set target-dev-hub={alias}')

    # Run commands individually
    for command in commands:
        logging.info(command)
        run_command(command)

    # Delete temporary file with the URL
    os.remove(url_file)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.alias, inputs.url)
