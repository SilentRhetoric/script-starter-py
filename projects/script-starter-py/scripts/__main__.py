import logging
from algokit_utils.config import config
from algokit_utils import AlgoAmount, AlgorandClient, PaymentParams
from dotenv import load_dotenv

config.configure(populate_app_call_resources=True)

# Set up logging and load environment variables
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)-10s: %(message)s"
)
logger = logging.getLogger(__name__)
logger.info("Loading .env")
load_dotenv()


# --------------------------- Main Logic --------------------------- #


def main() -> None:
    algorand = AlgorandClient.from_environment()
    alice = algorand.account.from_environment("ALICE", AlgoAmount(algo=100))
    bob = algorand.account.from_environment("BOB", AlgoAmount(algo=100))

    pay_result = algorand.send.payment(
        PaymentParams(
            sender=alice.address,
            receiver=bob.address,
            amount=AlgoAmount(algo=2),
            note=b"Thanks, Bob!"
            )
        )
    print(f"Transaction confirmed with ID: {pay_result.tx_id}")


if __name__ == "__main__":
    main()
