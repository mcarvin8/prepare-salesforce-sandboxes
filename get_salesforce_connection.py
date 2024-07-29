"""
    Functions used to create the Simple Salesforce connection using the Salesforce CLI.
"""
import json
import subprocess
from simple_salesforce import Salesforce

def get_salesforce_connection_alias(alias):
    """
        Connect to Salesforce using the Salesforce CLI and Simple Salesforce via an alias
    """
    sfdx_cmd = subprocess.run(f'sf org display --target-org {alias} --json',
                                 check=True, shell=True, stdout=subprocess.PIPE)
    sfdx_info = json.loads(sfdx_cmd.stdout)

    access_token = sfdx_info['result']['accessToken']
    instance_url = sfdx_info['result']['instanceUrl']
    api_version = sfdx_info['result']['apiVersion']
    if 'sandbox' in instance_url:
        domain = 'test'
    else:
        domain = 'login'
    return Salesforce(instance_url=instance_url,session_id=access_token,domain=domain,version=api_version)

def get_salesforce_connection_url(url):
    """
        Connect to Salesforce using the Salesforce CLI and Simple Salesforce via a URL
        Requires Salesforce CLI 2.24.4 or newer
    """
    login_cmd = f'echo {url} | sf org login sfdx-url --set-default --sfdx-url-stdin -'
    subprocess.run(login_cmd, check=True, shell=True)
    display_cmd = subprocess.run('sf org display --json',
                                 check=True, shell=True, stdout=subprocess.PIPE)
    sfdx_info = json.loads(display_cmd.stdout)

    access_token = sfdx_info['result']['accessToken']
    instance_url = sfdx_info['result']['instanceUrl']
    api_version = sfdx_info['result']['apiVersion']
    if 'sandbox' in instance_url:
        domain = 'test'
    else:
        domain = 'login'
    return Salesforce(instance_url=instance_url,session_id=access_token,domain=domain,version=api_version)
