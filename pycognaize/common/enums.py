import enum

ID = "_id"
START = 'start'
END = 'end'
HASH_FILE = "document_summary_hash.md5"

IMG_EXTENSION = 'jpeg'
OCR_DATA_EXTENSION = 'json'
SNAPSHOT_EXTENSION = 'pickle'


class FieldDataTypeEnum(enum.Enum):
    extraction = 'extraction'
    computation = 'computation'
    classification = 'classification'
    extraction_and_computation = 'extraction and computation'


class StorageEnum(enum.Enum):
    ocr_folder = 'data'
    image_folder = 'images'
    doc_file = 'document.json'
    pdf_file = 'original.pdf'
    html_file = 'source.html'
    # snap_file = f"snap.{SNAPSHOT_EXTENSION}"


class EnvConfigEnum(enum.Enum):
    IQ_DB_URL = "IQ_DB_URL"
    IQ_SNAP_STORAGE_PATH = "IQ_SNAP_STORAGE_PATH"
    IQ_DOCUMENTS_STORAGE_PATH = "IQ_DOCUMENTS_STORAGE_PATH"  # Images and OCR
    # IQ_DATASNAP_URL = "IQ_DATASNAP_URL"
    SNAPSHOT_ID = 'SNAPSHOT_ID'
    SNAPSHOT_PATH = "SNAPSHOT_PATH"  # Images, OCR and snap.json
    HOST = "API_HOST"


class IqCollectionEnum(enum.Enum):
    documents = 'documents'
    collections = 'collections'
    templates = 'templates'
    recipes = 'datarecipes'
    datasets = 'datasets'


class IqDatasetKeyEnum(enum.Enum):
    collections = 'collections'
    dataset_type = "type"
    recipe_id = "dataRecipeId"


class IqDatasetTypeEnum(enum.Enum):
    snapshot = "snapshot"
    pipeline = "pipeline"


class IqDocumentKeysEnum(enum.Enum):
    collection_id = 'collectionId'
    data_type = 'dataType'
    table = 'table'
    templates = 'templates'
    template = 'template'
    fields = 'fields'
    tags = 'tags'
    pages = 'pages'
    name = 'name'
    section = 'section'
    field_type = 'fieldType'
    field_category = 'fieldCategories'
    field_id = '_id'
    src_field_id = "srcFieldId"
    page = 'page'
    src = 'src'
    page_src = 'src'
    text_span = 'text-span'


# TODO: move Document enum values to corresponding enum (field/tag etc)
class IqFieldKeyEnum(enum.Enum):
    data_type = 'dataType'
    field_type = 'fieldType'
    group = 'group'
    group_key = 'groupKey'
    has_valid_value = 'hasValidValue'
    multiple = 'multiple'
    name = 'name'
    order = 'order'
    repeatable = 'repeatable'
    required = 'required'
    src_field_id = 'srcFieldId'
    tags = 'tags'
    template_id = 'templateId'
    value = 'value'
    calculated_value = 'calculatedValue'
    ocr_value = 'ocrValue'
    repeat_parent = 'repeatParent'
    section = 'section'
    scale = "scale"


class IqTagKeyEnum(enum.Enum):
    value = 'value'
    has_valid_value = 'hasValidValue'
    top = 'top'
    left = 'left'
    width = 'width'
    height = 'height'
    page = 'page'
    ocr_value = 'ocrValue'
    has_valid_ocr_value = 'hasValidOcrValue'
    is_table = 'isTable'
    confidence = 'confidence'


class IqPageEnum(enum.Enum):
    page = 'page'
    src = 'src'


class IqDataTypesEnum(enum.Enum):
    table = 'table'
    text = 'text'
    section = 'section'
    date = 'date'
    number = 'number'
    area = 'area'
    link = 'link'
    span = 'text-span'


class IqRecipeEnum(enum.Enum):
    id = '_id'
    field_id = 'fieldId'
    name = 'name'
    templates = 'templates'
    template = 'template'
    template_id = 'template_id'
    fields = 'fields'
    python_name = 'pythonName'
    document_name = 'document_name'
    user = 'user'
    raw_field_type = 'rawFieldType'
    version = '__v'


class IqTableTagEnum(enum.Enum):
    table = 'table'
    cells = 'cells'
    page = 'page'
    left = "left"
    top = "top"
    height = "height"
    width = "width"
    confidence = 'confidence'


class IqCellKeyEnum(enum.Enum):
    left_col_top_row = 'left_col_top_row'
    col_span = "colspan"
    row_span = "rowspan"
    text = "value"
    left = "left"
    top = "top"
    width = "width"
    height = "height"


class PythonShellEnum(enum.Enum):
    zmq_interactive_shell = 'ZMQInteractiveShell'
    terminal_interactive_shell = 'TerminalInteractiveShell'
    other_type_shell = 'OtherTypeShell'
    standard_python_interpreter = 'StandardPythonInterpreter'


class FieldTypeEnum(enum.Enum):
    """Enumeration of field types"""
    INPUT_FIELD = 'input'
    OUTPUT_FIELD = 'output'
    BOTH = 'both'


class XBRLTagEnum(enum.Enum):
    """Enumeration for XBRL document fields"""
    source = 'source'
    td_id = '_id'
    xpath = 'xpath'
    anchor_id = 'anchorId'
    id = 'id'
    is_bold = 'isBold'
    left_indentation = 'leftIndentation'
    ids = 'ids'
    row_index = 'rowIndex'
    col_index = 'colIndex'
    tag_id = 'tagId'
    ocr_value = 'ocrValue'
    value = 'value'
    is_table = 'isTable'
    html = 'html'
    parent_id = 'parentId'


class XBRLCellEnum(enum.Enum):
    id = 'id'
    source = 'source'
    ids = 'ids'
    html_id = 'id'
    xpath = 'xpath'
    row_index = 'rowIndex'
    col_index = 'colIndex'
    col_span = 'colspan'
    row_span = 'rowspan'
    raw_value = 'value'
    is_bold = 'isBold'
    left_indentation = 'leftIndentation'


class XBRLTableTagEnum(enum.Enum):
    source = 'source'
    ocr_value = 'ocrValue'
    value = 'value'
    is_table = 'isTable'
    is_bold = 'isBold'
    left_indentation = 'leftIndentation'
    anchor_id = 'anchorId'
    xpath = 'xpath'
    table = 'table'
    cells = 'cells'
    title = 'title'
    _id = '_id'


class PageLayoutEnum(enum.Enum):
    """Enum of page layout blocks, including tables"""
    TEXT = 'page_layout__text'
    # 'page_layout__picture'
    CAPTION = 'page_layout__caption'
    SECTION_HEADER = 'page_layout__section_header'
    FOOTNOTE = 'page_layout__footnote'
    FORMULA = 'page_layout__formula'
    # 'page_layout__table'
    LIST_ITEM = 'page_layout__list_item'
    PAGE_HEADER = 'page_layout__page_header'
    PAGE_FOOTER = 'page_layout__page_footer'
    TITLE = 'page_layout__title'
    TABLE = 'tables__table'
