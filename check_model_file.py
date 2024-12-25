import h5py

try:
    with h5py.File("trained_plant_disease_model.keras", 'r') as file:
        print("File opened successfully")
except Exception as e:
    print(f"Error opening file: {e}")
