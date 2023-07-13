import importlib
from pycognaize.common.decorators import module_not_found
from pycognaize.common.enums import PageLayoutEnum
from pycognaize.document.document import Document
from pycognaize.document.field import Field, TableField


class LangchainLoader:

    """ Convert Pycognaize Document Object to Langchain Document Object """

    INPUT_FIELDS: list[str] = list(i.value for i in PageLayoutEnum)
    OVERLAP = 512
    LIMIT = 2048

    @module_not_found()
    def __init__(self, document: Document) -> None:
        """The constructor takes a cognaize document object as an input.
        The cognaize document object should have page layout and table data in
        document.x, the pythonnames for each field is defined as a class
        attribute.
        """
        transformers = importlib.import_module('transformers')
        self.document = document
        self.tokenizer = transformers.GPT2TokenizerFast.from_pretrained("gpt2")

    @module_not_found()
    def load_and_split(self):
        """
        load and split the Document into separate langchain document objects
        """
        langchain = importlib.import_module('langchain')
        text_blocks_w_metadata: list[list[tuple[dict, str]]] = self.document.to_text()
        metadata_list, text_list = self._create_text_and_metadata(
            text_blocks_w_metadata,
            document_id=self.get_document_src())
        text_splitter = langchain.text_splitter.RecursiveCharacterTextSplitter(
            chunk_size=self.LIMIT,
            chunk_overlap=self.OVERLAP,
            length_function=self.count_tokens)
        docs = text_splitter.create_documents(texts=text_list,
                                              metadatas=metadata_list)
        return docs

    def get_document_src(self) -> str:
        """Get the SHA of the document"""
        return self.document.metadata['src']

    def count_tokens(self, text: str) -> int:
        """Tokenize the text and count the number of tokens"""
        return len(self.tokenizer.encode(text))

    @staticmethod
    def _create_text_and_metadata(
        text_blocks_w_metadata: list[list[tuple[dict, str]]],
        document_id: str
    ) -> tuple[list[dict], list[str]]:
        """
        Creates metadata and texts for creating LangChain Document objects
        """
        metadata_list = []
        text_list = []
        for group in text_blocks_w_metadata:
            group_text = ''
            group_metadata = {"pages": set(), "source": []}
            for metadata, text in group:
                tag = metadata['tag']
                group_metadata['pages'].add(tag.page.page_number)
                group_metadata['source'].append((tag.left, tag.top,
                                                 tag.right, tag.bottom,
                                                 tag.page.page_number))
                group_text += f' {text}'
            group_metadata['pages'] = list(group_metadata['pages'])
            group_metadata['document'] = document_id
            metadata_list.append(group_metadata)
            text_list.append(group_text)
        return metadata_list, text_list
