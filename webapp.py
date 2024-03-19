import streamlit as st


st.title("Testing")


st.title("Testing 2")

st.header("First Header ")

# markdown
st.markdown("Markdown")

# Success text - green
st.success("OK Messages - Green")

# Error text - red
st.error("Oops, error - Red")

# Warning - yellow
st.warning("Warning !!! -  Yellow")

# info - blue
st.info("Information - Blue")

# Actual exceptions
st.exception("Dummy error")

# help = inbuilt docs
st.help(range)

# write
a = 9
st.write(a)

# image
st.image("./images/2.png")

if st.checkbox("1st check box"):
    st.text("Selected Check box")