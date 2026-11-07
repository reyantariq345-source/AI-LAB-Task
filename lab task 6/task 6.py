# lab6_tasks.py  

import sys
import re
import csv
import time
from pathlib import Path
from lab6_core import *

strategies = ["0", "10", "sentence"]
names = {"0": "window-0", "10": "window-10", "sentence": "sentence-40"}


# =====================================================================
# TASK 1 : tokenization + FAQ chatbot
# =====================================================================
samples = ["AI, search!", "I can't log in.", "help@example.com",
           "CS4944", "", "یہ ایک مثال ہے",
           "Mail ali.khan@uni.edu.pk, version 2.1!"]

faq = [
    {"question": "How do I reset my password?",
     "answer": "Use the recovery link on the login page.", "source": "it_help.txt"},
    {"question": "Where do I submit my assignment?",
     "answer": "Use the assignment upload page in the learning portal.", "source": "assessment.txt"},
    {"question": "Can illness justify a late submission?",
     "answer": "Request an extension with medical evidence before the deadline.", "source": "handbook.txt"},
    # two new FAQs added for the task
    {"question": "How do I connect to campus Wi-Fi?",
     "answer": "Select the campus network and sign in with your student account.", "source": "it_network.txt"},
    {"question": "How do I request an official transcript?",
     "answer": "Submit the transcript form at the registrar office.", "source": "registrar.txt"},
]


def faq_reply(query, method="tfidf", model=None):
    if query.strip() == "":
        return "Please enter a question."
    # exact question -> give the stored answer
    for f in faq:
        if query.strip().lower() == f["question"].lower():
            return f["answer"] + " [source: " + f["source"] + "]"
    # otherwise only show suggestions
    texts = [f["question"] + " " + f["answer"] for f in faq]
    scores = get_scores(method, texts, [query], model)[0]
    order = sorted(range(len(faq)), key=lambda i: -scores[i])[:3]
    if method == "tfidf" and scores[order[0]] == 0:
        return "No matching FAQ. Please contact the help desk."
    lines = ["Possible matches, choose or rephrase your question:"]
    for i in order:
        lines.append("  - " + faq[i]["question"] + " (score " + format(scores[i], ".3f")
                     + ", source: " + faq[i]["source"] + ")")
    return "\n".join(lines)


def task1():
    print("===== TASK 1: tokenization =====")
    model = load_model()
    for text in samples:
        ws = text.split()
        words = re.findall(r"\b\w+\b", text)
        print("\nOriginal  :", repr(text))
        print("Whitespace:", ws, len(ws))
        print("Word-like :", words, len(words))
    if model is not None:
        print("\nModel tokenizer (sub-words):")
        for text in ["I can't log in.", "help@example.com"]:
            t = model.tokenizer.tokenize(text)
            print(" ", repr(text), t, len(t))
    print("""
Two differences:
 1. "I can't log in." -> whitespace gives 4, regex gives 5 because can't becomes can + t.
 2. "help@example.com" -> whitespace gives 1, regex gives 3 (help, example, com).
Normalization risk: lowercasing or removing punctuation can change the meaning
(can't -> can t loses the negation) and can break identifiers like CS4944.
So keep the original text and only use a cleaned copy for searching.
The regex is not a full multilingual tokenizer, it just splits on word characters.""")

    print("\n===== TASK 1: FAQ chatbot (tfidf) =====")
    for q in ["How do I reset my password?", "password recovery",
              "How do I get my transcript?", "", "volcano geology"]:
        print("You:", repr(q))
        print("Bot:", faq_reply(q))
        print()
    print("""Why does the bot ask for confirmation on non-exact questions?
A similarity score only says two texts look alike. It does not prove the FAQ
really answers the question, so the user must confirm the suggestion.""")


