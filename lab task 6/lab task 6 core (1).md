# lab6_core.py  (file 1 of 2)
# Data, chunking and scoring functions used by lab6_tasks.py
# All text here is made-up (synthetic) teaching data.

import re
from sklearn.feature_extraction.text import TfidfVectorizer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# ---------------- documents (5 docs, 150-250 words each) ----------------
docs = {
    "late_ug": (
        "Undergraduate Assessment Policy (synthetic). All coursework must be "
        "submitted through the learning portal before the stated deadline, and "
        "the final file must be a single PDF no larger than ten megabytes. Late "
        "submission is normally penalized by ten percent of the available marks "
        "for each calendar day after the deadline. Students who are ill may "
        "request an extension, but an illness extension requires a medical "
        "certificate to be uploaded before the deadline passes, except in "
        "emergency hospital admission where the certificate may follow within "
        "three working days. Group projects follow the same rule and the group "
        "leader must make the request on behalf of every member who is affected "
        "by the illness. Plagiarism cases are handled separately by the "
        "integrity committee, and any extension granted does not pause or cancel "
        "an integrity investigation that is already open for the same piece of "
        "coursework, so students should keep drafts, notes and version history "
        "until the committee has formally closed the case. Questions about marks "
        "should be sent to the course coordinator, who will reply within five "
        "working days during the normal teaching term."
    ),
    "late_pg": (
        "Postgraduate Assessment Policy (synthetic). Postgraduate students "
        "submit coursework and research reports through the learning portal "
        "before the stated deadline, and the file may be a PDF or a Word "
        "document. Late submission is normally penalized by five percent of the "
        "available marks for each calendar day after the deadline. Students who "
        "are ill may request an extension, and a postgraduate illness extension "
        "requires a letter from a registered doctor to be sent to the programme "
        "office within seven days of the deadline, except in thesis milestone "
        "submissions where no extension can be granted without written approval "
        "from the supervisor and the dean. Research students should also record "
        "every approved extension in their supervision log so that the examiners "
        "can see the revised timeline when the thesis is finally assessed, and "
        "they should remember that the log is reviewed at the end of each "
        "semester by the graduate committee together with attendance and "
        "progress notes. Questions about marks should be sent to the programme "
        "office, which keeps a record of every request for audit purposes."
    ),
    "password": (
        "IT Account Recovery Guide (synthetic). If a student forgets a password, "
        "the account can be recovered with the recovery link on the login page, "
        "which sends a one-time code to the registered mobile number. The code "
        "expires after fifteen minutes, and after three wrong attempts the "
        "account is locked for one hour, except for accounts that were locked by "
        "the security team, which can only be unlocked in person at the IT help "
        "desk with a university identity card. Staff accounts follow a different "
        "process and must be reset by the IT service desk after verification by "
        "the line manager. Never share recovery codes with anyone, including "
        "people who claim to work for the university, because the IT department "
        "will never ask for a code by phone, chat or email, and any message that "
        "asks for one should be forwarded to the security mailbox so that the "
        "team can block the sender and warn other users about the attempt. "
        "Passwords must contain at least twelve characters and should not reuse "
        "any of the previous five passwords."
    ),
    "remote": (
        "Remote Work Policy (synthetic). Employees may request remote work for "
        "up to two days each week with written approval from their line manager, "
        "and the arrangement is reviewed every six months. Contractors can work "
        "remotely only if the signed contract explicitly permits it, except when "
        "a department head grants a written exception, and employee remote work "
        "rules do not apply to contractors in any other situation. All remote "
        "workers must use the university virtual private network, keep their "
        "laptop software updated and avoid working on confidential student "
        "records in public places such as cafes or airports, because screens can "
        "be read by strangers and public wireless networks are not considered "
        "secure enough for protected data, even when a personal hotspot or a "
        "password is used. Equipment loaned to remote workers must be returned "
        "within five working days of the end of the arrangement. Requests are "
        "decided by the human resources office, which may ask for a short "
        "written reason and the proposed working schedule before approval."
    ),
    "printer": (
        "Printer Troubleshooting Guide (synthetic). For blank printer pages, "
        "first check the ink or toner level, then run the cleaning utility from "
        "the printer menu, and finally print a test page to confirm the result. "
        "Warning: switch off and unplug the printer before opening any panel, "
        "except when the manual explicitly tells you to remove a cartridge while "
        "the device is powered on. If the pages are still blank after cleaning "
        "twice, contact the IT help desk and quote the device model, because "
        "several office models use a different cartridge type and the cleaning "
        "routine for one model can damage the print head of another model if it "
        "is repeated too many times in a row without waiting. Scanners have a "
        "separate guide: for a blank scanned image, check that the document is "
        "placed face down and that the correct scanning source is selected. "
        "Paper jams are covered in a different section of the manual, and the "
        "help desk can supply spare cartridges on request."
    ),
}

