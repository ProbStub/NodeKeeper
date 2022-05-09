"""
    Creates a new job on the oracle node. Requires unique job name, id & oracle address in job spe.

    Args:
        job_spec_file (string): Fully qualified path to TOML file.
        method (string): Oracle query method. Default "api" anything else attempts ChainLink CLI.
        session (requests.Session()): Authenticated HTTP session. Can be obtained from login().

    Returns:
        None or api error response.

"""
import os
import subprocess
from os import getenv
import uuid
import hashlib
import time
import json
import toml
import requests
import dotenv

def create_node_job(job_spec_file, method="api", session=None):
    """
    Creates a new job on the oracle node. Needs unique job name, id & oracle address in job spec.

    Args:
        job_spec_file (string): Fully qualified path to TOML file.
        method (string): Oracle query method. Default "api" anything else attempts ChainLink CLI.
        session (requests.Session): Authenticated HTTP session. Can be obtained from login().

    Returns:
        requests object or api error response.

    """
    node_url = getenv("NODE_URL") + ":" + getenv("NODE_PORT")
    job_create_err = None
    job_create_out = None
    node_session = session
    if method == "api":
        job_spec_text = ""
        with open(job_spec_file, ) as f:
            job_spec_text = f.read()
        query_url = node_url + "/query"
        query_dict = {
            "operationName": "CreateJob",
            "variables": {
                "input": {
                    "TOML": job_spec_text
                }
            },
            "query": "mutation CreateJob($input: CreateJobInput!) {"
                     "\n  createJob(input: $input) {"
                     "\n    ... on CreateJobSuccess {"
                     "\n      job {"
                     "\n        id"
                     "\n        __typename"
                     "\n      }"
                     "\n      __typename"
                     "\n    }"
                     "\n    ... on InputErrors {"
                     "\n      errors {"
                     "\n        path"
                     "\n        message"
                     "\n        code"
                     "\n        __typename"
                     "\n      }"
                     "\n      __typename"
                     "\n    }"
                     "\n    __typename"
                     "\n  }"
                     "\n}"
                     "\n"
        }
        req_ret = node_session.post(query_url, json.dumps(query_dict))

        if req_ret.ok is False:
            job_create_err = "ERROR Job creation error: " + str(req_ret.reason)
        else:
            job_create_out = req_ret.json()
    else:
        jobs_p = subprocess.Popen(["chainlink", "jobs", "create", job_spec_file])
        job_create_out, job_create_err = jobs_p.communicate()
    return job_create_err


def get_node_jobs(method="api", session=None):
    """
    Retrieves list of existing jobs on the oracle node.

    Args:
        method (string): Oracle query method. Default "api" anything else attempts ChainLink CLI
        session (requests.Session()): Authenticated HTTP session. Can be obtained from login()

    Returns:
        A list of jobs and an api error response if aplicable.

    """
    node_url = getenv("NODE_URL") + ":" + getenv("NODE_PORT")
    job_list_err = None
    job_list_out = None
    node_session = session

    if method == "api":
        query_url = node_url+"/query"
        query_dict = {
            "operationName": "FetchJobs",
            "variables": {
                "offset": 0,
                "limit": 1000
            },
            "query": "fragment JobsPayload_ResultsFields on Job {"
                     "\n  id"
                     "\n  name"
                     "\n  externalJobID"
                     "\n  createdAt"
                     "\n  spec {"
                     "\n    __typename"
                     "\n    ... on OCRSpec {"
                     "\n      contractAddress"
                     "\n      keyBundleID"
                     "\n      transmitterAddress"
                     "\n      __typename"
                     "\n    }"
                     "\n  }"
                     "\n  __typename"
                     "\n}"
                     "\n"
                     "\nquery FetchJobs($offset: Int, $limit: Int) {"
                     "\n  jobs(offset: $offset, limit: $limit) {"
                     "\n    results {"
                     "\n      ...JobsPayload_ResultsFields"
                     "\n      __typename"
                     "\n    }"
                     "\n    metadata {"
                     "\n      total"
                     "\n      __typename"
                     "\n    }"
                     "\n    __typename"
                     "\n  }"
                     "\n}"
                     "\n"
        }
        req_ret = node_session.post(query_url, json.dumps(query_dict))

        if req_ret.text.lower().find("error") > 0:
            job_list_err = "ERROR - Job retrieval error: " + str(req_ret.text)
        else:
            job_list_out = req_ret.json()["data"]["jobs"]["results"]
    else:
        job_list_p = subprocess.Popen(["chainlink",
                                       "--json", "jobs", "list"],
                                      stdout=subprocess.PIPE)
        job_list_out, job_list_err = job_list_p.communicate()
        job_list_out = json.loads(job_list_out)

    return job_list_err, job_list_out


