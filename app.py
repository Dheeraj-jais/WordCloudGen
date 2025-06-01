import streamlit as st
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import io # For handling image bytes for download

# --- Configuration for the Page ---
st.set_page_config(
    page_title="Word Cloud Generator",
    layout="wide" # "centered" or "wide"
)

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- Helper Function to Generate Word Cloud ---
def generate_wordcloud(text, max_words, background_color, colormap, custom_stopwords, mask_image_array, contour_width, contour_color, use_contour):
    """Generates and returns a word cloud image."""
    stopwords_set = set(STOPWORDS)
    if custom_stopwords:
        stopwords_set.update([word.strip().lower() for word in custom_stopwords.split(',') if word.strip()])

    wc = WordCloud(
        background_color=background_color,
        stopwords=stopwords_set,
        max_words=max_words,
        mask=mask_image_array,
        contour_width=contour_width if use_contour and mask_image_array is not None else 0,
        contour_color=contour_color if use_contour and mask_image_array is not None else 'black',
        colormap=colormap,
        width=1200 if mask_image_array is None else None, # Width/height less important if mask is used
        height=600 if mask_image_array is None else None,
        min_font_size=10,
        prefer_horizontal=0.9 # Prefer horizontal words
    )
    try:
        wc.generate(text)
        return wc
    except ValueError as e:
        # Handle cases like empty text after stopword removal
        if "empty" in str(e).lower():
            st.warning("The provided text resulted in no words to display after processing (e.g., all stopwords or too short). Please try different text or fewer stopwords.")
            return None
        else:
            raise e


# --- Streamlit App UI ---
st.title("Interactive Word Cloud Generator")
st.markdown("Create beautiful word clouds from your text. Customize colors, shapes, and Download it !")

# --- Layout with Columns ---
col1, col2 = st.columns([2, 1]) # Input text area takes 2/3, controls take 1/3

with col1:
    st.subheader("📝 Input Your Text")
    user_text = st.text_area(
        "Paste your text below:",
        height=300,
        placeholder="Enter a long piece of text here to see a meaningful word cloud. The more frequent a word, the larger it will appear."
    )

    # --- Download Button Preparation ---
    # We'll populate this after generation
    wordcloud_image_bytes = None


with col2:
    st.subheader("⚙️ Customization Options")

    max_words = st.slider("Maximum Words:", min_value=10, max_value=500, value=100, step=10)
    background_color = st.color_picker("Background Color:", "#FFFFFF") # Default white

    # Available colormaps (curated list for better visuals)
    # Full list: https://matplotlib.org/stable/gallery/color/colormap_reference.html
    colormap_options = [
        'viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Purples',
        'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd',
        'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn',
        'YlGn', 'Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1',
        'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c', 'ocean', 'gist_earth'
    ]
    selected_colormap = st.selectbox("Word Color Scheme (Colormap):", colormap_options, index=colormap_options.index('viridis'))

    custom_stopwords_input = st.text_input("Additional Stopwords (comma-separated):", placeholder="e.g., thing, stuff, like")

    mask_array = None
    use_contour = False
    contour_width = 0
    contour_color = 'black'

# --- Generate Button and Display ---
if st.button("🚀 Generate Word Cloud", type="primary", use_container_width=True):
    if user_text and user_text.strip():
        with st.spinner("Generating your word cloud... Please wait."):
            wordcloud_object = generate_wordcloud(
                user_text,
                max_words,
                background_color,
                selected_colormap,
                custom_stopwords_input,
                mask_array,
                contour_width,
                contour_color,
                use_contour
            )

        if wordcloud_object:
            st.subheader("🎉 Your Word Cloud:")

            # Display using Matplotlib to have more control for download
            fig, ax = plt.subplots(figsize=(12, 6)) # Adjust as needed
            ax.imshow(wordcloud_object, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)

            # Prepare image for download
            img_byte_arr = io.BytesIO()
            fig.savefig(img_byte_arr, format='PNG', bbox_inches='tight', pad_inches=0.1, dpi=300)
            img_byte_arr.seek(0)
            wordcloud_image_bytes = img_byte_arr.getvalue()

    elif not user_text or not user_text.strip():
        st.warning("Please enter some text to generate a word cloud.")

# Add download button outside the generate button logic so it persists if image exists
if wordcloud_image_bytes: # Check if bytes exist from a previous generation
    st.download_button(
        label="📥 Download Word Cloud (PNG)",
        data=wordcloud_image_bytes,
        file_name="my_word_cloud.png",
        mime="image/png",
        use_container_width=True
    )


st.markdown("---")
st.markdown("Created by Dheeraj jaiswal")

