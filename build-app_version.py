import os

from OverworldShuffle import __version__ as OWVersion

with(open(os.path.join("resources","app","meta","manifests","app_version.txt"),"w+")) as f:
  f.write(OWVersion)
