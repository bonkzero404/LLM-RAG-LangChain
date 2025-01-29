import re
from typing import List
from langchain.schema import Document
from langchain_community.document_loaders import DirectoryLoader
from config import DATA_PATH

class VectorDocument:
    def __init__(self):
        self.new_documents = []

    def load_documents(self) -> List[Document]:
        loader = DirectoryLoader(DATA_PATH, glob="*.txt")
        documents = loader.load()
        return documents

    def split_by_subtopics(self, text: str) -> List[str]:
        subtopic_pattern = r"\[T\](.*?)\[/T\]"
        subtopics = re.findall(subtopic_pattern, text, re.DOTALL)
        return subtopics

    def split_by_content(self, text: str) -> List[str]:
        content_pattern = r"\[PC\](.*?)\[/PC\]"
        content = re.findall(content_pattern, text, re.DOTALL)
        return content

    def format_list_items(self, content: str) -> str:
        list_item_pattern = r"(^|\n)- (.*?)(?=\n|$)"
        formatted_content = re.sub(r"(-\s.*?)(?=\s*-|\n|$)", r"\n\1", content).strip()
        return formatted_content

    def chunk_documents_by_subtopic(self, documents: List[Document]) -> List[Document]:
        self.new_documents = []

        for doc in documents:
            metadata = doc.metadata
            page_content = doc.page_content

            subtopics = self.split_by_subtopics(page_content)
            content_blocks = self.split_by_content(page_content)
            formatted_content = [self.format_list_items(content) for content in content_blocks]

            for subtopic, content in zip(subtopics, formatted_content):
                parts = subtopic.split("\n", 1)
                topic = parts[0].strip()

                new_metadata = metadata.copy()
                new_metadata["topic"] = topic

                self.new_documents.append(
                    Document(page_content=f"{topic}\n{content}", metadata=new_metadata)
                )

        return self.new_documents