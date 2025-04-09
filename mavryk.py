import json
import hashlib
import os
from pytezos.crypto.key import Key

def generate_mavryk_wallets_from_seed(seed_phrase, count=1):
    # Lowercase the seed phrase and strip any extra spaces
    seed_phrase = seed_phrase.lower().strip()
    
    wallets = []
    
    # Generate the first wallet directly from the mnemonic
    try:
        key = Key.from_mnemonic(seed_phrase)
        address = key.public_key_hash()
        
        wallets.append({
            "index": 0,
            "private_key": key.secret_key(),
            "public_key": key.public_key(),
            "address": address
        })
        print(f"Successfully generated wallet 1 with address: {address}")
    except Exception as e:
        print(f"Error generating primary wallet: {e}")
    
    # For additional wallets, create new "synthetic" mnemonics by hashing the original
    # with a counter to create deterministic but different keys
    for i in range(1, count):
        try:
            # Create a derived seed by combining original seed with index
            derived_seed = f"{seed_phrase}_{i}"
            # Hash it to create a deterministic but different seed
            h = hashlib.sha256(derived_seed.encode()).hexdigest()
            
            # Use this hash to create a unique passphrase for the mnemonic
            # This will create a different but deterministic wallet for each index
            key = Key.from_mnemonic(seed_phrase, passphrase=h)
            address = key.public_key_hash()
            
            wallets.append({
                "index": i,
                "private_key": key.secret_key(),
                "public_key": key.public_key(),
                "address": address,
                "derivation_hash": h[:8]  # Store part of the hash for reference
            })
            print(f"Successfully generated wallet {i+1} with address: {address}")
        except Exception as e:
            print(f"Error generating wallet at index {i}: {e}")
    
    return wallets

def read_seed_phrases(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def main():
    # Define file path for the seed phrases
    file_path = "seedphrase.txt"
    
    # Ask the user for the number of wallets to generate
    try:
        wallet_count = int(input("How many wallets per seed phrase? "))
    except ValueError:
        print("❌ Invalid number entered.")
        return
    
    # Read seed phrases from the file
    try:
        seed_phrases = read_seed_phrases(file_path)
        if not seed_phrases:
            print("❌ No seed phrases found in the file.")
            return
    except Exception as e:
        print(f"❌ Error reading seed phrases: {e}")
        return
    
    # Create the Mavryk directory if it doesn't exist
    output_dir = "Mavryk"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    all_wallets = []
    all_addresses = []
    all_private_keys = []
    
    # Process each seed phrase and generate wallets
    for idx, phrase in enumerate(seed_phrases, start=1):
        try:
            # Show only first few words of seed phrase for privacy
            words = phrase.split()
            display_phrase = ' '.join(words[:3]) + '...' if len(words) > 3 else phrase
                
            print(f"Processing Seed Phrase {idx}: {display_phrase}")
            wallets = generate_mavryk_wallets_from_seed(phrase, wallet_count)
            for wallet in wallets:
                all_wallets.append({
                    "seed_phrase": phrase,
                    **wallet
                })
                
                # Collect addresses and private keys for separate files
                all_addresses.append(wallet["address"])
                all_private_keys.append(wallet["private_key"])
                
        except Exception as e:
            print(f"Error processing phrase {idx}:\n  {display_phrase}\n  Error: {str(e)}\n")
    
    # Save the generated wallets to a JSON file inside the Mavryk folder
    with open(os.path.join(output_dir, "generated_mavryk_wallets.json"), "w") as f:
        json.dump(all_wallets, f, indent=4)
    
    # Save addresses to wallets.txt inside the Mavryk folder
    with open(os.path.join(output_dir, "wallets.txt"), "w") as f:
        for address in all_addresses:
            f.write(f"{address}\n")
    
    # Save private keys to priv_keys.txt inside the Mavryk folder
    with open(os.path.join(output_dir, "priv_keys.txt"), "w") as f:
        for private_key in all_private_keys:
            f.write(f"{private_key}\n")
    
    print(f"\n✅ Generated {len(all_wallets)} Mavryk wallets from {len(seed_phrases)} seed phrases.")
    print(f"✅ Saved addresses to {os.path.join(output_dir, 'wallets.txt')}")
    print(f"✅ Saved private keys to {os.path.join(output_dir, 'priv_keys.txt')}")
    print(f"✅ Saved full wallet data to {os.path.join(output_dir, 'generated_mavryk_wallets.json')}")

if __name__ == "__main__":
    main()
