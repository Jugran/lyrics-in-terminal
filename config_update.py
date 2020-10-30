from lyrics import CONFIG_PATH
import re

def getContents(filename):
    with open(filename) as f:
        contents = f.read()
    return contents

def getOptions(config):
    regex = r'(\w+)=.*'
    options = re.findall(regex, config)
    return set(options)

def updateChanges():

    if CONFIG_PATH.exists():
        # check for changes
        old_config = getContents(CONFIG_PATH)
        new_config = getContents('lyrics/lyrics.cfg')
        new_options = getOptions(new_config) - getOptions(old_config)

        if len(new_options) == 0:
            return
        
        with open(CONFIG_PATH, 'a') as file: 
            for option in new_options:
                new_option = re.findall(fr'({option}=.*)', new_config)[0]
                file.write(new_option + '\n')