# =====================================================================
# TASK 2 : chunking + semantic suggestions
# =====================================================================
def task2():
    check_data()
    print("===== TASK 2: chunking =====")
    original_words = sum(len(t.split()) for t in docs.values())
    print("Documents:", len(docs), " Total words:", original_words)
    print("\nstrategy      chunks  avg words  max words  duplicate words  evidence in one chunk")
    for s in strategies:
        chunks = make_chunks(docs, s)
        sizes = [len(c["text"].split()) for c in chunks]
        total = sum(sizes)
        kept = []
        for d in evidence:
            for c in chunks:
                if c["doc"] == d and evidence[d] in c["text"]:
                    kept.append(d)
                    break
        for c in chunks:
            assert c["text"] == docs[c["doc"]][c["start"]:c["end"]]
        print(names[s].ljust(14), str(len(chunks)).ljust(7), format(total / len(chunks), ".1f").ljust(10),
              str(max(sizes)).ljust(10), str(total - original_words).ljust(16),
              str(len(kept)) + "/" + str(len(evidence)))
        broken = [d for d in evidence if d not in kept]
        print("   evidence split in:", broken if broken else "none")

    print("\nChunk ids and offsets (sentence, doc late_ug):")
    for c in make_chunks({"late_ug": docs["late_ug"]}, "sentence"):
        print("  ", c["id"], c["start"], c["end"], "words =", len(c["text"].split()))

    print("\n----- boundary tests -----")
    assert word_windows("") == []
    assert sentence_chunks("") == []
    assert word_windows("short text") == [(0, 10)]
    for size, overlap in [(2, 2), (2, 5), (0, 0), (5, -1)]:
        try:
            word_windows("a b c", size, overlap)
            print("ERROR: bad overlap accepted", size, overlap)
        except ValueError:
            pass
    long_sentence = " ".join(["word"] * 95) + "."
    parts = sentence_chunks(long_sentence)
    assert all(len(long_sentence[a:b].split()) <= 40 for a, b in parts)
    print("empty text ok, short doc = 1 chunk, bad overlap gives ValueError,")
    print("95-word sentence split into", len(parts), "chunks")

    example = "Dr. Khan approved the form. Late work is penalized."
    print("\nSentence splitter problem:")
    print("  ", re.split(r"(?<=[.!?])\s+", example))
    print("   'Dr.' is treated as the end of a sentence (also fails on U.S., 3.5, Urdu full stop).")

    print("\n===== TASK 2: paraphrased queries =====")
    paraphrases = ["How can I regain access to my account?",
                   "My employer is not a permanent staff member, can I work from home?",
                   "The printer gives me empty sheets"]
    chunks = make_chunks(docs, "sentence")
    texts = [c["text"] for c in chunks]
    model = load_model()
    methods = ["tfidf"]
    if model is not None:
        methods.append("embedding")
    for method in methods:
        print("\n### method:", method)
        scores = get_scores(method, texts, paraphrases, model)
        for q, row in zip(paraphrases, scores):
            print("Query:", q)
            top3 = sorted(range(len(row)), key=lambda i: -row[i])[:3]
            for i in top3:
                c = chunks[i]
                print("  ", c["id"], c["start"], c["end"], "score =", format(row[i], ".3f"))
                print("      ", c["text"][:120], "...")
    if model is None:
        print("\n(embedding part skipped, run again with internet to download the model)")


# =====================================================================
# TASK 3 : evaluation
# =====================================================================
def csv_file():
    theory = Path(__file__).resolve().parent.parent / "theory"
    if theory.exists():
        return theory / "retrieval_log.csv"
    return Path("retrieval_log.csv")


