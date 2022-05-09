# TL;DR
NodeKeeper is a Python wrapper to ChainLink nodes API. This allows
you to easily create integration tests on a local development network.
Additionally, you may use NodeKeeper to automate your node operations.

![GitHub commits since latest release (by date) for a branch](https://img.shields.io/github/commits-since/Probstub/NodeKeeper/0.0.1/master)
![GitHub branch checks state](https://img.shields.io/github/checks-status/probstub/NodeKeeper/master)
![Codacy grade](https://img.shields.io/codacy/grade/23890bea152e49b296f411d83a85619c)

# Purpose
Testing for smart contracts that reference oracles is often tedious 
on live chains, and slow. Yet, everyone wants to test as much as possible, 
given many smart contracts manage money in some way. 

NodeKeeper allows to integrate more complex test cases into
your testing strategy and run them faster. ChainLinks oracles offer a hidden
API which is abstracted by the NodeKeeper API. 

You can use the NodeKeeper
functions to create new jobs, change keys and perform many other activities
that usually would require either the ChainLink CLI or web UI.

Performing such activities on a ChainLink node not installed on your local
machine either requires many clicks on a browser based UI or heavy shell
scripting to call up SSH sessions into your node. Neither may be very practical
if all you want to do is write integration tests for your software

# Installation

NodeKeeper is available as a Python package. Additionally, you may choose to 
install from source.

Installation of the Python package:
```
pip install -i cl-node-keeper
```

Installation from source:
```
git clone https://github.com/ProbStub/NodeKeeper
cd NodeKeeper
python3 -m pip install --upgrade build
python3 -m build 
pip install dist/dist/cl-node-keeper-0.0.2.tar.gz
```

# Examples
A basic use case for NodeKeeper is provided in the [examples](examples) folder.
To run the examples please follow the steps below. If you have a running ChainLink
oracle node you may skip step 2-4 and just modify your ``.env`` file with the 
applicable credentials. The below assumes that you own a funded Ethereum
wallet (with both ETH and LINK).

Example run instructions:
1. Rename the file ``dotenv`` to ``.env`` provided in the
   [infrastructure](examples/infrastructure/) folder.


2. Set values for the infrastructure configuration in the ``.env`` file. At least provide values 
   for ``chainlink_private_key``, ``chainlink_node_user`` and ``chainlink_node_pw``. 
   
   **Note:** that these three values must match the ``NODE_*`` parameters in the 
   blockchain section (step #5).


3. If you do not have a kubernetes cluster available you may start a local ``minikube`` cluster
   running:
   ```
   cd examples/infrastructure/local/scripts/cluster/ 
   ./generate.sh 
   ./start.sh
   ```

4. If you do have an available kubernetes cluster create the ChainLink oracle by running the below.
   
   **Note:** This will create kubernetes resources in the default namespace!
   ```
   cd examples/infrastructure/local/scripts/columndb/ 
   ./generate.sh 
   ./start.sh
   cd examples/infrastructure/local/scripts/chainlinknode/ 
   ./generate.sh 
   ./start.sh
   ```
   If the infrastructure setup worked you should be able to access the ChainLink node web UI at
   [http://localhost:6688/]( http://localhost:6688/). Try to login with the credentials
   defined in step #2 


5. Enter your wallets ``PRIVATE_KEY``, your ``WEB3_INFURA_PROJECT_ID``as well as the
   ``NODE_USERID``and ``NODE_USERPW`` into the parameters in the blockchain section of ``.env`` 
   The ``NODE_URL`` and ``NODE_PORT`` may be adapted if you are running your own node.


6. To test NodeKeeper run the ``create_oracle.py`` script with brownie and observe how 
   the node wallet is retrieved, check for a blance, funded and jobs are created through the API:
   ```
   brownie run scripts/create_oracle.py --network rinkeby
   ```


# Yes, Please!

This is not my main project and pull requests are welcome.

The original code was created as part of another project, and I decided
to contribute here during the ChainLink 2022 SpringHackathon. 
Documentation, testing, coding standards are all under heavy development.
