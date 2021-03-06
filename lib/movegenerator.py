# DESCRIPTION: The part of the chess engine that generates the legal moves.

# 50726f6772616d6d696e6720697320627265616b696e67206f66206f6e652062696720696d706f
# 737369626c65207461736b20696e746f207365766572616c207665727920736d616c6c20706f73
# 7369626c65207461736b732e

# NOTE:
# ================
# This file is currently a work in progress. The original chessboard.py file has
# become overly bloated and is detrimental to the moral of the project. This new
# script is aimed at taking only the methods that pertain to the move gen, while
# separating the other components into their own scrips

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~MAIN~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from copy import deepcopy
from lib import core, chessboard, vectors, pieces

  #####  ####### ######  #######
 #     # #     # #     # #
 #       #     # #     # #
 #       #     # ######  #####
 #       #     # #   #   #
 #     # #     # #    #  #
  #####  ####### #     # #######


class _CoreMoveGenerator:
    """Contains the core methods that are used in the move generation."""

    def __init__(self, currentboardstate):
        self.board = deepcopy(currentboardstate)
        return

    def _positiononboard(self, positon):
        """Checks that the position is on the board."""
        return all([0 <= x <= 7 for x in core.Position(positon).coordinate])

    @staticmethod
    def _piecesareonsameside(*pieces):
        """Checks to see if the passed pieces are all on the same side."""
        try:
            side = None
            for piece in pieces:
                if side == None:
                    side = piece.colour  # Use the first piece's colour as comparison.
                    continue
                elif piece.colour != side:  # If pieces are on different sides.
                    return False
                else:
                    continue
            return True  # If it makes it all the way through the loop, then good.
        except AttributeError:
            raise TypeError("You must pass pieces from the pieces module.")

    def _piecesbetween(self, start, end, inclusive=False):
        """Find the pieces between the start and end positions, not inclusive."""
        # Start by defining direction of unitvector and starting position.
        startvec = core.Position(start).vector
        endvec = core.Position(end).vector
        unitrelvec = (endvec - startvec).unitvector()
        if inclusive:
            currentposvec = startvec
            endvec += unitrelvec  # HACK: Shift up end point if inclusive.
        else:
            currentposvec = startvec + unitrelvec

        # Iterate over the squares between start and end.
        pieceslist = list()
        while currentposvec != endvec:
            if self.board[currentposvec] != None:
                pieceslist.append(self.board[currentposvec])
            currentposvec += unitrelvec
        return pieceslist

    def _movesforpiece(self, piece, pos, defendingmoves=False):
        """Get the moves for the piece at position 'pos'. The optional parameter
        'defendingmoves' adds the move even if it captures its "own piece" in
        order to look at exchanges in the brains of the engine.
        """
        allowedmoves = list()
        for unitvector in piece.moveunitvectors:
            movetopos = core.Position(pos).vector + unitvector

            while self._positiononboard(movetopos):
                endsquare = self.board[movetopos]
                if endsquare != None:
                    if self._piecesareonsameside(piece, endsquare):
                        if defendingmoves: allowedmoves.append(movetopos)
                        break
                    elif piece.type == pieces.PawnPiece:  # Pawns can't capture forward
                        break
                    else:  # If opposition piece.
                        allowedmoves.append(movetopos)
                        break  # Can't go further then capture.
                else:
                    allowedmoves.append(movetopos)

                if piece.crawler: break
                else: movetopos += unitvector

            continue  # Just to show where while loop ends.
        return allowedmoves

    def basicmoves(self, colour, defendingmoves=False):
        """Get the most basic moves, such as simple captures and movement."""
        # Sanity checks.
        if colour not in core.COLOURS:
            raise core.ColourError()

        # Now apply that method to each piece on the board.
        movelist = list()
        for index, square in enumerate(self.board):
            if square == None:
                continue
            elif square.colour != colour:
                continue  # Skip over piece if it is different colour.
            startpos = index
            endposlist = map(
                lambda x: core.Position(x).index,
                self._movesforpiece(square, startpos, defendingmoves)
            )
            movepairs = map(lambda x: (startpos, x), endposlist)
            movelist.append(movepairs)
        return core.flattenlist(movelist)

    def kingincheck(self, kingcolour):
        """Determine if the king of a certain colour is in check."""
        # Find the king first.
        try:
            oppositioncolour = core.oppositecolour(kingcolour)
            kingpos = self.board.findpiece(pieces.KingPiece, kingcolour.lower())[0]
        except IndexError:
            raise RuntimeError("We can't find the %s king!" % kingcolour)

        # Then look for any square that is attacking.
        for index, square in enumerate(self.board):
            if square == None:
                continue
            elif square.colour == kingcolour:
                continue  # Skip over piece if it is same colour.
            endposlist = core.convertlist(
                self._movesforpiece(square, index), toindex=True)

            if kingpos in endposlist: return True
            else: continue
        return False

    def pawnonendline(self, colour):
        """Determine if a pawn has reached the backline."""
        if colour.lower() == 'white':
            backline = range(56, 64)
        elif colour.lower() == 'black':
            backline = range(0, 8)
        else:
            raise core.ColourError()

        for ii in backline:
            square = self.board[ii]
            if square == None:
                continue
            elif square.type == pieces.PawnPiece and square.colour == colour:
                return True  # NOTE: There should only ever be one pawn on backline.
        return False




 #     # ####### #     # #######
 ##   ## #     # #     # #
 # # # # #     # #     # #
 #  #  # #     # #     # #####
 #     # #     #  #   #  #
 #     # #     #   # #   #
 #     # #######    #    #######

  #####  ####### #     # ####### ######     #    ####### ### ####### #     #
 #     # #       ##    # #       #     #   # #      #     #  #     # ##    #
 #       #       # #   # #       #     #  #   #     #     #  #     # # #   #
 #  #### #####   #  #  # #####   ######  #     #    #     #  #     # #  #  #
 #     # #       #   # # #       #   #   #######    #     #  #     # #   # #
 #     # #       #    ## #       #    #  #     #    #     #  #     # #    ##
  #####  ####### #     # ####### #     # #     #    #    ### ####### #     #


