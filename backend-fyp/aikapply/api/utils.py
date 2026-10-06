import pandas as pd
import os

def get_university_context():
    # The dataset ships next to this file; the old hard-coded Windows path only existed on one PC
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pakistan_universities.xlsx")
    if not os.path.exists(file_path):
        return "University dataset is currently unavailable."
    
    try:
        df = pd.read_excel(file_path)
        # Use CSV instead of markdown since pandas to_markdown requires the "tabulate" library
        return df.to_csv(index=False)
    except Exception as e:
        return f"[Error loading dataset: {str(e)}]"
