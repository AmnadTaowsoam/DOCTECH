# text_extractor.py
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import os
import logging
import docx  # For .docx files
import textract  # For .doc, .rtf files
from typing import Optional

logger = logging.getLogger(__name__)

class TextExtractor:
    def __init__(self):
        pass

    def extract_text(self, file_path: str, file_type: str) -> str:
        if file_type == 'application/pdf':
            text = self.extract_text_from_pdf(file_path)
            if not text:
                # Fallback to OCR if pdfplumber fails
                text = self.extract_text_from_pdf_with_ocr(file_path)
        elif file_type.startswith('image/'):
            text = self.extract_text_from_image(file_path)
        elif file_type == 'application/msword':
            text = self.extract_text_from_doc(file_path)
        elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            text = self.extract_text_from_docx(file_path)
        elif file_type == 'text/plain':
            text = self.extract_text_from_txt(file_path)
        elif file_type == 'application/rtf':
            text = self.extract_text_from_rtf(file_path)
        else:
            text = ""

        return text

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ''
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n'
                return text.strip()
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
            return ""

    def extract_text_from_pdf_with_ocr(self, pdf_path: str) -> str:
        try:
            pages = convert_from_path(pdf_path, 300)
            text = ''
            for page in pages:
                text += pytesseract.image_to_string(page, lang='eng')
            return text.strip()
        except Exception as e:
            logger.error(f"Tesseract OCR extraction failed: {e}")
            return ""

    def extract_text_from_image(self, image_path: str) -> str:
        try:
            return pytesseract.image_to_string(image_path, lang='eng').strip()
        except Exception as e:
            logger.error(f"Image OCR extraction failed: {e}")
            return ""

    def extract_text_from_doc(self, doc_path: str) -> Optional[str]:
        try:
            return textract.process(doc_path).decode('utf-8').strip()
        except Exception as e:
            logger.error(f"DOC extraction failed: {e}")
            return ""

    def extract_text_from_docx(self, docx_path: str) -> Optional[str]:
        try:
            doc = docx.Document(docx_path)
            return '\n'.join([para.text for para in doc.paragraphs]).strip()
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            return ""

    def extract_text_from_txt(self, txt_path: str) -> Optional[str]:
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"TXT extraction failed: {e}")
            return ""

    def extract_text_from_rtf(self, rtf_path: str) -> Optional[str]:
        try:
            return textract.process(rtf_path).decode('utf-8').strip()
        except Exception as e:
            logger.error(f"RTF extraction failed: {e}")
            return ""
