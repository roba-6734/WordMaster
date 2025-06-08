import os
import sys


def show_error_detail(error_msg):
    _,_,exc_tb = sys.exc_info(error_msg)
    file_name = exc_tb.tb_frame.f_code.co_filename # type: ignore
    error_message = f"Error occurred in python script name {file_name} and line number {exc_tb.tb_lineno} erro message {str(error_message)}"
    return error_message


class CustomException(Exception):
    def __init__(self, error_message):
        super().__init__(error_message)
        self.error_message = show_error_detail(error_msg=error_message)

    def __str__(self):
        return self.error_message
