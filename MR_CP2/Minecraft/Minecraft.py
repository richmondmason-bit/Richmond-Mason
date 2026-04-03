from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Vec3, WindowProperties,
    CollisionTraverser, CollisionNode, CollisionRay,
    CollisionHandlerQueue, BitMask32
)
from direct.task import Task

# --- CONFIG ---
BLOCK_SIZE = 1
WORLD_SIZE = 16
GROUND_HEIGHT = 4


class MiniMinecraft(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        # --- Camera ---
        self.camera.setPos(WORLD_SIZE / 2, -WORLD_SIZE * 1.5, GROUND_HEIGHT + 2)
        self.pitch = 0
        self.yaw = 0
        self.sensitivity = 0.2

        # --- Mouse ---
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(props)

        # --- Load Model ---
        self.block_model = self.loader.loadModel("models/box")

        # --- COLORS instead of textures ---
        self.colors = {
            "grass": (0.2, 0.8, 0.2, 1),
            "dirt": (0.5, 0.3, 0.1, 1),
            "stone": (0.5, 0.5, 0.5, 1)
        }

        self.blocks = {}

        # --- Generate Flat Terrain ---
        self.generate_terrain()

        # --- Input ---
        self.keys = {}
        for key in ["w", "a", "s", "d", "space", "shift"]:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])

        self.accept("mouse1", self.break_block)
        self.accept("mouse3", self.place_block)

        # --- Tasks ---
        self.taskMgr.add(self.update_movement, "movement")
        self.taskMgr.add(self.update_mouse, "mouse")

        # --- Raycasting ---
        self.cTrav = CollisionTraverser()
        self.ray = CollisionRay()

        self.rayNode = CollisionNode("ray")
        self.rayNode.addSolid(self.ray)
        self.rayNode.setFromCollideMask(BitMask32.bit(1))
        self.rayNP = self.camera.attachNewNode(self.rayNode)

        self.rayHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.rayNP, self.rayHandler)

    # --- Input ---
    def set_key(self, key, value):
        self.keys[key] = value

    # --- Terrain ---
    def generate_terrain(self):
        for x in range(WORLD_SIZE):
            for y in range(WORLD_SIZE):
                for z in range(GROUND_HEIGHT):
                    if z == GROUND_HEIGHT - 1:
                        block_type = "grass"
                    elif z > GROUND_HEIGHT - 4:
                        block_type = "dirt"
                    else:
                        block_type = "stone"

                    self.create_block(x, y, z, block_type)

    # --- Blocks ---
    def create_block(self, x, y, z, block_type="grass"):
        if (x, y, z) in self.blocks:
            return

        block = self.block_model.copyTo(self.render)
        block.setPos(x * BLOCK_SIZE, y * BLOCK_SIZE, z * BLOCK_SIZE)
        block.setScale(BLOCK_SIZE)

        # Use color instead of texture
        block.setColor(self.colors[block_type])

        block.setCollideMask(BitMask32.bit(1))
        self.blocks[(x, y, z)] = block

    def remove_block(self, x, y, z):
        block = self.blocks.pop((x, y, z), None)
        if block:
            block.removeNode()

    # --- Raycast ---
    def get_target_block(self):
        self.ray.setOrigin(self.camera.getPos(self.render))
        self.ray.setDirection(self.camera.getQuat(self.render).getForward())

        self.cTrav.traverse(self.render)

        if self.rayHandler.getNumEntries() > 0:
            self.rayHandler.sortEntries()
            entry = self.rayHandler.getEntry(0)

            node = entry.getIntoNodePath()
            pos = node.getNetPos(self.render)
            normal = entry.getSurfaceNormal(self.render)

            block_pos = tuple(int(round(coord)) for coord in pos)
            place_pos = tuple(int(round(coord)) for coord in (pos + normal * 0.5))

            return block_pos, place_pos

        return None, None

    # --- Actions ---
    def break_block(self):
        block_pos, _ = self.get_target_block()
        if block_pos:
            self.remove_block(*block_pos)

    def place_block(self):
        _, place_pos = self.get_target_block()
        if place_pos:
            if place_pos not in self.blocks:
                self.create_block(*place_pos, "dirt")

    # --- Movement ---
    def update_movement(self, task):
        dt = globalClock.getDt()
        speed = 5 * dt

        forward = self.camera.getQuat().getForward()
        right = self.camera.getQuat().getRight()

        forward.setZ(0)
        right.setZ(0)
        forward.normalize()
        right.normalize()

        if self.keys.get("w"):
            self.camera.setPos(self.camera.getPos() + forward * speed)
        if self.keys.get("s"):
            self.camera.setPos(self.camera.getPos() - forward * speed)
        if self.keys.get("a"):
            self.camera.setPos(self.camera.getPos() - right * speed)
        if self.keys.get("d"):
            self.camera.setPos(self.camera.getPos() + right * speed)
        if self.keys.get("space"):
            self.camera.setZ(self.camera.getZ() + speed)
        if self.keys.get("shift"):
            self.camera.setZ(self.camera.getZ() - speed)

        return Task.cont

    # --- Mouse Look ---
    def update_mouse(self, task):
        if self.mouseWatcherNode.hasMouse():
            md = self.win.getPointer(0)

            x = md.getX() - self.win.getXSize() // 2
            y = md.getY() - self.win.getYSize() // 2

            self.yaw -= x * self.sensitivity
            self.pitch -= y * self.sensitivity
            self.pitch = max(-90, min(90, self.pitch))

            self.camera.setHpr(self.yaw, self.pitch, 0)

            self.win.movePointer(
                0,
                self.win.getXSize() // 2,
                self.win.getYSize() // 2
            )

        return Task.cont


# --- Run ---
app = MiniMinecraft()
app.run()