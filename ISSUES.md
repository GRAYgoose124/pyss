- Something about depth drawing is breaking on the board edges
  - Notably the knight cannot take on top edge and a pawn that reaches the top edge suicides. (Presumably this is 7 and it's a boundary issue.)
- Somehow depth list is not complete anymore?
  - i think what's happening is it's not checking what happens after a capture - before it just ignore captures, now they're being included somehow

- Files are inverted on the board - in piece_dict.yaml file 3==f5
  - i think ranks are inverted too along with the order of their notation