import glob
import importlib.util
import sys
 
# assign directory
directory = 'genisys/modules'
 
# iterate over files in modules folder
for filename in glob.iglob(f'{directory}/*'):
    #returns module spec based on file location
    spec = importlib.util.spec_from_file_location(filename, directory)

    #create module based on spec
    mod = importlib.util.module_from_spec(spec)

    #get modules
    sys.modules[filename] = mod

    #load module
    spec.loader.exec_module(mod)
