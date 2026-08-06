import tkinter as tk


class BaseCluster:
    def __init__(self, app, canvas):
        self.app = app
        self.canvas = canvas

    def draw_static_base(self):
        raise NotImplementedError

    def update_cluster(self, rpm):
        raise NotImplementedError
