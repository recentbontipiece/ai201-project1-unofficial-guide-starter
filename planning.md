# Project 1 Planning: The Unofficial Guide
> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.
---

## Domain
<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
Selected Domain: Computer Science Student Survival Guide

I chose to build a Retrieval-Augmented Generation (RAG) system focused on Computer Science students in general rather than a single university. CS students frequently seek advice about internships, technical interviews, course selection, career paths, and skill development. This knowledge is often shared informally through Reddit communities such as r/csMajors, r/cscareerquestions, and r/learnprogramming.

My system will aggregate these student-generated discussions and allow users to ask natural language questions such as:

- How do I get my first internship?
- Is LeetCode enough for technical interviews?
- Should I pursue a Master's degree?
- What projects should I include on my resume?

The system will retrieve relevant discussions and generate grounded answers with citations to the original sources.

---

## Documents
<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | dev.to — Landing Your First CS Internship | Strategic guide on internship hunting with no experience: networking, projects, timing, and applications | https://dev.to/jaber1028/landing-your-first-cs-internship-a-strategic-guide-81j — saved as `documents/first_internship_devto.txt` |
| 2 | dev.to — LeetCode Alone Won't Save You in 2026 | Argues LeetCode is insufficient for FAANG interviews; covers system design, behavioral prep, and pattern-based study | https://dev.to/somadevtoo/leetcode-alone-wont-save-you-in-2026-prepare-these-7-topics-22nl — saved as `documents/leetcode_not_enough_devto.txt` |
| 3 | dev.to — 10 Great Programming Projects to Improve Your Resume | Specific project ideas for CS students to build portfolio-worthy work with real-world impact | https://dev.to/seattledataguy/10-great-programming-projects-to-improve-your-resume-and-learn-to-program-1e2h — saved as `documents/resume_projects_devto.txt` |
| 4 | dev.to — Is a Master's/PhD Worth It in Software Engineering? | Community discussion on ROI of graduate degrees vs. industry experience for software engineers | https://dev.to/fedekau/is-a-mastersphd-degree-worth-the-effortmoney-in-the-software-engineering-universe-27m1 — saved as `documents/masters_degree_worth_it_devto.txt` |
| 5 | dev.to — Imposter Syndrome as a Beginner/Junior Developer | Personal experience and community advice on handling imposter syndrome early in a CS career | https://dev.to/usaidpeerzada/my-experience-with-imposter-syndrome-as-a-beginner-junior-developer-11ec — saved as `documents/imposter_syndrome_devto.txt` |
| 6 | GeeksforGeeks — Complete Technical Interview Preparation Guide | Step-by-step placement prep covering DSA, OOP, DBMS, OS, and interview rounds | https://www.geeksforgeeks.org/technical-interview-preparation/ — saved as `documents/interview_prep_gfg.txt` |
| 7 | GeeksforGeeks — How to Contribute to Open Source | Beginner guide on getting started with open source: finding first issues, making PRs, building a reputation | https://www.geeksforgeeks.org/git/how-to-contribute-open-source/ — saved as `documents/open_source_contribution_gfg.txt` |
| 8 | GeeksforGeeks — How to Build a GitHub Developer Portfolio | Advice on showcasing projects on GitHub to impress recruiters, portfolio structure, and project selection | https://www.geeksforgeeks.org/blogs/how-to-build-a-awesome-github-developer-portfolio/ — saved as `documents/github_portfolio_gfg.txt` |
| 9 | Ask HN — What advice would you give to a CS student today? | Hacker News thread with experienced engineers advising CS students on what to focus on | https://news.ycombinator.com/item?id=43499119 — saved as `documents/cs_student_advice_hn.txt` |
| 10 | Ask HN — What should CS students do to prepare for the job market? | Hacker News discussion on job market preparation, skill-building, and career strategy after graduation | https://news.ycombinator.com/item?id=45120088 — saved as `documents/job_market_prep_hn.txt` |

---

## Chunking Strategy
<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 400 characters

**Overlap:** 80 characters

