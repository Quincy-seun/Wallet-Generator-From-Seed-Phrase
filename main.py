import inquirer
import subprocess

def main():
    # Define the menu options
    questions = [
        inquirer.List(
            'wallet',
            message="Which wallet generator would you like to run?",
            choices=['Cosmos', 'EVM', 'Mavryk', 'Solana', 'Exit'],
        ),
    ]
    
    while True:
        # Get the user's choice using arrow keys to navigate
        answers = inquirer.prompt(questions)

        if answers['wallet'] == 'Exit':
            print("Exiting...")
            break
        
        print(f"Running {answers['wallet']} wallet generator...")

        # Map the selected option to the script
        wallet_script_mapping = {
            'Cosmos': 'cosmos.py',
            'EVM': 'evm.py',
            'Mavryk': 'mavryk.py',
            'Solana': 'solana.py',
        }

        # Get the script name from the mapping
        selected_script = wallet_script_mapping.get(answers['wallet'])

        # If a valid script is found, run it
        if selected_script:
            subprocess.run(["python", selected_script])
        else:
            print(f"❌ No script found for {answers['wallet']}")

        # After running the script, ask again for the next selection
        print("Press Enter to continue...")
        input()

if __name__ == "__main__":
    main()
