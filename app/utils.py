from colorama import Fore, Style # pip install colorama
import hashlib

class Utils:

    @staticmethod
    def print_help_command():
        print("This tool is translated from the work of Loc Nguyen and shared on J2Team")
        print("\n\nFlags: ")
        print("\t/F [PATH] Source path contains all downloaded courses. (Mandatory)")
        print("\t/RM\tRemoves courses in databases after decryption is complete. (Optional)")
        print("\t/DB [PATH] Use Database to rename folder course, module... (Mandatory)")
        print("\t/OUT [PATH] Specifies an output directory instead of using the same source path. (Optional)")
        print("\t/TRANS\tGenerate subtitles file (.srt) if the course are supported. (Optional)")
        print("\t/HELP\tSee usage of other commands. (Optional)")
        print(Fore.YELLOW + "**Note**\nIf you want to use /RM flag, please make sure the output path that not the same with the source path.\n" + Style.RESET_ALL)

    @staticmethod
    def print_input_path_mandatory():
        print('\t-f\t flag is mandatory. Please you the /HELP flag to more information.')

    @staticmethod
    def md5(s):
        #result = hashlib.md5(s.encode('utf-8'))
        result = hashlib.md5(s)
        return result.digest()
