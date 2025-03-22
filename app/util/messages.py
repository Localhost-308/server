
class Messages:
    @staticmethod
    def ERROR_NOT_FOUND(obj_nm: str):
        return f"{obj_nm} not found"

    @staticmethod
    def ERROR_INVALID_DATA(obj_nm: str):
        return f"Data invalid for {obj_nm}"

    @staticmethod
    def UNKNOWN_ERROR(obj_nm: str):
        return f"An unexpected error occurred while processing {obj_nm}. Please try again later."

    @staticmethod
    def SUCCESS_SAVE_SUCCESSFULLY(obj_nm: str):
        return f"Data saved successfully for {obj_nm}"
