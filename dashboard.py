import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set style untuk visualisasi
sns.set(style='darkgrid')

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    data = pd.read_csv('all_data.csv')  # Pastikan path ke file sudah benar
    data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'], errors='coerce')
    data['order_delivered_customer_date'] = pd.to_datetime(data['order_delivered_customer_date'], errors='coerce')
    data['review_creation_date'] = pd.to_datetime(data['review_creation_date'], errors='coerce')
    return data

# Fungsi untuk mempersiapkan data untuk visualisasi
def prepare_data(data):
    # Filter data untuk setahun terakhir
    last_year = data[data['order_purchase_timestamp'] >= (pd.Timestamp.now() - pd.DateOffset(years=1))]
    
    # Cek jumlah data dalam setahun terakhir
    st.write(f"Jumlah data dalam setahun terakhir: {len(last_year)}")

    # Grup data per bulan dan wilayah geografis (state)
    monthly_trends = last_year.groupby([pd.Grouper(key='order_purchase_timestamp', freq='M'), 'customer_state'])['order_id'].count().reset_index()
    monthly_trends.columns = ['Month', 'State', 'Order Count']

    # Cek data trend bulanan
    st.write("Data Tren Bulanan:", monthly_trends.head())

    # Menghitung korelasi antara waktu pengiriman dan skor ulasan
    valid_delivery_data = data.dropna(subset=['order_delivered_customer_date', 'order_purchase_timestamp'])
    valid_delivery_data['delivery_time'] = (valid_delivery_data['order_delivered_customer_date'] - valid_delivery_data['order_purchase_timestamp']).dt.days
    delivery_satisfaction = valid_delivery_data[['delivery_time', 'review_score']].dropna()

    # Cek data kepuasan pelanggan
    st.write("Data Kepuasan Pelanggan:", delivery_satisfaction.head())

    # Filter data kategori produk dalam 6 bulan terakhir
    last_6_months = data[data['order_purchase_timestamp'] >= (pd.Timestamp.now() - pd.DateOffset(months=6))]
    product_sales = last_6_months.groupby('product_category_name')['order_id'].count().reset_index()
    product_sales.columns = ['Product Category', 'Sales Count']
    product_sales = product_sales.sort_values(by='Sales Count', ascending=False)

    # Cek data kategori produk
    st.write("Data Penjualan Kategori Produk:", product_sales.head())

    # Melakukan analisis RFM
    rfm_data = calculate_rfm(data)
    
    return monthly_trends, delivery_satisfaction, product_sales, rfm_data

def calculate_rfm(data):
    # Menghitung nilai RFM
    snapshot_date = data['order_purchase_timestamp'].max() + pd.DateOffset(days=1)
    rfm = data.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days,  # Recency
        'order_id': 'count',  # Frequency
        'payment_value': 'sum'  # Monetary
    })
    
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    rfm = rfm.reset_index()

    # Manual Grouping untuk RFM
    rfm['Recency Group'] = pd.cut(rfm['Recency'], bins=[0, 30, 90, 180, float('inf')], 
                                   labels=['Baru', 'Sedang', 'Lama', 'Sangat Lama'])
    rfm['Frequency Group'] = pd.cut(rfm['Frequency'], bins=[0, 1, 3, 6, float('inf')],
                                    labels=['Rendah', 'Sedang', 'Tinggi', 'Sangat Tinggi'])
    rfm['Monetary Group'] = pd.cut(rfm['Monetary'], bins=[0, 100, 500, 1000, float('inf')],
                                    labels=['Rendah', 'Sedang', 'Tinggi', 'Sangat Tinggi'])

    return rfm

