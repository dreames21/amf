"""

General settings

"""

app_name = 'Automated Multilayer Fabrication'

delimiter = ','

data_dir = '../data'

last_generated_filename = 'last_generated.txt'

local_server_port = 8089

dry_run_filename = None

chambers = ['r_and_d1', 'r_and_d2', 'mlpc']

runs = ['platen_mode', 'mandrel_mode', 'linear_mode']

welcome = """Welcome to the Automated Multilayer Fabrication Instruction generator

This application will guide you through the process of generating a set of instructions for LabVIEW to follow to manufacture an optic. At any time press cancel to go back to the previous step """
