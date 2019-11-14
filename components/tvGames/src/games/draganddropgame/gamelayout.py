import math
import operator
from collections import defaultdict, OrderedDict


class GameLayout:
    def __init__(self, scene, pieces, minimum_piece_width, minimum_piece_height, piece_spacing=5, max_pieces_per_row = 5, margins=None):
        self.scene = scene
        self.pieces = pieces
        self.__minimum_piece_width = minimum_piece_width
        self.__minimum_piece_height = minimum_piece_height
        self.piece_spacing = piece_spacing
        self.margins = [20,5,20,5]
        self.max_pieces_per_row = max_pieces_per_row

    @property
    def scene(self):
        return self.__scene

    @scene.setter
    def scene(self, value):
        self.__scene = value

    @property
    def pieces(self):
        return self.__pieces

    @pieces.setter
    def pieces(self, value):
        self.__pieces = value

    @property
    def piece_spacing(self):
        return self.__piece_spacing

    @piece_spacing.setter
    def piece_spacing(self, value):
        self.__piece_spacing = value

    @property
    def max_pieces_per_row(self):
        return self.__max_pieces_per_row

    @max_pieces_per_row.setter
    def max_pieces_per_row(self, value):
        self.__max_pieces_per_row = value

    @property
    def margin_left(self):
        return self.margins[3]

    @margin_left.setter
    def margin_left(self, value):
        self.margins[3] = value

    @property
    def margin_right(self):
        return self.margins[1]

    @margin_right.setter
    def margin_right(self, value):
        self.margins[1] = value

    @property
    def margin_top(self):
        return self.margins[0]

    @margin_top.setter
    def margin_top(self, value):
        self.margins[0] = value

    @property
    def margin_bottom(self):
        return self.margins[2]

    @margin_bottom.setter
    def margin_bottom(self, value):
        self.margins[2] = value

    @property
    def scene_rect(self):
        if len(self.scene.views()) > 0:
            game_space_rect = self.scene.views()[0].sceneRect().toRect()
        else:
            game_space_rect = self.scene.boundingRect().toRect()
        return game_space_rect

    @scene_rect.setter
    def scene_rect(self, value):
        assert value, "Scene rect can't be set from the layout!"

    @property
    def scene_width(self):
        return self.scene_rect.width()

    @scene_width.setter
    def scene_width(self, value):
        assert value, "Scene width can't be set from the layout!"

    @property
    def scene_height(self):
        return self.scene_rect.height()

    @scene_height.setter
    def scene_height(self, value):
        assert value, "Scene height can't be set from the layout!"

    def get_initial_piece_positions(self):
        initial_positions = OrderedDict()
        last_occupied_x = self.margin_left
        last_occupied_y = self.margin_top
        last_occupied_y += self.piece_spacing
        # TODO: move to propertie
        rows = int(math.ceil(len(self.pieces) / float(self.max_pieces_per_row)))
        columns = len(self.pieces) if len(self.pieces) < self.max_pieces_per_row else self.max_pieces_per_row
        if len(self.scene.views()) > 0:
            max_piece_size = self.calculate_max_piece_size()
            for l_index, piece in enumerate(sorted(self.pieces, key = operator.attrgetter('index'))):
                current_column = l_index % self.max_pieces_per_row
                current_row = int(math.ceil(l_index / float(self.max_pieces_per_row)))
                new_x_for_piece = self.x_for_piece_in_column(current_column, columns, max_piece_size)
                new_y_for_piece = self.y_for_piece_in_row(current_row, rows, max_piece_size)
                last_occupied_x += self.piece_spacing
                initial_positions[piece] = (last_occupied_x, last_occupied_y)
                last_occupied_x += max_piece_size
                last_occupied_x += self.piece_spacing

    def x_for_piece_in_column(self, column, total_columns, piece_size):
        column_width = self.scene_width / total_columns
        assert piece_size[0] < column_width, "Piece width can't me widther than the column width"
        column_initial_x = column_width * column
        piece_offset = (column_width - piece_size[0]) / 2
        return column_initial_x + piece_offset

    def y_for_piece_row(self):
        pass

    def y_for_row(self):
        pass

    def calculate_max_piece_size(self):
        assert self.check_pieces_resolution(), "All pieces must have the same ratio"
        max_width = self.calculate_max_piece_width()
        max_height = self.calculate_max_piece_height()

        # Algorithm by Pilar Bachiller
        width_ratio = max_width / self.pieces[-1].width
        height_ratio = max_height / self.pieces[-1].height

        ratio = min(width_ratio, height_ratio )
        new_width = int(self.pieces[-1].width * ratio)
        new_height = int(self.pieces[-1].height * ratio)
        return (new_width, new_height)




    def calculate_max_piece_height(self):
        assert len(self.pieces) > 0, "Can't calculate max piece size for 0 pieces"
        rows = math.ceil(len(self.pieces) / float(self.max_pieces_per_row))
        # We need to calculate the height thinking that the bottom half of the screen is for destinations
        spacing_needed_space = (rows*2 + 1) * self.piece_spacing
        max_piece_height = (self.scene_height / rows / 2) - spacing_needed_space
        return max_piece_height



    def calculate_max_piece_width(self):
        assert len(self.pieces)>0, "Can't calculate max piece size for 0 pieces"

        if len(self.scene.views()) > 0:
            game_space_rect = self.scene.views()[0].sceneRect().toRect()
        else:
            game_space_rect = self.scene.boundingRect().toRect()
        spacing_needed_space = (len(self.pieces)+1)*self.piece_spacing
        max_piece_width = (game_space_rect.width()/len(self.pieces)) - spacing_needed_space
        return max_piece_width


    def check_pieces_resolution(self):
        ratios = defaultdict(list)
        for piece in self.pieces:
            ratios[piece.width/float(piece.height)].append(piece)
        if len(ratios) > 1:
            # get the ratio that represent less pieces
            print("Problem: the images for the pieces must have the same ratio of width x height")
            min_value = min(map(len, ratios.values()))
            min_list = [value for key, value in ratios.items() if value == min_value]
            print("There's %d different ratios. These are the pieces for each ratio:")
            for ratio, pieces in ratios:
                print("\nFor the ratio %f these pieces:"%ratio)
                for piece in pieces:
                    print("\n\nPiece %s"%piece.path)
            return False
        return True



