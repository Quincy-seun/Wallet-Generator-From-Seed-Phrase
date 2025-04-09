import os
from mnemonic import Mnemonic
import hashlib
import hmac
import struct
import ecdsa
import binascii
from web3 import Web3
from Crypto.Hash import RIPEMD160, SHA256

# Load seed phrases from file
with open('seedphrase.txt', 'r') as f:
    seed_phrases = f.readlines()

# Ask the user how many EVM wallets they want to generate per seed phrase
try:
    num_wallets = int(input("How many EVM wallets do you want to generate per seed phrase? "))
    if num_wallets <= 0:
        print("❌ Please enter a number greater than 0.")
        exit()
except ValueError:
    print("❌ Invalid input. Please enter a valid number.")
    exit()

# Connect to Web3 provider
web3 = Web3()

# Create the EVM directory if it doesn't exist
output_dir = "EVM"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# BIP32 constants
MAINNET_PRIVATE = b'\x04\x88\xAD\xE4'
MAINNET_PUBLIC = b'\x04\x88\xB2\x1E'
HARDENED = 0x80000000

# BIP32 path constants
PURPOSE = 44
COIN_TYPE = 60  # Ethereum
ACCOUNT = 0
CHANGE = 0  # External chain

# BIP32 implementation functions
def hmac_sha512(key, msg):
    return hmac.new(key, msg, hashlib.sha512).digest()

def derive_master_key(seed):
    """ Derive a master key from a BIP39 seed """
    key = b'Bitcoin seed'
    h = hmac_sha512(key, seed)
    master_key, master_chain_code = h[:32], h[32:]
    return master_key, master_chain_code

def ckd_priv(private_key, chain_code, index):
    """ Child Key Derivation for private keys """
    is_hardened = index >= HARDENED
    
    if is_hardened:
        # Hardened derivation
        data = b'\x00' + private_key + struct.pack('>L', index)
    else:
        # Normal derivation
        point = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1).verifying_key.to_string("compressed")
        data = point + struct.pack('>L', index)
    
    h = hmac_sha512(chain_code, data)
    child_private_key_int = (int.from_bytes(h[:32], 'big') + int.from_bytes(private_key, 'big')) % ecdsa.SECP256k1.order
    child_private_key = child_private_key_int.to_bytes(32, 'big')
    child_chain_code = h[32:]
    
    return child_private_key, child_chain_code

def derive_bip44_path(seed, account_index, change, address_index):
    """ 
    Derive the BIP44 path: m/44'/60'/0'/0/{address_index}
    m / purpose' / coin_type' / account' / change / address_index
    """
    # Derive master key from seed
    master_key, master_chain_code = derive_master_key(seed)
    
    # Derive purpose level: m/44'
    purpose = PURPOSE | HARDENED
    key, chain_code = ckd_priv(master_key, master_chain_code, purpose)
    
    # Derive coin type: m/44'/60'
    coin_type = COIN_TYPE | HARDENED
    key, chain_code = ckd_priv(key, chain_code, coin_type)
    
    # Derive account: m/44'/60'/0'
    account = account_index | HARDENED
    key, chain_code = ckd_priv(key, chain_code, account)
    
    # Derive change level: m/44'/60'/0'/0
    key, chain_code = ckd_priv(key, chain_code, change)
    
    # Derive address index: m/44'/60'/0'/0/{address_index}
    key, chain_code = ckd_priv(key, chain_code, address_index)
    
    return key

# Function to generate wallets from the seed phrase
def generate_wallets_from_seed(seed_phrase, num_wallets):
    mnemonic = Mnemonic("english")
    
    # Convert seed phrase to seed using BIP39
    seed = mnemonic.to_seed(seed_phrase)
    
    wallets = []
    
    for i in range(num_wallets):
        try:
            # Derive private key using BIP44 path m/44'/60'/0'/0/i
            private_key_bytes = derive_bip44_path(seed, ACCOUNT, CHANGE, i)
            private_key_hex = "0x" + binascii.hexlify(private_key_bytes).decode('utf-8')
            
            # Generate Ethereum address from private key using web3
            account = web3.eth.account.from_key(private_key_hex)
            address = account.address
            
            # Save the wallet info
            wallets.append({"private_key": private_key_hex, "address": address})
            print(f"Generated wallet {i+1} with address: {address}")
            
        except Exception as e:
            print(f"Error generating wallet at index {i}: {str(e)}")
    
    return wallets

# Process each seed phrase and generate wallets
all_private_keys = []
all_addresses = []

for idx, seed_phrase in enumerate(seed_phrases, start=1):
    seed_phrase = seed_phrase.strip()
    if not seed_phrase:
        continue  # Skip empty lines
    
    print(f"Generating wallets for Seed Phrase {idx}")
    
    try:
        # Generate wallets from the seed phrase
        wallets = generate_wallets_from_seed(seed_phrase, num_wallets)
        
        # Save private keys and addresses to files in the EVM folder
        with open(os.path.join(output_dir, f'seed_pk_{idx}.txt'), 'w') as pk_file, open(os.path.join(output_dir, f'seed_wallets_{idx}.txt'), 'w') as wallets_file:
            for wallet in wallets:
                pk_file.write(f"{wallet['private_key']}\n")
                wallets_file.write(f"{wallet['address']}\n")
                
                # Collect all keys and addresses
                all_private_keys.append(wallet['private_key'])
                all_addresses.append(wallet['address'])
        
        print(f"✅ {len(wallets)} EVM wallets generated and saved for Seed Phrase {idx}.")
    except Exception as e:
        print(f"❌ Error generating wallets for Seed Phrase {idx}: {str(e)}")

# Save all private keys and addresses to combined files
with open(os.path.join(output_dir, 'all_private_keys.txt'), 'w') as f:
    for pk in all_private_keys:
        f.write(f"{pk}\n")

with open(os.path.join(output_dir, 'all_addresses.txt'), 'w') as f:
    for addr in all_addresses:
        f.write(f"{addr}\n")

print(f"\nAll wallets generated and saved in the 'EVM' folder.")
print(f"✅ Combined lists saved as 'all_private_keys.txt' and 'all_addresses.txt' in the EVM folder.")
