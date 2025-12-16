from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str

    # Model settings
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # Chunking settings
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Retrieval settings
    top_k: int = 5

    # Paths
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = base_dir / "data" / "pdfs"
    chroma_dir: Path = base_dir / "chroma_db"
    outputs_dir: Path = base_dir / "outputs"

    # Document identifiers
    forecast_doc_name: str = "outlook-2025"
    midyear_doc_name: str = "mid-year-outlook-2025"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
