"""
eGit - A CLI tool for enhanced Git commit messages and tasks using LLMs
"""

__version__ = "0.5.0"

## Fancy header thing
TITLE = r"""
        _____ _____ _______ 
       / ____|_   _|__   __|
   ___| |  __  | |    | |   
  / _ \ | |_ | | |    | |   
 |  __/ |__| |_| |_   | |   
  \___|\_____|_____|  |_|   
  
By Sweet Papa Technologies, LLC                            
eGit - version {__version__}
                            
"""


def print_title():
    print(TITLE.format(__version__=__version__))

print_title()