**Reasoning:** My documents are a mix of dev.to articles (multi-paragraph listicles), GeeksforGeeks guides (structured with headers and bullet points), and Hacker News threads (short, standalone comments). Most key pieces of advice fit within one to three sentences — a 400-character chunk captures a complete thought without merging unrelated points. Chunks smaller than ~200 characters lose enough context that a chunk like "this is especially true for junior roles" would be unretrivable on its own. Chunks larger than ~600 characters start mixing multiple distinct tips, diluting the semantic signal for the embedding model. An 80-character overlap ensures that advice split across a paragraph boundary is still retrievable from either chunk.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers` — runs fully locally with no API key or rate limits.

**Top-k:** 5. CS career advice questions are broad enough that 5 chunks gives the LLM meaningful variety (e.g., internship advice from 2–3 different sources). Fewer than 4 risks missing the most relevant passage; more than 6 risks diluting the context with loosely related content.

**Production tradeoff reflection:** `all-MiniLM-L6-v2` has a 256-token context window, which is tight — chunks longer than ~180 words get silently truncated before embedding. For a production system I would evaluate `text-embedding-3-small` (OpenAI) for its 8,192-token window and stronger accuracy, or `voyage-large-2` (Voyage AI) which is specifically tuned for retrieval tasks and handles longer passages. The tradeoffs are cost (both charge per token vs. free local inference), latency (API round-trip vs. local), and data privacy (text leaves your machine). For a student advice corpus that is not sensitive, the API options would be acceptable; for a system handling private student records, local inference would be mandatory.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do experienced developers and CS students recommend for landing a first software internship with no prior experience? | Apply early (big tech opens in August), build 2–3 personal projects, use LinkedIn and career fairs, leverage referrals from classmates and alumni, don't wait until you feel "ready" |
| 2 | Is practicing LeetCode alone enough to pass technical interviews at large tech companies like Google or Amazon? | No — LeetCode covers coding but not system design, behavioral interviews, or communication. Students recommend supplementing with system design study (ByteByteGo), mock interviews, and learning problem patterns rather than memorizing individual problems |
| 3 | What kinds of projects do CS students and developers say actually stand out to recruiters on a resume? | Full-stack projects with real users or measurable outcomes, tools that solve a genuine problem, deployed applications (not tutorial clones), and AI/ML projects; 2–3 quality projects beats 10 throwaway ones |
| 4 | Is a Master's degree in Computer Science worth pursuing for a software engineering career? | Mixed consensus — worth it for research roles, career switches, or top-10 programs; generally not worth the cost vs. 2–3 years of industry experience for standard software engineering roles |
| 5 | How do CS students and junior developers say you should handle imposter syndrome when starting your career? | Recognize it is universal (senior developers feel it too), track your own progress rather than comparing to others, use Google freely, collaborate instead of compete, and treat uncertainty as a sign you're growing |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning. -->

1. **Noisy article text after scraping:** dev.to and GeeksforGeeks pages include navigation bars, "Related Articles" sidebars, cookie banners, and comment sections that are not substantive content. If cleaning doesn't strip these, chunks will contain fragments like "Read Next" or "Share this article" that have no semantic value and will pollute retrieval results with off-topic matches.

2. **Key advice split across chunk boundaries:** Many articles structure their advice as numbered lists where the list item header ("3. Build real projects") is on one line and the explanation spans the next two paragraphs. If the chunk boundary falls between the header and the explanation, neither chunk is self-contained — the first has a label with no content and the second has content with no label. The 80-character overlap is designed to mitigate this but may not fully solve it for long list items.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages. -->

```mermaid
flowchart LR
    A["Raw .txt files\n(10 articles saved\nfrom web)"] -->|"ingest.py\nload + strip HTML\nnav, ads, footers"| B["Clean Plain Text\nper document"]
    B -->|"chunk.py\nsplit on paragraphs\n400 chars / 80 overlap"| C["Chunks\n~150–400 total\nwith source metadata"]
    C -->|"embed.py\nall-MiniLM-L6-v2\nsentence-transformers"| D[("ChromaDB\nVector Store\nsource + chunk_id metadata")]
    D -->|"retrieve.py\ntop-k = 5\ncosine similarity"| E["Top 5 Chunks\n+ source filenames\n+ distance scores"]
    E -->|"query.py\nGroq API\nllama-3.3-70b-versatile"| F["Grounded Answer\nwith inline citations"]
    F --> G["Gradio Web UI\napp.py\nlocalhost:7860"]
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe which AI tool, what input, expected output, and how you'll verify. -->

**Milestone 3 — Ingestion and chunking:**
I will give Groq (`llama-3.3-70b-versatile` via the Groq API) my Documents section (the 10 source URLs and file types) and my Chunking Strategy section (400-char chunks, 80-char overlap, paragraph-split reasoning). I will ask it to implement `ingest.py` — a script that loads `.txt` files from `documents/`, strips HTML tags and common web boilerplate (nav text, "Read more" links, share buttons), and writes clean text per document — and `chunk.py` — a function that splits clean text by paragraph boundaries (`\n\n`), enforces a 400-character max per chunk with 80-character overlap, and attaches the source filename as metadata. I will verify by printing 5 random chunks and checking each is readable, self-contained, and free of HTML artifacts.

**Milestone 4 — Embedding and retrieval:**
I will give Groq my Architecture diagram (the mermaid diagram above) and Retrieval Approach section. I will ask it to implement `embed.py` — loads all chunks from Milestone 3, embeds each with `SentenceTransformer("all-MiniLM-L6-v2")`, and stores them in a ChromaDB collection with `source` and `chunk_id` metadata fields — and `retrieve.py` — a function `retrieve(query: str, k: int = 5)` that returns the top-k chunks with their text, source filename, and cosine distance score. I will verify by running 3 of my 5 evaluation questions through `retrieve()` and confirming the returned chunks are visibly on-topic and distance scores are below 0.5.

**Milestone 5 — Generation and interface:**
I will give Groq the signature of my `retrieve()` function, my grounding requirement ("the LLM must answer only from the retrieved chunks and must not use its training knowledge — if the documents don't contain enough information, it must say so explicitly"), and the Gradio skeleton from the assignment instructions. I will ask it to implement `query.py` — calls `retrieve()`, formats the chunks into a numbered context block, calls the Groq API (`llama-3.3-70b-versatile`) with a system prompt enforcing grounding, and returns `{answer: str, sources: list[str]}` — and `app.py` — a Gradio UI with a question textbox and two output boxes (answer and sources). I will verify by asking a question that is not in any of my documents and confirming the system responds with "I don't have enough information" rather than hallucinating an answer.
