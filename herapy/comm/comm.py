# -*- coding: utf-8 -*-

import grpc
import base58

from google.protobuf.json_format import MessageToJson

from herapy.grpc import rpc_pb2
from herapy.grpc import rpc_pb2_grpc
from herapy.grpc import account_pb2

class Comm:
    def __init__(self, target):
        self.channel = grpc.insecure_channel(target)
        self.rpc_stub = rpc_pb2_grpc.AergoRPCServiceStub(self.channel)
        self.result = None

    def get_result_to_json(self):
        return MessageToJson(self.result)

    # XXX works not well. what for?
    def get_node_state(self, timeout):
        timeout_b = timeout.to_bytes(8, byteorder='little')
        single_bytes = rpc_pb2.SingleBytes()
        single_bytes.value = timeout_b
        self.result = self.rpc_stub.NodeState(single_bytes)
        return self.result

    def get_blockchain_status(self):
        self.result = self.rpc_stub.Blockchain(rpc_pb2.Empty())
        return self.result

    def get_block_headers(self, block_hash=b'', height=0, size=20, offset=0, order_by_asc=True):
        params = rpc_pb2.ListParams()
        params.hash = block_hash
        params.height = height
        params.size = size
        params.offset = offset
        params.asc = order_by_asc
        self.result = self.rpc_stub.ListBlockHeaders(params)
        return self.result

    def get_block(self, block_hash=None, block_height=0):
        single_bytes = rpc_pb2.SingleBytes()

        if block_hash is None:
            block_height_b = block_height.to_bytes(8, byteorder='little')
            single_bytes.value = block_height_b
        else:
            single_bytes.value = block_hash

        self.result = self.rpc_stub.GetBlock(single_bytes)
        return self.result

    def get_tx(self):
        pass

    def get_block_tx(self):
        pass

    def get_receipt(self):
        pass

    def get_abi(self):
        pass

    def send_tx(self):
        pass

    def commit_tx(self):
        pass

    def get_state(self):
        pass

    def get_account_state(self, account):
        self.result = self.rpc_stub.GetState(account)
        return self.result

    def get_account_state_from_address(self, address):
        account = account_pb2.Account()
        account.address = address
        return self.get_account_state(account)

    # XXX why?? remove it!!!!
    def create_account(self, passphrase):
        personal = rpc_pb2.Personal()
        personal.passphrase = passphrase
        self.result = self.rpc_stub.CreateAccount(personal)
        return self.result

    # return account list
    def get_accounts(self):
        self.result = self.rpc_stub.GetAccounts(rpc_pb2.Empty())
        return self.result

    def get_account_state_from_b58address(self, b58address):
        return self.get_account_state_from_address(base58.b58decode_check(b58address))

    # XXX why???
    # return locked account
    def lock_account(self, address, passphrase):
        personal = rpc_pb2.Personal()
        personal.account.address = address
        personal.passphrase = passphrase
        self.result = self.rpc_stub.LockAccount(personal)
        return self.result

    # XXX why???
    # return locked account
    def lock_account_from_b58address(self, b58address, passphrase):
        return self.lock_account(base58.b58decode_check(b58address), passphrase)

    # XXX why???
    # return unlocked account
    def unlock_account(self, address, passphrase):
        personal = rpc_pb2.Personal()
        personal.passphrase = passphrase
        personal.account.address = address
        self.result = self.rpc_stub.UnlockAccount(personal)
        return self.result

    # XXX why???
    # return unlocked account
    def unlock_account_from_b58address(self, b58address, passphrase):
        return self.unlock_account(base58.b58decode_check(b58address), passphrase)

    def sign_tx(self):
        pass

    def verify_tx(self):
        pass

    def query_contract(self):
        pass

    def get_peers(self):
        self.result = self.rpc_stub.GetPeers(rpc_pb2.Empty())
        return self.result

    def get_votes(self):
        pass

