import logging
from time import sleep
from algokit_utils.config import config
from algokit_utils import (
    AlgoAmount,
    AlgorandClient,
    AssetCreateParams,
    AssetOptInParams,
    AssetTransferParams,
    PaymentParams,
)
from dotenv import load_dotenv

config.configure(populate_app_call_resources=True)

# Set up logging and load environment variables
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)-10s: %(message)s"
)
logger = logging.getLogger(__name__)
load_dotenv()


# --------------------------- Main Logic ------------------------------------- #
# Uncomment the code below one step at a time to follow along with the tutorial


def main() -> None:
    print("👋 Enjoy this Python Utils tutorial by the Developer Relations team!")

    # -------------------------------- Step 1 -------------------------------- #
    # Initialize an Algorand Client that will be used to interact with the chain
    # For learning and development, use LocalNet so that you can reset the chain
    # as needed and have access to the genesis accounts with all 10B Algo
    algorand = AlgorandClient.default_localnet()

    # -------------------------------- Step 2 -------------------------------- #
    # Create two LocalNet accounts, Alice and Bob, funded with 100 Algos each
    alice = algorand.account.from_environment("ALICE", AlgoAmount(algo=100))
    bob = algorand.account.from_environment("BOB", AlgoAmount(algo=100))
    print(
        f"\nAlice's generated account address: {alice.address}. \nView her account on Lora at https://lora.algokit.io/localnet/account/{alice.address}."
    )
    print(
        f"\nBob's generated account address: {bob.address}. \nView his account on Lora at https://lora.algokit.io/localnet/account/{bob.address}."
    )

    # -------------------------------- Step 3 -------------------------------- #
    # Alice sends an Algo payment transaction to Bob
    pay_result = algorand.send.payment(
        PaymentParams(
            sender=alice.address,
            receiver=bob.address,
            amount=AlgoAmount(
                algo=2
            ),  # The AlgoAmount class is a helper to be explicit about amounts between microAlgos and Algos
            note=b"Hi, Bob!",
        )
    )
    print(
        f"\nPay transaction confirmed with TxnID: {pay_result.tx_id}. \nView it on Lora at https://lora.algokit.io/localnet/transaction/{pay_result.tx_id}."
    )

    # -------------------------------- Step 4 -------------------------------- #
    # Alice creates an Algorand Standard Asset (ASA)
    # See the docs to learn which parameters are (im)mutable:
    # https://dev.algorand.co/concepts/assets/overview/
    create_asset_result = algorand.send.asset_create(
        AssetCreateParams(
            sender=alice.address,
            asset_name="My First ASA",  # A human-readable name for the asset
            unit_name="MFA",  # A short ticker; this is not a unique identifier
            total=1_000_000_000_000,  # The true supply of indivisible units
            decimals=6,  # Used for displaying the asset amount off chain
            default_frozen=False,  # This asset can be transferred freely
            manager=alice.address,  # Account that can change the asset's config
            reserve=alice.address,  # Account to hold non-circulating supply
            freeze=alice.address,  # Account that can freeze asset holdings
            clawback=alice.address,  # Account that can revoke asset holdings
            url="https://algorand.co/algokit",  # Often used to point to metadata
            note=b"This is my first Algorand Standard Asset!",
        )
    )
    # Store the Asset ID Alice created in a variable for later use in the script
    # This UInt64 Asset ID is a unique identifier for the asset on the chain
    created_asset = create_asset_result.asset_id
    print(
        f"\nAsset ID {created_asset} create transaction confirmed with TxnID: {create_asset_result.tx_id}.\nView it on Lora at https://lora.algokit.io/localnet/asset/{created_asset}."
    )

    # -------------------------------- Step 5 -------------------------------- #
    # Get ASA information from algod's /v2/assets REST API endpoint
    # The response will contain all of the asset's current parameters
    asset_info = algorand.asset.get_by_id(created_asset)
    print(
        f"\nAsset information from algod's /v2/assets/{{asset-id}} REST API endpoint: {asset_info}. \nLearn about and explore the algod REST API at https://dev.algorand.co/reference/rest-api/overview/#algod-rest-endpoints."
    )

    # -------------------------------- Step 6 -------------------------------- #
    # Bob opts in to the ASA so that he will be able to hold it
    bob_opt_in_result = algorand.send.asset_opt_in(
        AssetOptInParams(
            sender=bob.address,
            asset_id=created_asset,
        )
    )
    print(
        f"\nAsset opt-in transaction confirmed with TxnID: {bob_opt_in_result.tx_id}. \nView it on Lora at https://lora.algokit.io/localnet/transaction/{bob_opt_in_result.tx_id}."
    )

    # -------------------------------- Step 7 -------------------------------- #
    # Alice sends some of the ASA to Bob
    send_asset_result = algorand.send.asset_transfer(
        AssetTransferParams(
            sender=alice.address,
            receiver=bob.address,
            asset_id=created_asset,
            amount=3_000_000,  # The amount is in the smallest unit of the asset
            note=b"Have a few of my first ASA!",
        )
    )
    print(
        f"\nAsset transfer transaction confirmed with TxnID: {send_asset_result.tx_id}. \nView it on Lora at https://lora.algokit.io/localnet/transaction/{send_asset_result.tx_id}."
    )

    # -------------------------------- Step 8 -------------------------------- #
    # Get Bob's account information
    # This will include all of the current ledger state for Bob's account,
    # including Algo balance, asset balances with some asset information,
    # as well as application-related information like local state, and more.
    bob_account_info = algorand.account.get_information(bob.address)
    print(
        f"\nBob's account information from algod's /v2/accounts/{{address}} REST API endpoint: \n{bob_account_info}. \nLearn about and explore the algod REST API at https://dev.algorand.co/reference/rest-api/overview/#algod-rest-endpoints."
    )

    # -------------------------------- Step 9 -------------------------------- #
    # Build an atomic transaction group with two transactions
    # Utils provides this fluent way of chaining method calls to build the group
    # rather than using the SDK to create transactions and manually group them.
    # These transactions will be either confirmed or rejected together.
    group_result = (
        algorand.send.new_group()
        .add_payment(
            PaymentParams(
                sender=bob.address,
                receiver=alice.address,
                amount=AlgoAmount(algo=1),
                note=b"Thanks, Alice!",
            )
        )
        .add_asset_transfer(
            AssetTransferParams(
                sender=bob.address,
                receiver=alice.address,
                asset_id=created_asset,
                amount=1_000_000,
                note=b"Sending back one of your token!",
            )
        )
    ).send()
    print(
        f"\nAtomic transaction group confirmed with first TxnID: {group_result.tx_ids[0]}. \nView it on Lora at https://lora.algokit.io/localnet/transaction/{group_result.tx_ids[0]}."
    )

    # -------------------------------- Step 10 -------------------------------- #
    # Search the indexer for the asset transfer transactions
    # We add a short delay here because indexer can be a bit slow on LocalNet.
    # Engineering will be working on improving this in the future.
    print(
        "\nSleeping for 30 seconds to let the LocalNet indexer to catch up, which can sometimes take a moment."
    )
    sleep(30)

    # Here the AlgorandClient exposes the underlying SDK indexer client to build
    # the query with various parameters. Be mindful of how broad the query is
    # to avoid long-running requests or needing to page through many results.
    transfer_search_results = algorand.client.indexer.search_transactions(
        asset_id=created_asset,
        txn_type="axfer",
    )
    found_txn_ids = [txn["id"] for txn in transfer_search_results["transactions"]]
    print(
        f"\nAsset transfer transaction IDs found by searching the indexer: {found_txn_ids}. \nLearn about and explore the indexer REST API at https://dev.algorand.co/reference/rest-api/overview/#indexer-rest-endpoints."
    )

    print("🙌 Congrats on interacting with the Algorand chain with Python!")


if __name__ == "__main__":
    main()
