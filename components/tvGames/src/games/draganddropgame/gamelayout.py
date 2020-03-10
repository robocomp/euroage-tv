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
        self.initial_positions = OrderedDict()
        self.destination_positions = OrderedDict()
        self.piece_size = None
        self.columns = None
        self.__get_initial_piece_positions()


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
            # take de rect of the view
            view = self.scene.views()[0]
            view_rect = view.rect()
            game_space_rect = view.mapToScene(view_rect).boundingRect().toRect()
        else:
            game_space_rect = self.scene.sceneRect().toRect()
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

    @property
    def initial_positions(self):
        return self.__initial_positions

    @initial_positions.setter
    def initial_positions(self, value):
        assert isinstance(value, dict), "Initial positions must be a dict with the pieces as key"
        self.__initial_positions = value


    @property
    def destination_positions(self):
        return self.__destination_positions

    @destination_positions.setter
    def destination_positions(self, value):
        assert isinstance(value, dict), "Initial destinations must be a dict with the pieces as key"
        self.__destination_positions = value

    @property
    def piece_size(self):
        return self.__piece_size

    @piece_size.setter
    def piece_size(self, value):
        assert value is None or isinstance(value, (tuple,list)), "Piece size must be a tuple, list or None"
        assert value is None or len(value) == 2, "Piece must be a len of exactly 2"
        self.__piece_size = value


    def __get_initial_piece_positions(self):
        # TODO: move to properties
        self.rows = int(math.ceil(len(self.pieces) / float(self.max_pieces_per_row)))
        self.columns = len(self.pieces) if len(self.pieces) < self.max_pieces_per_row else self.max_pieces_per_row
        self.piece_size = self.calculate_max_piece_size()

        for l_index, piece in enumerate(sorted(self.pieces, key=operator.attrgetter('index'))):
            current_column = l_index % self.max_pieces_per_row
            current_row = int(l_index / float(self.max_pieces_per_row))
            new_x_for_piece = self.x_for_piece_in_column(current_column)
            new_y_for_piece = self.y_for_piece_in_row(current_row, False)
            new_y_for_piece_destination = self.y_for_piece_in_row(current_row, True)
            self.initial_positions[piece] = (new_x_for_piece, new_y_for_piece)
            self.destination_positions[piece] = (new_x_for_piece, new_y_for_piece_destination)


    def x_for_piece_in_column(self, column):
        column_width = self.scene_width / self.columns
        assert self.piece_size[0] <= column_width, "Piece width can't be wider than the column width"
        column_initial_x = column_width * column
        piece_offset = (column_width - self.piece_size[0]) / 2
        return column_initial_x + piece_offset

    def y_for_piece_in_row(self, row, destination=False):
        row_height = (self.scene_height / self.rows)/2
        assert self.piece_size[1] <= row_height, "Piece width can't be higher than the column width"
        if not destination:
            row_initial_y = row_height * row
        else:
            row_initial_y = self.scene_height/2 + (row_height * row)
        piece_offset = (row_height - self.piece_size[1]) / 2
        return row_initial_y + piece_offset



    def calculate_max_piece_size(self):
        assert self.check_pieces_resolution(), "All pieces must have the same ratio"
        max_width = self.calculate_max_piece_width()
        max_height = self.calculate_max_piece_height()
        assert max_width>0 and max_height>0, "Unable to show those pieces with so large spacing"

        # Algorithm by Pilar Bachiller
        width_ratio = max_width / self.pieces[-1].width
        height_ratio = max_height / self.pieces[-1].height

        ratio = min(width_ratio, height_ratio )
        new_width = int(self.pieces[-1].width * ratio)-(self.piece_spacing*2)
        new_height = int(self.pieces[-1].height * ratio)-(self.piece_spacing*2)
        return (new_width, new_height)




    def calculate_max_piece_height(self):
        assert len(self.pieces) > 0, "Can't calculate max piece size for 0 pieces"

        # We need to calculate the height thinking that the bottom half of the screen is for destinations
        spacing_needed_space = self.piece_spacing*2
        max_piece_height = (self.scene_height / (self.rows*2)) - spacing_needed_space
        return max_piece_height


    def calculate_max_piece_width(self):
        assert len(self.pieces)>0, "Can't calculate max piece size for 0 pieces"

        spacing_needed_space = self.piece_spacing*2
        max_piece_width = (self.scene_width/self.columns) - spacing_needed_space
        return max_piece_width


    def check_pieces_resolution(self):
        ratios = defaultdict(list)
        for piece in self.pieces:
            # Truncated float for the ratio
            ratio = float(int((piece.width/float(piece.height))*100))/100.
            ratios[ratio].append(piece)
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



