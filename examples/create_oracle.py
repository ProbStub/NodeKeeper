"""
Programmatically deploys and configures a ChainLink Oracle.
Deployment success verification is established with a simple Oracle consumer request.

"""
import os
from os import getenv
import uuid
import hashlib
import time
import toml

import dotenv
from brownie import network, config, accounts
from brownie import Oracle, OracleConsumer, LinkToken, Contract

from cl_node_keeper.cl_node_keeper import \
    create_node_job, \
    get_node_jobs, \
    get_node_wallets, \
    node_login

# TODO: Add local develoment network example
def main(job_name="New Job"):
    """
    Runs an oracle creation using the brownie environment

    Args:
        job_name (string): Name of the job to create on the Chainlink node

    Returns:
        -
    """

    key_list_err = None
    key_list_out = None
    node_wallet_list = None

    dotenv.load_dotenv(".infrastructure/.env")
    # Ensure working directory is set to the current system component
    if os.getcwd().find(getenv("COMPONENT_RELATIVE_PATH")) < 0:
        os.chdir(os.getcwd() + "/" + getenv("COMPONENT_RELATIVE_PATH"))

    creator_addr = accounts.add(config["wallets"]["from_key"])

    # 1. Deploy Oracle contract and set address_link to the networks LINK contract address
    oracle_contract = Oracle.deploy(config["networks"][network.show_active()]["link_token"],
                                    {"from": creator_addr})

    # 2. Link Oracle contract to ChainLink node wallet (setFullfillment)
    node_wallet = None

    auth_err, node_session = node_login()
    if auth_err is None:
        key_list_err, key_list_out = get_node_wallets(session=node_session)
    else:
        print("ERROR: Chainlink node login failed!")

    if key_list_err is None:
        # Fetching the first wallet with eth >= 0.00001
        node_wallet_list = key_list_out
        for wallet in node_wallet_list:
            if float(wallet["ethBalance"]) >= 0.0001:
                node_wallet = wallet["address"]
                break
    if node_wallet is None:
        if len(node_wallet_list) > 0:
            node_wallet = node_wallet_list[0]["address"]
            print("WARNING: Node not founded. Adding min eth of creator to first node wallet!")
            fund_node_with_eth(node_wallet, creator_addr)
        else:
            print("ERROR: No node wallet found or insufficient funds in wallet(s)!")
    trx = oracle_contract.setFulfillmentPermission(node_wallet, True, {"from": creator_addr})
    trx.wait(1)

    # 3. Create a job at ChainLink node and insert the Oracle contract address
    job_location_root = getenv("JOBS_LOCATION_ROOT")
    job_file_extension = getenv("JOBS_FILE_EXTENSION")
    job_id = str(uuid.uuid1())
    job_name_collision = False

    job_spec = toml.load(job_location_root+"oracle_api_job_template."+job_file_extension)

    job_spec["contractAddress"] = oracle_contract.address
    job_spec["externalJobID"] = job_id

    job_spec["observationSource"] = job_spec["observationSource"].\
        replace("youroraclecontractaddress", oracle_contract.address, 2)

    # Job names must be unique... so need to check if a name exists fist
    if auth_err is None:
        job_list_err, job_list_out = get_node_jobs(session=node_session)
        if job_list_err is None:
            job_list = job_list_out
            for job in job_list:
                if job["name"] == job_name:
                    job_name_collision = True
        if job_name_collision:
            pseudo_random_id = hashlib.sha1(bytes(str(time.time_ns()), "utf-8")).hexdigest()[0:8]
            job_spec["name"] = job_name + "-" + pseudo_random_id
            print("WARNING: Job name exists. Did you want to do this? Job name changed to: "
                  + job_name + "-" + pseudo_random_id)
        else:
            job_spec["name"] = job_name
    else:
        print("ERROR: Chainlink node login failed!")

    job_spec_file = job_location_root+str(network.show_active())+"_"+job_id+"."+job_file_extension
    with open(job_spec_file, "w", encoding='utf-8') as file:
        toml.dump(job_spec, file)

    job_create_err = create_node_job(job_spec_file, session=node_session)
    if job_create_err is not None:
        print("ERROR: ChainLink job creation failed!")

    # 4. Fund ChainLink Oracle node wallet (ETH) and Oracle contract (LINK)
    fund_node_with_eth(node_wallet, creator_addr)
    fund_oracle_with_link(oracle_contract, creator_addr)

    # 5. Deploy and fund the Oracle consumer contract with Oracle
    oracle_consumer = OracleConsumer.deploy({"from": creator_addr})
    fund_oracle_with_link(oracle_consumer, creator_addr)

    # 6. Invoke the Oracle consumer with Oracle contract & job ID (CANNOT have ANY dashes!!)
    trx = oracle_consumer.requestEthereumPrice(oracle_contract, job_id.replace("-", "", 4),
                                               {"from": creator_addr})
    trx.wait(6)

    # 7. Report successful deployment and jobid (with/without dashes) and Oracle Address
    print("SUCCESS: Oracle deployed and consumer working nominally. ETH x 10:"
          + str(oracle_consumer.currentPrice()))


def fund_oracle_with_link(contract_addr, creator_addr):
    """
    Provides minimal amount of LINK token to an oracle contract.

    Args:
        contract_addr (string): Existing oracle contract address hex.
        creator_addr (string): Existing and LINK funded wallet address hex.

    Returns:
        -
    """

    link_initial_funding_amount = getenv("ORACLE_INITIAL_FUNDING_LINK")
    link_abi_download = getenv("ABI_DOWNLOAD")
    link_token = None

    if link_abi_download is True:
        # fetching online contract source for Link tokens
        link_token = Contract.from_explorer(config["networks"][network.show_active()]["link_token"])
    else:
        print("ERROR: This example required ABI code load from the chain. Check .env config!")
    link_token.transfer(contract_addr, link_initial_funding_amount, {"from": creator_addr})


def fund_node_with_eth(node_wallet_addr, creator_addr):
    """
    Provides minimal amount of ETH token to an oracle node.

    Args:
        node_wallet_addr (string): Existing oracle node wallet address hex.
        creator_addr (string): Existing and LINK funded wallet address hex.

    Returns:
        -
    """

    if int(network.web3.eth.get_balance(node_wallet_addr)) <= int(getenv("NODE_MIN_FUNDING_ETH")):
        creator_addr.transfer(node_wallet_addr, getenv("NODE_MIN_FUNDING_ETH"))

# EOF
