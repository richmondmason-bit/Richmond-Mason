from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, WindowProperties, CollisionTraverser, CollisionNode, CollisionSphere, CollisionHandlerPusher, CollisionRay, CollisionHandlerQueue, BitMask32
from direct.task import Task

# --- CONFIG ---
BLOCK_SIZE = 1
WORLD_SIZE = 16
PLAYER_HEIGHT = 2
GRAVITY = -9.8
JUMP_SPEED = 5
MOVEMENT_SPEED = 5

class MiniMinecraft(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        # --- FPS Camera Setup ---
        self.camera.setPos(WORLD_SIZE/2, -WORLD_SIZE*1.5, PLAYER_HEIGHT + 5)
        self.pitch = 0
        self.yaw = 0
        self.sensitivity = 0.2

        # Hide & lock cursor
        self.props = WindowProperties()
        self.props.setCursorHidden(True)
        self.props.setMouseMode(WindowProperties.M_confined)
        self.win.requestProperties(self.props)
        self.mouse_locked = True

        # --- Load Block Model & Textures ---
        self.block_model = self.loader.loadModel("models/box")
        # fallback color if texture missing
        self.block_model.setColor(0.5,0.5,0.5,1)

        self.blocks = {}  # dict for blocks

        # --- Generate Flat Terrain ---
        self.generate_terrain()

        # --- Key Handling ---
        self.keys = {}
        for key in ["w","a","s","d","space","shift","escape"]:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])
        for i in range(1,10):
            self.accept(str(i), self.set_key, ["block"+str(i), True])

        # --- Player Collision ---
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        self.playerCollider = self.camera.attachNewNode(CollisionNode('player'))
        self.playerCollider.node().addSolid(CollisionSphere(0,0,PLAYER_HEIGHT/2,PLAYER_HEIGHT/2))
        self.playerCollider.node().setFromCollideMask(BitMask32.bit(1))
        self.playerCollider.node().setIntoCollideMask(BitMask32.allOff())
        self.cTrav.addCollider(self.playerCollider, self.pusher)
        self.pusher.addCollider(self.playerCollider, self.camera)

        # --- Ray for Block Picking ---
        self.ray = CollisionRay()
        self.rayNode = CollisionNode("ray")
        self.rayNode.addSolid(self.ray)
        self.rayNode.setFromCollideMask(BitMask32.bit(1))
        self.rayNode.setIntoCollideMask(BitMask32.allOff())
        self.rayNP = self.camera.attachNewNode(self.rayNode)
        self.rayHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.rayNP, self.rayHandler)

        # --- Movement & Gravity ---
        self.velocity = Vec3(0,0,0)
        self.is_jumping = False

        self.taskMgr.add(self.update, "update")

        # --- Mouse Click Events ---
        self.accept("mouse1", self.break_block)
        self.accept("mouse3", self.place_block)

    # --- Key Handling ---
    def set_key(self, key, value):
        self.keys[key] = value
        if key == "escape" and value:
            self.mouse_locked = not self.mouse_locked
            props = WindowProperties()
            props.setCursorHidden(not self.mouse_locked)
            props.setMouseMode(WindowProperties.M_confined if self.mouse_locked else WindowProperties.M_absolute)
            self.win.requestProperties(props)

    # --- Terrain ---
    def generate_terrain(self):
        for x in range(WORLD_SIZE):
            for y in range(WORLD_SIZE):
                height = 3
                for z in range(height):
                    self.create_block(x, y, z, "grass" if z==height-1 else "dirt")

    def create_block(self, x, y, z, texture="grass"):
        block = self.block_model.copyTo(self.render)
        block.setPos(x*BLOCK_SIZE, y*BLOCK_SIZE, z*BLOCK_SIZE)
        block.setScale(BLOCK_SIZE)
        block.setCollideMask(BitMask32.bit(1))
        self.blocks[(x,y,z)] = block

    def remove_block(self, x, y, z):
        block = self.blocks.pop((x,y,z), None)
        if block:
            block.removeNode()

    # --- Raycast ---
    def get_target(self):
        self.ray.setOrigin(self.camera.getPos(self.render))
        self.ray.setDirection(self.camera.getQuat(self.render).getForward())
        self.cTrav.traverse(self.render)
        if self.rayHandler.getNumEntries() > 0:
            self.rayHandler.sortEntries()
            entry = self.rayHandler.getEntry(0)
            pos = entry.getIntoNodePath().getPos(self.render)
            normal = entry.getSurfaceNormal(self.render)
            block = tuple(int(round(c)) for c in pos)
            place = tuple(int(round(c)) for c in (pos + normal*0.5))
            return block, place
        return None, None

    def break_block(self):
        block, _ = self.get_target()
        if block:
            self.remove_block(*block)

    def place_block(self):
        _, place = self.get_target()
        if place:
            self.create_block(*place)

    # --- Update ---
    def update(self, task):
        dt = globalClock.getDt()
        self.update_mouse()
        self.update_movement(dt)
        return Task.cont

    def update_movement(self, dt):
        direction = Vec3(0,0,0)
        if self.keys.get("w"): direction += Vec3(0,1,0)
        if self.keys.get("s"): direction += Vec3(0,-1,0)
        if self.keys.get("a"): direction += Vec3(-1,0,0)
        if self.keys.get("d"): direction += Vec3(1,0,0)

        direction.normalize()
        direction *= MOVEMENT_SPEED * dt

        # Apply horizontal movement
        self.camera.setPos(self.camera, direction)

        # Gravity
        self.velocity.z += GRAVITY * dt

        # Jump
        if self.keys.get("space") and not self.is_jumping:
            self.velocity.z = JUMP_SPEED
            self.is_jumping = True

        # Move vertically
        self.camera.setZ(self.camera.getZ() + self.velocity.z * dt)

    def update_mouse(self):
        if self.mouse_locked and self.mouseWatcherNode.hasMouse():
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

# --- Run ---
app = MiniMinecraft()
app.run()