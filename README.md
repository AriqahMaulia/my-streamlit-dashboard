# my-streamlit-dashboard

# Setup Environment - Shell/Terminal
- pip install virtualenv
- mkdir proyek_akhir
- cd proyek_akhir

# Membuat environment bernama .env
- python -m venv .env  
- .\.env\Scripts\activate  #pada powershell windows

# Membuat Requirements
- pip install -r requirements.txt

# Untuk menonaktifkan virtual environment. Gunakan command:
(.env) $ deactivate

# Kita dapat melihat package apa saja yang telah di install pada virtual env dengan command berikut
(.env) $ pip list

# Run streamlit
streamlit run dashboard.py