# Fungsi untuk menampilkan visualisasi tren pesanan bulanan
def plot_monthly_trends(monthly_trends):
    st.subheader('Trend Pesanan Bulanan di Berbagai Wilayah')
    
    if not monthly_trends.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=monthly_trends, x='Month', y='Order Count', hue='State', ax=ax, palette='tab10')
        ax.set_title('Trend Jumlah Pesanan Bulanan per Wilayah Geografis', fontsize=16)
        ax.set_ylabel('Jumlah Pesanan', fontsize=14)
        ax.set_xlabel('Bulan', fontsize=14)
        ax.legend(title='Wilayah', bbox_to_anchor=(1.05, 1), loc='upper left')
        st.pyplot(fig)
    else:
        st.write("Tidak ada data yang cukup untuk ditampilkan.")

# Fungsi untuk menampilkan visualisasi hubungan waktu pengiriman dengan kepuasan pelanggan
def plot_delivery_satisfaction(delivery_satisfaction):
    st.subheader('Hubungan antara Waktu Pengiriman dan Kepuasan Pelanggan')
    if not delivery_satisfaction.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=delivery_satisfaction, x='delivery_time', y='review_score', ax=ax, color='orange')
        ax.set_title('Waktu Pengiriman vs Skor Review', fontsize=16)
        ax.set_xlabel('Waktu Pengiriman (Hari)', fontsize=14)
        ax.set_ylabel('Skor Review', fontsize=14)
        st.pyplot(fig)
    else:
        st.write("Tidak ada data yang cukup untuk ditampilkan.")

# Fungsi untuk menampilkan visualisasi kategori produk dengan penjualan terbanyak
def plot_product_sales(product_sales):
    st.subheader('Kategori Produk dengan Penjualan Terbanyak dalam 6 Bulan Terakhir')
    
    if not product_sales.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=product_sales, x='Sales Count', y='Product Category', ax=ax, palette='viridis')
        ax.set_title('Penjualan per Kategori Produk', fontsize=16)
        ax.set_xlabel('Jumlah Penjualan', fontsize=14)
        ax.set_ylabel('Kategori Produk', fontsize=14)
        st.pyplot(fig)
    else:
        st.write("Tidak ada data yang cukup untuk ditampilkan.")

# Fungsi untuk menampilkan visualisasi RFM
def plot_rfm(rfm):
    st.subheader('Analisis RFM dan Pengelompokan Manual')
    
    if not rfm.empty:
        st.write(rfm[['customer_id', 'Recency', 'Recency Group', 'Frequency', 'Frequency Group', 'Monetary', 'Monetary Group']])
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.countplot(data=rfm, x='Recency Group', hue='Frequency Group', ax=ax, palette='rocket')
        ax.set_title('Distribusi Pengelompokan RFM', fontsize=16)
        ax.set_xlabel('Grup Recency', fontsize=14)
        ax.set_ylabel('Jumlah Pelanggan', fontsize=14)
        ax.legend(title='Frequency Group')
        st.pyplot(fig)
    else:
        st.write("Tidak ada data yang cukup untuk ditampilkan.")

# Streamlit layout
def main():
    st.set_page_config(page_title='Dashboard E-Commerce', layout='wide', initial_sidebar_state='expanded')
    st.title('Dashboard Analisis Data E-Commerce')
    st.sidebar.header('Proyek Analisis Data')


    # Load data
    data = load_data()

    # Siapkan data untuk visualisasi
    monthly_trends, delivery_satisfaction, product_sales, rfm_data = prepare_data(data)

    # Tampilkan visualisasi
    col1, col2 = st.columns(2)

    with col1:
        plot_monthly_trends(monthly_trends)
        plot_delivery_satisfaction(delivery_satisfaction)

    with col2:
        plot_product_sales(product_sales)
        plot_rfm(rfm_data)

    # Tambahkan informasi kontak dan copyright
    st.markdown("""
    ---
    **Nama:** Ariqah Maulia Listiani  
    **Email:** [m002b4kx0652@bangkit.academy](mailto:m002b4kx0652@bangkit.academy)  
    **ID Dicoding:** armalist  
    <p style="text-align: center;">Copyright @ Ariqah</p>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
