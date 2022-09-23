import sys
import json
import asyncio
import eth_keys

sys.path.append('./tutorial')

from console import blue_strong, blue, red
from utils import compile_deploy, invoke_tx_hash, print_n_wait, fund_account, get_evaluator, get_client, to_uint
from starkware.starknet.public.abi import get_selector_from_name
from starknet_py.net.models import InvokeFunction

with open("./config.json", "r") as f:
  data = json.load(f)

async def main():
    blue_strong.print("Your mission:")
    blue.print("\t 1) implement account contract interface 'get_nonce'")
    blue.print("\t 2) implement account contract interface 'get_signer'")
    blue.print("\t 3) deploy account contract")
    blue.print("\t 4) sign calldata")
    blue.print("\t 5) invoke check\n")

    pk = eth_keys.keys.PrivateKey(b'\x01' * 32)

    client = get_client()

    sig3, sig3_addr = await compile_deploy(client=client, contract=data['SIGNATURE_3'], args=[data['ETHEREUM_ADDRESS']], account=True)

    reward_account = await fund_account(sig3_addr)
    if reward_account == "":
      red.print("Account must have ETH to cover transaction fees")
      return
      
    _, evaluator_address = await get_evaluator(client)
    #
    # Format calldata
    # 

    #
    # ACTION ITEM 3: call @view 'get_nonce' to include in tx signature
    #
    calldata = [evaluator_address, get_selector_from_name("validate_signature_3"), 1, reward_account]

    #
    # Submit the invoke transaction
    #
    nonce = await client.get_contract_nonce(sig3_addr)

    hash = invoke_tx_hash(sig3_addr, calldata, nonce)

    signature = pk.sign_msg_hash((hash).to_bytes(32, byteorder="big"))
    sig_r = to_uint(signature.r)
    sig_s = to_uint(signature.s)

    invoke = InvokeFunction(
      calldata=calldata,
      signature=[signature.v, *sig_r, *sig_s],
      max_fee=data['MAX_FEE'],
      version=1,
      nonce=nonce,
      contract_address=sig3_addr,
    )

    resp = await sig3.send_transaction(invoke)
    await print_n_wait(client, resp)

asyncio.run(main())
