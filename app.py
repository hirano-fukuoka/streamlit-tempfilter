import streamlit as st
import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
from datetime import datetime

st.set_page_config(page_title="バンドストップフィルタ", layout="wide")
st.title("📉 温度データ バンドストップフィルタ Webアプリ")

uploaded_file = st.file_uploader("CSV または Excelファイルをアップロードしてください", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".xlsx"):
        sheet_names = pd.ExcelFile(uploaded_file).sheet_names
        selected_sheet = st.selectbox("シートを選択", sheet_names)
        try:
            df = pd.read_excel(uploaded_file, sheet_name=selected_sheet, header=2)
        except Exception as e:
            st.error(f"Excelファイルの読み込みに失敗しました: {e}")
            st.stop()
    else:
        df = pd.read_csv(uploaded_file)

    st.subheader("アップロードされたデータのプレビュー:")
    st.dataframe(df.head())

    time_col = st.selectbox("時間列を選択", df.columns)
    temp_col = st.selectbox("温度列を選択", df.columns)

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
        try:
            time_series = pd.to_numeric(df[time_col], errors='coerce')
            temp_series = pd.to_numeric(df[temp_col], errors='coerce')
            temp_data = temp_series.dropna().to_numpy()

            if len(temp_data) < 10:
                st.error("有効なデータが10件未満です。入力データを確認してください。")
                st.stop()

            nyq = 0.5 * fs
            low = lowcut / nyq
            high = highcut / nyq
            b, a = butter(order, [low, high], btype='bandstop')
            filtered_temp = filtfilt(b, a, temp_data)

            st.line_chart({
                "元データ": temp_data,
                "フィルタ後": filtered_temp
            })

            # NaNを除いたインデックスに戻して代入
            df_filtered = df.copy()
            df_filtered["Filtered"] = np.nan
            df_filtered.loc[temp_series.dropna().index, "Filtered"] = filtered_temp

            # CSV出力
            csv = df_filtered.to_csv(index=False).encode("utf-8")
            
            # ファイル名に日時を付ける
            timestamp = datetime.now().strftime("%m%d%H%M")
            filename = f"filtered_data_{timestamp}.csv"
            
            st.download_button("📥 フィルタ結果をCSVでダウンロード", csv, filename, "text/csv")
            
        except Exception as e:
            st.error(f"フィルタ処理中にエラーが発生しました: {e}")
