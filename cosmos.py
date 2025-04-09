import os
import hashlib
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
import bech32
from Crypto.Hash import RIPEMD160

# Configuration
SEED_FILE = "seedphrase.txt"  # File containing seed phrases (one per line)

# Chain configurations
CHAINS = {
    "cosmos": {"coin_type": 118, "prefix": "cosmos", "address_file": "cosmos_wallets.txt", "private_key_file": "cosmos_private_keys.txt"},
    "babylon": {"coin_type": 118, "prefix": "bbn", "address_file": "babylon_wallets.txt", "private_key_file": "babylon_private_keys.txt"},
    "stride": {"coin_type": 118, "prefix": "stride", "address_file": "stride_wallets.txt", "private_key_file": "stride_private_keys.txt"},
    "stargaze": {"coin_type": 118, "prefix": "stars", "address_file": "stargaze_wallets.txt", "private_key_file": "stargaze_private_keys.txt"},
}

def derive_wallet(seed_phrase: str, account_index: int, address_index: int, coin_type: int, prefix: str):
    """Derive a wallet for a specific chain using BIP-44 standard."""
    # Generate seed from mnemonic
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()

    # Derive the master key for the specified coin type
    bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.COSMOS)  # Use Cosmos as base, adjust coin type manually

    # Derive account at index `account_index` (hardened)
    bip44_acc = bip44_mst.Purpose().Coin().Account(account_index)

    # Derive external chain (change = 0) and address at `address_index`
    bip44_addr = bip44_acc.Change(Bip44Changes.CHAIN_EXT).AddressIndex(address_index)

    # Get the 32-byte private key
    private_key = bip44_addr.PrivateKey().Raw().ToBytes()

    # Get the public key
    public_key = bip44_addr.PublicKey().RawCompressed().ToBytes()

    # Generate address from the public key
    # Step 1: Hash the public key using SHA-256
    sha256_hash = hashlib.sha256(public_key).digest()

    # Step 2: Use RIPEMD-160 to hash the SHA-256 result (using pycryptodome's RIPEMD160)
    ripemd160_hash = RIPEMD160.new(sha256_hash).digest()

    # Step 3: Encode the RIPEMD-160 hash in Bech32 format with the chain's prefix
    address = bech32.bech32_encode(prefix, bech32.convertbits(ripemd160_hash, 8, 5))

    return address, private_key.hex()


def main():
    """Main function to generate wallets for multiple chains from seed phrases."""
    if not os.path.exists(SEED_FILE):
        print(f"Error: Seed file '{SEED_FILE}' not found!")
        return

    # Ask the user for the number of wallets to generate per seed phrase
    try:
        num_wallets_per_seed = int(input("How many wallets per seed phrase? "))
        if num_wallets_per_seed <= 0:
            print("❌ Invalid number. Please enter a number greater than 0.")
            return
    except ValueError:
        print("❌ Invalid input. Please enter a valid number.")
        return

    # Create the main folder "Cosmos" if it doesn't exist
    if not os.path.exists("Cosmos"):
        os.makedirs("Cosmos")

    # Initialize output files inside the "Cosmos" folder
    output_files = {}
    for chain, config in CHAINS.items():
        output_files[chain] = {
            "address_file": open(os.path.join("Cosmos", config["address_file"]), "w"),
            "private_key_file": open(os.path.join("Cosmos", config["private_key_file"]), "w"),
        }

    # Read seed phrases line by line
    with open(SEED_FILE, "r") as seed_file:
        for line_number, seed_phrase in enumerate(seed_file, start=1):
            seed_phrase = seed_phrase.strip()
            if not seed_phrase:
                continue  # Skip empty lines

            print(f"\nProcessing Seed Phrase {line_number}: {seed_phrase}")

            # Generate wallets for the current seed phrase
            for i in range(num_wallets_per_seed):
                for chain, config in CHAINS.items():
                    # Use account index 0 and address index i
                    wallet_address, private_key = derive_wallet(
                        seed_phrase,
                        account_index=0,
                        address_index=i,
                        coin_type=config["coin_type"],
                        prefix=config["prefix"],
                    )

                    # Print wallet details
                    print(f"  {chain.capitalize()} Wallet {i + 1}: {wallet_address}")
                    print(f"  Private Key (32 bytes hex): {private_key}")

                    # Save wallet address and private key to their respective files
                    output_files[chain]["address_file"].write(f"{wallet_address}\n")
                    output_files[chain]["private_key_file"].write(f"{private_key}\n")

    # Close all output files
    for chain_files in output_files.values():
        chain_files["address_file"].close()
        chain_files["private_key_file"].close()

    print(f"\n✅ Generated wallets for all seed phrases!")
    for chain, config in CHAINS.items():
        print(f"🔹 {chain.capitalize()} addresses saved to 'Cosmos/{config['address_file']}'")
        print(f"🔹 {chain.capitalize()} private keys saved to 'Cosmos/{config['private_key_file']}'")


if __name__ == "__main__":
    main()
