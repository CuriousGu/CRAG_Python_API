from typing import Dict
import json
from io import BytesIO
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.infrastructure.config import settings


class DocumentReader:

    @staticmethod
    async def split_text(text: str):
        return RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            is_separator_regex=False,
        ).split_text(text)

    @staticmethod
    async def read_file(file) -> Dict[str, str]:
        try:
            document = {
                "name": file.filename,
                "extension":  file.filename.split('.')[-1]
            }
            content = await file.read()
            document["content"] = await eval(
                f"DocumentReader._read_{document['extension']}"
            )(content)

            document["content"] = await DocumentReader.split_text(
                document["content"]
            )
            return document

        except Exception as e:
            raise ValueError(
                f"File type not supported: {file.content_type}\n{e}"
            )

    @staticmethod
    async def _read_json(contents):
        return json.loads(contents)

    @staticmethod
    async def _read_pdf(contents):
        pdf_document = PdfReader(BytesIO(contents))
        pdf_text = ""
        for page in pdf_document.pages:
            pdf_text += page.extract_text()
        return pdf_text

    @staticmethod
    async def _read_txt(contents):
        return contents.decode('utf-8')
