"""Enhanced corpus loader that extracts from both TXT and PDF files."""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple
import PyPDF2

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from app.models.database import Base, LegalDocument, init_db, enable_pgvector

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large-instruct")


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file."""
    text_parts = []
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(text)
                except Exception as e:
                    print(f"    ⚠ Warning: Could not extract page {page_num + 1} from {pdf_path}: {e}")
                    continue
        return '\n'.join(text_parts)
    except Exception as e:
        print(f"    ✗ Error reading PDF {pdf_path}: {e}")
        return ""


def parse_pdf_into_articles(text: str, law_code: str, filename: str) -> List[Tuple[str, str, str, str]]:
    """Parse PDF text into logical sections/articles."""
    articles = []

    # Detect Mauritanian law code from filename
    if "code_du_travail" in filename.lower():
        law_code = "Code du Travail"
    elif "code du travail" in filename.lower():
        law_code = "Code du Travail"
    elif "convention collective" in filename.lower():
        law_code = "Convention Collective du Travail"
    elif "obligations" in filename.lower() or "contrats" in filename.lower():
        law_code = "Code des Obligations et des Contrats"
    elif "commerce" in filename.lower():
        law_code = "Code du Commerce"
    elif "international" in filename.lower():
        law_code = "Conventions Internationales"

    # Split by article markers
    article_pattern = r'(?:^|\n)(ARTICLE\s+\d+|Article\s+\d+|ART\.\s+\d+)\s*:?\s*(.+?)(?=\n(?:ARTICLE|Article|ART\.|TITRE|Title|CHAPITRE|Chapter)|\Z)'

    matches = re.finditer(article_pattern, text, re.IGNORECASE | re.DOTALL | re.MULTILINE)

    article_num = 0
    for match in matches:
        article_header = match.group(1).strip()
        article_content = match.group(2).strip()

        if len(article_content) > 30:  # Minimum content length
            article_num += 1
            articles.append((
                law_code,
                article_header.replace('\n', ' '),
                "",  # title
                article_content[:2000]  # Limit content size
            ))

    # If no articles found, split into sections by large paragraphs
    if not articles:
        sections = re.split(r'\n\n+', text)
        for i, section in enumerate(sections):
            if len(section) > 100:  # Reasonable section length
                articles.append((
                    law_code,
                    f"Section {i + 1}",
                    "",
                    section[:1000]
                ))

    return articles


def load_all_corpus(session_maker, embedding_model):
    """Load legal corpus from all available sources."""

    session = session_maker()
    total_loaded = 0

    try:
        # Load embedding model
        print(f"\n📦 Loading embedding model: {embedding_model}")
        model = SentenceTransformer(embedding_model)

        # Determine resource paths
        ressource_dir = Path("/app/data/corpus")
        txt_file = ressource_dir / "les lois.txt"

        if not ressource_dir.exists():
            print(f"✗ Resource directory not found: {ressource_dir}")
            return False

        print(f"\n📂 Found resource directory: {ressource_dir}\n")

        # Load TXT corpus first
        if txt_file.exists():
            print(f"📄 Processing: les lois.txt")
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()

            laws = parse_txt_corpus(content)
            print(f"   → Extracted {len(laws)} articles from TXT")

            for i, (law_code, article, title, content) in enumerate(laws):
                if not content or len(content) < 10:
                    continue

                try:
                    embedding = model.encode(content, normalize_embeddings=True)
                    doc = LegalDocument(
                        law_code=law_code,
                        article=article,
                        article_title=title,
                        content=content,
                        embedding=embedding,
                        jurisdiction="Mauritanie",
                        category="labor" if "Travail" in law_code else "corporate"
                    )
                    session.add(doc)
                    total_loaded += 1

                    if (total_loaded % 20) == 0:
                        session.commit()
                        print(f"     Loaded {total_loaded} documents...")

                except Exception as e:
                    print(f"     ⚠ Error: {e}")
                    continue

        # Load all PDF files
        pdf_files = sorted(ressource_dir.glob("*.pdf"))
        print(f"\n📑 Found {len(pdf_files)} PDF files\n")

        for pdf_file in pdf_files:
            print(f"📄 Processing: {pdf_file.name}")

            try:
                text = extract_text_from_pdf(str(pdf_file))
                if not text.strip():
                    print(f"   ⚠ No text extracted")
                    continue

                laws = parse_pdf_into_articles(text, "", pdf_file.name)
                print(f"   → Extracted {len(laws)} sections from PDF")

                for law_code, article, title, content in laws:
                    if not content or len(content) < 10:
                        continue

                    try:
                        embedding = model.encode(content, normalize_embeddings=True)
                        doc = LegalDocument(
                            law_code=law_code,
                            article=article,
                            article_title=title,
                            content=content,
                            embedding=embedding,
                            jurisdiction="Mauritanie",
                            category="labor" if "Travail" in law_code else "corporate"
                        )
                        session.add(doc)
                        total_loaded += 1

                        if (total_loaded % 20) == 0:
                            session.commit()
                            print(f"     Loaded {total_loaded} documents...")

                    except Exception as e:
                        print(f"     ⚠ Error: {e}")
                        continue

            except Exception as e:
                print(f"   ✗ Error processing {pdf_file.name}: {e}")
                continue

        # Final commit
        session.commit()
        print(f"\n✅ Successfully loaded {total_loaded} legal documents into pgvector")

        # Show statistics
        from sqlalchemy import func
        stats = session.query(
            LegalDocument.law_code,
            func.count(LegalDocument.id)
        ).group_by(LegalDocument.law_code).all()

        print(f"\n📊 Corpus Statistics:")
        for law_code, count in sorted(stats, key=lambda x: x[1], reverse=True):
            print(f"   • {law_code}: {count} documents")

        return True

    except Exception as e:
        print(f"✗ Error loading corpus: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        return False

    finally:
        session.close()


def parse_txt_corpus(content: str) -> List[Tuple[str, str, str, str]]:
    """Parse les lois.txt file."""
    laws = []
    current_article = None
    current_section = None
    current_content_lines = []
    current_law_code = "Convention Collective du Travail"

    lines = content.split('\n')

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Detect article headers
        if re.match(r'^Article \d+', line):
            # Save previous article
            if current_article and current_content_lines:
                article_content = '\n'.join(current_content_lines).strip()
                if article_content:
                    laws.append((
                        current_law_code,
                        current_article,
                        current_section or "",
                        article_content
                    ))

            # Start new article
            match = re.match(r'^Article (\d+)\s*:\s*(.*)', line)
            if match:
                current_article = f"Article {match.group(1)}"
                current_section = match.group(2).strip() if match.group(2) else ""
                current_content_lines = []

        elif current_article:
            current_content_lines.append(line)

    # Save last article
    if current_article and current_content_lines:
        article_content = '\n'.join(current_content_lines).strip()
        if article_content:
            laws.append((
                current_law_code,
                current_article,
                current_section or "",
                article_content
            ))

    return laws


def main():
    """Main corpus loading function."""

    if not DATABASE_URL:
        print("✗ DATABASE_URL not set")
        return False

    print("\n" + "=" * 70)
    print("🔍 COMPREHENSIVE LEGAL CORPUS LOADER")
    print("=" * 70)

    # Create database engine
    print(f"\n🔗 Connecting to database...")
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=3600
    )

    # Initialize database
    print("🗄️  Initializing database...")
    enable_pgvector(sessionmaker(bind=engine)())
    init_db(engine)

    # Create session maker
    SessionLocal = sessionmaker(bind=engine)

    # Load corpus
    success = load_all_corpus(SessionLocal, EMBEDDING_MODEL)

    if success:
        print("\n" + "=" * 70)
        print("✅ CORPUS LOADING COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\n🎉 Your system is ready for Phase 3 - Agent Implementation")
        return True
    else:
        print("\n" + "=" * 70)
        print("❌ CORPUS LOADING FAILED")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
