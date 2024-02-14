![githubtitle](https://user-images.githubusercontent.com/61150608/190930239-9999a202-e830-43c9-a0ec-b316bd9ce4f5.png)
Basically 'make hollow' but things get connected. This is build using [PyVMF](https://github.com/GorangeNinja/PyVMF) by GorangeNinja.

## Downloads
Latest Release:
[Connectors](https://github.com/Gerb-24/Connectors/releases/latest)

the .zip file is the only thing you have to download

## Usage
![c-example](https://github.com/Gerb-24/Connectors/assets/61150608/6368aa7c-2e1e-474c-815f-62e403446ee8)

The GUI currently consists of three parts: Standard Connectors, Jump Connectors and a Utility Section.

### Standard Connectors
With standard connectors we create a connector from a group of touching solids that all have the 'search texture'. The floor will then be walkable. Compile then makes a new vmf with the name '(your_name)_connected.vmf' in the same directory.

### Jump Connectors
Jump connectors does a lot more. We load a directory with all the jumps as separate vmfs, being named 'jump_(number).vmf' in the order of the jumps. In the vmfs we have a start and end block, indicating the start area and the end area. The connector is made out of touching solids with the search texture. With 'Combine into single vmf', we add the corresponding info_teleport_destination, create teledoors, link these together, create the connectors, put a trigger_teleport on top of the floors together with a trigger_catapult, put a trigger_teleport on top of the skips (and a catapult), and we put all the vmfs into a single vmf.

### Utility/Miscellaneous 
We can save our settings, so that everything is still there when we reload the GUI
We can also create randomly generated connectors with 'Generate Random Connector'
Most other things are just to standardize the way things are build.

## Work in progress
There are a lot more other scripts:
- lights.py: automatically generates lights from a pre-connector
- second_attempt.py: the current way connectors are build does not work when we have parts on top of each other. Second attempt is a different approach that tries to fix these.
- preworker.py and bezier_connector.py: an attempt at making randomly generated connectors, by letting the connector be guided along drawn 3D Bezier curves


## Licenses
The GUI part of this project, i.e. gui.py use the GPLv3 License as they use PyQt6
The actual python code, i.e. main.py etc use the MIT License as they use PyVMF

