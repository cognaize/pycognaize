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
        text_blocks_w_metadata: list[list[tuple[dict, str]]] =\
            self._get_as_text(self.document)
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
    def _get_table_group(current_group: list[tuple[dict, str]],
                         metadata, text_block):
        if current_group and current_group[-1][0]['block'] in \
                (PageLayoutEnum.PAGE_HEADER,
                 PageLayoutEnum.SECTION_HEADER):
            table_group = [current_group[-1], (metadata, text_block)]
            current_group = current_group[:-1]
        else:
            table_group = [(metadata, text_block)]

        return table_group, current_group

    def _get_as_text(self, document: Document) -> list[list[tuple[dict, str]]]:
        """Given a cognaize document object, return a list of strings,
        where each string represents a single chunk/block.
        The tables and text are always in separate groups.
        """
        fields = []
        for pname in self.INPUT_FIELDS:
            if pname not in document.x:
                continue
            block_fields = [(pname, i) for i in document.x[pname]]
            fields.extend(block_fields)
        ordered_blocks_w_metadata: list[
            tuple[dict, str]] = self._order_text_blocks(fields)
        groups = []
        current_group = None
        for block_n, (metadata, text_block) in \
                enumerate(ordered_blocks_w_metadata):
            # First block, create a new group
            if block_n == 0:
                current_group = [(metadata, text_block)]
            # Table, create a separate group
            if metadata['block'] is PageLayoutEnum.TABLE:
                table_group, current_group =\
                    self._get_table_group(current_group, metadata, text_block)
                # finalize the previous group
                groups.append(current_group)
                # finalized the table group
                groups.append(table_group)
                # create an empty group
                current_group = []
            elif metadata['block'] in (PageLayoutEnum.PAGE_HEADER,
                                       PageLayoutEnum.SECTION_HEADER):
                # If all elements are headers in the group, continue with the
                # same group
                if all((
                        g[0]['block']
                        in (PageLayoutEnum.PAGE_HEADER,
                            PageLayoutEnum.SECTION_HEADER)
                        for g in current_group
                )):
                    current_group.append((metadata, text_block))
                elif current_group:
                    groups.append(current_group)
                    current_group = [(metadata, text_block)]
                else:
                    current_group = [(metadata, text_block)]
                # Create a new group
            elif block_n == len(ordered_blocks_w_metadata) - 1 and\
                    current_group:
                groups.append(current_group)
            else:
                current_group.append((metadata, text_block))
        return groups

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
                group_text += f'\n{text}'
            group_metadata['pages'] = list(group_metadata['pages'])
            group_metadata['document'] = document_id
            metadata_list.append(group_metadata)
            text_list.append(group_text)
        return metadata_list, text_list

    @staticmethod
    def _order_text_blocks(fields: list[tuple[str, Field]]) -> \
            list[tuple[dict, str]]:
        """
        Order the fields as they appear in the original document.
        Order by page, top coordinate and left coordinate in that order.
        """
        text_blocks = []
        filtered_fields = []
        for block_type, field in fields:
            if isinstance(field, TableField) and field.tags:
                filtered_fields.append(
                    (
                        {
                            'block': PageLayoutEnum(block_type),
                            'tag': field.tags[0],
                        },
                        field
                    )
                )
            else:
                if field.tags and field.tags[0].raw_value.strip():
                    filtered_fields.append(
                        (
                            {
                                'block': PageLayoutEnum(block_type),
                                'tag': field.tags[0],
                            },
                            field
                        )
                    )
        fields: list[tuple[dict, Field]] = sorted(
            filtered_fields,
            key=lambda x: (x[1].tags[0].page.page_number,
                           x[1].tags[0].top, x[1].tags[0].left))

        for metadata, field in fields:
            if isinstance(field, TableField):
                value: str = field.tags[0].to_string()
            else:
                value = field.value
            text_blocks.append((metadata, value))
        return text_blocks
