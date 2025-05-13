from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import NumericProperty, BooleanProperty, StringProperty, ListProperty
import time

class LapLabel(Label): # Custom Label for Laps defined in KV
    pass

class StopwatchLayout(BoxLayout):
    elapsed_time = NumericProperty(0.0)
    running = BooleanProperty(False)
    start_time = NumericProperty(0.0) # Time when stopwatch was last started/resumed
    paused_time = NumericProperty(0.0) # Time accumulated before pausing
    laps = ListProperty([])
    lap_counter = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_event = None

    def format_time(self, total_seconds):
        """Formats time in MM:SS.CS (centiseconds)"""
        if total_seconds < 0: total_seconds = 0 # Ensure no negative time display
        minutes = int(total_seconds / 60)
        seconds = int(total_seconds % 60)
        centiseconds = int((total_seconds * 100) % 100)
        return f"{minutes:02}:{seconds:02}.{centiseconds:02}"

    def update_time_display(self, dt=None):
        """Callback for Clock.schedule_interval"""
        if self.running:
            current_lap_time = time.time() - self.start_time
            self.elapsed_time = self.paused_time + current_lap_time
            self.ids.time_label.text = self.format_time(self.elapsed_time)
        else:
            # Ensure display is correct even when paused
            self.ids.time_label.text = self.format_time(self.elapsed_time)


    def toggle_start_stop(self):
        if not self.running:
            # Starting or Resuming
            self.running = True
            self.start_time = time.time() # Record new start/resume time
            if self.update_event is None:
                 # Schedule update every 0.01s for centisecond precision
                self.update_event = Clock.schedule_interval(self.update_time_display, 0.01)
            self.ids.start_stop_button.text = "Stop"
            self.ids.start_stop_button.background_color = (0.8, 0.2, 0.2, 1) # Reddish for Stop
            self.ids.lap_reset_button.text = "Lap"
            self.ids.lap_reset_button.disabled = False
        else:
            # Stopping
            self.running = False
            if self.update_event:
                self.update_event.cancel()
                self.update_event = None
            # Accumulate elapsed time before this pause
            self.paused_time = self.elapsed_time
            self.ids.start_stop_button.text = "Resume"
            self.ids.start_stop_button.background_color = (0.2, 0.6, 0.3, 1) # Greenish for Resume
            self.ids.lap_reset_button.text = "Reset"
            # Lap button should be disabled when paused, Reset enabled
            self.ids.lap_reset_button.disabled = False


    def lap_or_reset(self):
        if self.running:
            # Lap action
            lap_time = self.elapsed_time
            self.laps.append(lap_time) # Store raw lap time

            # Calculate split time (time for this specific lap)
            if len(self.laps) > 1:
                previous_lap_time = sum(self.laps[:-1]) # This is incorrect for split time calculation
                # Let's store cumulative lap times. Split time is current - previous total.
                # No, let's store individual lap segment times.
                # If we store cumulative times:
                # lap_text = f"Lap {self.lap_counter}: {self.format_time(lap_time)}"
                # If we want split times, we need to store the time of the *last* lap action
                # For simplicity, let's just display the cumulative time at lap press.

                # Correct approach for displaying lap times:
                # The first lap is just the elapsed time.
                # Subsequent laps are elapsed_time - time_of_previous_lap_mark.
                # To simplify, we'll display total elapsed time at lap press, and difference from previous lap.

                lap_display_time = lap_time
                if self.lap_counter > 1:
                    # Find the time of the *previous* lap entry in self.laps
                    # For this, we need to know what self.laps stores.
                    # Let's make self.laps store the *cumulative* time at each lap.
                    split_time = lap_time - self.laps[-2] # -2 because current lap is already appended
                    lap_text = f"Lap {self.lap_counter}: {self.format_time(lap_display_time)} (+{self.format_time(split_time)})"
                else:
                    lap_text = f"Lap {self.lap_counter}: {self.format_time(lap_display_time)}"

            else: # First lap
                lap_text = f"Lap {self.lap_counter}: {self.format_time(lap_time)}"


            self.lap_counter += 1
            lap_label_widget = LapLabel(text=lap_text)
            self.ids.laps_layout.add_widget(lap_label_widget, index=0) # Add to top

        else:
            # Reset action (only when paused)
            self.running = False
            if self.update_event:
                self.update_event.cancel()
                self.update_event = None
            self.elapsed_time = 0.0
            self.paused_time = 0.0
            self.start_time = 0.0
            self.laps = []
            self.lap_counter = 1
            self.ids.time_label.text = self.format_time(0.0)
            self.ids.laps_layout.clear_widgets()
            self.ids.start_stop_button.text = "Start"
            self.ids.start_stop_button.background_color = (0.2, 0.6, 0.3, 1) # Greenish
            self.ids.lap_reset_button.text = "Lap"
            self.ids.lap_reset_button.disabled = True


class StopwatchApp(App):
    def build(self):
        return StopwatchLayout()

if __name__ == '__main__':
    StopwatchApp().run()