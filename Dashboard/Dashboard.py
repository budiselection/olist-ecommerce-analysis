# =====================================================
# DASHBOARD STREAMLIT - E-COMMERCE OLIST ANALYSIS
# =====================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Konfigurasi halaman
st.set_page_config(
    page_title="Olist E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

# Fungsi Load data dengan Dynamic Path
@st.cache_data
def load_data():
    # Mengambil lokasi folder tempat script Dashboard.py berada
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'main_data.csv')
    
    # Membaca file
    df = pd.read_csv(file_path)
    
    # Konversi waktu
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    return df

# Menjalankan fungsi load data dengan error handling sederhana
try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    st.info("Pastikan file 'main_data.csv' berada di dalam folder yang sama dengan 'Dashboard.py'")
    st.stop()

# Sidebar
st.sidebar.header('🔍 Filter Data')

# Filter rentang tanggal
min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()

start_date, end_date = st.sidebar.date_input(
    'Pilih Rentang Tanggal',
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Filter kategori produk
categories = ['Semua'] + sorted(df['product_category_name_english'].dropna().unique().tolist())
selected_category = st.sidebar.selectbox('Pilih Kategori Produk', categories)

# Filter data berdasarkan input
filtered_df = df[
    (df['order_purchase_timestamp'].dt.date >= start_date) &
    (df['order_purchase_timestamp'].dt.date <= end_date)
]

if selected_category != 'Semua':
    filtered_df = filtered_df[filtered_df['product_category_name_english'] == selected_category]

# Header
st.title('🛒 E-Commerce Olist Dashboard')
st.markdown('---')

# Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_orders = filtered_df['order_purchase_timestamp'].nunique() if 'order_purchase_timestamp' in filtered_df else 0
    st.metric('📦 Total Pesanan', f'{total_orders:,}')

with col2:
    total_revenue = filtered_df['payment_value'].sum()
    st.metric('💰 Total Pendapatan', f'R$ {total_revenue:,.2f}')

with col3:
    avg_order_value = filtered_df['payment_value'].mean()
    st.metric('💵 Rata-rata Nilai Pesanan', f'R$ {avg_order_value:,.2f}')

with col4:
    avg_review = filtered_df['review_score'].mean()
    st.metric('⭐ Rata-rata Skor Ulasan', f'{avg_review:.2f}')

st.markdown('---')

# Row 1: Tren Bulanan & Top Kategori
col_left, col_right = st.columns(2)

with col_left:
    st.subheader('📈 Tren Pesanan & Pendapatan Bulanan')
    
    # Agregasi bulanan
    monthly_data = filtered_df.groupby('order_month').agg(
        jumlah_pesanan=('payment_value', 'count'),
        total_pendapatan=('payment_value', 'sum')
    ).reset_index()
    
    if not monthly_data.empty:
        fig, ax1 = plt.subplots(figsize=(10, 5))
        
        # Bar chart jumlah pesanan
        ax1.bar(monthly_data['order_month'], monthly_data['jumlah_pesanan'], 
                color='#4A90E2', alpha=0.7, label='Jumlah Pesanan')
        ax1.set_xlabel('Bulan')
        ax1.set_ylabel('Jumlah Pesanan', color='#4A90E2')
        ax1.tick_params(axis='y', labelcolor='#4A90E2')
        ax1.tick_params(axis='x', rotation=45)
        
        # Line chart pendapatan
        ax2 = ax1.twinx()
        ax2.plot(monthly_data['order_month'], monthly_data['total_pendapatan'], 
                 color='#E24A4A', marker='o', linewidth=2, label='Pendapatan')
        ax2.set_ylabel('Total Pendapatan (R$)', color='#E24A4A')
        ax2.tick_params(axis='y', labelcolor='#E24A4A')
        
        plt.title('Tren Bulanan: Pesanan vs Pendapatan', fontsize=12)
        ax1.grid(True, alpha=0.2)
        st.pyplot(fig)
    else:
        st.info('Tidak ada data untuk ditampilkan.')

with col_right:
    st.subheader('🏆 Top 5 Kategori Produk')
    
    if not filtered_df.empty:
        top_categories = filtered_df['product_category_name_english'].value_counts().head(5)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(
            y=top_categories.index,
            x=top_categories.values,
            palette='Blues_r',
            ax=ax
        )
        ax.set_title('5 Kategori Produk Terlaris', fontsize=12)
        ax.set_xlabel('Jumlah Item Terjual')
        ax.set_ylabel('')
        ax.bar_label(ax.containers[0], padding=3)
        st.pyplot(fig)
    else:
        st.info('Tidak ada data untuk ditampilkan.')

# Row 2: Metode Pembayaran & Skor Ulasan
col_left, col_right = st.columns(2)

with col_left:
    st.subheader('💳 Metode Pembayaran')
    
    if not filtered_df.empty:
        payment_counts = filtered_df['payment_type'].value_counts()
        
        # Perkecil figsize agar proporsional di dalam kolom
        fig, ax = plt.subplots(figsize=(6, 6)) 
        colors = sns.color_palette('pastel')[0:len(payment_counts)]
        
        # Gunakan pctdistance agar angka persentase tidak tabrakan dengan label
        ax.pie(
            payment_counts.values,
            labels=payment_counts.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=140,
            textprops={'fontsize': 10}
        )
        ax.set_title('Proporsi Metode Pembayaran', fontsize=14, pad=20)
        
        # Menghilangkan frame agar lebih clean
        plt.tight_layout()
        st.pyplot(fig, clear_figure=True)
    else:
        st.info('Tidak ada data pembayaran.')

with col_right:
    st.subheader('⭐ Skor Ulasan')
    
    if not filtered_df.empty:
        # Memastikan skor ulasan terurut 1-5
        review_counts = filtered_df['review_score'].value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=(6, 6))
        # Menggunakan palette yang konsisten (Merah ke Hijau)
        colors_review = ['#ff4d4d', '#ffa64d', '#ffff4d', '#a6ff4d', '#4dff4d']
        
        sns.barplot(
            x=review_counts.index,
            y=review_counts.values,
            palette=colors_review,
            ax=ax,
            hue=review_counts.index, # Menghindari warning matplotlib terbaru
            legend=False
        )
        
        ax.set_title('Distribusi Skor Ulasan', fontsize=14, pad=20)
        ax.set_xlabel('Skor (1-5)', fontsize=10)
        ax.set_ylabel('Jumlah', fontsize=10)
        
        # Tambahkan label angka di atas bar
        ax.bar_label(ax.containers[0], padding=3, fontsize=10)
        
        # Optimasi layout
        plt.tight_layout()
        st.pyplot(fig, clear_figure=True)
    else:
        st.info('Tidak ada data ulasan.')

# Row 3: Geospatial (Peta Sederhana) 
st.subheader('📍 Sebaran Pelanggan per State')

if not filtered_df.empty:
    state_counts = filtered_df['customer_state'].value_counts().reset_index()
    state_counts.columns = ['state', 'count']
    
    # Visualisasi bar chart horizontal
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
        y=state_counts['state'],
        x=state_counts['count'],
        palette='viridis',
        ax=ax,
        order=state_counts.sort_values('count', ascending=False)['state']
    )
    ax.set_title('Jumlah Pelanggan per State', fontsize=14)
    ax.set_xlabel('Jumlah Pelanggan')
    ax.set_ylabel('State')
    ax.bar_label(ax.containers[0], padding=3)
    st.pyplot(fig)
else:
    st.info('Tidak ada data untuk ditampilkan.')

# Footer
st.markdown('---')
st.caption('© 2026 Olist E-Commerce Analysis Dashboard | Dibuat untuk Proyek Akhir Dicoding')