import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import requests
import io

# Configure Gemini API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])


def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(input_text)
    return response.text


def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += str(page.extract_text())
    return text


def download_pdf_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        return io.BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading PDF: {e}")
        return None


# Streamlit UI setup
st.set_page_config(page_title="Paper Genie",
                   page_icon="📑", layout="centered")
st.title("📑 Paper Genie")
st.markdown(
    "Research paper analyzer that provides easy-to-understand summaries and insights")

# UI Layout - Two options for input
input_option = st.radio(
    "Choose input method:",
    ["Upload PDF", "Enter PDF URL"]
)

paper_text = None

if input_option == "Upload PDF":
    uploaded_file = st.file_uploader(
        "Upload Research Paper", type=["pdf"], help="Upload the research paper in PDF format")

    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            paper_text = input_pdf_text(uploaded_file)

else:  # URL option
    pdf_url = st.text_input("Enter URL to PDF paper:",
                            placeholder="https://example.com/research-paper.pdf")

    if pdf_url:
        with st.spinner("Downloading and extracting text from PDF..."):
            pdf_file = download_pdf_from_url(pdf_url)
            if pdf_file:
                paper_text = input_pdf_text(pdf_file)

# Submit Button
submit = st.button("🔍 Analyze Paper", use_container_width=True)

# Prompt Template
input_prompt_template = """
You are an expert research paper analyst with deep knowledge across multiple scientific domains.
Analyze the provided research paper and create an accessible breakdown for a general audience.

Please provide your analysis in the following structure:

1. SUMMARY:
   - Provide a clear, concise summary of the paper in simple language (2-3 paragraphs)
   - Include the main research question, methodology, and findings

2. KEY TAKEAWAYS:
   - List 4-6 bullet points of the most important findings or contributions
   - Explain why these findings are significant
   - Highlight any novel techniques or approaches introduced

3. FUTURE WORK IDEAS:
   - Suggest 3-5 potential research directions that could build upon this paper
   - Identify gaps or limitations in the current research that future work could address
   - Propose practical applications of the research findings

Research Paper:
{text}
"""

if submit:
    if not paper_text:
        st.warning("⚠️ Please provide a research paper (upload or URL).")
    else:
        with st.spinner("Analyzing research paper with AI..."):
            filled_prompt = input_prompt_template.format(text=paper_text)
            response = get_gemini_response(filled_prompt)

            st.markdown("### 📊 Analysis Results")
            st.markdown(response)
