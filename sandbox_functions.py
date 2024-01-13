"""
    Functions used to create, refresh, delete sandboxes.
"""
import datetime
import json
import re
import subprocess
from simple_salesforce import Salesforce

def parse_iso_datetime(datetime_str):
    """
        Function to parse the datetime string with milliseconds
    """
    datetime_pattern = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})")
    match = datetime_pattern.search(datetime_str)
    if match:
        datetime_without_milliseconds = match.group(1)
        return datetime.datetime.fromisoformat(datetime_without_milliseconds)
    return None

def get_salesforce_connection(alias):
    """
        Connect to Salesforce using the Salesforce CLI and Simple Salesforce
    """
    # production domain = 'login'
    # sandbox domain = 'test'
    domain = 'login'
    sfdx_cmd = subprocess.Popen(f'sf org display --target-org {alias} --json',
                                shell=True,stdout=subprocess.PIPE)
    sfdx_info = json.loads(sfdx_cmd.communicate()[0])

    access_token = sfdx_info['result']['accessToken']
    instance_url = sfdx_info['result']['instanceUrl']

    return Salesforce(instance_url=instance_url,session_id=access_token,domain=domain)

def is_sandbox_eligible(start_date):
    """
        Determine if sandbox is eligible.
        Sandbox type refresh intervals:
            Developer Sandbox: 1 day
            Developer Pro Sandbox: 1 day
            Partial Data Sandbox: 5 days
            Full Copy Sandbox: 29 days
    """
    if not start_date:
        return False
    current_time = datetime.datetime.now()
    delta = current_time - start_date
    return delta.days >= 1

def find_eligible_sandbox(records):
    """
        Parse the records for an elgibile sandbox.
    """
    elgible_sandbox_info = {}
    sandbox_id = None

    for item in records:
        sandbox_name_str = item.get('SandboxName')
        start_date_str = item.get('StartDate')
        sandbox_status = item.get('Status')
        if sandbox_status in {'Deleted', 'Deleting'}:
            continue
        if sandbox_name_str not in elgible_sandbox_info:
            start_date = parse_iso_datetime(start_date_str)
            if is_sandbox_eligible(start_date):
                elgible_sandbox_info[sandbox_name_str] = (sandbox_name_str, start_date)
                sandbox_id = item.get('SandboxInfoId')
                break

    return sandbox_id, elgible_sandbox_info
