from dotenv import load_dotenv
import logging
from logging import Logger
import os
import typer

# Load environment variables from the .env file
load_dotenv()

# DEFINITIONS


def main(
    log_level: int = logging.INFO,
) -> None:
    logger: Logger = logging.getLogger(__name__)
    logging.basicConfig(level=log_level)
    logger.info(f"Script has been launched")
    logger.info(f"Value of env file is : {os.getenv('value1')}")
    



if __name__ == "__main__":
    typer.run(main)