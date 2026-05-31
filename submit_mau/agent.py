from collections import deque


class Agent:
    """Standalone safe rule-based sample agent for Bomberland submission."""

    ACTION_DELTAS = {
        0: (0, 0),
        1: (-1, 0),
        2: (1, 0),
        3: (0, -1),
        4: (0, 1),
    }

    GRASS = 0
    WALL = 1
    BOX = 2
    ITEM_RADIUS = 3
    ITEM_CAPACITY = 4

    MAX_BOMB_RADIUS = 5

    def __init__(self, agent_id: int):
        self.agent_id = int(agent_id)

    def act(self, obs: dict) -> int:
        try:
            return int(self._act(obs))
        except Exception:
            return 0

    def _act(self, obs: dict) -> int:
        grid = obs["map"]
        players = obs["players"]
        bombs = obs["bombs"]

        if self.agent_id >= len(players):
            return 0

        me = players[self.agent_id]
        if int(me[2]) != 1:
            return 0

        my_pos = (int(me[0]), int(me[1]))
        bombs_left = int(me[3])
        my_radius = 1 + int(me[4])

        bomb_positions = self._bomb_positions(bombs)
        danger_tiles, urgent_tiles, min_timer = self._danger_maps(grid, players, bombs)

        if my_pos in urgent_tiles or min_timer.get(my_pos, 99) <= 3:
            escape = self._move_to_safe(grid, my_pos, bomb_positions, danger_tiles, urgent_tiles)
            if escape is not None:
                return escape

        item_targets = self._item_targets(grid, danger_tiles)
        item_move = self._move_to_targets(grid, my_pos, item_targets, bomb_positions, danger_tiles)
        if item_move is not None:
            return item_move

        enemies = self._alive_enemy_positions(players)
        if bombs_left > 0 and my_pos not in bomb_positions:
            boxes_hit = self._count_boxes_in_blast(grid, my_pos, my_radius)
            hits_enemy = self._can_hit_enemy(grid, my_pos, enemies, my_radius)
            if (boxes_hit > 0 or hits_enemy) and self._can_escape_after_bomb(
                grid, players, bombs, my_pos, my_radius
            ):
                return 5

        bomb_spots = self._box_bomb_spots(grid, bomb_positions, danger_tiles)
        farm_move = self._move_to_targets(grid, my_pos, bomb_spots, bomb_positions, danger_tiles)
        if farm_move is not None:
            return farm_move

        enemy_move = self._move_to_targets(grid, my_pos, set(enemies), bomb_positions, danger_tiles)
        if enemy_move is not None:
            return enemy_move

        return self._best_safe_action(grid, my_pos, bomb_positions, danger_tiles)

    def _height_width(self, grid):
        return int(grid.shape[0]), int(grid.shape[1])

    def _next_pos(self, pos, action):
        dx, dy = self.ACTION_DELTAS[action]
        return pos[0] + dx, pos[1] + dy

    def _in_bounds(self, grid, pos):
        h, w = self._height_width(grid)
        return 0 <= pos[0] < h and 0 <= pos[1] < w

    def _passable(self, grid, pos):
        if not self._in_bounds(grid, pos):
            return False
        return int(grid[pos[0], pos[1]]) in (self.GRASS, self.ITEM_RADIUS, self.ITEM_CAPACITY)

    def _bomb_positions(self, bombs):
        positions = set()
        for bomb in bombs:
            positions.add((int(bomb[0]), int(bomb[1])))
        return positions

    def _alive_enemy_positions(self, players):
        enemies = []
        for idx, player in enumerate(players):
            if idx != self.agent_id and int(player[2]) == 1:
                enemies.append((int(player[0]), int(player[1])))
        return enemies

    def _bomb_radius(self, players, owner_id):
        if 0 <= owner_id < len(players):
            return min(self.MAX_BOMB_RADIUS, 1 + int(players[owner_id][4]))
        return 1

    def _blast_tiles(self, grid, pos, radius):
        tiles = {pos}
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for step in range(1, int(radius) + 1):
                nxt = (pos[0] + dx * step, pos[1] + dy * step)
                if not self._in_bounds(grid, nxt):
                    break
                cell = int(grid[nxt[0], nxt[1]])
                if cell == self.WALL:
                    break
                tiles.add(nxt)
                if cell == self.BOX:
                    break
        return tiles

    def _danger_maps(self, grid, players, bombs):
        danger = set()
        urgent = set()
        min_timer = {}
        for bomb in bombs:
            bx, by = int(bomb[0]), int(bomb[1])
            timer = int(bomb[2]) if len(bomb) > 2 else 7
            owner_id = int(bomb[3]) if len(bomb) > 3 else -1
            radius = self._bomb_radius(players, owner_id)
            tiles = self._blast_tiles(grid, (bx, by), radius)
            danger.update(tiles)
            if timer <= 2:
                urgent.update(tiles)
            for tile in tiles:
                min_timer[tile] = min(timer, min_timer.get(tile, timer))
        return danger, urgent, min_timer

    def _valid_move_actions(self, grid, pos, bomb_positions):
        actions = []
        for action in (0, 1, 2, 3, 4):
            nxt = self._next_pos(pos, action)
            if action == 0:
                actions.append(action)
            elif self._passable(grid, nxt) and nxt not in bomb_positions:
                actions.append(action)
        return actions

    def _move_to_safe(self, grid, start, bomb_positions, danger, urgent):
        safe_tiles = {
            (x, y)
            for x in range(self._height_width(grid)[0])
            for y in range(self._height_width(grid)[1])
            if self._passable(grid, (x, y)) and (x, y) not in danger and (x, y) not in bomb_positions
        }
        return self._move_to_targets(grid, start, safe_tiles, bomb_positions, urgent, allow_start=False)

    def _move_to_targets(self, grid, start, targets, bomb_positions, blocked_danger, allow_start=True):
        if not targets:
            return None

        queue = deque([(start, None)])
        seen = {start}

        while queue:
            pos, first_action = queue.popleft()
            if pos in targets and (allow_start or first_action is not None):
                return first_action if first_action is not None else 0

            for action in (1, 2, 3, 4):
                nxt = self._next_pos(pos, action)
                if nxt in seen:
                    continue
                if not self._passable(grid, nxt):
                    continue
                if nxt in bomb_positions:
                    continue
                if nxt in blocked_danger and nxt not in targets:
                    continue
                seen.add(nxt)
                queue.append((nxt, action if first_action is None else first_action))

        return None

    def _item_targets(self, grid, danger):
        targets = set()
        h, w = self._height_width(grid)
        for x in range(h):
            for y in range(w):
                if int(grid[x, y]) in (self.ITEM_RADIUS, self.ITEM_CAPACITY) and (x, y) not in danger:
                    targets.add((x, y))
        return targets

    def _count_boxes_in_blast(self, grid, pos, radius):
        return sum(1 for tile in self._blast_tiles(grid, pos, radius) if int(grid[tile[0], tile[1]]) == self.BOX)

    def _can_hit_enemy(self, grid, pos, enemies, radius):
        blast = self._blast_tiles(grid, pos, radius)
        return any(enemy in blast for enemy in enemies)

    def _can_escape_after_bomb(self, grid, players, bombs, pos, radius):
        bomb_positions = self._bomb_positions(bombs) | {pos}
        danger, urgent, _ = self._danger_maps(grid, players, bombs)
        danger = danger | self._blast_tiles(grid, pos, radius)
        urgent = urgent | self._blast_tiles(grid, pos, radius)
        return self._move_to_safe(grid, pos, bomb_positions, danger, urgent) is not None

    def _box_bomb_spots(self, grid, bomb_positions, danger):
        spots = set()
        h, w = self._height_width(grid)
        for x in range(h):
            for y in range(w):
                if int(grid[x, y]) != self.BOX:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    spot = (x + dx, y + dy)
                    if self._passable(grid, spot) and spot not in bomb_positions and spot not in danger:
                        spots.add(spot)
        return spots

    def _open_neighbors(self, grid, pos, bomb_positions, danger):
        count = 0
        for action in (1, 2, 3, 4):
            nxt = self._next_pos(pos, action)
            if self._passable(grid, nxt) and nxt not in bomb_positions and nxt not in danger:
                count += 1
        return count

    def _best_safe_action(self, grid, pos, bomb_positions, danger):
        best_action = 0
        best_score = -10**9
        for action in self._valid_move_actions(grid, pos, bomb_positions):
            nxt = self._next_pos(pos, action)
            score = 0
            if nxt not in danger:
                score += 100
            else:
                score -= 100
            score += 5 * self._open_neighbors(grid, nxt, bomb_positions, danger)
            if action == 0:
                score -= 2
            if score > best_score:
                best_score = score
                best_action = action
        return best_action

