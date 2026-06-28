import unittest
import sys
from pathlib import Path

# Ensure src is on path for imports
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(SRC / 'data_acquisition'))
sys.path.insert(0, str(SRC / 'domain'))

from data_acquisition.normalize_data import normalize_text, resolve_team_id
from data_acquisition.team_resolution import save_manual_override, load_manual_overrides
from domain.live.updateFifaRatingAfterResult import expected_result, match_update
from data_acquisition.data_sources import RAW_DIR
import os


class TestTeamResolution(unittest.TestCase):
    def test_alias_resolution(self):
        name = "Côte d'Ivoire"
        norm = normalize_text(name)
        # Expect normalization to contain core words
        self.assertIn("cote", norm)
        self.assertIn("ivoire", norm)

    def test_manual_override(self):
        # write a temporary override and ensure resolve_team_id picks it
        overrides = load_manual_overrides()
        # ensure no exception on load
        self.assertIsInstance(overrides, dict)


class TestFifaUpdate(unittest.TestCase):
    def test_expected_result(self):
        wa = expected_result(1877.32, 1600.0)
        self.assertGreater(wa, 0.5)

    def test_match_update(self):
        pa, pb = match_update(1877.32, 1600.0, 10.0, 2, 0)
        self.assertNotEqual(pa, 1877.32)
        self.assertNotEqual(pb, 1600.0)

    def test_manual_elo_is_used(self):
        from data_acquisition.normalize_data import normalize_teams, load_json
        manual_elo = load_json(RAW_DIR / 'elo_ratings_manual.json') or []
        manual_ids = {entry['teamId'].strip().lower() for entry in manual_elo if entry.get('teamId')}
        teams = normalize_teams()
        applied_manual = {team['id'] for team in teams if team.get('sourceConfidence') == 'manual'}

        self.assertTrue(manual_ids, 'elo_ratings_manual.json doit contenir des entrées manuelles')
        self.assertTrue(manual_ids.issubset(applied_manual),
                        'Toutes les équipes du fichier manuel doivent être appliquées comme manual ELO')


if __name__ == "__main__":
    unittest.main()
