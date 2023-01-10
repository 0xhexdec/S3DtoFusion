class ElementNotFoundException(Exception):

    def __init__(self, elementName: str) -> None:
        self.message = f"The Element <{elementName}> was not found."
        super().__init__()

    def __str__(self) -> str:
        return self.message
