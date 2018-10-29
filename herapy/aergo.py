# -*- coding: utf-8 -*-

"""Main module."""

import json

from google.protobuf.json_format import MessageToJson
from herapy.grpc import blockchain_pb2
from herapy.transaction import Transaction

from . import account as acc
from . import comm
from . import block
from . import transaction
from .peer import Peer

class Aergo:
    def __init__(self):
        self.__account = None
        self.__comm = None

    @property
    def account(self):
        """
        Returns the account object.
        :return:
        """
        return self.__account

    def create_account(self, password):
        """
        Creates a new account with password `password`.
        :param password:
        :return:
        """
        self.__account = acc.Account(password)
        return self.__comm.create_account(address=self.__account.address, passphrase=password)

    def new_account(self, password, private_key=None):
        self.__account = acc.Account(password, private_key)
        if private_key is not None:
            self.get_account_state(self.__account.address)
        return self.__account

    def get_account_state(self, account=None):
        """
        Return the account state of account `account`.
        :param account:
        :return:
        """
        if self.__comm is None:
            return None

        if account is None:
            address = self.__account.address
        else:
            address = account.address

        state = self.__comm.get_account_state(address)

        if account is None:
            self.__account.state = state
        else:
            account.state = state

        return MessageToJson(state)

    def connect(self, target):
        """
        Connect to the gRPC server running on port `target` e.g. target="localhost:7845".
        :param target:
        :return:
        """
        if target is None:
            raise ValueError('need target value')

        self.__comm = comm.Comm(target)
        self.__comm.connect()

    def disconnect(self):
        """
        Disconnect from the gRPC server.
        """
        if self.__comm is not None:
            self.__comm.disconnect()

    def get_blockchain_status(self):
        """
        Returns the highest block hash and block height so far.
        :return:
        """
        if self.__comm is None:
            return None, -1

        status = self.__comm.get_blockchain_status()
        return status.best_block_hash, status.best_height

    def get_block(self, block_hash=None, block_height=-1):
        """
        Returns information about block `block_hash`.
        :param block_hash:
        :param block_height:
        :return:
        """
        if self.__comm is None:
            return None

        if block_height > 0:
            query = block_height.to_bytes(8, byteorder='little')
        else:
            if isinstance(block_hash, str):
                block_hash = block.Block.decode_block_hash(block_hash)

            query = block_hash

        result = self.__comm.get_block(query)
        b = block.Block()
        b.info = result
        return b

    def get_node_accounts(self):
        """
        Returns a list of all node accounts.
        :return:
        """
        result = self.__comm.get_accounts()
        accounts = []
        for a in result.accounts:
            account = acc.Account("", empty=True)
            account.address = a.address
            accounts.append(account)

        return accounts

    def get_peers(self):
        """
        Returns a list of peers.
        :return:
        """
        result = self.__comm.get_peers()
        peers = []
        for i in range(len(result.peers)):
            p = result.peers[i]
            s = result.states[i]
            peer = Peer()
            peer.info = p
            peer.state = s
            peers.append(peer)

        return peers

    def get_node_state(self, timeout=1):
        """
        Returns information about the node state.
        :return:
        """
        result = self.__comm.get_node_state(timeout)
        json_txt = result.value.decode('utf8').replace("'", '"')
        return json.loads(json_txt)

    def get_tx(self, tx_hash):
        """
        Returns info on transaction with hash `tx_hash`.
        :param tx_hash:
        :return:
        """
        return self.__comm.get_tx(tx_hash)

    def lock_account(self, address, passphrase):
        """
        Locks the account with address `address` with the passphrase `passphrase`.
        :param address:
        :param passphrase:
        :return:
        """
        return self.__comm.lock_account(address, passphrase)

    def unlock_account(self, address, passphrase):
        """
        Unlocks the account with address `address` with the passphrase `passphrase`.
        :param address:
        :param passphrase:
        :return:
        """
        return self.__comm.unlock_account(address=address, passphrase=passphrase)

    # TODO can we have limit, price defaults of 0?
    def send(self, from_address, to_address, amount, payload, limit, price):
        """
        Sends `amount` of currency from account `from_address` to account `to_address` with payload `payload` (can be blank bytestring b"").
        Necessary to unlock accounts before sending/receiving transactions.
        :param from_address:
        :param to_address:
        :param amount:
        :param payload:
        :param limit:
        :param price:
        :return:
        """
        normal_tx_type = blockchain_pb2.TxType.Value(name='NORMAL')
        incremented_nonce = self.__account.increment_nonce()
        tx_body = blockchain_pb2.TxBody(nonce=incremented_nonce,
                                        account=from_address,
                                        recipient=to_address,
                                        amount=amount,
                                        payload=payload,
                                        limit=limit,
                                        price=price,
                                        type=normal_tx_type)

        tx = blockchain_pb2.Tx(body=tx_body)
        tx_hash = Transaction.calculate_tx_hash(tx)
        tx.hash = tx_hash

        signed_tx = self.sign_tx(tx)
        return self.send_tx(signed_tx)

    def sign_tx(self, tx):
        """
        Signs the transaction `tx` with the signing key in the __account object in Aergo.
        :param tx:
        :return:
        """
        tx_hash = Transaction.calculate_tx_hash(tx)
        tx_signature = self.__account.sign_message(tx_hash)
        tx.body.sign = tx_signature
        tx.hash = tx_hash
        return tx

    def send_tx(self, tx):
        """
        Sends the transaction `tx`.
        :param tx:
        :return:
        """
        ""
        return self.__comm.send_tx(tx)

    def commit_tx(self, txs):
        """
        Send a set of transactions `txs` simultaneously.
        :param txs:
        :return:
        """
        tx_list = blockchain_pb2.TxList()
        tx_list.txs.extend(txs)
        return self.__comm.commit_tx(tx_list)

    def get_peers(self):
        """
        Return a list of peers.
        :return:
        """
        return self.__comm.get_peers()

