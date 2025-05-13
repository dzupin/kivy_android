from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.core.window import Window
import datetime
import time  # Using time.time() for more precise elapsed time


class StopwatchApp(App):
    elapsed_time_seconds = NumericProperty(0.0)
    is_running = BooleanProperty(False)
    stopwatch_display = StringProperty("00:00.00")
    current_time_display = StringProperty("00:00:00")

    # For more accurate stopwatch timing
    _last_tick = NumericProperty(0.0)

    def build(self):
        # Set a dark background for the window
        Window.clearcolor = (0.1, 0.1, 0.1, 1)  # Dark gray

        # Main layout
        root_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Stopwatch display label
        self.stopwatch_label = Label(
            text=self.stopwatch_display,
            font_size='110sp',  # Very large font
            size_hint_y=0.6,  # Takes 60% of vertical space
            color=(0.9, 0.9, 0.9, 1),  # Light gray text
            halign='center',
            valign='middle'
        )
        # Bind the label's text to our StringProperty
        self.bind(stopwatch_display=self.stopwatch_label.setter('text'))

        # Current time display label
        self.current_time_label = Label(
            text=self.current_time_display,
            font_size='30sp',  # Smaller font
            size_hint_y=0.1,  # Takes 10% of vertical space
            color=(0.7, 0.7, 0.7, 1),  # Medium gray text
            halign='center',
            valign='middle'
        )
        self.bind(current_time_display=self.current_time_label.setter('text'))

        # Button layout
        button_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=0.3)

        self.start_stop_button = Button(
            text="Start",
            font_size='40sp',
            on_press=self.toggle_stopwatch,
            background_color=(0.2, 0.6, 0.2, 1),  # Greenish
            color=(1, 1, 1, 1)  # White text
        )
        # Make button text bold
        self.start_stop_button.bold = True

        self.reset_button = Button(
            text="Reset",
            font_size='40sp',
            on_press=self.reset_stopwatch,
            background_color=(0.8, 0.2, 0.2, 1),  # Reddish
            color=(1, 1, 1, 1)  # White text
        )
        self.reset_button.bold = True

        button_layout.add_widget(self.start_stop_button)
        button_layout.add_widget(self.reset_button)

        # Add widgets to root layout
        root_layout.add_widget(self.stopwatch_label)
        root_layout.add_widget(self.current_time_label)
        root_layout.add_widget(button_layout)

        # Schedule current time update every second
        Clock.schedule_interval(self.update_current_time, 1)
        # Initial update for current time
        self.update_current_time(0)  # dt argument is not used here

        return root_layout

    def update_current_time(self, dt):
        now = datetime.datetime.now()
        self.current_time_display = now.strftime("%H:%M:%S")

    def update_stopwatch_display(self, dt):
        if self.is_running:
            # More accurate timing using time.time()
            current_tick = time.time()
            self.elapsed_time_seconds += (current_tick - self._last_tick)
            self._last_tick = current_tick

        minutes = int(self.elapsed_time_seconds // 60)
        seconds = int(self.elapsed_time_seconds % 60)
        milliseconds = int((self.elapsed_time_seconds * 100) % 100)  # Show two decimal places for seconds
        self.stopwatch_display = f"{minutes:02}:{seconds:02}.{milliseconds:02}"

    def toggle_stopwatch(self, instance):
        if self.is_running:
            self.is_running = False
            self.start_stop_button.text = "Start"
            self.start_stop_button.background_color = (0.2, 0.6, 0.2, 1)  # Greenish
            Clock.unschedule(self.update_stopwatch_display)
        else:
            self.is_running = True
            self.start_stop_button.text = "Stop"
            self.start_stop_button.background_color = (0.7, 0.5, 0.1, 1)  # Orangish/Yellowish
            self._last_tick = time.time()  # Reset last_tick before starting
            # Update stopwatch display more frequently for smoother milliseconds
            Clock.schedule_interval(self.update_stopwatch_display, 0.01)  # Update 100 times/sec

    def reset_stopwatch(self, instance):
        if self.is_running:
            self.is_running = False
            self.start_stop_button.text = "Start"
            self.start_stop_button.background_color = (0.2, 0.6, 0.2, 1)  # Greenish
            Clock.unschedule(self.update_stopwatch_display)

        self.elapsed_time_seconds = 0.0
        self.update_stopwatch_display(0)  # Update display immediately


if __name__ == '__main__':
    StopwatchApp().run()