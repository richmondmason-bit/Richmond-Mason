from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, WindowProperties, CollisionTraverser, CollisionNode, CollisionSphere
from panda3d.core import CollisionHandlerPusher, CollisionRay, CollisionHandlerQueue, BitMask32
from panda3d.core import CollisionBox, Point3, DirectionalLight, AmbientLight
from direct.task import Task

# --- CONFIG ---
BLOCK_SIZE = 1
WORLD_SIZE = 16
PLAYER_HEIGHT = 2.0
GRAVITY = -24.0
JUMP_SPEED = 8.0
MOVEMENT_SPEED = 5.0
SPRINT_MULTIPLIER = 1.8

class MiniMinecraft(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        # --- CAMERA MOUSE SETTINGS (EASILY TWEAKABLE) ---
        self.pitch = 0
        self.yaw = 0
        self.sensitivity = 11.0      # ←←← CHANGED TO 1.0 (was 0.3)
                                        # If still too slow, change to 1.5 or 2.0
                                        # If too fast, lower to 0.7
        self.mouse_locked = True

        # Initial lock
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_confined)
        self.win.requestProperties(props)

        # Extra safety lock (fixes "funny" lock behavior on some Windows setups)
        self.taskMgr.doMethodLater(0.1, self.force_mouse_lock, "forceMouseLock")

        # Spawn on terrain
        self.camera.setPos(WORLD_SIZE / 2.0, WORLD_SIZE / 2.0, 6.0)

        # --- Block Types ---
        self.block_types = {
            1: ("grass", (0.2, 0.8, 0.2, 1)),
            2: ("dirt",  (0.55, 0.4, 0.25, 1)),
            3: ("stone", (0.6, 0.6, 0.6, 1)),
        }
        self.current_block = 1

        self.block_model = self.loader.loadModel("models/box")
        self.block_model.setColor(0.5, 0.5, 0.5, 1)

        self.blocks = {}

        # Collision System
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()

        self.playerCollider = self.camera.attachNewNode(CollisionNode('player'))
        self.playerCollider.node().addSolid(CollisionSphere(0, 0, PLAYER_HEIGHT / 2, PLAYER_HEIGHT / 2))
        self.playerCollider.node().setFromCollideMask(BitMask32.bit(1))
        self.playerCollider.node().setIntoCollideMask(BitMask32.allOff())
        self.cTrav.addCollider(self.playerCollider, self.pusher)
        self.pusher.addCollider(self.playerCollider, self.camera)

        # Block picking ray
        self.ray = CollisionRay()
        self.rayNode = CollisionNode("ray")
        self.rayNode.addSolid(self.ray)
        self.rayNode.setFromCollideMask(BitMask32.bit(1))
        self.rayNode.setIntoCollideMask(BitMask32.allOff())
        self.rayNP = self.camera.attachNewNode(self.rayNode)
        self.rayHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.rayNP, self.rayHandler)

        # Ground detection ray
        self.groundRay = CollisionRay(0, 0, 0.05, 0, 0, -1)
        self.groundNode = CollisionNode('groundRay')
        self.groundNode.addSolid(self.groundRay)
        self.groundNode.setFromCollideMask(BitMask32.bit(1))
        self.groundNode.setIntoCollideMask(BitMask32.allOff())
        self.groundNP = self.camera.attachNewNode(self.groundNode)
        self.groundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.groundNP, self.groundHandler)

        self.velocity = Vec3(0, 0, 0)
        self.on_ground = False

        self.generate_terrain()
        self.setup_lighting()

        self.keys = {k: False for k in ["w", "a", "s", "d", "space", "shift", "escape"]}
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])

        for i in range(1, 4):
            self.accept(str(i), self.set_key, [f"block{i}", True])

        self.accept("mouse1", self.break_block)
        self.accept("mouse3", self.place_block)

        self.taskMgr.add(self.update, "update")

        print("=== MiniMinecraft Started ===")
        print("Mouse sensitivity set to 1.0 (you can change it in the code)")
        print("Click inside the game window once if mouse still feels off")
        print("ESC = toggle mouse lock")

    def force_mouse_lock(self, task):
        if self.mouse_locked:
            props = WindowProperties()
            props.setCursorHidden(True)
            props.setMouseMode(WindowProperties.M_confined)
            self.win.requestProperties(props)
        return Task.done

    def set_key(self, key, value):
        if key.startswith("block"):
            try:
                num = int(key[5:])
                if num in self.block_types:
                    self.current_block = num
                    return
            except ValueError:
                pass
        self.keys[key] = value

        if key == "escape" and value:
            self.mouse_locked = not self.mouse_locked
            props = WindowProperties()
            props.setCursorHidden(not self.mouse_locked)
            props.setMouseMode(WindowProperties.M_confined if self.mouse_locked else WindowProperties.M_absolute)
            self.win.requestProperties(props)
            print(f"Mouse lock toggled → {'LOCKED' if self.mouse_locked else 'UNLOCKED'}")

    def setup_lighting(self):
        dlight = DirectionalLight("dlight")
        dlight.setColor((0.8, 0.8, 0.7, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(45, -60, 0)
        self.render.setLight(dlnp)

        alight = AmbientLight("alight")
        alight.setColor((0.3, 0.3, 0.35, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

    def generate_terrain(self):
        for x in range(WORLD_SIZE):
            for y in range(WORLD_SIZE):
                height = 3
                for z in range(height):
                    block_type = "grass" if z == height - 1 else "dirt"
                    self.create_block(x, y, z, block_type)

    def create_block(self, x, y, z, block_type="grass"):
        block = self.block_model.copyTo(self.render)
        block.setPos(x * BLOCK_SIZE, y * BLOCK_SIZE, z * BLOCK_SIZE)
        block.setScale(BLOCK_SIZE)

        for name, color in self.block_types.values():
            if name == block_type:
                block.setColor(*color)
                break

        cnode = CollisionNode(f"block_{x}_{y}_{z}")
        cnode.addSolid(CollisionBox(Point3(0, 0, 0), 0.5, 0.5, 0.5))
        cnode.setFromCollideMask(BitMask32.allOff())
        cnode.setIntoCollideMask(BitMask32.bit(1))
        block.attachNewNode(cnode)

        self.blocks[(x, y, z)] = block

    def remove_block(self, x, y, z):
        key = (x, y, z)
        if key in self.blocks:
            self.blocks[key].removeNode()
            del self.blocks[key]

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
            place = tuple(int(round(c)) for c in (pos + normal * 0.5))
            return block, place
        return None, None

    def break_block(self):
        block, _ = self.get_target()
        if block:
            self.remove_block(*block)

    def place_block(self):
        _, place = self.get_target()
        if not place:
            return
        player_pos = self.camera.getPos(self.render)
        place_vec = Vec3(*place)
        if (player_pos - place_vec).length() < PLAYER_HEIGHT:
            return
        block_type = list(self.block_types[self.current_block])[0]
        self.create_block(*place, block_type)

    def update(self, task):
        dt = globalClock.getDt()
        self.update_mouse()
        self.update_movement(dt)
        self.cTrav.traverse(self.render)
        self.update_ground_check()

        if self.camera.getZ() < -50:
            self.camera.setPos(WORLD_SIZE / 2.0, WORLD_SIZE / 2.0, 6.0)
            self.velocity.z = 0
            self.on_ground = True

        return Task.cont

    def update_mouse(self):
        if not self.mouse_locked or not self.mouseWatcherNode.hasMouse():
            return

        x = self.mouseWatcherNode.getMouseX()
        y = self.mouseWatcherNode.getMouseY()

        # Apply rotation
        self.yaw -= x * self.sensitivity
        self.pitch -= y * self.sensitivity
        self.pitch = max(-90, min(90, self.pitch))
        self.camera.setHpr(self.yaw, self.pitch, 0)

        # Recenter mouse (this is what makes the lock feel "solid")
        self.win.movePointer(0,
                             int(self.win.getProperties().getXSize() / 2),
                             int(self.win.getProperties().getYSize() / 2))

    def update_movement(self, dt):
        direction = Vec3(0, 0, 0)
        if self.keys.get("w"): direction += Vec3(0, 1, 0)
        if self.keys.get("s"): direction += Vec3(0, -1, 0)
        if self.keys.get("a"): direction += Vec3(-1, 0, 0)
        if self.keys.get("d"): direction += Vec3(1, 0, 0)

        speed = MOVEMENT_SPEED * (SPRINT_MULTIPLIER if self.keys.get("shift") else 1.0)

        if direction.length() > 0:
            direction.normalize()
            direction *= speed * dt
        self.camera.setPos(self.camera, direction)

        self.velocity.z += GRAVITY * dt

        if self.keys.get("space") and self.on_ground:
            self.velocity.z = JUMP_SPEED
            self.on_ground = False

        self.camera.setZ(self.camera.getZ() + self.velocity.z * dt)

    def update_ground_check(self):
        self.groundHandler.sortEntries()
        self.on_ground = False
        if self.groundHandler.getNumEntries() > 0:
            entry = self.groundHandler.getEntry(0)
            surface_point = entry.getSurfacePoint(self.camera)
            dist = -surface_point.getZ()

            if dist <= 1.3:
                self.on_ground = True
                if self.velocity.z <= 0:
                    self.velocity.z = 0

                # Anti-sink snap (keeps you from falling through)
                hit_pos = entry.getSurfacePoint(self.render)
                desired_z = hit_pos.getZ() + (PLAYER_HEIGHT / 2) + 0.01
                self.camera.setZ(desired_z)

# --- Run ---
app = MiniMinecraft()
app.run()