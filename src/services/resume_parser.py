import io

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from src.core.exceptions import ResumeParseError


class ResumeParserService:
    def extract_text(self, file_content: bytes) -> str:
        """
        Extracts text from a PDF file.
        
        Args:
            file_content: The binary content of the PDF file.
            
        Returns:
            The extracted text as a string.
            
        Raises:
            ResumeParseError: If the PDF is invalid, empty, or corrupt.
        """
        if not file_content:
            raise ResumeParseError("Empty PDF file.")
            
        try:
            reader = PdfReader(io.BytesIO(file_content))
            
            if not reader.pages:
                raise ResumeParseError("PDF has no pages.")
                
            extracted_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
                    
            extracted_text = extracted_text.strip()
            
            if not extracted_text:
                raise ResumeParseError("No text could be extracted from the PDF.")
                
            return extracted_text
            
        except PdfReadError as e:
            raise ResumeParseError(f"Corrupt or invalid PDF file: {str(e)}") from e
        except ResumeParseError:
            raise
        except Exception as e:
            raise ResumeParseError(f"Error parsing PDF: {str(e)}") from e
