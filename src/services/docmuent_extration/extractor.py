import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from docx import Document
from PyPDF2 import PdfReader
import re

class Reader:
    """
    Classe para leitura e processamento de diferentes tipos de arquivos (JSON, PDF, DOCX, TXT).
    
    Esta classe fornece uma interface unificada para ler diferentes formatos de arquivo,
    processando-os em documentos individuais e gerando identificadores únicos e metadados
    para cada documento.

    Attributes:
        supported_extensions (set): Extensões de arquivo suportadas (.json, .pdf, .docx, .txt)
        documents (list): Lista dos documentos processados
        ids (list): Lista de identificadores únicos para cada documento
        metadata (list): Lista de metadados associados a cada documento

    Example:
        >>> reader = Reader("documento.pdf", "noticia")
        >>> print(len(reader.documents))  # número de documentos
        >>> print(reader.ids)  # lista de IDs gerados
        >>> print(reader.metadata)  # metadados dos documentos

    Note:
        - Arquivos PDF e DOCX são tratados como um único documento
        - Arquivos JSON podem conter múltiplos documentos
        - Arquivos TXT são tratados como um único documento
    """
    
    def __init__(self, file_path: str, document_content: str):
     
        self.supported_extensions = {'.json', '.pdf', '.docx', '.txt'}
        # Inicializa os atributos
        self.documents = []
        self.ids = []
        self.metadata = []
        # Processa o arquivo na inicialização
        self.documents, self.ids, self.metadata = self.__call__(file_path, document_content)
    
    def __call__(self, file_path: str, document_content: str) -> Tuple[List[str], List[str], List[Dict]]:

        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Extensão não suportada: {path.suffix}")
        
        # Resto do código permanece igual
        readers = {
            '.json': self._read_json,
            '.pdf': self._read_pdf,
            '.docx': self._read_docx,
            '.txt': self._read_txt
        }
        
        reader = readers.get(path.suffix.lower())
        documents = reader(file_path)
        
        ids = [f"{document_content}_{i+1}" for i in range(len(documents))]
        metadata = [{'document_content': document_content} for _ in range(len(documents))]
        
        return documents, ids, metadata
    
    def _read_json(self, file_path: str) -> Tuple[List[str], Dict]:
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        if isinstance(data, list):
            documents = [item.get('texto', '') for item in data]
        else:
            documents = [data.get('texto', '')]
        return documents
    
    def _read_pdf(self, file_path: str) -> Tuple[List[str], Dict]:
        
        reader = PdfReader(file_path)

        # Combina todo o texto do PDF em um único documento
        full_text = " ".join(page.extract_text() or "" for page in reader.pages).strip()

        # Cria uma lista com um único documento
        documents = [full_text]

        return documents

    def _read_docx(self, file_path: str) -> Tuple[List[str], Dict]:
        
        doc = Document(file_path)
        # Combina todos os parágrafos em um único texto, separando por espaços
        full_text = " ".join(paragraph.text.strip() for paragraph in doc.paragraphs if paragraph.text.strip())
        # Retorna uma lista com um único documento
        documents = [full_text]

        return documents

    def _read_txt(self, file_path: str) -> Tuple[List[str], Dict]:
        
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            documents = [text]

        return documents
