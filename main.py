import os
import random
from typing import Optional

import kivy.core.audio
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from config import COLS, ROWS, MUSIC_DIR
from widgets import SnakeGame
from tools.signal_bus import SignalBus

from kivy.core.audio import SoundLoader


class SnakeApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical')

        top_layout = BoxLayout(size_hint=(1, 0.2), padding=10, spacing=10)
        
        reset_button = Button(text='Reset', size_hint=(0.5, 1))
        reset_button.bind(on_press=self.reset_game)
        top_layout.add_widget(reset_button)

        self.score_label = Label(text='Score: 0', size_hint=(0.5, 1))
        top_layout.add_widget(self.score_label)

        pause_track_button = Button(text='Pause Track', size_hint=(0.5, 1))
        pause_track_button.bind(on_press=self.play_pause_track)
        top_layout.add_widget(pause_track_button)

        root.add_widget(top_layout)

        outer_container = AnchorLayout(size_hint=(1, 0.8), padding=10)

        self.game = SnakeGame(size_hint=(None, None))

        outer_container.add_widget(self.game)
        root.add_widget(outer_container)

        # Привязка события изменения размера для динамического пересчета размеров
        outer_container.bind(size=self.update_game_size, pos=self.update_game_size)

        SignalBus.subscribe('score_updated', self.update_score)
        
        self.music_playlist: list[kivy.core.audio.Sound] = self.load_playlist(True)
        self.current_track_index: int = 0
        self.music: Optional[kivy.core.audio.Sound] = None
        self.play_next_track()

        return root
    
    def load_playlist(self, shuffle: bool = False) -> list[kivy.core.audio.Sound]:
        folder = MUSIC_DIR
        supported_formats = ('.mp3', '.ogg', '.wav')
        files = os.listdir(folder)
        result = [os.path.join(folder, f) for f in files if f.lower().endswith(supported_formats)]
        result = list(filter(None, map(SoundLoader.load, result)))
        
        if shuffle:
            random.shuffle(result)
        
        return result

    def play_next_track(self, *args):
        if not self.music_playlist:
            print("Нет треков для воспроизведения.")
            return

        if self.music:
            self.music.unbind(on_stop=self.play_next_track)
            self.music.stop()

        for _ in range(len(self.music_playlist)):
            self.music = self.music_playlist[self.current_track_index]
            self.current_track_index = (self.current_track_index + 1) % len(self.music_playlist)

            if self.music:
                self.music.volume = 0.5
                self.music.bind(on_stop=self.play_next_track)
                self.music.play()
                return

        print("Не удалось воспроизвести ни один трек.")

    def play_pause_track(self, instance: Button):
        if not self.music:
           return

        if self.music.state == 'play':
            self.music.unbind(on_stop=self.play_next_track)
            self.music.stop()
            instance.text = 'Play Track'
        else:
            self.music.play()
            self.music.bind(on_stop=self.play_next_track)
            instance.text = 'Stop Track'

    def on_stop(self):
        if self.music:
            self.music.stop()
    
    def reset_game(self, instance):
        self.game.reset_game()

    def update_score(self, score):
        self.score_label.text = f'Score: {score}'

    def update_game_size(self, instance, value):
        outer_width, outer_height = instance.size
        padding_x1, padding_x2, padding_y1, padding_y2 = instance.padding

        available_width = outer_width - padding_x1 - padding_x2
        available_height = outer_height - padding_y1 - padding_y2

        cell_size_width = available_width / COLS
        cell_size_height = available_height / ROWS

        cell_size = min(cell_size_width, cell_size_height)
        
        SignalBus.emit('cell_size_updated', cell_size)

        game_width = COLS * cell_size
        game_height = ROWS * cell_size
        self.game.size = (game_width, game_height)
        self.game.pos = (
            (outer_width - self.game.width) / 2,
            (outer_height - self.game.height) / 2
        )


if __name__ == '__main__':
    SnakeApp().run()
