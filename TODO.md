- What if instead of discarding depth lists on move, we pruned the depth lists at the two changed positions and updated them for all existing depth lists? Theoretically after a few turns of caching this would lead to pretty performant gameplay even with `depth >= 5`.

IMPORTANT!!!
- pawn promotion
- castling blocked by enemy line of sight
- check/checkmate including line of sight checks and king entering checks

FEATURES
- save / load game
- network
- simple bots
- themes

REFACTORING
- depth_bins and associated content can probably be isolated
- board and app probably need to be be separated more, perhaps a game wrapper around board intermediate?