def get_node_wallets(method="api", session=None):
    """
    Retrieves list of wallet addresses on the oracle node.

    Args:
        method (string): Oracle query method. Default "api" anything else attempts ChainLink CLI
        session (requests.Session()): Authenticated HTTP session. Can be obtained from login()

    Returns:
        A list of wallet addresses registered on the oracle node and
         an api error response if applicable.

    """
    node_url = getenv("NODE_URL") + ":" + getenv("NODE_PORT")
    key_list_err = None
    key_list_out = None
    node_session = session

    if method == "api":
        query_url = node_url+"/query"
        query_dict = {
            "operationName": "FetchETHKeys",
            "variables": {},
            "query": "fragment ETHKeysPayload_ResultsFields on EthKey {\n  "
                     "address\n  "
                     "chain {\n    "
                     "id\n    __typename\n  }\n  "
                     "createdAt\n  "
                     "ethBalance\n  "
                     "isFunding\n  "
                     "linkBalance\n  __typename\n}"
                     "\n\nquery FetchETHKeys {\n  "
                     "ethKeys {\n    "
                     "results {\n"
                     "      ...ETHKeysPayload_ResultsFields\n      __typename\n    }\n"
                     "    __typename\n  }\n}\n"
        }
        req_ret = node_session.post(query_url, json.dumps(query_dict))

        if req_ret.text.lower().find("error") > 0:
            key_list_err = "ERROR - Key retrieval error: " + str(req_ret.text)
        else:
            key_list_out = req_ret.json()["data"]["ethKeys"]["results"]
    else:
        key_list_p = subprocess.Popen(["chainlink",
                                       "--json", "keys", "eth", "list"],
                                      stdout=subprocess.PIPE)
        key_list_out, key_list_err = key_list_p.communicate()
        key_list_out = json.loads(key_list_out)
    return key_list_err, key_list_out


def node_login(method="api"):
    """
    Authenticates a user with login credentials against the oracle node

    Args:
        method (string): Oracle query method. Default "api" anything else attempts ChainLink CLI

    Returns:
        requests.Session() with an authenticated HTTP session and any applicable error string

    """

    node_userid = getenv("NODE_USERID")
    node_userpw = getenv("NODE_USERPW")
    node_url = getenv("NODE_URL")+":"+getenv("NODE_PORT")
    session = requests.Session()
    auth_err = None
    if method == "api":
        login_url = node_url+"/sessions"
        node_auth_params = {"email": node_userid,
                            "password": node_userpw}
        req_ret = session.post(login_url, json.dumps(node_auth_params))
        if req_ret.text.lower().find("error") > 0:
            auth_err = "ERROR - Login error: " + str(req_ret.text)

    else:
        # Write to temp file and remove after read. chainlink command does not allow pw piping
        with open("credentials.txt", "utf-8") as file:
            file.write(node_userid + "\n" + node_userpw)
        # Ensure chainlink is in path (~/go/bin has been loaded to path)
        auth_p = subprocess.Popen(["chainlink", "admin", "login", "-f", "credentials.txt"])
        auth_out, auth_err = auth_p.communicate()
        os.system("rm  credentials.txt")
    return auth_err, session