class MoveGenerator(_CoreMoveGenerator):
    """Generates the possible moves based off the rules of chess."""

    def illegalmove(self, movepair, kingcolour):
        """Checks to see if the supplied move if illegal."""
        # Make the move and see if the king is in check, then restore board state.
        if isinstance(movepair[0],tuple) and isinstance(movepair[1],tuple):  # NOTE: This is a castling move.
            for move in movepair: self.board.move(move[0], move[1])
            result = self.kingincheck(kingcolour)
            for move in movepair: self.board.move(move[1], move[0])
        else:
            self.board.move(movepair[0], movepair[1])
            result = self.kingincheck(kingcolour)
            self.board.move(movepair[1], movepair[0])
        return result

    def onlylegalmoves(self, colour, movepairlist):
        """Filter a list, keeping only legal moves."""
        oppositioncolour = core.oppositecolour(colour.lower())

        ii = 0
        while ii < len(movepairlist):
            if self.illegalmove(movepairlist[ii], colour):
                del movepairlist[ii]
            else:
                ii += 1
        return movepairlist

    def pawnpushmoves(self, colour):
        """Gets the moves allowed for pawn pushing."""
        # Determine where the frontline is.
        if colour == 'white':
            frontline = range(8, 16); push = 16
        elif colour == 'black':
            frontline = range(48, 56); push = -16
        else:
            raise core.ColourError()

        # Add the push moves if required.
        movelist = list()
        for ii in frontline:  # Iterate over frontline.
            square = self.board[ii]
            if square == None:
                continue
            elif square.type == pieces.PawnPiece:
                # Make sure only pawn is on frontline and up to push.
                if len(self._piecesbetween(ii, ii + push, inclusive=True)) != 1:
                    continue
                else:
                    movelist.append((ii, ii + push))
            else:
                continue
        return movelist

    def pawncapturemoves(self, colour):
        """Finds where pawns are able to capture normally."""
        # ---------------------------------------------------------------------
        def capturemoveat(endvec):
            """Determines if there is a capture move at endvec."""
            try:
                square = self.board[endvec]
                if square == None:
                    return False
                elif square.colour != colour:
                    return True
                else:  # Can't capture same colour.
                    return False
            except IndexError:
                return False  # Position isn't on the board.
            return -1
        # ---------------------------------------------------------------------

        if colour == 'white':
            captureleft = core.Vector(1, -1)
            captureright = core.Vector(1, 1)
        elif colour == 'black':
            captureleft = core.Vector(-1, -1)
            captureright = core.Vector(-1, 1)
        else:
            raise core.ColourError()

        pawnsonboard = self.board.findpiece(pieces.PawnPiece, colour)
        capturelist = list()
        for pawnindex in pawnsonboard:
            pawnvec = core.Position(pawnindex).vector
            vecleft = pawnvec + captureleft
            vecright = pawnvec + captureright

            if capturemoveat(vecleft):
                capturelist.append(
                    (pawnindex, core.Position(vecleft).index)
                )
            if capturemoveat(vecright):
                capturelist.append(
                    (pawnindex, core.Position(vecright).index)
                )
        return capturelist

    def castlemoves(self, colour):
        """Get the caslting moves."""
        # ---------------------------------------------------------------------
        def isking(position):
            """Determine if the piece at position is a king."""
            try:
                result = (self.board[position].type == pieces.KingPiece)
            except AttributeError:
                result = False  # If position is empty, return false.
            return result

        def isrook(position):
            """Determine if the piece at position is a rook."""
            try:
                result = (self.board[position].type == pieces.RookPiece)
            except AttributeError:
                result = False  # If position is empty, return false.
            return result
        # ---------------------------------------------------------------------
        castlemoves = list(); castleleft = True; castleright = True

        # See if allowed to castle at all.
        if not self.board.cancastleleft: castleleft = False
        if not self.board.cancastleright: castleright = False
        if not castleleft and not castleright:
            return castlemoves  # Early exit to reduce overhead.

        # Determine where the king and rook are.
        if colour == 'white': kingpos, rookleftpos, rookrightpos = 4, 0, 7
        elif colour == 'black': kingpos, rookleftpos, rookrightpos = 60, 56, 63
        else:
            raise core.ColourError('%r is neither white nor black' % colour)

        # See if king or rook out of place.
        if not isking(kingpos):
            self.board.cancastleleft = False; self.board.cancastleright = False
            castleleft = False; castleright = False
        else:
            if not isrook(rookleftpos):
                castleleft = False; self.board.cancastleleft = False
            if not isrook(rookrightpos):
                castleright = False; self.board.cancastleright = False

        # Confirm that the king isn't already in check.
        if self.kingincheck(colour):
            castleleft = False; castleright = False

        # See if there are pieces between the rook and king.
        if self._piecesbetween(rookleftpos, kingpos):
            castleleft = False
        if self._piecesbetween(rookrightpos, kingpos):
            castleright = False

        # See if the castle start/end/during puts the king in check.
        castleleftsteps = range(kingpos-1, kingpos - 3, -1)
        if not castleleft:
            pass
        else:
            for step in castleleftsteps:
                if self.illegalmove((kingpos, step), colour):
                    castleleft = False
                else:
                    continue
        castlerightsteps = range(kingpos+1, kingpos + 3)
        if not castleright:
            pass
        else:
            for step in castlerightsteps:
                if self.illegalmove((kingpos, step), colour):
                    castleright = False
                else:
                    continue

        # Then see what castle moves can be added and add them.
        if castleleft:
            castlemoves.append(
                ((kingpos, kingpos-2), (rookleftpos, rookleftpos+3))
            )
        if castleright:
            castlemoves.append(
                ((kingpos, kingpos+2), (rookleftpos, rookleftpos-2))
            )
        return castlemoves


    # TODO: Fix this up now the chessboard doesn't store the information.
    def enpassantmoves(self, colour):
        """Get the en passant moves."""
        def addtomovesifcanenpassant(pos, thelist):
            """Determines if the piece at pos can en passant."""
            if colour == 'white': capturerank = 5
            else: capturerank = 2

            square = self.board[pos]
            if square == None:
                return thelist
            elif square.type == pieces.PawnPiece:
                if square.colour == colour:
                    startindex = core.convert(pos, toindex=True)
                    endindex = core.convert((capturerank, file_), toindex=True)
                    thelist.append((startindex, endindex))
            return thelist

        # Determine if there are any en passant moves present.
        if self.board.playercolour == colour:
            enpassant = self.board.enpassantforplayer
        else:
            enpassant = self.board.enpassantforcomputer

        if enpassant == None: return list()
        else: file_ = enpassant

        # See if there are pawns of correct colour on either side.
        if colour == 'white': rank_ = 4
        else: rank_ = 3
        enpassantleft = (rank_, file_-1); enpassantright = (rank_, file_+1)
        movelist = list()
        if self._positiononboard(enpassantleft):
            movelist = addtomovesifcanenpassant(enpassantleft, movelist)
        if self._positiononboard(enpassantright):
            movelist = addtomovesifcanenpassant(enpassantright, movelist)
        return movelist

    def generatemovelist(self, colour):
        """Generate all of the possible moves for colour."""
        basicmoves = self.basicmoves(colour)
        pawnpushmoves = self.pawnpushmoves(colour)
        pawncapturemoves = self.pawncapturemoves(colour)
        castlemoves = self.castlemoves(colour)
        enpassantmoves = self.enpassantmoves(colour)
        allmoves = core.combinelists(
            basicmoves,
            pawnpushmoves,
            pawncapturemoves,
            castlemoves,
            enpassantmoves
        )

        allmoves = self.onlylegalmoves(colour, allmoves)
        return allmoves
