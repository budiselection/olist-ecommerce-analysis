# E-Commerce Olist Dashboard

## Setup Environment - Anaconda

conda create --name olist-ds python=3.9
conda activate olist-ds
pip install -r requirements.txt

## Setup Environment - Shell/Terminal

mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt

## Run Streamlit App

streamlit run dashboard/dashboard.py

## Struktur Proyek

submission/
├───dashboard/
│ ├───main_data.csv
│ └───dashboard.py
├───data/
│ └─── (9 file dataset CSV)
├───notebook.ipynb
├───requirements.txt
└───url.txt

## Catatan

- Pastikan file `main_data.csv` berada di dalam folder `dashboard/` sebelum menjalankan aplikasi.
- Dashboard dapat diakses secara lokal melalui `http://localhost:8501`.
- Untuk deploy ke Streamlit Cloud, pastikan file `requirements.txt` dan struktur folder sesuai.
