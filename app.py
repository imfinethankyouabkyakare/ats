import streamlit as st
import PyPDF2
import nltk
from collections import Counter
from docx import Document
import difflib  # For calculating similarity in plagiarism check
from dotenv import load_dotenv
load_dotenv()
import base64
import os
from PIL import Image
import pdf2image
import google.generativeai as genai
from io import BytesIO
from fpdf import FPDF
import plotly.graph_objects as go

# Set Streamlit page config at the top
st.set_page_config(page_title="GLA ATS System", page_icon=":guardsman:")

nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()
    return text

def input_pdf_setup(pdf_file):
    return [extract_text_from_pdf(pdf_file)]


# Streamlit UI
st.title("**GLA University ATS System**")
st.subheader("About")
st.write("This sophisticated ATS project, developed with Gemini Pro and Streamlit, seamlessly incorporates advanced features including resume match percentage, keyword analysis to identify missing criteria, and the generation of comprehensive profile summaries, enhancing the efficiency and precision of the candidate evaluation process for discerning talent acquisition professionals.")

st.markdown("""  
  - [Streamlit](https://streamlit.io/)  
  - [Gemini Pro](https://deepmind.google/technologies/gemini/#introduction)  
  - [makersuit API Key](https://makersuite.google.com/)  
""")

# Sidebar for input
st.sidebar.header("Upload Your Job Description")
job_desc_file = st.sidebar.file_uploader("Upload Job Description (PDF)", type="pdf")

# Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager tasked with evaluating resumes against job descriptions. 
Using the provided job description and resume text, perform a detailed analysis. Highlight the following:
1. Candidate's strengths in relation to the job requirements.
2. Key weaknesses or areas needing improvement.
3. Specific skills or experiences that align with the job description.
4. Overall fit for the role.
Return the evaluation in a clear, professional format.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
Your task is to evaluate the resume against the provided job description and provide a match percentage.
The output should be a numerical percentage value only, without any additional text or symbols (e.g., 75).
"""

input_prompt4 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality,
your task is to evaluate the resume against the provided job description. Give me the relevant skills if the resume matches
the job description. The output should come as text containing all relevant skills required for the given job description.
"""

input_prompt5 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality,
your task is to evaluate the resume against the provided job description. Give me the non-relevant skills if the resume matches
the job description. The output should come as text containing all non-relevant skills mentioned in the resume that are not required for the given job description.
"""

input_prompt6 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
Your task is to evaluate the resume against the provided job description and provide a plagiarism percentage.
The output should be a numerical percentage value only, without any additional text or symbols (e.g., 75).
"""

input_prompt7 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
Your task is to evaluate the resume against the provided job description and return only the Relevant Projects for the given job description.
The output should come as text containing all relevant projects required for the given job description.
"""

input_prompt8 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
Your task is to evaluate the resume against the provided job description and return only the Recommended Skills required that are not available in the resume but given in the job description.
The output should come as text containing all recommended skills required for the given job description.
"""

# If a job description is uploaded
if job_desc_file is not None:
    pdf_content = input_pdf_setup(job_desc_file)
    job_desc_text = pdf_content[0]

    st.subheader("Your Resume")
    resume_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf")

    if resume_file is not None:
        opt = st.sidebar.selectbox("Available Options", ["Choose an option", "Percentage match", "Show Relevant Skills", "Non-relevant Skills", "Plagiarism Score", "Relevant Projects", "Recommended Skills", "Tell Me About the Resume"])

        resume_pdf_content = input_pdf_setup(resume_file)
        resume_text = resume_pdf_content[0]

        # Get match percentage
        if opt == "Percentage match":
            response = get_gemini_response(input_prompt3, pdf_content, job_desc_text[0])
            # Display the percentage as a progress bar
            st.subheader("Percentage Match")
            st.progress(int(response))
            st.write(f"Match: {response}%")

        # Get relevant skills
        if opt == "Show Relevant Skills":
            relevant_skills = get_gemini_response(resume_text, pdf_content, input_prompt4)
            st.write("Relevant Skills:")
            st.write(relevant_skills)

        # Get non-relevant skills
        if opt == "Non-relevant Skills":
            non_relevant_skills = get_gemini_response(resume_text, pdf_content, input_prompt5)
            st.write("Non-Relevant Skills:")
            st.write(non_relevant_skills)

        # Get plagiarism percentage
        if opt == "Plagiarism Score":
            response = get_gemini_response(input_prompt6, pdf_content, job_desc_text[0])
            st.subheader("Plagiarism Score")
            # Display the percentage as a progress bar
            st.progress(int(response))
            st.write(f"Match: {response}%")

        # Get relevant projects
        if opt == "Relevant Projects":
            relevant_projects = get_gemini_response(resume_text, pdf_content, input_prompt7)
            st.write("Relevant Projects:")
            st.write(relevant_projects)

        # Get recommended skills
        if opt == "Recommended Skills":
            recommended_skills = get_gemini_response(resume_text, pdf_content, input_prompt8)
            st.write("Recommended Skills:")
            st.write(recommended_skills)

        if opt == "Tell Me About the Resume":
            response = get_gemini_response( resume_text, job_desc_text[0], input_prompt1)
            st.subheader("Resume Tells")
            st.write(response)
