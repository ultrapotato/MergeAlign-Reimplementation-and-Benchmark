import os
from pathlib import Path

def list_test_cases():
    """List and select test cases from RV100 folder"""
    test_cases = []
    rv100_path = Path("RV100")  
    
    for file in rv100_path.glob("*.tfa"):
        test_cases.append(file)
    
    if not test_cases:
        print("No .tfa files found in RV100 directory!")
        return None
        
    print("\nAvailable test cases:")
    for i, case in enumerate(test_cases):
        print(f"{i+1}. {case.name}")
    
    while True:
        try:
            choice = int(input("\nEnter the number of the test case you want to use: "))
            if 1 <= choice <= len(test_cases):
                selected_file = test_cases[choice-1]
                print(f"\nSelected test file: {selected_file}")
                return str(selected_file.absolute())
            else:
                print("Invalid choice! Please select a valid number.")
        except ValueError:
            print("Please enter a valid number!")

if __name__ == "__main__":
    print("Looking for test cases in RV100 folder...")
    sequence_file = list_test_cases()
    if sequence_file:
        print(f"\nYou can now use this file ({sequence_file}) with the MAFFT script!")