"""Script to load legal corpus into pgvector database."""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple

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


def parse_laws_file(file_path: str) -> List[Tuple[str, str, str, str]]:
    """
    Parse les_lois.txt and extract structured legal content.

    Returns: List of (law_code, article, article_title, content) tuples
    """
    laws = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse Convention Collective du Travail structure
    current_section = None
    current_article = None
    current_content_lines = []
    current_law_code = "Convention Collective du Travail"

    lines = content.split('\n')

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Detect article headers (Article N :)
        if re.match(r'^Article \d+', line):
            # Save previous article if exists
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


def load_corpus(session_maker, embedding_model):
    """Load legal corpus into database with embeddings."""

    session = session_maker()

    try:
        # Load embedding model
        print(f"Loading embedding model: {embedding_model}")
        model = SentenceTransformer(embedding_model)

        # Parse laws file
        laws_file = Path(__file__).parent.parent.parent / "data" / "laws" / "les_lois.txt"

        # Check if file exists, if not use the ressourse folder
        if not laws_file.exists():
            laws_file = Path.home() / "Desktop" / "iscae" / "s6" / "pfe2026" / "ressourse" / "les lois.txt"

        if not laws_file.exists():
            print(f"✗ Laws file not found at {laws_file}")
            return False

        print(f"Parsing laws from: {laws_file}")
        laws = parse_laws_file(str(laws_file))
        print(f"Extracted {len(laws)} articles")

        # Load into database with embeddings
        print("Embedding and loading articles...")

        for i, (law_code, article, title, content) in enumerate(laws):
            if not content or len(content) < 10:
                continue

            try:
                # Create embedding
                embedding = model.encode(content, normalize_embeddings=True)

                # Create document
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

                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1}/{len(laws)} articles...")
                    session.commit()

            except Exception as e:
                print(f"  Error processing {article}: {e}")
                continue

        # Final commit
        session.commit()
        print(f"✓ Successfully loaded {len(laws)} legal articles")
        return True

    except Exception as e:
        print(f"✗ Error loading corpus: {e}")
        session.rollback()
        return False

    finally:
        session.close()


def main():
    """Main corpus loading function."""

    if not DATABASE_URL:
        print("✗ DATABASE_URL not set")
        return False

    print("=" * 60)
    print("Legal Corpus Loader")
    print("=" * 60)

    # Create database engine
    print(f"Connecting to database...")
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=3600
    )

    # Initialize database
    print("Initializing database...")
    enable_pgvector(sessionmaker(bind=engine)())
    init_db(engine)

    # Create session maker
    SessionLocal = sessionmaker(bind=engine)

    # Load corpus
    success = load_corpus(SessionLocal, EMBEDDING_MODEL)

    if success:
        print("\n✓ Corpus loading completed successfully!")
        return True
    else:
        print("\n✗ Corpus loading failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
