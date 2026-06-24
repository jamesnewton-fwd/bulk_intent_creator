class BulkIntentCreatorError(Exception):
    pass


class APIError(BulkIntentCreatorError):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"API error {status_code}: {message}")


class CSVValidationError(BulkIntentCreatorError):
    def __init__(self, row: int, message: str) -> None:
        self.row = row
        super().__init__(f"Row {row}: {message}")