def task3():
    check_data()
    print("===== TASK 3: evaluation =====")
    start = time.perf_counter()
    model = load_model()
    print("model load seconds:", format(time.perf_counter() - start, ".2f"))
    qtexts = [q[0] for q in queries]
    methods = ["tfidf"] + (["embedding"] if model is not None else [])

    results = {}      # (strategy, method) -> info
    log = []          # rows for the csv
    print("\nstrategy     method     chunks  dev Hit/MRR   test Hit/MRR   encode s  search s")
    for s in strategies:
        chunks = make_chunks(docs, s)
        texts = [c["text"] for c in chunks]
        if model is not None:
            lens = [len(model.tokenizer(t)["input_ids"]) for t in texts + qtexts]
            print("token check", names[s], "max tokens =", max(lens), "limit =", model.max_seq_length)
            assert max(lens) <= model.max_seq_length
        for method in methods:
            # time for turning text into vectors
            t = time.perf_counter()
            if method == "tfidf":
                vec = TfidfVectorizer()
                C = vec.fit_transform(texts)
                Q = vec.transform(qtexts)
            else:
                C = model.encode(texts, normalize_embeddings=True)
                Q = model.encode(qtexts, normalize_embeddings=True)
            encode_time = time.perf_counter() - t
            # time for comparing queries with chunks
            t = time.perf_counter()
            scores = Q @ C.T
            if method == "tfidf":
                scores = scores.toarray()
            search_time = time.perf_counter() - t

            dev_idx = [i for i, q in enumerate(queries) if q[2] == "dev"]
            test_idx = [i for i, q in enumerate(queries) if q[2] == "test"]
            dev = hit_and_mrr(scores[dev_idx], chunks, [queries[i] for i in dev_idx])
            test = hit_and_mrr(scores[test_idx], chunks, [queries[i] for i in test_idx])
            results[(s, method)] = {"chunks": chunks, "scores": scores, "dev": dev, "test": test}
            print(names[s].ljust(12), method.ljust(10), str(len(chunks)).ljust(7),
                  format(dev[0], ".3f") + "/" + format(dev[1], ".3f"), "   ",
                  format(test[0], ".3f") + "/" + format(test[1], ".3f"), "    ",
                  format(encode_time, ".4f"), " ", format(search_time, ".5f"))

            for (q, d, split), row in zip(queries, scores):
                top3 = sorted(range(len(row)), key=lambda i: -row[i])[:3]
                for rank, i in enumerate(top3, 1):
                    c = chunks[i]
                    log.append({"strategy": names[s], "method": method, "query": q,
                                "split": split, "answerable": d is not None, "rank": rank,
                                "score": round(float(row[i]), 4), "chunk_id": c["id"],
                                "start": c["start"], "end": c["end"], "text": c["text"]})

    with open(csv_file(), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(log[0].keys()))
        writer.writeheader()
        writer.writerows(log)
    print("\ncsv saved:", csv_file())

    # pick the best setting using DEV results only
    best = max(results, key=lambda k: (results[k]["dev"][1], results[k]["dev"][0], -len(results[k]["chunks"])))
    r = results[best]
    print("\nSelected on dev:", names[best[0]], "+", best[1])
    print("  dev  Hit@3 =", format(r["dev"][0], ".3f"), " MRR@3 =", format(r["dev"][1], ".3f"))
    print("  test Hit@3 =", format(r["test"][0], ".3f"), " MRR@3 =", format(r["test"][1], ".3f"), "(not tuned)")

    print("\nTop-3 results of the selected setting:")
    for (q, d, split), row in zip(queries, r["scores"]):
        print("\n[" + split + "]", q, "(correct doc:", d, ")")
        top3 = sorted(range(len(row)), key=lambda i: -row[i])[:3]
        for rank, i in enumerate(top3, 1):
            c = r["chunks"][i]
            good = d is not None and is_relevant(c, d, evidence[d])
            print("  " + str(rank) + ".", c["id"], c["start"], c["end"], "score =",
                  format(row[i], ".3f"), "RELEVANT" if good else "")
            print("     ", c["text"])

    print("\nFAILURES (no relevant chunk in top 3):")
    for (s, method), info in results.items():
        for (q, d, split), row in zip(queries, info["scores"]):
            if d is None:
                continue
            top3 = sorted(range(len(row)), key=lambda i: -row[i])[:3]
            if not any(is_relevant(info["chunks"][i], d, evidence[d]) for i in top3):
                c = info["chunks"][top3[0]]
                print(" -", names[s], method, "|", q, "| top-1:", c["id"], "|", c["text"][:70], "...")

    print("\nUNANSWERABLE queries (selected setting):")
    top1 = r["scores"].max(axis=1)
    for i, (q, d, split) in enumerate(queries):
        if d is None:
            best_chunk = r["chunks"][int(r["scores"][i].argmax())]
            print("  [" + split + "]", q, "-> top-1", best_chunk["id"], "score =", format(top1[i], ".3f"))
    dev_answerable = [top1[i] for i, q in enumerate(queries) if q[2] == "dev" and q[1] is not None]
    dev_unanswerable = [top1[i] for i, q in enumerate(queries) if q[2] == "dev" and q[1] is None]
    if max(dev_unanswerable) < min(dev_answerable):
        threshold = (max(dev_unanswerable) + min(dev_answerable)) / 2
        print("  threshold from dev =", format(threshold, ".3f"))
        for i, q in enumerate(queries):
            if q[2] == "test":
                print("    test:", q[0], "->", "ACCEPT" if top1[i] >= threshold else "REJECT")
    else:
        print("  dev scores overlap, so no safe threshold. Always show candidates for confirmation.")
    print("""
Why does the system still return text for an unanswerable question?
Ranking just sorts all chunks by score and returns the best ones. The best
chunk is only the 'least bad' one, a high score does not prove it answers the question.""")


# =====================================================================
# chatbots (live input / output)
# =====================================================================
def faqbot(method):
    model = load_model() if method == "embedding" else None
    print("FAQ assistant. Type exit to stop.")
    while True:
        try:
            q = input("You: ")
        except (EOFError, KeyboardInterrupt):
            break
        if q.strip().lower() == "exit":
            break
        print("Bot:", faq_reply(q, method, model))


def docbot(strategy, method):
    model = load_model() if method == "embedding" else None
    chunks = make_chunks(docs, strategy)
    texts = [c["text"] for c in chunks]
    print("Evidence assistant (" + names[strategy] + ", " + method + "). Type exit to stop.")
    while True:
        try:
            q = input("Question: ")
        except (EOFError, KeyboardInterrupt):
            break
        if q.strip().lower() == "exit":
            break
        if q.strip() == "":
            print("Please enter a question.")
            continue
        row = get_scores(method, texts, [q], model)[0]
        top3 = sorted(range(len(row)), key=lambda i: -row[i])[:3]
        if method == "tfidf" and row[top3[0]] == 0:
            print("No candidate evidence; rephrase or contact a human.")
            continue
        print("Candidate evidence (please check it yourself):")
        for n, i in enumerate(top3, 1):
            print(n, chunks[i]["id"], format(row[i], ".3f"), "characters", chunks[i]["start"], chunks[i]["end"])
        choice = input("Choose 1-3 to read, or press Enter if none fits: ")
        if not choice.isdigit() or not 1 <= int(choice) <= len(top3):
            print("No answer selected. Rephrase or contact a human.")
            continue
        c = chunks[top3[int(choice) - 1]]
        print("Passage:", c["text"])
        print("Source:", c["doc"], "characters", c["start"], c["end"])


# =====================================================================
if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    method = "embedding" if "--embedding" in sys.argv else "tfidf"
    if cmd in ("task1", "all"):
        task1()
    if cmd in ("task2", "all"):
        task2()
    if cmd in ("task3", "all"):
        task3()
    if cmd == "faqbot":
        faqbot(method)
    if cmd == "docbot":
        docbot("sentence", method)