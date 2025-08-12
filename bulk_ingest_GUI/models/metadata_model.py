"""
MetadataModel 模块
"""

class MetadataModel:
    """
    用于存储和管理文档元数据的模型类。
    """
    def __init__(self, source, input_type, processed_date, file_path, file_type, file_size, processing_method, structural_info, total_elements, titles_count, tables_count, lists_count, narrative_blocks, other_elements, chunking_method, avg_chunk_size):
        self.source = source
        self.input_type = input_type
        self.processed_date = processed_date
        self.file_path = file_path
        self.file_type = file_type
        self.file_size = file_size
        self.processing_method = processing_method
        self.structural_info = structural_info
        self.total_elements = total_elements
        self.titles_count = titles_count
        self.tables_count = tables_count
        self.lists_count = lists_count
        self.narrative_blocks = narrative_blocks
        self.other_elements = other_elements
        self.chunking_method = chunking_method
        self.avg_chunk_size = avg_chunk_size

    def update_structural_info(self, elements):
        """
        更新结构化信息。
        """
        self.structural_info = {
            "total_elements": len(elements),
            "titles_count": sum(1 for e in elements if type(e).__name__ == 'Title'),
            "tables_count": sum(1 for e in elements if type(e).__name__ == 'Table'),
            "lists_count": sum(1 for e in elements if type(e).__name__ == 'ListItem'),
            "narrative_blocks": sum(1 for e in elements if type(e).__name__ == 'NarrativeText'),
            "other_elements": sum(1 for e in elements if type(e).__name__ not in ['Title', 'Table', 'ListItem', 'NarrativeText'])
        }

    def to_dict(self):
        """
        将模型转换为字典。
        """
        return self.__dict__
