from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty, StringProperty, ListProperty
import time

class LapLabel(Label):  # Custom Label for Laps defined in KV
    pass


class StopwatchLayout(BoxLayout):
    elapsed_time = NumericProperty(0.0)
    running = BooleanProperty(False)
    start_time = NumericProperty(0.0)  # Time when stopwatch was last started/resumed (epoch time)
    paused_time = NumericProperty(0.0)  # Time accumulated before pausing (duration)
    laps = ListProperty([])
    lap_counter = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_event = None

    def format_duration(self, total_seconds_float):
        """Formats an elapsed duration in HH:MM:SS"""
        if total_seconds_float < 0: total_seconds_float = 0

        total_seconds = int(round(total_seconds_float))

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def get_current_system_timestamp_str(self):
        """Returns the current system time and date as 'HH:MM:SS   DD/MM/YYYY' string"""
        # Format: HH:MM:SS   DD/MM/YYYY
        return time.strftime("%H:%M:%S   %d/%m/%Y", time.localtime())

    def update_time_display(self, dt=None):
        """Callback for Clock.schedule_interval to update stopwatch display"""
        if self.running:
            current_segment_time = time.time() - self.start_time  # duration since last start/resume
            self.elapsed_time = self.paused_time + current_segment_time
            self.ids.time_label.text = self.format_duration(self.elapsed_time)
        else:
            # Ensure display is correct even when paused
            self.ids.time_label.text = self.format_duration(self.elapsed_time)

    def toggle_start_stop(self):
        current_button_action_text = self.ids.start_stop_button.text  # "Start", "Stop", or "Resume"
        system_timestamp_str = self.get_current_system_timestamp_str()  # Get system time & date for logging

        if not self.running:
            # Current state is PAUSED or INITIAL
            # Action will be STARTING or RESUMING

            log_message_prefix = ""

            if current_button_action_text == "Start":
                log_message_prefix = "Start"
            elif current_button_action_text == "Resume":
                log_message_prefix = "Resume"
            else:
                log_message_prefix = "Unknown Resume"  # Fallback

            log_entry = f"{log_message_prefix}: {system_timestamp_str}"  # Use system time & date for log
            log_label_widget = LapLabel(text=log_entry)
            self.ids.laps_layout.add_widget(log_label_widget, index=0)

            # Actual stopwatch state change
            self.running = True
            self.start_time = time.time()  # Record new start/resume epoch time
            if self.update_event is None:
                self.update_event = Clock.schedule_interval(self.update_time_display, 0.01)

            self.ids.start_stop_button.text = "Stop"
            self.ids.start_stop_button.background_color = (0.8, 0.2, 0.2, 1)  # Reddish for Stop
            self.ids.lap_reset_button.text = "Lap"
            self.ids.lap_reset_button.disabled = False
        else:
            # Current state is RUNNING
            # Action will be STOPPING

            current_segment_time = time.time() - self.start_time
            exact_stop_elapsed_time = self.paused_time + current_segment_time

            log_entry = f"Stop: {system_timestamp_str}"  # Use system time & date for log
            log_label_widget = LapLabel(text=log_entry)
            self.ids.laps_layout.add_widget(log_label_widget, index=0)

            # Actual stopwatch state change
            self.running = False
            if self.update_event:
                self.update_event.cancel()
                self.update_event = None

            self.elapsed_time = exact_stop_elapsed_time
            self.paused_time = self.elapsed_time

            self.update_time_display()

            self.ids.start_stop_button.text = "Resume"
            self.ids.start_stop_button.background_color = (0.2, 0.6, 0.3, 1)
            self.ids.lap_reset_button.text = "Reset"
            self.ids.lap_reset_button.disabled = False

    def lap_or_reset(self):
        if self.running:
            # Lap action
            lap_time_at_press = self.elapsed_time

            self.laps.append(lap_time_at_press)

            lap_display_time = lap_time_at_press
            if self.lap_counter > 1:
                split_time = lap_time_at_press - self.laps[-2]
                lap_text = f"Lap {self.lap_counter}: {self.format_duration(lap_display_time)} (+{self.format_duration(split_time)})"
            else:
                lap_text = f"Lap {self.lap_counter}: {self.format_duration(lap_display_time)}"

            self.lap_counter += 1
            lap_label_widget = LapLabel(text=lap_text)
            self.ids.laps_layout.add_widget(lap_label_widget, index=0)

        else:
            # Reset action (only when paused or stopped)
            system_timestamp_str = self.get_current_system_timestamp_str()  # Get system time & date for logging reset

            self.running = False
            if self.update_event:
                self.update_event.cancel()
                self.update_event = None
            self.elapsed_time = 0.0
            self.paused_time = 0.0
            self.start_time = 0.0
            self.laps = []
            self.lap_counter = 1

            self.ids.time_label.text = self.format_duration(0.0)
            self.ids.laps_layout.clear_widgets()  # Clear all previous laps and event logs

            # Log the Reset event
            log_entry = f"Reset: {system_timestamp_str}"
            log_label_widget = LapLabel(text=log_entry)
            self.ids.laps_layout.add_widget(log_label_widget, index=0)  # Add Reset log to the (now empty) layout

            self.ids.start_stop_button.text = "Start"
            self.ids.start_stop_button.background_color = (0.2, 0.6, 0.3, 1)
            self.ids.lap_reset_button.text = "Lap"
            self.ids.lap_reset_button.disabled = True


class StopwatchApp(App):
    def build(self):
        return StopwatchLayout()


if __name__ == '__main__':
    StopwatchApp().run()