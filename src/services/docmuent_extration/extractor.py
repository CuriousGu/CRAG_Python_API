import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from docx import Document
from PyPDF2 import PdfReader
import re
from dataclasses import dataclass

@dataclass
class DocumentResult:
    """
    Classe para armazenar o resultado da leitura de documentos.
    
    Attributes:
        documents (List[str]): Lista de documentos processados
        ids (List[str]): Lista de identificadores únicos
        metadata (List[Dict]): Lista de metadados associados
    """
    documents: List[str]
    ids: List[str]
    metadata: List[Dict]

class DocumentFileReader:
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
    
    def __init__(self, file_path: str, tags_documnets: str, documnet_id: Optional[str] = None):
        """
        Inicializa o leitor de documentos.

        Args:
            file_path (str): Caminho do arquivo a ser lido
            tags_documnets (str): Tipo de conteúdo do documento (ex: "noticia", "artigo")

        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            ValueError: Se a extensão do arquivo não for suportada
        """
        self.supported_extensions = {'.json', '.pdf', '.docx', '.txt'}
        result = self.__call__(file_path, tags_documnets, documnet_id)
        self.documents = result.documents
        self.ids = result.ids
        self.metadata = result.metadata
    
    def __call__(self, file_path: str, tags_documnets: str, documnet_id: Optional[str] = None) -> DocumentResult:
        """
        Processa o arquivo e retorna os resultados estruturados.

        Args:
            file_path (str): Caminho do arquivo a ser lido
            tags_documnets (str): Tipo de conteúdo do documento

        Returns:
            DocumentResult: Objeto contendo documentos, IDs e metadados

        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            ValueError: Se a extensão do arquivo não for suportada
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Extensão não suportada: {path.suffix}")
        
        readers = {
            '.json': self._read_json,
            '.pdf': self._read_pdf,
            '.docx': self._read_docx,
            '.txt': self._read_txt
        }
        
        reader = readers.get(path.suffix.lower())
        documents = reader(file_path)
        
        # Gerando IDs únicos
        if documnet_id is None:
            ids = [f"{tags_documnets}_{i}" for i in range(len(documents))]
        else:
            ids = [documnet_id]
        metadata = [{'id': doc_id, 'tags_documnets': tags_documnets} for doc_id in ids]
        
        # Retornando o DocumentResult
        return DocumentResult(
            documents=documents,
            ids=ids,
            metadata=metadata
        )

    def _read_json(self, file_path: str) -> List[str]:
        """
        Lê e processa arquivos JSON.

        Args:
            file_path (str): Caminho do arquivo JSON

        Returns:
            List[str]: Lista de documentos extraídos do JSON

        Notes:
            - Espera-se que o JSON contenha uma chave 'texto' em cada item
            - Pode processar tanto JSON único quanto lista de JSONs
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        if isinstance(data, list):
            documents = [item.get('texto', '') for item in data]
        else:
            documents = [data.get('texto', '')]
        return documents
    
    def _read_pdf(self, file_path: str) -> List[str]:
        """
        Lê e processa arquivos PDF.

        Args:
            file_path (str): Caminho do arquivo PDF

        Returns:
            List[str]: Lista contendo o texto completo do PDF

        Notes:
            - Todo o conteúdo do PDF é combinado em um único documento
            - Páginas vazias são ignoradas
        """
        reader = PdfReader(file_path)

        # Combina todo o texto do PDF em um único documento
        full_text = " ".join(page.extract_text() or "" for page in reader.pages).strip()

        # Cria uma lista com um único documento
        documents = [full_text]

        return documents

    def _read_docx(self, file_path: str) -> List[str]:
        """
        Lê e processa arquivos DOCX.

        Args:
            file_path (str): Caminho do arquivo DOCX

        Returns:
            List[str]: Lista contendo o texto completo do documento

        Notes:
            - Parágrafos vazios são ignorados
            - Todo o conteúdo é combinado em um único documento
        """
        doc = Document(file_path)
        # Combina todos os parágrafos em um único texto, separando por espaços
        full_text = " ".join(paragraph.text.strip() for paragraph in doc.paragraphs if paragraph.text.strip())
        # Retorna uma lista com um único documento
        documents = [full_text]

        return documents

    def _read_txt(self, file_path: str) -> List[str]:
        """
        Lê e processa arquivos de texto.

        Args:
            file_path (str): Caminho do arquivo TXT

        Returns:
            List[str]: Lista contendo o texto completo do arquivo

        Notes:
            - O arquivo inteiro é tratado como um único documento
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            documents = [text]

        return documents
    