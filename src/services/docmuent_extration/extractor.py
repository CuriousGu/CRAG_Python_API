import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from docx import Document
from PyPDF2 import PdfReader
import re

class Reader:
    """
    Classe genérica para leitura de diferentes tipos de arquivos (JSON, PDF, DOCX, TXT).
    """
    
    def __init__(self):
        """Inicializa o leitor de documentos."""
        self.supported_extensions = {'.json', '.pdf', '.docx', '.txt'}
    
    def __call__(self, file_path: str, document_content: str) -> Tuple[List[str], List[str], List[Dict]]:
        """
        Lê um arquivo e retorna seus documentos, IDs e metadados.
        
        Args:
            file_path (str): Caminho para o arquivo
            document_content (str): Tipo do documento (ex: 'noticia', 'artigo', 'contrato')
            
        Returns:
            Tuple[List[str], List[str], List[Dict]]: (documentos, ids, metadados)
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Extensão não suportada: {path.suffix}")
        
        # Seleciona o método apropriado baseado na extensão
        readers = {
            '.json': self._read_json,
            '.pdf': self._read_pdf,
            '.docx': self._read_docx,
            '.txt': self._read_txt
        }
        
        reader = readers.get(path.suffix.lower())
        documents, content = reader(file_path)
        
        # Adiciona os documentos ao content para uso no _generate_metadata
        content['documents'] = documents
        
        # Gera IDs e metadados
        ids = [f"{document_content}_{i+1}" for i in range(len(documents))]
        metadata = self._generate_metadata(content, document_content, path.name)
        
        return documents, ids, metadata
    
    def _read_json(self, file_path: str) -> Tuple[List[str], Dict]:
        """Lê arquivo JSON."""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        if isinstance(data, list):
            documents = [item.get('texto', '') for item in data]
            content = {
                'titulos': [item.get('titulo', '') for item in data],
                'subtitulos': [item.get('subtitulo', '') for item in data],
                'datas': [item.get('data', '') for item in data]
            }
        else:
            documents = [data.get('texto', '')]
            content = {
                'titulos': [data.get('titulo', '')],
                'subtitulos': [data.get('subtitulo', '')],
                'datas': [data.get('data', '')]
            }
            
        return documents, content
    
    def _read_pdf(self, file_path: str) -> Tuple[List[str], Dict]:
        """Lê arquivo PDF como um único documento."""
        reader = PdfReader(file_path)

        # Combina todo o texto do PDF em um único documento
        full_text = " ".join(page.extract_text() or "" for page in reader.pages).strip()

        # Cria uma lista com um único documento
        documents = [full_text]

        # Metadata com informações do PDF
        content = {
            'total_pages': len(reader.pages),
            'file_name': Path(file_path).name,
            'file_type': 'pdf',
            'file_size': Path(file_path).stat().st_size,  # tamanho em bytes
            'created_at': str(Path(file_path).stat().st_ctime),  # data de criação
            'modified_at': str(Path(file_path).stat().st_mtime)  # data de modificação
        }

        return documents, content