# the exact part of each document that answers the question
evidence = {
    "late_ug": "an illness extension requires a medical certificate to be "
               "uploaded before the deadline passes, except in emergency "
               "hospital admission where the certificate may follow within "
               "three working days.",
    "late_pg": "a postgraduate illness extension requires a letter from a "
               "registered doctor to be sent to the programme office within "
               "seven days of the deadline, except in thesis milestone "
               "submissions where no extension can be granted without written "
               "approval from the supervisor and the dean.",
    "password": "If a student forgets a password, the account can be recovered "
                "with the recovery link on the login page, which sends a "
                "one-time code to the registered mobile number.",
    "remote": "Contractors can work remotely only if the signed contract "
              "explicitly permits it, except when a department head grants a "
              "written exception",
    "printer": "For blank printer pages, first check the ink or toner level, "
               "then run the cleaning utility from the printer menu, and "
               "finally print a test page to confirm the result.",
}

# (question, correct document, dev or test). None = no answer exists
queries = [
    ("What is required for an undergraduate illness extension?", "late_ug", "dev"),
    ("How do I reset a forgotten password?", "password", "dev"),
    ("Can contractors work remotely?", "remote", "dev"),
    ("What should I do about blank printer pages?", "printer", "dev"),
    ("What are tomorrow's flight prices?", None, "dev"),
    ("I was sick and missed the deadline, what proof do I need as an undergraduate?", "late_ug", "test"),
    ("How can I regain access to my login?", "password", "test"),
    ("Does a postgraduate student need a doctor's letter for an extension?", "late_pg", "test"),
    ("My printer outputs empty sheets, which steps should I follow?", "printer", "test"),
    ("Who won the football match?", None, "test"),
]


def check_data():
    # every doc must be 150-250 words and every evidence must be inside its doc
    for name in docs:
        n = len(docs[name].split())
        assert 150 <= n <= 250, name + " has " + str(n) + " words"
    for q, d, split in queries:
        if d is not None:
            assert evidence[d] in docs[d]


# ---------------- chunking ----------------
def word_windows(text, size=40, overlap=10, offset=0):
    # fixed windows of `size` words, moving forward by size - overlap
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("need size > 0 and 0 <= overlap < size")
    words = [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]
    result = []
    for i in range(0, len(words), size - overlap):
        j = min(i + size, len(words))
        result.append((offset + words[i][0], offset + words[j - 1][1]))
        if j == len(words):
            break
    return result


def sentence_chunks(text, size=40):
    # join whole sentences until the word limit is reached
    if size <= 0:
        raise ValueError("size must be positive")
    # cut points = just after ". " or "! " or "? "
    cuts = [0] + [m.end() for m in re.finditer(r"[.!?]\s+", text)] + [len(text)]
    chunks = []
    current = None      # (start, end) of the chunk we are building
    count = 0           # words in current chunk
    for a, b in zip(cuts, cuts[1:]):
        n = len(text[a:b].split())
        if n == 0:
            continue
        if n > size:
            # sentence is too long -> save current, then split it by words
            if current is not None:
                chunks.append(current)
            chunks.extend(word_windows(text[a:b], size, 0, a))
            current, count = None, 0
        elif current is not None and count + n <= size:
            current = (current[0], b)
            count += n
        else:
            if current is not None:
                chunks.append(current)
            current, count = (a, b), n
    if current is not None:
        chunks.append(current)
    # remove trailing spaces from the end positions
    return [(a, a + len(text[a:b].rstrip())) for a, b in chunks]


def make_chunks(docs, strategy):
    # strategy is "0", "10" or "sentence"
    result = []
    for doc_id in docs:
        text = docs[doc_id]
        if strategy == "sentence":
            spans = sentence_chunks(text, 40)
        else:
            spans = word_windows(text, 40, int(strategy))
        for i, (a, b) in enumerate(spans):
            result.append({"id": doc_id + ":" + str(i), "doc": doc_id,
                           "start": a, "end": b, "text": text[a:b]})
    return result


# ---------------- scoring ----------------
def load_model():
    # returns the embedding model, or None if it cannot be loaded
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(MODEL_NAME, device="cpu")
    except Exception as e:
        print("Embedding model not available:", type(e).__name__)
        return None


def get_scores(method, chunk_texts, query_texts, model=None):
    # returns a table: one row per query, one column per chunk
    if method == "tfidf":
        vec = TfidfVectorizer()
        c = vec.fit_transform(chunk_texts)
        q = vec.transform(query_texts)
        return (q @ c.T).toarray()
    c = model.encode(chunk_texts, normalize_embeddings=True)
    q = model.encode(query_texts, normalize_embeddings=True)
    return q @ c.T


def is_relevant(chunk, doc, ev):
    # relevant = right document AND the full evidence is inside the chunk
    return chunk["doc"] == doc and ev in chunk["text"]


def hit_and_mrr(all_scores, chunks, items):
    # items = list of (question, doc, split); only answerable ones counted
    hits, rr = [], []
    for row, (q, d, split) in zip(all_scores, items):
        if d is None:
            continue
        top3 = sorted(range(len(row)), key=lambda i: -row[i])[:3]
        rank = 0
        for pos, i in enumerate(top3, 1):
            if is_relevant(chunks[i], d, evidence[d]):
                rank = pos
                break
        hits.append(1 if rank else 0)
        rr.append(1 / rank if rank else 0)
    return sum(hits) / len(hits), sum(rr) / len(rr)


if __name__ == "__main__":
    check_data()
    print("data ok:", {k: len(v.split()) for k, v in docs.items()})