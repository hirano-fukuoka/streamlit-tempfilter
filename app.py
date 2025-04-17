import streamlit as st
import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
import io

st.title("温度データ バンドストップフィルタ Webアプリ")

# ファイルアップロード
uploaded_file = st.file_uploader("CSVまたはExcelファイルをアップロードしてください", type=["csv", "xlsx"])

if uploaded_file is not None:
    # ファイル読み込み
    if uploaded_file.name.endswith(".xlsx"):
        sheet_names = pd.ExcelFile(uploaded_file).sheet_names
        selected_sheet = st.selectbox("シートを選択", sheet_names)
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
    else:
        df = pd.read_csv(uploaded_file)

    st.write("アップロードされたデータのプレビュー:")
    st.dataframe(df.head())

    # 列名の選択
    time_col = st.selectbox("時間列を選択", df.columns)
    temp_col = st.selectbox("温度列を選択", df.columns)

    # プリセットの選択
    preset = st.selectbox("プリセットを選択", ["カスタム設定", "低周波ノイズ除去", "高周波ノイズ除去", "中周波除去"])

    if preset == "低周波ノイズ除去":
        lowcut, highcut = 0.025, 0.04
    elif preset == "高周波ノイズ除去":
        lowcut, highcut = 1.0, 2.5
    elif preset == "中周波除去":
        lowcut, highcut = 0.1, 0.3
    else:
        lowcut = st.number_input("Low Cut [Hz]", value=0.025)
        highcut = st.number_input("High Cut [Hz]", value=0.04)

    fs = st.number_input("サンプリング周波数 [Hz]", value=5.0)
    order = st.slider("フィルタ次数", 1, 10, 4)

    if st.button("フィルタを適用する"):
        time = df[time_col].to_numpy()
        temp = df[temp_col].to_numpy()

        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='bandstop')
        filtered_temp = filtfilt(b, a, temp)

        st.line_chart({"元データ": temp, "フィルタ後": filtered_temp})

        df["Filtered"] = filtered_temp
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("フィルタ結果をCSVでダウンロード", csv, "filtered_data.csv", "text/csv")
