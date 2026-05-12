# =========================
    # Trộn puzzle
    # =========================
    def shuffle(self):
        moves = ["up", "down", "left", "right"]

        for _ in range(100):
            self.move(random.choice(moves))

        self.status_label.config(text="")