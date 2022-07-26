
class TextSpan:
    """Represents a slice of SpanGroup object"""

    def __init__(self, text_value, x_coordinate, y_coordinate):
        self.__text_value = text_value
        self.__x_coordinate = x_coordinate
        self.__y_coordinate = y_coordinate

    @property
    def text_value(self):
        """Returns the text value of the text span"""
        return self.__text_value

    @property
    def x_coordinate(self):
        """Returns the x coordinate of the text span"""
        return self.__x_coordinate

    @property
    def y_coordinate(self):
        """Returns the y coordinate of the text span"""
        return self.__y_coordinate

    def __getitem__(self, val):
        """Returns slice of the span object"""
        return TextSpan(self.__text_value[val], self.__x_coordinate, self.__y_coordinate)

    def __repr__(self):
        return f"TextSpan(text_value={self.__text_value}, x_coordinate={self.__x_coordinate}," \
               f" y_coordinate={self.__y_coordinate})"


class SpanGroup:
    """Represents a collection of text span objects created from
    texts in document.json"""

    def __init__(self):
        self.text_spans = []
        self.iterate_document()

    @staticmethod
    def create_span(text_value: str,
                    x_coordinate: float,
                    y_coordinate: float) -> TextSpan:
        """Creates text span object from texts in documents.json"""
        span = TextSpan(text_value, x_coordinate, y_coordinate)
        return span

    def iterate_document(self) -> None:
        """Iterate over all texts in document.json and create text spans"""
        document = {}
        for key, value in document.items():
            span = self.create_span(value, value, value)
            self.text_spans.append(span)

    def texts_in_area(self, x_coordinate: float, y_coordinate:float) -> TextSpan:
        """Searches and returns all text tags in given area"""
        ...

    def get_span_by_text(self, text: str) -> TextSpan:
        """Returns span by text"""
        ...
