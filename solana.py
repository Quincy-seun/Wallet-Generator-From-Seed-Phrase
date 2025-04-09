import os
import base58
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from solders.keypair import Keypair

# Configuration
SEED_FILE = "seedphrase.txt"
OUTPUT_DIR = "Solana"  # Output folder for saving files

# Function to derive a Solana wallet from a seed phrase
def derive_solana_wallet(seed_phrase: str, index: int):
    """Derive a Solana wallet from a seed phrase using BIP-44 standard."""
    
    # Generate seed from mnemonic
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()

    # Derive the master key for Solana
    bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA)

    # Derive account at index `index`
    bip44_acc = bip44_mst.Purpose().Coin().Account(index).Change(Bip44Changes.CHAIN_EXT)

    # Get the 32-byte secret key
    secret_key = bip44_acc.PrivateKey().Raw().ToBytes()

    # Generate a Solana keypair from the 32-byte seed
    solana_keypair = Keypair.from_seed(secret_key)
    
    # Get the public key (Solana wallet address)
    public_key = str(solana_keypair.pubkey())

    # Full private key (64-byte) = 32-byte secret key + 32-byte public key
    full_private_key = bytes(solana_keypair)

    # Convert the full private key to Base58 for Phantom/Backpack
    phantom_secret_key = base58.b58encode(full_private_key).decode()

    return public_key, full_private_key.hex(), phantom_secret_key

def main():
    """Main function to generate Solana wallets."""
    
    # Ask how many wallets to generate
    try:
        num_wallets = int(input("How many wallets would you like to generate? "))
    except ValueError:
        print("❌ Invalid number entered. Exiting...")
        return

    # Check if the seed file exists
    if not os.path.exists(SEED_FILE):
        print(f"❌ Error: Seed file '{SEED_FILE}' not found!")
        return

    # Create Solana folder if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    wallets = []
    private_keys = []
    phantom_keys = []

    with open(SEED_FILE, "r") as file:
        # Read seed phrases line by line
        seed_phrases = file.readlines()

    for seed_phrase in seed_phrases:
        seed_phrase = seed_phrase.strip()  # Remove any extra whitespace or newline

        if len(seed_phrase.split()) != 12:
            print(f"❌ Skipping invalid seed phrase: {seed_phrase}")
            continue

        print(f"Generating wallets for Seed Phrase: {seed_phrase}")

        for i in range(num_wallets):
            wallet_address, full_private_key, phantom_secret_key = derive_solana_wallet(seed_phrase, i)
            wallets.append(wallet_address)
            private_keys.append(full_private_key)
            phantom_keys.append(phantom_secret_key)

            print(f"Wallet {i + 1}: {wallet_address}")
            print(f"Full Private Key (64 bytes hex): {full_private_key}")
            print(f"Phantom-Compatible Private Key (Base58): {phantom_secret_key}\n")

    # Save wallets to the "Solana" folder
    with open(os.path.join(OUTPUT_DIR, "wallets.txt"), "w") as file:
        file.write("\n".join(wallets) + "\n")

    # Save full private keys (64 bytes hex) to the "Solana" folder
    with open(os.path.join(OUTPUT_DIR, "private_keys.txt"), "w") as file:
        file.write("\n".join(private_keys) + "\n")

    # Save Phantom-compatible private keys (Base58) to the "Solana" folder
    with open(os.path.join(OUTPUT_DIR, "secret_keys.txt"), "w") as file:
        file.write("\n".join(phantom_keys) + "\n")

    print(f"\n✅ Generated {num_wallets * len(seed_phrases)} Solana wallets!")
    print(f"🔹 Wallets saved to '{os.path.join(OUTPUT_DIR, 'wallets.txt')}'")
    print(f"🔹 Full Private Keys (64 bytes hex) saved to '{os.path.join(OUTPUT_DIR, 'private_keys.txt')}'")
    print(f"🔹 Phantom-Compatible Private Keys (Base58) saved to '{os.path.join(OUTPUT_DIR, 'secret_keys.txt')}'")

if __name__ == "__main__":
    main()
