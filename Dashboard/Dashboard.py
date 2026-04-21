# =====================================================
# DASHBOARD STREAMLIT - E-COMMERCE OLIST ANALYSIS (REVISI)
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

# Load data dengan path relatif yang aman untuk Streamlit Cloud
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, 'main_data.csv')
    df = pd.read_csv(csv_path)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    # Filter hanya data 2017-2018 (sesuai analisis)
    df = df[(df['order_purchase_timestamp'].dt.year >= 2017)]
    df['order_month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    return df

df = load_data()

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
st.title('🛒 E-Commerce Olist Dashboard (2017-2018)')
st.markdown('---')

# Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_orders = filtered_df['order_id'].nunique()
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
    
    monthly_data = filtered_df.groupby('order_month').agg(
        jumlah_pesanan=('order_id', 'nunique'),
        total_pendapatan=('payment_value', 'sum')
    ).reset_index()
    
    if not monthly_data.empty:
        fig, ax1 = plt.subplots(figsize=(8, 4.5))
        
        # Bar chart jumlah pesanan (warna biru muda)
        ax1.bar(monthly_data['order_month'], monthly_data['jumlah_pesanan'], 
                color='#90CAF9', alpha=0.9, label='Jumlah Pesanan')
        ax1.set_xlabel('Bulan')
        ax1.set_ylabel('Jumlah Pesanan', color='#1E88E5')
        ax1.tick_params(axis='y', labelcolor='#1E88E5')
        ax1.tick_params(axis='x', rotation=45)
        
        # Line chart pendapatan (warna oranye)
        ax2 = ax1.twinx()
        ax2.plot(monthly_data['order_month'], monthly_data['total_pendapatan'], 
                 color='#FF8C00', marker='o', linewidth=2, label='Pendapatan')
        ax2.set_ylabel('Total Pendapatan (R$)', color='#FF8C00')
        ax2.tick_params(axis='y', labelcolor='#FF8C00')
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x/1e6:.1f}M'))
        
        plt.title('Tren Bulanan: Pesanan vs Pendapatan', fontsize=12)
        ax1.grid(True, alpha=0.2)
        fig.tight_layout()
        st.pyplot(fig)
    else:
        st.info('Tidak ada data untuk ditampilkan.')

with col_right:
    st.subheader('🏆 Top 5 Kategori Produk')
    
    if not filtered_df.empty:
        top_categories = filtered_df['product_category_name_english'].value_counts().head(5)
        
        # Warna: highlight merah untuk peringkat 1, biru untuk lainnya
        colors = ['#FF5252' if i == 0 else '#1E88E5' for i in range(len(top_categories))]
        
        fig, ax = plt.subplots(figsize=(7, 4))
        bars = ax.barh(top_categories.index, top_categories.values, color=colors)
        ax.set_title('5 Kategori Produk Terlaris', fontsize=12)
        ax.set_xlabel('Jumlah Item Terjual')
        ax.invert_yaxis()
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 2, bar.get_y() + bar.get_height()/2, f'{int(width)}', va='center')
        fig.tight_layout()
        st.pyplot(fig)
    else:
        st.info('Tidak ada data untuk ditampilkan.')

# Row 2: Metode Pembayaran & Skor Ulasan
col_left, col_right = st.columns(2)

with col_left:
    st.subheader('💳 Distribusi Metode Pembayaran')
    
    if not filtered_df.empty:
        payment_counts = filtered_df['payment_type'].value_counts()
        
        fig, ax = plt.subplots(figsize=(6, 4.5))
        colors = ['#1E88E5', '#42A5F5', '#64B5F6', '#90CAF9', '#BBDEFB']
        ax.pie(
            payment_counts.values,
            labels=payment_counts.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        ax.set_title('Proporsi Metode Pembayaran', fontsize=12)
        fig.tight_layout()
        st.pyplot(fig)
    else:
        st.info('Tidak ada data untuk ditampilkan.')

with col_right:
    st.subheader('⭐ Distribusi Skor Ulasan')
    
    if not filtered_df.empty:
        review_counts = filtered_df['review_score'].value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=(6, 4.5))
        colors = ['#EF5350', '#FFA726', '#FFEE58', '#9CCC65', '#66BB6A']
        bars = ax.bar(review_counts.index.astype(str), review_counts.values, color=colors)
        ax.set_title('Distribusi Skor Ulasan Pelanggan', fontsize=12)
        ax.set_xlabel('Skor Ulasan')
        ax.set_ylabel('Jumlah Ulasan')
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 2, f'{int(height)}', ha='center')
        fig.tight_layout()
        st.pyplot(fig)
    else:
        st.info('Tidak ada data untuk ditampilkan.')

# Row 3: Sebaran Pelanggan per State
st.subheader('📍 Sebaran Pelanggan per State')

if not filtered_df.empty:
    state_counts = filtered_df['customer_state'].value_counts().head(10).reset_index()
    state_counts.columns = ['state', 'count']
    
    # Warna: highlight merah untuk peringkat 1
    colors = ['#FF5252' if i == 0 else '#1E88E5' for i in range(len(state_counts))]
    
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.barh(state_counts['state'], state_counts['count'], color=colors)
    ax.set_title('Top 10 State dengan Pelanggan Terbanyak', fontsize=12)
    ax.set_xlabel('Jumlah Pelanggan')
    ax.invert_yaxis()
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 5, bar.get_y() + bar.get_height()/2, f'{int(width)}', va='center')
    fig.tight_layout()
    st.pyplot(fig)
else:
    st.info('Tidak ada data untuk ditampilkan.')

# Footer
st.markdown('---')
st.caption('© 2026 Olist E-Commerce Analysis Dashboard | Dibuat untuk Proyek Akhir Dicoding')