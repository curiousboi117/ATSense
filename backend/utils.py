import logging
import os

# Configure basic logging for the backend
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("atsense")

def get_project_root() -> str:
    """
    Returns the absolute path to the backend directory.
    """
    return os.path.dirname(os.path.abspath(__file__))
