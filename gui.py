import copy
import threading
from dataclasses import dataclass

import pygame

from game_logic import GameLogic
from genetic_algorithm import GeneticAlgorithm


PUZZLE_SIZE = 5
RANDOMIZE_MOVES = 50
POPULATION_SIZE = 100
CHROMOSOME_LENGTH = 100
MUTATION_RATE = 0.05
GENERATIONS = 100

WINDOW_WIDTH = 1180
WINDOW_HEIGHT = 840
FPS = 60
BOARD_PIXELS = 600
TILE_GAP = 6
ANIMATION_SECONDS = 0.18

BG = (22, 24, 29)
PANEL = (35, 39, 47)
PANEL_LIGHT = (47, 53, 64)
TEXT = (238, 241, 245)
MUTED = (165, 174, 188)
ACCENT = (96, 180, 145)
ACCENT_DARK = (70, 136, 110)
TILE = (235, 238, 232)
TILE_ALT = (215, 225, 220)
TILE_TEXT = (30, 35, 42)
EMPTY = (58, 65, 76)
DISABLED = (78, 84, 96)
WARNING = (238, 179, 89)


@dataclass
class Button:
    label: str
    rect: pygame.Rect
    action: callable
    enabled: bool = True

    def draw(self, screen, font):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.enabled and self.rect.collidepoint(mouse_pos)
        color = ACCENT_DARK if is_hovered else ACCENT
        if not self.enabled:
            color = DISABLED

        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, PANEL_LIGHT, self.rect, width=2, border_radius=8)

        text_surface = font.render(self.label, True, TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if (
            self.enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        ):
            self.action()


@dataclass
class TextInput:
    label: str
    value: str
    rect: pygame.Rect
    active: bool = False

    def draw(self, screen, label_font, value_font, enabled=True):
        label_surface = label_font.render(self.label, True, MUTED if enabled else DISABLED)
        screen.blit(label_surface, (self.rect.x, self.rect.y - 22))

        border = ACCENT if self.active and enabled else PANEL_LIGHT
        fill = (28, 31, 38) if enabled else PANEL
        pygame.draw.rect(screen, fill, self.rect, border_radius=6)
        pygame.draw.rect(screen, border, self.rect, width=2, border_radius=6)

        value_surface = value_font.render(self.value, True, TEXT if enabled else DISABLED)
        screen.blit(value_surface, (self.rect.x + 10, self.rect.y + 9))

    def handle_event(self, event, enabled=True):
        if not enabled:
            self.active = False
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            return

        if not self.active or event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_BACKSPACE:
            self.value = self.value[:-1]
        elif event.key in (pygame.K_RETURN, pygame.K_TAB, pygame.K_ESCAPE):
            self.active = False
        elif len(self.value) < 10 and event.unicode in "0123456789.":
            if event.unicode == "." and "." in self.value:
                return
            self.value += event.unicode


class SlidingPuzzleApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Sliding Puzzle - Genetic Algorithm")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("segoeui", 24)
        self.small_font = pygame.font.SysFont("segoeui", 18)
        self.big_font = pygame.font.SysFont("segoeui", 34, bold=True)

        self.config = {
            "puzzle_size": PUZZLE_SIZE,
            "randomize_moves": RANDOMIZE_MOVES,
            "population_size": POPULATION_SIZE,
            "chromosome_length": CHROMOSOME_LENGTH,
            "mutation_rate": MUTATION_RATE,
            "generations": GENERATIONS,
        }

        self.board_origin = (40, 118)
        self.tile_size = BOARD_PIXELS // self.config["puzzle_size"]

        self.solved_game = GameLogic(self.config["puzzle_size"])
        self.problem_game = copy.deepcopy(self.solved_game)
        self.visual_game = copy.deepcopy(self.problem_game)

        self.solution_moves = []
        self.solution_fitness = None
        self.solution_solves = False
        self.is_solving = False
        self.status = "Clique em Embaralhar ou Resolver."
        self.progress = {
            "generation": 0,
            "current_best_fitness": 0,
            "best_overall_fitness": 0,
            "best_moves_count": 0,
        }
        self.progress_lock = threading.Lock()

        self.animation_queue = []
        self.animation = None
        self.is_animating = False

        self.inputs = self.create_inputs()
        self.buttons = self.create_buttons()
        self.randomize_puzzle()

    def create_buttons(self):
        top = 40
        width = 132
        height = 44
        gap = 14
        start_x = 340
        labels_actions = [
            ("Embaralhar", self.randomize_puzzle),
            ("Resolver", self.start_solver),
            ("Animar", self.start_animation),
            ("Reset", self.reset_puzzle),
        ]

        buttons = []
        for index, (label, action) in enumerate(labels_actions):
            rect = pygame.Rect(start_x + index * (width + gap), top, width, height)
            buttons.append(Button(label, rect, action))
        return buttons

    def create_inputs(self):
        x = 710
        y = 196
        width = 132
        height = 40
        row_gap = 78
        col_gap = 172
        fields = [
            ("Tamanho", "puzzle_size"),
            ("Embaralhar", "randomize_moves"),
            ("Populacao", "population_size"),
            ("Cromossomo", "chromosome_length"),
            ("Mutacao", "mutation_rate"),
            ("Geracoes", "generations"),
        ]

        inputs = {}
        for index, (label, key) in enumerate(fields):
            col = index % 2
            row = index // 2
            rect = pygame.Rect(x + col * col_gap, y + row * row_gap, width, height)
            inputs[key] = TextInput(label, str(self.config[key]), rect)
        return inputs

    def randomize_puzzle(self):
        if self.is_solving or self.is_animating:
            return

        if not self.apply_config_from_inputs():
            return

        self.solved_game = GameLogic(self.config["puzzle_size"])
        self.problem_game = GameLogic(self.config["puzzle_size"])
        self.problem_game.randomize(moves=self.config["randomize_moves"])
        self.visual_game = copy.deepcopy(self.problem_game)
        self.tile_size = BOARD_PIXELS // self.config["puzzle_size"]
        self.solution_moves = []
        self.solution_fitness = None
        self.solution_solves = False
        self.animation_queue = []
        self.animation = None
        self.status = "Puzzle embaralhado. Clique em Resolver."
        self.reset_progress()

    def reset_puzzle(self):
        if self.is_solving or self.is_animating:
            return

        if not self.apply_config_from_inputs():
            return

        self.solved_game = GameLogic(self.config["puzzle_size"])
        self.problem_game = copy.deepcopy(self.solved_game)
        self.visual_game = copy.deepcopy(self.problem_game)
        self.tile_size = BOARD_PIXELS // self.config["puzzle_size"]
        self.solution_moves = []
        self.solution_fitness = None
        self.solution_solves = False
        self.animation_queue = []
        self.animation = None
        self.status = "Puzzle resetado para o estado resolvido."
        self.reset_progress()

    def reset_progress(self):
        with self.progress_lock:
            self.progress = {
                "generation": 0,
                "current_best_fitness": 0,
                "best_overall_fitness": 0,
                "best_moves_count": 0,
            }

    def apply_config_from_inputs(self):
        try:
            new_config = {
                "puzzle_size": int(self.inputs["puzzle_size"].value),
                "randomize_moves": int(self.inputs["randomize_moves"].value),
                "population_size": int(self.inputs["population_size"].value),
                "chromosome_length": int(self.inputs["chromosome_length"].value),
                "mutation_rate": float(self.inputs["mutation_rate"].value),
                "generations": int(self.inputs["generations"].value),
            }
        except ValueError:
            self.status = "Confira os parametros: use apenas numeros validos."
            return False

        if not 2 <= new_config["puzzle_size"] <= 8:
            self.status = "Tamanho deve ficar entre 2 e 8."
            return False
        if new_config["randomize_moves"] < 0:
            self.status = "Embaralhar deve ser 0 ou maior."
            return False
        if new_config["population_size"] < 3:
            self.status = "Populacao deve ser pelo menos 3."
            return False
        if new_config["chromosome_length"] < 3:
            self.status = "Cromossomo deve ser pelo menos 3."
            return False
        if not 0 <= new_config["mutation_rate"] <= 1:
            self.status = "Mutacao deve ficar entre 0 e 1."
            return False
        if new_config["generations"] < 1:
            self.status = "Geracoes deve ser pelo menos 1."
            return False

        self.config = new_config
        return True

    def start_solver(self):
        if self.is_solving or self.is_animating:
            return

        previous_size = self.problem_game.size
        if not self.apply_config_from_inputs():
            return

        if previous_size != self.config["puzzle_size"]:
            self.solved_game = GameLogic(self.config["puzzle_size"])
            self.problem_game = GameLogic(self.config["puzzle_size"])
            self.problem_game.randomize(moves=self.config["randomize_moves"])
            self.tile_size = BOARD_PIXELS // self.config["puzzle_size"]

        self.is_solving = True
        self.solution_moves = []
        self.solution_fitness = None
        self.solution_solves = False
        self.visual_game = copy.deepcopy(self.problem_game)
        self.status = "Algoritmo genetico em execucao..."
        self.reset_progress()

        solver_problem = copy.deepcopy(self.problem_game)
        thread = threading.Thread(target=self.solve_worker, args=(solver_problem,), daemon=True)
        thread.start()

    def solve_worker(self, solver_problem):
        def on_progress(data):
            with self.progress_lock:
                self.progress = data

        ag = GeneticAlgorithm(
            population_size=self.config["population_size"],
            chromosome_length=self.config["chromosome_length"],
            mutation_rate=self.config["mutation_rate"],
            generations=self.config["generations"],
            problem=solver_problem,
        )

        best_solution = ag.run(progress_callback=on_progress, verbose=False)
        if best_solution is None:
            best_solution = []

        best_solution = [str(move) for move in best_solution]

        verification_game = copy.deepcopy(self.problem_game)
        verification_game.play_moves(best_solution)

        self.solution_moves = best_solution
        self.solution_fitness = getattr(ag, "best_overall_fitness", None)
        self.solution_solves = verification_game.is_solved()
        self.visual_game = copy.deepcopy(self.problem_game)

        if self.solution_solves:
            self.status = f"Resolvido com {len(best_solution)} movimentos."
        else:
            self.status = f"Melhor sequencia parcial: {len(best_solution)} movimentos."

        self.is_solving = False

    def start_animation(self):
        if self.is_solving or self.is_animating or not self.solution_moves:
            return

        self.visual_game = copy.deepcopy(self.problem_game)
        self.animation_queue = list(self.solution_moves)
        self.animation = None
        self.is_animating = True
        self.status = "Animando a melhor sequencia encontrada..."

    def update_animation(self, dt):
        if not self.is_animating:
            return

        if self.animation is None:
            self.start_next_move()

        if self.animation is None:
            self.finish_animation()
            return

        self.animation["elapsed"] += dt
        progress = self.animation["elapsed"] / ANIMATION_SECONDS
        if progress >= 1:
            self.animation = None
            if not self.animation_queue:
                self.finish_animation()

    def start_next_move(self):
        while self.animation_queue:
            move = self.animation_queue.pop(0)
            old_empty = tuple(self.visual_game.empty_pos)
            target = self.target_for_move(old_empty, move)

            if target is None:
                self.visual_game.move(move)
                continue

            target_row, target_col = target
            tile_value = int(self.visual_game.board[target_row, target_col])
            self.visual_game.move(move)

            self.animation = {
                "tile": tile_value,
                "from": target,
                "to": old_empty,
                "elapsed": 0.0,
            }
            return

        self.animation = None

    def finish_animation(self):
        self.is_animating = False
        if self.visual_game.is_solved():
            self.status = "Animacao concluida: puzzle resolvido."
        else:
            self.status = "Animacao concluida: melhor sequencia parcial aplicada."

    def target_for_move(self, empty_pos, move):
        row, col = empty_pos
        if move == "up" and row > 0:
            return row - 1, col
        if move == "down" and row < self.config["puzzle_size"] - 1:
            return row + 1, col
        if move == "left" and col > 0:
            return row, col - 1
        if move == "right" and col < self.config["puzzle_size"] - 1:
            return row, col + 1
        return None

    def update_buttons(self):
        has_solution = bool(self.solution_moves)
        for button in self.buttons:
            if button.label in ("Embaralhar", "Resolver", "Reset"):
                button.enabled = not self.is_solving and not self.is_animating
            elif button.label == "Animar":
                button.enabled = has_solution and not self.is_solving and not self.is_animating

    def draw(self):
        self.screen.fill(BG)
        self.draw_header()
        self.draw_board()
        self.draw_config_panel()
        self.draw_status_panel()

        for button in self.buttons:
            button.draw(self.screen, self.small_font)

        pygame.display.flip()

    def draw_header(self):
        title = self.big_font.render("Sliding Puzzle GA", True, TEXT)
        self.screen.blit(title, (32, 34))

        params = (
            f"{self.config['puzzle_size']}x{self.config['puzzle_size']} | "
            f"Pop {self.config['population_size']} | "
            f"Crom {self.config['chromosome_length']} | "
            f"Ger {self.config['generations']}"
        )
        params_surface = self.small_font.render(params, True, MUTED)
        self.screen.blit(params_surface, (32, 72))

    def draw_board(self):
        board_rect = pygame.Rect(
            self.board_origin[0] - 10,
            self.board_origin[1] - 10,
            BOARD_PIXELS + 20,
            BOARD_PIXELS + 20,
        )
        pygame.draw.rect(self.screen, PANEL, board_rect, border_radius=10)

        skip_cell = None
        if self.animation is not None:
            skip_cell = self.animation["to"]

        puzzle_size = self.config["puzzle_size"]
        for row in range(puzzle_size):
            for col in range(puzzle_size):
                if skip_cell == (row, col):
                    self.draw_empty_cell(row, col)
                    continue

                value = int(self.visual_game.board[row, col])
                if value == puzzle_size * puzzle_size:
                    self.draw_empty_cell(row, col)
                else:
                    self.draw_tile(value, row, col)

        if self.animation is not None:
            self.draw_moving_tile()

    def draw_empty_cell(self, row, col):
        rect = self.cell_rect(row, col)
        pygame.draw.rect(self.screen, EMPTY, rect, border_radius=8)

    def draw_tile(self, value, row, col, override_pos=None):
        rect = self.cell_rect(row, col)
        if override_pos is not None:
            rect = pygame.Rect(override_pos[0], override_pos[1], rect.width, rect.height)

        color = TILE if value % 2 else TILE_ALT
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, (190, 201, 196), rect, width=2, border_radius=8)

        number = self.font.render(str(value), True, TILE_TEXT)
        number_rect = number.get_rect(center=rect.center)
        self.screen.blit(number, number_rect)

    def draw_config_panel(self):
        panel_rect = pygame.Rect(690, 118, 452, 330)
        pygame.draw.rect(self.screen, PANEL, panel_rect, border_radius=10)

        title = self.font.render("Parametros", True, TEXT)
        self.screen.blit(title, (panel_rect.x + 20, panel_rect.y + 18))

        enabled = not self.is_solving and not self.is_animating
        for input_box in self.inputs.values():
            input_box.draw(self.screen, self.small_font, self.small_font, enabled=enabled)

    def draw_moving_tile(self):
        data = self.animation
        progress = min(1.0, data["elapsed"] / ANIMATION_SECONDS)
        progress = progress * progress * (3 - 2 * progress)

        start_x, start_y = self.cell_position(*data["from"])
        end_x, end_y = self.cell_position(*data["to"])
        x = start_x + (end_x - start_x) * progress
        y = start_y + (end_y - start_y) * progress

        self.draw_tile(data["tile"], data["to"][0], data["to"][1], override_pos=(x, y))

    def cell_position(self, row, col):
        x = self.board_origin[0] + col * self.tile_size + TILE_GAP // 2
        y = self.board_origin[1] + row * self.tile_size + TILE_GAP // 2
        return x, y

    def cell_rect(self, row, col):
        x, y = self.cell_position(row, col)
        return pygame.Rect(x, y, self.tile_size - TILE_GAP, self.tile_size - TILE_GAP)

    def draw_status_panel(self):
        panel_rect = pygame.Rect(32, WINDOW_HEIGHT - 96, WINDOW_WIDTH - 64, 64)
        pygame.draw.rect(self.screen, PANEL, panel_rect, border_radius=8)

        status_color = WARNING if self.is_solving else TEXT
        status_surface = self.small_font.render(self.status, True, status_color)
        self.screen.blit(status_surface, (panel_rect.x + 18, panel_rect.y + 12))

        with self.progress_lock:
            progress = dict(self.progress)

        fitness = self.solution_fitness
        if fitness is None:
            fitness = progress["best_overall_fitness"]

        info = (
            f"Geracao: {progress['generation']}/{self.config['generations'] - 1}   "
            f"Melhor fitness: {fitness}   "
            f"Movimentos: {len(self.solution_moves) or progress['best_moves_count']}"
        )
        info_surface = self.small_font.render(info, True, MUTED)
        self.screen.blit(info_surface, (panel_rect.x + 18, panel_rect.y + 36))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                input_enabled = not self.is_solving and not self.is_animating
                for input_box in self.inputs.values():
                    input_box.handle_event(event, enabled=input_enabled)
                for button in self.buttons:
                    button.handle_event(event)

            self.update_buttons()
            self.update_animation(dt)
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    app = SlidingPuzzleApp()
    app.run()
