from __future__ import annotations

import os

from dotenv import load_dotenv
from py_builder_signing_sdk.config import BuilderApiKeyCreds, BuilderConfig
from py_clob_client.client import ClobClient

from pmls.constants import (
    DEFAULT_CLOB_CHAIN_ID,
    DEFAULT_CLOB_HOST,
    ENV_CLOB_API_KEY,
    ENV_CLOB_API_PASSPHRASE,
    ENV_CLOB_API_SECRET, 
    ENV_CLOB_PRIVATE_KEY,
    FUNDER_ADDR
)


def public_client() -> ClobClient:
    return ClobClient(host=DEFAULT_CLOB_HOST, chain_id=DEFAULT_CLOB_CHAIN_ID)

def load_clob_credentials_from_env() -> dict[str, str]:
    load_dotenv(dotenv_path=".env", override=False)
    
    credentials = {
        ENV_CLOB_PRIVATE_KEY: os.getenv(ENV_CLOB_PRIVATE_KEY, ""),
        ENV_CLOB_API_KEY: os.getenv(ENV_CLOB_API_KEY, ""),
        ENV_CLOB_API_SECRET: os.getenv(ENV_CLOB_API_SECRET, ""),
        ENV_CLOB_API_PASSPHRASE: os.getenv(ENV_CLOB_API_PASSPHRASE, ""),
        FUNDER_ADDR: os.getenv(FUNDER_ADDR, ""),
    }
    
    missing = [name for name in credentials if not credentials.get(name)]
    if missing:
        missing_csv = ", ".join(missing)
        raise ValueError(f"Missing required CLOB credentials in environment: {missing_csv}")

    return credentials
    
def create_clob_client_from_env() -> ClobClient:
    credentials = load_clob_credentials_from_env()

    l1_client = ClobClient(
        host=DEFAULT_CLOB_HOST,
        chain_id=DEFAULT_CLOB_CHAIN_ID,
        key=credentials[ENV_CLOB_PRIVATE_KEY], 
    )

    l1_cred = l1_client.create_or_derive_api_creds() 
    
    builder_config = BuilderConfig(
        local_builder_creds=BuilderApiKeyCreds(
            key=credentials[ENV_CLOB_API_KEY],
            secret=credentials[ENV_CLOB_API_SECRET],
            passphrase=credentials[ENV_CLOB_API_PASSPHRASE],
        )
    )
    
    return ClobClient(
        host=DEFAULT_CLOB_HOST,
        chain_id=DEFAULT_CLOB_CHAIN_ID,
        key=credentials[ENV_CLOB_PRIVATE_KEY],
        creds=l1_cred,
        signature_type=1,
        funder=credentials[FUNDER_ADDR],
        builder_config=builder_config,
    )