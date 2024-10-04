# my-streamlit-dashboard

# Setup Environment - Shell/Terminal
- pip install virtualenv
- mkdir proyek_analisis_data
- cd proyek_analisis_data
- python -m venv .env  #Membuat environment bernama .env
- .\.env\Scripts\activate  #pada powershell windows
- pip install -r requirements.txt

# Untuk menonaktifkan virtual environment. Gunakan command:
(.env) $ deactivate

# Kita dapat melihat package apa saja yang telah di install pada virtual env dengan command berikut
(.env) $ pip list

# Run streamlit
streamlit run dashboard.py
