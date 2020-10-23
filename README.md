# Exiger-challenge
Exiger coding challenge



# Make or edit the config file
By following `create-config-file-ipynb` file you will be able to create your own config file. You can use Jupyter notebook to open the file. If you wish to manually edit the default config file, you can edit `settings.conf` file with a text editor.
<br>
**Note**: The path to the excel file is declared insidethe config file.

# How to run the code
Open a terminal and type `python3 exiger.py <path-to-config-file>  <output-file-name>`. 
- Note that `<path-to-config-file>` is the full path to the config file. If the script cannot find the file, it will use the default config file. 
- You can provide a name for the output file by sending a second argument when running the script. The default output file name is the current date-time in `"%Y%m%d-%H%M%S"` format
