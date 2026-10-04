import pandas as pd
import os

def get_university_context():
    # Found inside frontend root
    file_path = r"C:\Users\HP\Desktop\backend-fyp\aikapply\api\pakistan_universities.xlsx"
    
    if not os.path.exists(file_path):
        # Fallback to backend dir if moved
        file_path = r"C:\Users\HP\Desktop\backend-fyp\aikapply\api\pakistan_universities.xlsx"
        if not os.path.exists(file_path):
            return "University dataset is currently unavailable."
    
    try:
        df = pd.read_excel(file_path)
        # Use CSV instead of markdown since pandas to_markdown requires the "tabulate" library
        return df.to_csv(index=False)
    except Exception as e:
        return f"[Error loading dataset: {str(e)}]"
