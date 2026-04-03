import random
import json
import hashlib
import time


def _make_tx() -> str:
    seed = str(time.time()) + str(random.random())
    return "0x" + hashlib.sha256(seed.encode()).hexdigest()[:62]


def mint_profile_nft(wallet: str, name: str, role: str, skills: list, score: float) -> dict:
    """Simulate minting a Soulbound NFT. Returns token metadata."""
    token_id  = str(random.randint(10000, 99999))
    tx_hash   = _make_tx()
    metadata  = {
        "name":          f"{name}'s Connectra Profile",
        "description":   f"Verified on-chain talent profile for {name} ({role})",
        "attributes": [
            {"trait_type": "Role",           "value": role},
            {"trait_type": "Skills",         "value": ", ".join(skills[:5])},
            {"trait_type": "Overall Score",  "value": score},
            {"trait_type": "Token Type",     "value": "Soulbound"},
        ],
        "image": "ipfs://QmMockHashPlaceholder/avatar.png",
    }
    ipfs_uri  = f"ipfs://Qm{hashlib.md5(token_id.encode()).hexdigest()[:40]}"
    explorer  = f"https://amoy.polygonscan.com/token/0xConnectraNFT?a={token_id}"

    return {
        "token_id":   token_id,
        "tx_hash":    tx_hash,
        "ipfs_uri":   ipfs_uri,
        "explorer":   explorer,
        "metadata":   metadata,
        "network":    "Polygon Amoy (Testnet)",
        "gas_used":   str(random.randint(80000, 140000)),
        "block":      str(random.randint(5_000_000, 9_999_999)),
    }


def mint_application_nft(talent_wallet: str, job_id: int, match_score: float) -> dict:
    """Simulate minting an Application Receipt NFT."""
    tx_hash = _make_tx()
    token_id = str(random.randint(200000, 299999))
    return {
        "token_id":  token_id,
        "tx_hash":   tx_hash,
        "explorer":  f"https://amoy.polygonscan.com/tx/{tx_hash}",
        "type":      "Application Receipt",
    }


def simulate_job_post(wallet: str, title: str, budget: int) -> dict:
    """Simulate posting a job to Polygon."""
    tx_hash = _make_tx()
    return {
        "tx_hash":  tx_hash,
        "contract": "0xConnectraJobRegistry",
        "block":    str(random.randint(5_000_000, 9_999_999)),
        "gas_used": str(random.randint(60000, 90000)),
        "explorer": f"https://amoy.polygonscan.com/tx/{tx_hash}",
    }


def simulate_hire(talent_wallet: str, amount_usdc: int) -> dict:
    """Simulate USDC escrow + hire NFT."""
    tx_hash   = _make_tx()
    nft_id    = str(random.randint(300000, 399999))
    return {
        "tx_hash":       tx_hash,
        "escrow_amount": amount_usdc,
        "work_nft_id":   nft_id,
        "explorer":      f"https://amoy.polygonscan.com/tx/{tx_hash}",
        "status":        "Escrowed",
    }


def short_hash(tx_hash: str, chars: int = 10) -> str:
    if not tx_hash:
        return "—"
    return tx_hash[:6] + "..." + tx_hash[-4:]


def format_wallet(wallet: str) -> str:
    if not wallet or len(wallet) < 10:
        return wallet or "—"
    return wallet[:6] + "..." + wallet[-4:]
