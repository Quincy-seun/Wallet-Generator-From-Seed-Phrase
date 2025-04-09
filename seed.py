import os
from mnemonic import Mnemonic

# Ask user for number of seed phrases
try:
    num_phrases = int(input("How many seed phrases would you like to generate? "))
    if num_phrases <= 0:
        print("❌ Please enter a number greater than 0.")
        exit()
except ValueError:
    print("❌ Invalid input. Please enter a valid number.")
    exit()

# Ask user for number of words in each seed phrase
word_options = {12: 128, 18: 192, 24: 256}
print("Choose the number of words for each seed phrase (12, 18, or 24):")
try:
    word_count = int(input("Number of words: "))
    if word_count not in word_options:
        print("❌ Invalid choice. Please select 12, 18, or 24.")
        exit()
except ValueError:
    print("❌ Invalid input. Please enter a number.")
    exit()

# Create output directory
output_dir = "Generated seed phrases"
os.makedirs(output_dir, exist_ok=True)

# Initialize BIP39 mnemonic generator
mnemo = Mnemonic("english")

# Generate and save seed phrases
output_path = os.path.join(output_dir, "seedphrases.txt")
with open(output_path, "w") as f:
    for i in range(1, num_phrases + 1):
        entropy_bits = word_options[word_count]
        seed_phrase = mnemo.generate(strength=entropy_bits)
        f.write(f"Seed Phrase {i} ({word_count} words):\n{seed_phrase}\n\n")
        print(f"✅ Seed Phrase {i} generated.")

print(f"\n🎉 All {num_phrases} seed phrases saved to '{output_path}'")
