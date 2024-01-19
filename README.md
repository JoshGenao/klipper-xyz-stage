# klipper-xyz-stage
A Python library that simplifies the control of a Klipper programmed 3D printer. It is designed for automation of an xyz stage for side-channel analysis and fault injection.

## Installation
To install this package:
```
pip install git+https://github.com/JoshGenao/klipper-xyz-stage.git
```
Or:
1. Clone repository
2. Install requirements 
```
pip install -r requirements.txt
```
3. pip install
```
pip install -e .
```
## Usage
Example:
```Python
from klipperxyz.klipperxyz import *

url = "mainsailos.local"
client = KlipperXYZ(url)
client.home()

client.move(50, 50, 30)

print(client.get_position())

for x,y in client.xy_sweep(100, 120.0, 100.0, 120.0, step=1.0):
    print("At %f, %f"%(x,y))
```