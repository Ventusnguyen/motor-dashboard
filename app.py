import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Thiết lập giao diện ứng dụng Web
st.set_page_config(page_title="Motor LS16 Dashboard", layout="wide")
st.title("📊 VISUAL QUALITY INSIGHTS: MOTOR LS16 YA SPECIFICATION")
st.markdown("---")

# Tạo các Tabs để giao diện gọn gàng, chuyên nghiệp
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Pareto Lỗi", 
    "2. Phân bố Histogram", 
    "3. Boxplot So sánh", 
    "4. Tương quan Scatter", 
    "5. Biểu đồ Kiểm soát"
])

# ==========================================
# TAB 1: PARETO
# ==========================================
with tab1:
    st.header("1. Phân tích nguyên nhân lỗi (Pareto)")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Nhập dữ liệu")
        defects_input = st.text_input("Tên các lỗi (cách nhau bởi dấu phẩy):", "NG Ya, Insu 1000V, Insu bất thường, Không quay, B Lệch")
        counts_input = st.text_input("Số lượng tương ứng (cách nhau bởi dấu phẩy):", "1928, 93, 11, 6, 2")
    
    with col2:
        defects = [x.strip() for x in defects_input.split(',')]
        counts = [int(x.strip()) for x in counts_input.split(',')]
        
        if len(defects) == len(counts):
            fig, ax1 = plt.subplots(figsize=(8, 4))
            cum_percentage = np.cumsum(counts) / sum(counts) * 100
            
            ax1.bar(defects, counts, color="crimson")
            ax1.set_ylabel("Số lượng lỗi", color="crimson")
            ax1_twin = ax1.twinx()
            ax1_twin.plot(defects, cum_percentage, color="blue", marker="D")
            ax1_twin.set_ylabel("Tích lũy (%)", color="blue")
            
            st.pyplot(fig)
        else:
            st.error("Số lượng tên lỗi và số lượng dữ liệu không khớp nhau!")

# ==========================================
# TAB 2: HISTOGRAM
# ==========================================
with tab2:
    st.header("2. Phân bố Phân tích Đặc tính Ya & So sánh USL Spec")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Cài đặt thông số")
        usl_current = st.number_input("USL Hiện tại (mm):", value=50.0)
        usl_proposed = st.number_input("USL Đề xuất (mm):", value=55.0)
        mean_val = st.number_input("Giá trị trung bình Ya:", value=46.2)
        std_val = st.number_input("Độ lệch chuẩn Ya:", value=1.95)
    
    with col2:
        np.random.seed(42)
        ya_data = np.random.normal(loc=mean_val, scale=std_val, size=2000)
        
        fig, ax2 = plt.subplots(figsize=(8, 4))
        sns.histplot(ya_data, kde=True, color="teal", bins=30, ax=ax2)
        ax2.axvline(usl_current, color="red", linestyle="--", label=f"USL Cũ ({usl_current})")
        ax2.axvline(usl_proposed, color="green", linestyle="-.", label=f"USL Mới ({usl_proposed})")
        ax2.legend()
        st.pyplot(fig)

# ==========================================
# TAB 3: BOXPLOT
# ==========================================
with tab3:
    st.header("3. Boxplot: Mức Ya Motor vs Khả năng Hoạt động")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Nhập dữ liệu")
        ok_input = st.text_input("Dữ liệu Ya (Feeder OK):", "41.5, 45.7, 48.7, 51.1, 51.7, 54.1, 56.1, 57.0, 58.3")
        ng_input = st.text_input("Dữ liệu Ya (Feeder NG):", "66.7, 80.0")
        spec_box_old = st.number_input("Tiêu chuẩn cũ MAX (mm):", value=50.0)
        spec_box_new = st.number_input("Tiêu chuẩn mới MAX (mm):", value=55.0)
        
    with col2:
        ya_ok = [float(x.strip()) for x in ok_input.split(',')]
        ya_ng = [float(x.strip()) for x in ng_input.split(',')]
        
        fig, ax3 = plt.subplots(figsize=(8, 4))
        ax3.boxplot([ya_ok, ya_ng], labels=["ITF Feeder OK", "ITF Feeder NG"], patch_artist=True)
        ax3.axhline(spec_box_old, color="red", linestyle="--", label="Cũ")
        ax3.axhline(spec_box_new, color="green", linestyle="-.", label="Mới")
        ax3.legend()
        st.pyplot(fig)

# ==========================================
# TAB 4: SCATTER
# ==========================================
with tab4:
    st.header("4. Biểu đồ Tương quan: Motor Ya vs Feeder Offset L")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Nhập dữ liệu")
        x_input = st.text_input("Giá trị Ya Motor (X):", "41.5, 45.7, 48.7, 51.1, 51.7, 54.1, 56.1, 57.0, 66.7")
        y_input = st.text_input("Offset Feeder (Y):", "1.359, 1.391, 1.359, 1.380, 1.385, 1.390, 1.391, 1.391, 1.850")
        
    with col2:
        x_vals = [float(x.strip()) for x in x_input.split(',')]
        y_vals = [float(y.strip()) for y in y_input.split(',')]
        
        if len(x_vals) == len(y_vals):
            fig, ax4 = plt.subplots(figsize=(8, 4))
            ax4.scatter(x_vals, y_vals, color="darkorange", s=80, edgecolors="k")
            ax4.axvline(50.0, color="red", linestyle="--")
            ax4.axvline(55.0, color="green", linestyle="-.")
            st.pyplot(fig)
        else:
            st.error("Số lượng dữ liệu trục X và Y phải bằng nhau!")

# ==========================================
# TAB 5: CONTROL CHART
# ==========================================
with tab5:
    st.header("5. Biểu đồ Kiểm soát: Tỷ lệ %NG")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Nhập dữ liệu")
        p_input = st.text_input("Tỷ lệ NG 10 ngày (%):", "2.57, 2.60, 2.51, 2.55, 2.58, 0.16, 0.15, 0.14, 0.16, 0.15")
        
    with col2:
        p_rates = [float(x.strip()) for x in p_input.split(',')]
        days = [f"Day {i}" for i in range(1, len(p_rates)+1)]
        
        if len(p_rates) >= 5:
            fig, ax5 = plt.subplots(figsize=(8, 4))
            ax5.plot(days[:5], p_rates[:5], marker="o", color="crimson", label="Spec Cũ")
            ax5.plot(days[5:], p_rates[5:], marker="s", color="forestgreen", label="Spec Mới")
            ax5.axhline(np.mean(p_rates[:5]), color="red", linestyle=":")
            ax5.axhline(np.mean(p_rates[5:]), color="green", linestyle=":")
            ax5.legend()
            st.pyplot(fig)
        else:
            st.warning("Cần nhập ít nhất 5 ngày dữ liệu để vẽ biểu đồ.")
