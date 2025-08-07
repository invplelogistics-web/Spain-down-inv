import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import io

def extract_invoice_info(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    result = {
        "CLIENTE": "",
        "Hãng": "",
        "No PEDIDO": "",
        "FECHA OPERACIÓN/EXPEDICIÓN": "",
        "No DOCUMENTO": "",
        "IMPORTE": ""
    }

    lines = text.splitlines()

    # Trích CLIENTE
    for i, line in enumerate(lines):
        if "CLIENTE" in line.upper():
            if i + 1 < len(lines):
                result["CLIENTE"] = lines[i + 1].strip()
            break

    # Trích Hãng
    if "ZARA ESPAÑA" in text:
        result["Hãng"] = "ZARA ESPAÑA, S.A."

    # Trích các trường còn lại
    for i, line in enumerate(lines):
        if "Nº DOCUMENTO" in line:
            result["No DOCUMENTO"] = line.split(":")[-1].strip()
        elif "FECHA OPERACIÓN" in line:
            result["FECHA OPERACIÓN/EXPEDICIÓN"] = line.split(":")[-1].strip()
        elif "Nº PEDIDO" in line:
            result["No PEDIDO"] = line.split(":")[-1].strip()
        elif "IMPORTE EUR" in line:
            # Lấy dòng phía TRƯỚC dòng này, nơi chứa số tiền
            if i - 1 >= 0:
                possible_amount = lines[i - 1].strip()
                # Kiểm tra xem có phải số tiền không
                if possible_amount.replace(".", "").replace(",", "").isdigit():
                    result["IMPORTE"] = possible_amount

    return result

# Streamlit UI
st.set_page_config(page_title="Trích xuất hóa đơn nhiều PDF", layout="wide")
st.title("📂 Trích xuất nhiều hóa đơn PDF và tải CSV")

st.write("Tải nhiều file PDF để trích xuất thông tin: **CLIENTE, Hãng, No PEDIDO, FECHA, No DOCUMENTO, IMPORTE**")

uploaded_files = st.file_uploader("📤 Chọn các file PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_data = []
    with st.spinner("⏳ Đang xử lý các file..."):
        for file in uploaded_files:
            info = extract_invoice_info(file)
            info["Tên file"] = file.name
            all_data.append(info)

    df = pd.DataFrame(all_data)
    st.success(f"✅ Đã xử lý {len(uploaded_files)} file.")
    st.dataframe(df)

    # Tải kết quả về dưới dạng CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Tải kết quả CSV",
        data=csv_buffer.getvalue(),
        file_name="ket_qua_nhieu_hoa_don.csv",
        mime="text/csv"
    )
