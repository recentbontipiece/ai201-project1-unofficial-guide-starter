import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = "llama-3.3-70b-versatile"

# --- Embeddings ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --- Vector store ---
CHROMA_COLLECTION = "unofficial-guide"
CHROMA_PATH = "./chroma_db"

# --- Retrieval ---
N_RESULTS = 5

# --- Documents ---
DOCS_PATH = "./documents"

# --- Chunking ---
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80
MIN_CHUNK_LENGTH = 50

# --- Source catalog ---
# Maps each local document filename to its display name and original public URL.
# Used to cite the original article (not the private local .txt copy) in
# generated answers, and to render the sidebar source list in app.py.
SOURCES = [
    {
        "filename": "first_internship_devto.txt",
        "display_name": "First CS Internship Guide",
        "icon": "💼",
        "url": "https://dev.to/jaber1028/landing-your-first-cs-internship-a-strategic-guide-81j",
    },
    {
        "filename": "leetcode_not_enough_devto.txt",
        "display_name": "LeetCode Isn't Enough",
        "icon": "🧩",
        "url": "https://dev.to/somadevtoo/leetcode-alone-wont-save-you-in-2026-prepare-these-7-topics-22nl",
    },
    {
        "filename": "resume_projects_devto.txt",
        "display_name": "Resume Project Ideas",
        "icon": "🛠️",
        "url": "https://dev.to/seattledataguy/10-great-programming-projects-to-improve-your-resume-and-learn-to-program-1e2h",
    },
    {
        "filename": "masters_degree_worth_it_devto.txt",
        "display_name": "Master's Degree Worth It?",
        "icon": "🎓",
        "url": "https://dev.to/fedekau/is-a-mastersphd-degree-worth-the-effortmoney-in-the-software-engineering-universe-27m1",
    },
    {
        "filename": "imposter_syndrome_devto.txt",
        "display_name": "Imposter Syndrome",
        "icon": "🪞",
        "url": "https://dev.to/usaidpeerzada/my-experience-with-imposter-syndrome-as-a-beginner-junior-developer-11ec",
    },
    {
        "filename": "interview_prep_gfg.txt",
        "display_name": "Technical Interview Prep",
        "icon": "📝",
        "url": "https://www.geeksforgeeks.org/technical-interview-preparation/",
    },
    {
        "filename": "open_source_contribution_gfg.txt",
        "display_name": "Open Source Contribution",
        "icon": "🌱",
        "url": "https://www.geeksforgeeks.org/git/how-to-contribute-open-source/",
    },
    {
        "filename": "github_portfolio_gfg.txt",
        "display_name": "GitHub Portfolio Guide",
        "icon": "👤",
        "url": "https://www.geeksforgeeks.org/blogs/how-to-build-a-awesome-github-developer-portfolio/",
    },
    {
        "filename": "cs_student_advice_hn.txt",
        "display_name": "CS Student Advice (HN)",
        "icon": "💬",
        "url": "https://news.ycombinator.com/item?id=43499119",
    },
    {
        "filename": "job_market_prep_hn.txt",
        "display_name": "Job Market Prep (HN)",
        "icon": "📈",
        "url": "https://news.ycombinator.com/item?id=45120088",
    },
]

SOURCE_BY_FILENAME = {s["filename"]: s for s in SOURCES}
