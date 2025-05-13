import kivy

kivy.require('2.0.0')  # Ensure Kivy version compatibility

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import ButtonBehavior, Button  # For clickable pieces
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
import random

# Game Configuration
NUM_ROWS = 8
NUM_COLS = 8
NUM_PIECE_TYPES = 5  # Number of different colors/shapes
PIECE_SIZE = (60, 60)  # Approximate size, will be adapted by GridLayout
ANIM_DURATION = 0.2  # Animation speed

# Define piece colors (hex codes for nice modern colors)
PIECE_COLORS_HEX = [
    '#FF6B6B',  # Light Red
    '#4ECDC4',  # Turquoise
    '#45B7D1',  # Light Blue
    '#FED766',  # Yellow
    '#9B59B6',  # Purple
    '#2ECC71'  # Green
]
PIECE_COLORS = [get_color_from_hex(c) for c in PIECE_COLORS_HEX[:NUM_PIECE_TYPES]]


# --- Game Piece Widget ---
class GamePiece(ButtonBehavior, Widget):
    def __init__(self, row, col, piece_type=-1, **kwargs):
        super().__init__(**kwargs)
        self.row = row
        self.col = col
        self.piece_type = piece_type
        self.is_selected = False
        self.is_matched = False  # Flag for removal animation

        with self.canvas.before:
            self.border_color_instruction = Color(0, 0, 0, 0)  # Transparent initially
            self.border = Line(width=2)
        with self.canvas:
            self.color_instruction = Color(1, 1, 1, 1)  # Default white
            self.shape = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])

        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.set_type(piece_type)  # Apply initial type and color

    def update_graphics(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

        # Update border position and points (simple rectangle)
        x, y = self.pos
        w, h = self.size
        self.border.points = [x, y, x + w, y, x + w, y + h, x, y + h, x, y]

    def set_type(self, piece_type):
        self.piece_type = piece_type
        if piece_type == -1:  # Empty piece
            self.color_instruction.rgba = (0, 0, 0, 0)  # Transparent
            self.opacity = 0  # Make widget invisible if it's supposed to be empty
        else:
            self.color_instruction.rgba = PIECE_COLORS[piece_type % len(PIECE_COLORS)]
            self.opacity = 1
            # Vary radius slightly for visual distinction (optional)
            self.shape.radius = [5 + (piece_type * 2)] * 4
        self.is_matched = False

    def select(self):
        self.is_selected = True
        self.border_color_instruction.rgba = (1, 1, 1, 1)  # White border

    def deselect(self):
        self.is_selected = False
        self.border_color_instruction.rgba = (0, 0, 0, 0)  # Transparent border

    def animate_removal(self):
        self.is_matched = True
        anim = Animation(scale=0, opacity=0, duration=ANIM_DURATION)
        anim.bind(on_complete=lambda *args: self.set_type(-1))  # Set to empty after animation
        anim.start(self)
        return anim

    def animate_fall(self, new_pos):
        anim = Animation(pos=new_pos, duration=ANIM_DURATION)
        anim.start(self)
        return anim

    def animate_new(self):
        self.opacity = 0
        self.scale = 0.5
        anim = Animation(opacity=1, scale=1, duration=ANIM_DURATION)
        anim.start(self)
        return anim

    # Make scale property animatable
    def get_scale(self):
        return self.scale_value if hasattr(self, 'scale_value') else 1.0

    def set_scale(self, value):
        self.scale_value = value
        self.size_hint = (value, value)  # This might conflict with GridLayout
        # For direct size control with scale for animation:
        if hasattr(self, '_orig_size'):
            self.size = (self._orig_size[0] * value, self._orig_size[1] * value)
        else:
            self._orig_size = self.size
        self.center = self.center  # Re-center if size changes

    scale = property(get_scale, set_scale)


# --- Game Board Logic and Layout ---
class GameBoard(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = NUM_COLS
        self.rows = NUM_ROWS
        self.pieces = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        self.selected_piece = None
        self.game_logic_lock = False  # Prevent actions during animation/processing
        self.is_swapping_back = False  # Flag to avoid decrementing moves on swap back

        self.populate_initial_board()
        Clock.schedule_once(lambda dt: self.handle_all_matches_and_refills(is_initial=True), 0.1)

    def get_piece(self, r, c):
        if 0 <= r < NUM_ROWS and 0 <= c < NUM_COLS:
            return self.pieces[r][c]
        return None

    def populate_initial_board(self):
        self.clear_widgets()  # Clear previous widgets if any
        for r in range(NUM_ROWS):
            for c in range(NUM_COLS):
                piece_type = random.randint(0, NUM_PIECE_TYPES - 1)
                piece = GamePiece(row=r, col=c, piece_type=piece_type)
                piece.bind(on_press=self.on_piece_press)
                self.pieces[r][c] = piece
                self.add_widget(piece)
        # Ensure correct sizing after adding all widgets
        Clock.schedule_once(self._update_piece_sizes_and_positions, 0)

    def _update_piece_sizes_and_positions(self, *args):
        # This function helps ensure pieces know their final size after GridLayout settles
        for r in range(NUM_ROWS):
            for c in range(NUM_COLS):
                piece = self.pieces[r][c]
                if piece:
                    piece._orig_size = piece.size  # Store original size for scaling
                    piece.update_graphics()  # Refresh visuals

    def on_piece_press(self, piece_instance):
        if self.game_logic_lock or piece_instance.is_matched or piece_instance.piece_type == -1:
            return

        if not self.selected_piece:
            self.selected_piece = piece_instance
            piece_instance.select()
        else:
            self.selected_piece.deselect()
            if self.selected_piece == piece_instance:  # Clicked same piece
                self.selected_piece = None
                return

            if self.are_adjacent(self.selected_piece, piece_instance):
                self.game_logic_lock = True  # Lock input
                self.is_swapping_back = False  # Reset flag
                self.swap_pieces_and_check(self.selected_piece, piece_instance)
            else:  # Not adjacent, select the new piece
                self.selected_piece = piece_instance
                piece_instance.select()

    def are_adjacent(self, p1, p2):
        return (abs(p1.row - p2.row) == 1 and p1.col == p2.col) or \
            (abs(p1.col - p2.col) == 1 and p1.row == p2.row)

    def swap_pieces_and_check(self, p1, p2):
        # Store original data for potential swap back
        p1_orig_pos, p2_orig_pos = p1.pos, p2.pos

        # Animate swap
        anim_p1 = Animation(pos=p2_orig_pos, duration=ANIM_DURATION)
        anim_p2 = Animation(pos=p1_orig_pos, duration=ANIM_DURATION)

        def on_swap_animation_finish(*args):
            # Update logical grid and piece attributes AFTER animation
            # (because animation changes 'pos', grid layout might fight it otherwise)
            # We need to swap them in the self.pieces array
            self.pieces[p1.row][p1.col], self.pieces[p2.row][p2.col] = \
                self.pieces[p2.row][p2.col], self.pieces[p1.row][p1.col]

            # Swap internal row/col attributes
            p1.row, p2.row = p2.row, p1.row
            p1.col, p2.col = p2.col, p1.col

            # The animation has already visually moved them.
            # Ensure their internal pos reflects their new logical position
            # This helps if GridLayout tries to reposition them.
            # It's usually better to remove and re-add to GridLayout, but animations make this tricky.
            # For now, we rely on animation setting the final `pos`.
            # Let's force their positions according to their new row/col for consistency.
            # This is tricky. The actual positions are now p2_orig_pos for p1 and p1_orig_pos for p2.
            # So, their `pos` attribute is already correct IF animation completed.

            # Check for matches
            matches = self.find_all_matches()
            if matches:
                if not self.is_swapping_back:  # Only decrement moves on a successful forward swap
                    App.get_running_app().update_moves(-1)
                self.handle_all_matches_and_refills()
            elif not self.is_swapping_back:  # No matches, and it was a forward swap, so swap back
                self.is_swapping_back = True
                # Need to swap them back visually and logically
                self.swap_pieces_and_check(p1, p2)  # Re-call to swap back (p1 and p2 are now in swapped logical places)
            else:  # No matches, and it was a swap_back, so unlock
                self.game_logic_lock = False
                self.is_swapping_back = False

            self.selected_piece = None  # Clear selection after action

        anim_p1.bind(on_complete=on_swap_animation_finish)  # Only need one callback
        anim_p1.start(p1)
        anim_p2.start(p2)

    def find_all_matches(self):
        matches = set()
        # Horizontal matches
        for r in range(NUM_ROWS):
            for c in range(NUM_COLS - 2):
                p1 = self.get_piece(r, c)
                p2 = self.get_piece(r, c + 1)
                p3 = self.get_piece(r, c + 2)
                if p1 and p2 and p3 and p1.piece_type != -1 and \
                        p1.piece_type == p2.piece_type == p3.piece_type:
                    current_match = {(r, c), (r, c + 1), (r, c + 2)}
                    # Check for longer matches
                    for k in range(c + 3, NUM_COLS):
                        pk = self.get_piece(r, k)
                        if pk and pk.piece_type == p1.piece_type:
                            current_match.add((r, k))
                        else:
                            break
                    matches.update(current_match)

        # Vertical matches
        for c in range(NUM_COLS):
            for r in range(NUM_ROWS - 2):
                p1 = self.get_piece(r, c)
                p2 = self.get_piece(r + 1, c)
                p3 = self.get_piece(r + 2, c)
                if p1 and p2 and p3 and p1.piece_type != -1 and \
                        p1.piece_type == p2.piece_type == p3.piece_type:
                    current_match = {(r, c), (r + 1, c), (r + 2, c)}
                    # Check for longer matches
                    for k in range(r + 3, NUM_ROWS):
                        pk = self.get_piece(k, c)
                        if pk and pk.piece_type == p1.piece_type:
                            current_match.add((k, c))
                        else:
                            break
                    matches.update(current_match)
        return list(matches)

    def handle_all_matches_and_refills(self, is_initial=False):
        self.game_logic_lock = True  # Ensure lock during this process
        matches = self.find_all_matches()

        if not matches:
            self.game_logic_lock = False
            if not is_initial:  # Don't check game over during initial setup
                App.get_running_app().check_game_over()
                # Potentially check for no more moves here too (more complex)
            return

        if not is_initial:
            App.get_running_app().update_score(len(matches) * 10)

        # Animate removal
        removal_animations = []
        for r_idx, c_idx in matches:
            piece = self.get_piece(r_idx, c_idx)
            if piece and not piece.is_matched:
                removal_animations.append(piece.animate_removal())

        # Wait for all removal animations to complete
        if removal_animations:
            # Use a counter or Clock.schedule_once after max duration
            # For simplicity, schedule next step after ANIM_DURATION
            Clock.schedule_once(lambda dt: self.process_falling_pieces(), ANIM_DURATION)
        else:  # No animations, proceed directly (should not happen if matches were found)
            self.process_falling_pieces()

    def process_falling_pieces(self):
        falling_animations = []
        # For each column, make pieces fall
        for c in range(NUM_COLS):
            empty_slot_r = NUM_ROWS - 1  # Start checking from bottom
            for r in range(NUM_ROWS - 1, -1, -1):  # Iterate upwards in the column
                piece = self.get_piece(r, c)
                if piece.piece_type != -1:  # If this piece is not empty
                    if r < empty_slot_r:  # If there's an empty slot below it
                        # Move this piece down to empty_slot_r
                        target_piece_widget = self.get_piece(empty_slot_r,
                                                             c)  # This is the placeholder for the empty slot

                        # Swap in logical grid
                        self.pieces[r][c], self.pieces[empty_slot_r][c] = \
                            self.pieces[empty_slot_r][c], self.pieces[r][c]

                        # Update piece's internal row
                        piece.row = empty_slot_r
                        target_piece_widget.row = r  # The "empty" piece moves up

                        # Animate fall
                        # The target_piece_widget.pos is the correct destination position
                        falling_animations.append(piece.animate_fall(target_piece_widget.pos))
                    empty_slot_r -= 1  # Move to the next potential empty slot above

        if falling_animations:
            Clock.schedule_once(lambda dt: self.refill_top_rows(), ANIM_DURATION)
        else:
            self.refill_top_rows()

    def refill_top_rows(self):
        new_piece_animations = []
        for c in range(NUM_COLS):
            for r in range(NUM_ROWS - 1, -1, -1):  # Iterate from top to find empty spots
                piece = self.get_piece(r, c)
                if piece.piece_type == -1:  # This is an empty slot
                    new_type = random.randint(0, NUM_PIECE_TYPES - 1)
                    piece.set_type(new_type)  # Re-purpose the existing widget

                    # For animation, temporarily move it above its final position
                    orig_pos = piece.pos
                    piece.pos = (piece.pos[0], piece.pos[1] + piece.height)  # Start one row above
                    piece.opacity = 0  # Start invisible

                    anim = Animation(pos=orig_pos, opacity=1, duration=ANIM_DURATION)
                    new_piece_animations.append(anim)
                    anim.start(piece)

        if new_piece_animations:
            # After new pieces animate in, check for new matches (chain reaction)
            Clock.schedule_once(lambda dt: self.handle_all_matches_and_refills(), ANIM_DURATION + 0.05)  # Small delay
        else:
            # No new pieces, so chain reaction ends
            Clock.schedule_once(lambda dt: self.handle_all_matches_and_refills(), 0.05)


# --- Main App ---
class Match3App(App):
    def build(self):
        self.title = "Kivy Match-3 (Code-Only Graphics)"
        self.game_over_popup_shown = False

        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Top UI Panel
        self.ui_panel = BoxLayout(size_hint_y=None, height='60dp', spacing=10)
        self.score_label = Label(text="Score: 0", font_size='20sp', halign='center')
        self.moves_label = Label(text="Moves: 30", font_size='20sp', halign='center')
        self.ui_panel.add_widget(self.score_label)
        self.ui_panel.add_widget(self.moves_label)
        root.add_widget(self.ui_panel)

        self.game_board = GameBoard(size_hint=(1, 0.85))  # Give more space to board
        root.add_widget(self.game_board)

        self.score = 0
        self.moves_left = 30
        self.update_ui_labels()

        return root

    def update_score(self, points_to_add):
        self.score += points_to_add
        self.update_ui_labels()

    def update_moves(self, change):
        self.moves_left += change
        if self.moves_left < 0:
            self.moves_left = 0
        self.update_ui_labels()
        # self.check_game_over() # Check game over after move update

    def update_ui_labels(self):
        self.score_label.text = f"Score: {self.score}"
        self.moves_label.text = f"Moves: {self.moves_left}"

    def check_game_over(self):
        if self.moves_left <= 0 and not self.game_board.game_logic_lock and not self.game_over_popup_shown:
            self.show_game_over_popup("Out of Moves!")
        # Add check for no more possible moves (more complex)

    def show_game_over_popup(self, message):
        self.game_over_popup_shown = True
        content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        content.add_widget(Label(text=message, font_size='24sp'))
        content.add_widget(Label(text=f"Final Score: {self.score}", font_size='20sp'))

        restart_button = Button(text="Restart Game", size_hint_y=None, height='50dp')
        restart_button.bind(on_press=self.restart_game)
        content.add_widget(restart_button)

        self.popup = Popup(title="Game Over", content=content,
                           size_hint=(0.75, 0.5), auto_dismiss=False)
        self.popup.open()

    def restart_game(self, instance=None):
        if hasattr(self, 'popup') and self.popup:
            self.popup.dismiss()
            self.popup = None

        self.score = 0
        self.moves_left = 30
        self.game_over_popup_shown = False
        self.update_ui_labels()

        self.game_board.game_logic_lock = False
        self.game_board.selected_piece = None
        self.game_board.populate_initial_board()
        # Initial matches will be handled by populate_initial_board's scheduled call
        Clock.schedule_once(lambda dt: self.game_board.handle_all_matches_and_refills(is_initial=True), 0.2)


if __name__ == '__main__':
    Match3App().run()