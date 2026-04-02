import random

def mint_nft(wallet, name, role, skills, score):
    token_id = random.randint(10000, 99999)
    tx_hash = f"0x{random.randint(10**60, 10**70):064x}"
    metadata = {
        "name": f"{name}'s Connectra Profile",
        "role": role,
        "skills": skills,
        "overall_score": score,
        "image": "https://picsum.photos/400"  # placeholder
    }
    explorer_link = f"https://amoy.polygonscan.com/token/0xMockNFTContract?a={token_id}"
    return token_id, tx_hash, explorer_link, metadata