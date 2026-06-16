import os
import json
from pypdf import PdfReader

# 🔹 Settings
CHUNK_SIZE = 500   # characters per chunk


# ✅ Step 1: Split text into chunks
def split_text(text, chunk_size=CHUNK_SIZE):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]

        if chunk.strip():
            chunks.append(chunk.strip())

    return chunks


# ✅ Step 2: Read PDF files
def load_pdfs(folder_path):
    data = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):

            path = os.path.join(folder_path, filename)
            reader = PdfReader(path)

            print(f"🔍 Reading PDF: {filename}")

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()

                if not text:
                    continue

                chunks = split_text(text)

                for chunk in chunks:
                    data.append({
                        "source": filename,
                        "page": page_num + 1,
                        "text": chunk
                    })

    return data


# ✅ Step 3: Read TXT files
def load_txt(folder_path):
    data = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):

            path = os.path.join(folder_path, filename)

            print(f"🔍 Reading TXT: {filename}")

            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

                chunks = split_text(text)

                for chunk in chunks:
                    data.append({
                        "source": filename,
                        "page": None,
                        "text": chunk
                    })

    return data


# ✅ Step 4: Build knowledge base
def build_knowledge_base(input_folder, output_file):
    all_chunks = []

    pdf_chunks = load_pdfs(input_folder)
    txt_chunks = load_txt(input_folder)

    all_chunks.extend(pdf_chunks)
    all_chunks.extend(txt_chunks)

    # ✅ Save JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)

    print(f"\n✅ DONE: {len(all_chunks)} chunks created")
    print(f"📁 Saved to: {output_file}")