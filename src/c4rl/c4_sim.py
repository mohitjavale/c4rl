import torch


class C4_Sim:
    def __init__(
        self,
        num_envs=1,
        connect_n=4,
        render_mode="text",
        check_win_mode="brute",
        device="cpu",
    ):
        self.board_l = 7
        self.board_h = 6
        self.num_envs = num_envs
        self.render_mode = render_mode
        self.device = device
        self.p1 = 1
        self.p2 = -1
        self.connect_n = connect_n

        self.boards = torch.zeros(
            (self.num_envs, self.board_h, self.board_l),
            dtype=torch.int,
            device=self.device,
        )
        self.current_turn = (
            torch.randint(
                low=0,
                high=2,
                size=(self.num_envs,),
                dtype=torch.int,
                device=self.device,
            )
            * 2
            - 1
        )
        self.column_highest = torch.zeros(
            (self.num_envs, self.board_l), dtype=torch.int, device=self.device
        )

        self.render_dict = {
            None: (self.render_init_none, self.render_none),
            "text": (self.render_init_text, self.render_text),
        }
        self.render_init, self.render = self.render_dict[self.render_mode]
        self.render_init()

        self.check_win_dict = {
            "brute": self.check_win_brute,
            "brute_lastmove": self.check_win_brute_lastmove,
            "conv2d": self.check_win_conv2d,
            "conv2d_lastmove": self.check_win_conv2d_lastmove,
        }
        self.check_win = self.check_win_dict[self.check_win_mode]

    def reset_indices(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)

        self.boards[env_ids, :, :] = 0
        self.column_highest[env_ids, :] = 0
        self.current_turn[env_ids] = (
            torch.randint_like(self.current_turn[env_ids], low=0, high=2) * 2 - 1
        )

    def step(self, actions):
        self.boards[
            torch.arange(self.num_envs), self.column_highest[:, actions], actions
        ] = self.current_turn
        self.column_highest[:, actions] += 1
        self.current_turn *= -1

    def check_win_brute(self):
        for n in range(self.num_envs):
            board = self.boards[self.num_envs]
            for i in range(self.board_h):
                for j in range(self.board_l):
                    pass

    def render_init_none(self):
        pass

    def render_none(self):
        pass

    def render_init_text(self):
        self.p1_symbol = "o"
        self.p2_symbol = "x"
        self.blank_symbol = " "

    def render_text(self, env_id=0):
        board = self.boards[env_id, :, :]
        # print(" " + " ".join(str(i) for i in range(self.board_l)) + " ")
        for i in reversed(range(self.board_h)):
            for j in range(self.board_l):
                print("|", end="")
                if board[i, j] == 0:
                    print(self.blank_symbol, end="")
                if board[i, j] == 1:
                    print(self.p1_symbol, end="")
                if board[i, j] == -1:
                    print(self.p2_symbol, end="")

                if j == self.board_l - 1:
                    print("|")
        # print("-" + "-".join("-" for i in range(self.board_l)) + "-")
        print(" " + " ".join(str(i) for i in range(self.board_l)) + " ")
        print("".join("_" for i in range(self.board_l * 2 + 1)))

    def get_valid_action_mask(self, actions):
        return torch.where(
            self.column_highest < self.board_h,
            torch.zeros_like(self.column_highest),
            torch.full_like(self.column_highest, fill_value=-torch.inf),
        )


if __name__ == "__main__":
    c4_sim = C4_Sim()
    c4_sim.render()
    for i in range(1000):
        action = int(input(f""))
        c4_sim.step(torch.tensor([action], dtype=torch.int))
        c4_sim.render()
