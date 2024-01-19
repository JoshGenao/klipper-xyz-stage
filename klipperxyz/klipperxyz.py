import asyncio
from moonraker_api import MoonrakerListener, MoonrakerClient

class MoonrakerAPIConnector(MoonrakerListener):
    API_PORT = 7125

    def __init__(self, host):
        self.running = False
        self.client = MoonrakerClient(self, host, self.API_PORT)

    async def start(self) -> None:
        """Start the websocket connection."""
        self.running = True
        return await self.client.connect()
    
    async def stop(self) -> None:
        """Stop the websocket connection."""
        self.running = False
        await self.client.disconnect()

class KlipperXYZ():
    ''''
    Klipper XYZ Documentation
    ====================================
    API to control Klipper 3D printer. Requires the 3D printer to have Klipper firmware installed.
    
    For regular use of the KlipperXYZ stage, home the stepper motors first:

    Example
    -------------------------------------
        url = "mainsailos.local"
        client = KlipperXYZ(url)
        client.home()

    Once the 3D printer has been homed, you can use the API to set a position
        client.move(100, 100, 30)

    KlipperXYZ can also be swept along the XY axis:

        for x,y in client.xy_sweep(100, 120.0, 100.0, 120.0, step=1.0):
            print("At %f, %f"%(x,y))
    '''
    def __init__(self, host):
        self.host = host

    async def _run(self, method, **params):
        """Call a json-rpc method and wait for the response.

        :param method: _description_
        :return: A ``json`` object containing the ``response`` of the RPC method.
        """
        response = None
        self.connector = MoonrakerAPIConnector(self.host)
        for attempt in range(5):
            try:
                await self.connector.start()
                response =  await self.connector.client.call_method(method, **params)
                await self.connector.stop()
            except:
                print("Error Connecting")
                continue
            else:
                break
        
        return response
    
    async def _run_get_server_info(self):
        """Get the connected websocket id

        :return: A ``json`` object of connected websocket id
        """
        self.connector = MoonrakerAPIConnector(self.host)
        await self.connector.start()
        return await self.connector.client.get_server_info()

    def run_command(self, method, **params):
        """Creates an async event loop, runs the _run method event loop and closes the 
        event loop when the couroutine is complete.

        :param method: _description_
        :return: _description_
        """
        return asyncio.run(self._run(method, **params))
    
    def home(self):
        """Homes the printer. It is recommended that a homing command be performed after a stop is issued.
        """
        params = { "script": "G28" }
        self.run_command("printer.gcode.script", **params)

    def emergency_stop(self):
        """The "emergency_stop" endpoint is used to instruct Klipper to transition to a 
        "shutdown" state. It behaves similarly to the G-Code M112 command. 
        """
        self.run_command("printer.emergency_stop")

    def get_position(self):
        """The internal gcode position, including any offsets (gcode_offset, G92, etc) added to an axis.

        :return: Array containing [X, Y, Z, E]. The internal gcode position, including any offsets
        """
        params = { "objects": { "gcode_move" : None } }
        response = self.run_command("printer.objects.query", **params)
        return response['status']['gcode_move']['gcode_position']
    
    def xy_sweep(self, x_start, x_end, y_start, y_end, step=1.0, x_step=None, y_step=None):
        """Sweep X-Y range, yielding at each point.

        This function should be used in a simple sweep, for example:

        for x,y in client.xy_sweep(0, 5, 0, 5, step=0.5):
            print(“At %f, %f”%(x,y))

        :param x_start: Starting X coordinate
        :param x_end: Ending X coordinate
        :param y_start: Starting Y coordinate
        :param y_end: Ending Y coordinate
        :param step: Distance traveled in X,Y direction, defaults to 1.0
        :param x_step: Distance traveled in X direction, defaults to None
        :param y_step: Distance traveled in Y direction, defaults to None
        :raises ValueError: Ending location needs to greater than starting location
        :raises ValueError: Ending location needs to greater than starting location
        :yield: location in X, Y coordinates
        """
        if x_start > x_end:
            raise ValueError("x_end must be larger than x_start")
        if y_start > y_end:
            raise ValueError("y_end must be larger than y_start")

        if x_step is None:
            x_step = step
        if y_step is None:
            y_step = step

        x = x_start

        while x <= x_end:
            self.move(x=x)
            y = y_start
            while y <= y_end:
                self.move(y=y)
                yield (x, y)
                y+=y_step
            x+=x_step
    
    def move(self, x=None, y=None, z=None, debug=False):
        """Moves 3D printer to the commanded X, Y, Z location. Uses absolute positioning. Meaning that 
        your machine tool moves relative to a set and stationary point (origin)

        :param x: X coordinate, defaults to None
        :param y: Y coordinate, defaults to None
        :param z: Z coordinate, defaults to None
        :param debug: Prints cmdstr to screen, defaults to False
        """        
        params = { "script": None }
        cmdstr = "G90\nG1 "

        if x is not None:
            cmdstr += "X%.1f "%x
        if y is not None:
            cmdstr += "Y%.1f "%y
        if z is not None:
            cmdstr += "Z%.1f "%z

        params["script"] = cmdstr

        if debug:
            print(cmdstr)

        self.run_command("printer.gcode.script", **params)
            
    def get_server_info(self):
        """Get the connected websocket id server information

        :return: A ``json`` object of connected websocket id
        """
        return asyncio.run(self._run_get_server_info())
    