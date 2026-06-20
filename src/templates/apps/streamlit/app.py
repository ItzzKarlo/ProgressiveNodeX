import pandas as pd
import streamlit as st

st.set_page_config(page_title="Streamlit App", page_icon="🚀")

st.title("ProgressiveNodeX Streamlit starter")
st.write("Edit `app.py` to build your dashboard.")

data = pd.DataFrame(
    {
        "name": ["PNX", "Template", "App"],
        "value": [100, 75, 50],
    }
)

st.bar_chart(data, x="name", y="value")