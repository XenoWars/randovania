import dataclasses
import uuid

import pytest

from PySide2.QtWidgets import *

from randovania.games.game import RandovaniaGame
from randovania.gui.preset_settings.generation_tab import PresetGeneration
from randovania.interface_common.preset_editor import PresetEditor
from randovania.games.cave_story.gui.preset_settings.cs_generation_tab import PresetCSGeneration
from randovania.games.prime1.gui.preset_settings.prime_generation_tab import PresetPrimeGeneration

@pytest.mark.parametrize("game_data", [
    (RandovaniaGame.METROID_PRIME, True, True, PresetPrimeGeneration),
    (RandovaniaGame.METROID_PRIME_ECHOES, False, True, PresetGeneration),
    (RandovaniaGame.CAVE_STORY, True, False, PresetCSGeneration)
])
def test_on_preset_changed(skip_qtbot, preset_manager, game_data):
    # Setup
    game, has_specific_settings, has_min_logic, tab = game_data

    base = preset_manager.default_preset_for_game(game).get_preset()
    preset = dataclasses.replace(base,
                                 uuid=uuid.UUID('b41fde84-1f57-4b79-8cd6-3e5a78077fa6'),
                                 base_preset_uuid=base.uuid)
    editor = PresetEditor(preset)
    window: PresetGeneration = tab(editor)
    parent = QGroupBox()
    window.setParent(parent)

    # Run
    window.on_preset_changed(editor.create_custom_preset_with())

    # Assert
    assert window.trick_level_minimal_logic_check.isVisibleTo(parent) == has_min_logic
    assert window.game_specific_group.isVisibleTo(parent) == has_specific_settings
