import pygame

class KeyInputHandler:
    def __init__(self):
        self.keysPressed = ()
        self.keysPressedBefore = ()
        
        self.mouseKeysPressed = ()
        self.mouseKeysPressedBefore = ()
        self.mouseKeysReleased = ()

        self.keyBinds = {}
        self.mouseKeyBinds = {}

        self.actions = []
        self.actionsDoneBefore = []

        self.mouseWheelDirection = 0

    def addKeyBind(self, key: int, bind: str):
        self.keyBinds[key] = bind
    
    def removeKeyBind(self, key: int):
        self.keyBinds[key] = None
        self.keyBinds.pop(key)

    def update(self, mouseWheelEvent=None):
        """
        should be called after pygame.event.get function, or else mouse keys could not work as expected
        """
        self.keysPressedBefore = self.keysPressed
        self.mouseKeysPressedBefore = self.mouseKeysPressed
        self.actionsDoneBefore = self.actions
        self.mouseWheelDirection = 0

        if mouseWheelEvent:
            self.mouseWheelDirection = mouseWheelEvent.y

        self.keysPressed = pygame.key.get_pressed()
        self.mouseKeysPressed = pygame.mouse.get_pressed(num_buttons=5)

        self.keysReleased = self.getKeysReleased(self.keysPressed, self.keysPressedBefore)
        self.mouseKeysReleased = self.getKeysReleased(self.mouseKeysPressed, self.mouseKeysPressedBefore)

        self.actions = self.getActions()

    def getKeysReleased(self, keysPressed: tuple | list, keysPressedBefore: tuple | list):
        """
        WARNING: This does not work with keyboard, if the user presses f1 or left, it won't work!
        """
        keysReleased = [None for i in range(10000)]

        for key in range(len(keysPressedBefore)):
            if keysPressedBefore[key] and not keysPressed[key]:
                keysReleased[key] = True
            else:
                keysReleased[key] = False
        
        return keysReleased

    def keyPressed(self, key: int):
        return self.keysPressed[key]
    
    def keyPressedOnce(self, key: int):
        return self.keyPressed(key) and not self.keysPressedBefore[key]

    def mouseKeyPressed(self, key: int):
        return self.mouseKeysPressed[key]
    
    def mouseKeyPressedOnce(self, key: int):
        return self.mouseKeyPressed(key) and not self.mouseKeysPressedBefore[key]

    def mouseKeyReleased(self, key: int):
        return self.mouseKeysReleased[key]
    
    def getActions(self):
        actions = []
        for key, bind in self.keyBinds.items():
            if self.keyPressed(key) and bind not in actions:
                actions.append(bind)

        for key, bind in self.mouseKeyBinds.items():
            if self.mouseKeyPressed(key) and bind not in actions:
                actions.append(bind)
        
        return actions
    
    def actionDone(self, action: str):
        return action in self.actions

    def actionDoneOnce(self, action: str):
        return self.actionDone(action) and not action in self.actionsDoneBefore

    def mouseWheelDown(self):
        return True if self.mouseWheelDirection < 0 else False
    
    def mouseWheelUp(self):
        return True if self.mouseWheelDirection > 0 else False