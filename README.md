# Exiger-challenge
Exiger coding challenge



# Make or edit the config file
By following `create-config-file-ipynb` file you will be able to create your own config file. You can use Jupyter notebook to open the file. If you wish to edit the default config file manually, you can edit settings.conf file with a text editor.  
**Note**: The path to the excel file is declared inside the config file.
  
  

# How to run the code
Open a terminal and type `python3 exiger.py <path-to-config-file>  <output-file-name>`. 
- Note that `<path-to-config-file>` is the full path to the config file. If the script cannot find the file, it will use the default config file. 
- You can provide a name for the output file by sending a second argument when running the script. The default output file name is the current date-time in `"%Y%m%d-%H%M%S"` format


# How to run the tests

There are four tests written for this function that use the default excel and config files included in this repository. To run the test open a terminal, navigate to the project folder and run `python3 test_exiger.py`. Alternatively, you can install the `nose` module and then run `nosetests` command.

# Script structure