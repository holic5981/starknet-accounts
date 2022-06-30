import asyncio
import sys
import json

sys.path.append('./')

from utils import deploy_testnet, print_n_wait, mission_statement, get_evaluator, devnet_funding
from starknet_py.net.client import Client
from starkware.starknet.public.abi import get_selector_from_name

with open("./hints.json", "r") as f:
  data = json.load(f)

async def main():
    mission_statement()
    print("\t 1) deploy an account contract with an '__execute__' entrypoint")
    print("\t 2) fetch the 'random' storage_variable from the validator contract")
    print("\t 3) pass 'random' via calldata to your account contract\n")

    #
    # MISSION 1
    #
    # client = Client("testnet")
    client = Client(net=data['DEVNET_URL'], chain="testnet")

    #
    # MISSION 2
    #
    hello, hello_addr = await deploy_testnet(client=client, contract_path=data['HELLO'])

    await devnet_funding(data, hello_addr)

    evaluator, evaluator_address = await get_evaluator(client, data['EVALUATOR'])
    (random, ) = await evaluator.functions["get_random"].call()

    prepared = hello.functions["__execute__"].prepare(
        contract_address=evaluator_address,
        selector=get_selector_from_name("validate_hello"),
        calldata_len=2,
        calldata=[random, data['DEVNET_ACCOUNT']['ADDRESS']]) # MISSION 3
    invocation = await prepared.invoke(max_fee=data['MAX_FEE'])

    await print_n_wait(client, invocation)

asyncio.run(main())
