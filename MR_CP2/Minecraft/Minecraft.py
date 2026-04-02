from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, WindowProperties, CollisionTraverser, CollisionNode, CollisionRay, CollisionHandlerQueue, BitMask32
from direct.task import Task
from noise import pnoise2

# --- CONFIG ---
BLOCK_SIZE = 1
WORLD_SIZE = 16
HEIGHT_SCALE = 5

class MiniMinecraft(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        # --- FPS Camera Setup ---
        self.camera.setPos(WORLD_SIZE/2, -WORLD_SIZE*1.5, HEIGHT_SCALE*2)
        self.pitch = 0
        self.yaw = 0
        self.sensitivity = 0.2

        # Hide & lock cursor
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_confined)
        self.win.requestProperties(props)

        # --- Load Block Model & Textures ---
        self.block_model = self.loader.loadModel("models/box")
        self.textures = {
            "grass": self.loader.loadTexture("textures/grass.png"),
            "dirt": self.loader.loadTexture("textures/dirt.png"),
            "stone": self.loader.loadTexture("textures/stone.png")
        }

        # Dictionary for blocks
        self.blocks = {}

        # --- Generate Terrain ---
        self.generate_terrain()

        # --- Movement Keys ---
        self.keys = {}
        for key in ["w", "a", "s", "d", "space", "shift"]:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])

        # --- Tasks ---
        self.taskMgr.add(self.update_movement, "movement")
        self.taskMgr.add(self.update_mouse, "mouse_update")

        # --- Collision for Ray Picking ---
        self.cTrav = CollisionTraverser()
        self.ray = CollisionRay()
        self.rayNode = CollisionNode("ray")
        self.rayNode.addSolid(self.ray)
        self.rayNP = self.camera.attachNewNode(self.rayNode)
        self.rayNode.setFromCollideMask(BitMask32.bit(1))
        self.rayHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.rayNP, self.rayHandler)

        # --- Mouse Click Events ---
        self.accept("mouse1", self.break_block)
        self.accept("mouse3", self.place_block)

    # --- Key Handling ---
    def set_key(self, key, value):
        self.keys[key] = value

    # --- Terrain Generation ---
    def generate_terrain(self):
        for x in range(WORLD_SIZE):
            for y in range(WORLD_SIZE):
                height = int(pnoise2(x/10, y/10, octaves=3) * HEIGHT_SCALE + HEIGHT_SCALE/2)
                for z in range(height):
                    if z == height - 1:
                        texture = "grass"
                    elif z > height - 4:
                        texture = "dirt"
                    else:
                        texture = "stone"
                    self.create_block(x, y, z, texture)

    # --- Create/Remove Blocks ---
    def create_block(self, x, y, z, texture="grass"):
        block = self.block_model.copyTo(self.render)
        block.setPos(x*BLOCK_SIZE, y*BLOCK_SIZE, z*BLOCK_SIZE)
        block.setScale(BLOCK_SIZE)
        block.setTexture(self.textures[texture])
        block.setCollideMask(BitMask32.bit(1))
        self.blocks[(x, y, z)] = block

    def remove_block(self, x, y, z):
        block = self.blocks.pop((x, y, z), None)
        if block:
            block.removeNode()

    # --- Block Picking ---
    def get_target_block(self):
        self.cTrav.traverse(self.render)
        if self.rayHandler.getNumEntries() > 0:
            self.rayHandler.sortEntries()
            entry = self.rayHandler.getEntry(0)
            pos = entry.getIntoNodePath().getPos()
            return tuple(int(round(coord)) for coord in pos)
        return None

    def break_block(self):
        block = self.get_target_block()
        if block:
            self.remove_block(*block)

    def place_block(self):
        block = self.get_target_block()
        if block:
            x, y, z = block
            self.create_block(x, y, z+1, "dirt")

    # --- Movement ---
    def update_movement(self, task):
        dt = globalClock.getDt()
        speed = 5 * dt

        if self.keys.get("w"):
            self.camera.setPos(self.camera, Vec3(0, speed, 0))
        if self.keys.get("s"):
            self.camera.setPos(self.camera, Vec3(0, -speed, 0))
        if self.keys.get("a"):
            self.camera.setPos(self.camera, Vec3(-speed, 0, 0))
        if self.keys.get("d"):
            self.camera.setPos(self.camera, Vec3(speed, 0, 0))
        if self.keys.get("space"):
            self.camera.setZ(self.camera.getZ() + speed)
        if self.keys.get("shift"):
            self.camera.setZ(self.camera.getZ() - speed)

        return Task.cont

    # --- Mouse Look ---
    def update_mouse(self, task):
        if self.mouseWatcherNode.hasMouse():
            x = self.mouseWatcherNode.getMouseX()
            y = self.mouseWatcherNode.getMouseY()

            self.yaw -= x * self.sensitivity
            self.pitch -= y * self.sensitivity
            self.pitch = max(-90, min(90, self.pitch))

            self.camera.setHpr(self.yaw, self.pitch, 0)

            # Reset mouse to center
            self.win.movePointer(0,
                                 int(self.win.getProperties().getXSize()/2),
                                 int(self.win.getProperties().getYSize()/2))
        return Task.cont

# --- Run ---
app = MiniMinecraft()
app.run()