import os, sys
parent_dir = os.path.split(os.path.dirname(__file__))[:-1]
sys.path.append(parent_dir)

import amf.generator

if __name__ == "__main__":
  amf.generator.main()
