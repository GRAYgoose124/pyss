# Importing arcade module
import arcade
# Importing arcade gui
import arcade.gui

# Creating MainGame class


class MainGame(arcade.Window):
    def __init__(self):
        super().__init__(600, 600, title="Buttons")

        # Changing background color of screen
        arcade.set_background_color(arcade.color.BLUE)

        # Creating a UI MANAGER to handle the UI
        self.uimanager = arcade.gui.UIManager()
        self.uimanager.enable()

        # Creating Button using UIFlatButton
        start_button = arcade.gui.UIFlatButton(text="Start Game",
                                               width=200)

        # Adding button in our uimanager
        self.uimanager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=start_button)
        )

    # Creating on_draw() function to draw on the screen

    def on_draw(self):
        arcade.start_render()

        # Drawing our ui manager
        self.uimanager.draw()


# Calling MainGame class
MainGame()
arcade.run()
