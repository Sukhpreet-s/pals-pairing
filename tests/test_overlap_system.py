import unittest

from overlap_system.normalizers import (
    normalize_bool,
    normalize_energy_level,
    normalize_pipe_list,
    normalize_user_profile,
)
from overlap_system.pipeline import score_pair
from overlap_system.scorers.games import score_games
from overlap_system.scorers.genres import score_genres


class NormalizerTests(unittest.TestCase):
    def test_normalize_pipe_list(self) -> None:
        values = normalize_pipe_list("BG3 |  Minecraft|bg3| ")
        self.assertEqual(values, {"bg3", "minecraft"})

    def test_normalize_bool(self) -> None:
        self.assertTrue(normalize_bool("true"))
        self.assertFalse(normalize_bool("FALSE"))
        self.assertIsNone(normalize_bool("null"))

    def test_normalize_energy_level(self) -> None:
        self.assertEqual(normalize_energy_level("high"), "high")
        self.assertEqual(normalize_energy_level("balanced"), "medium")
        self.assertIsNone(normalize_energy_level("unknown"))

    def test_normalize_user_profile_handles_missing(self) -> None:
        profile = normalize_user_profile({})
        self.assertEqual(profile["games_likes"], set())
        self.assertIsNone(profile["playstyle_cooperative"])
        self.assertIsNone(profile["personality_energy_level"])


class ScorerTests(unittest.TestCase):
    def _base_row(self, post_id: str) -> dict[str, str]:
        return {
            "post_id": post_id,
            "games_currently_plays": "",
            "games_likes": "",
            "games_dislikes": "",
            "games_used_to_play": "",
            "games_open_to_try": "",
            "games_wants_to_play": "",
            "genres_likes": "",
            "genres_dislikes": "",
            "genres_avoids": "",
            "genres_open_to_try": "",
            "genres_unknown": "",
            "genres_metadata": "[]",
            "playstyle_cooperative": "null",
            "playstyle_competitive": "null",
            "playstyle_casual_chill": "null",
            "social_wants_long_term": "null",
            "social_wants_group": "null",
            "social_open_to_chat": "null",
            "personality_chill": "null",
            "personality_energy_level": "null",
            "personality_introverted": "null",
        }

    def test_games_overlap_and_conflict(self) -> None:
        row_a = self._base_row("a")
        row_b = self._base_row("b")
        row_a["games_likes"] = "bg3|minecraft"
        row_b["games_likes"] = "bg3"
        row_b["games_dislikes"] = "minecraft"
        profile_a = normalize_user_profile(row_a)
        profile_b = normalize_user_profile(row_b)
        result = score_games(profile_a, profile_b)
        self.assertEqual(result["raw_features"]["shared_strong_games"], ["bg3"])
        self.assertEqual(result["raw_features"]["game_conflicts"], ["minecraft"])
        self.assertGreaterEqual(result["score"], 0.0)
        self.assertLessEqual(result["score"], 1.0)

    def test_genre_conflict_penalty(self) -> None:
        row_a = self._base_row("a")
        row_b = self._base_row("b")
        row_a["genres_likes"] = "rpg|survival"
        row_b["genres_avoids"] = "survival"
        profile_a = normalize_user_profile(row_a)
        profile_b = normalize_user_profile(row_b)
        result = score_genres(profile_a, profile_b)
        self.assertEqual(result["raw_features"]["genre_conflicts_avoid"], ["survival"])
        self.assertGreaterEqual(result["score"], 0.0)
        self.assertLessEqual(result["score"], 1.0)

    def test_score_pair_output_shape(self) -> None:
        row_a = self._base_row("a")
        row_b = self._base_row("b")
        row_a["games_likes"] = "bg3"
        row_b["games_likes"] = "bg3"
        row_a["playstyle_cooperative"] = "true"
        row_b["playstyle_cooperative"] = "true"

        result = score_pair(row_a, row_b)
        self.assertIn("overall_overlap_score", result)
        self.assertIn("domain_scores", result)
        self.assertIn("raw_features", result)
        self.assertGreaterEqual(result["overall_overlap_score"], 0.0)
        self.assertLessEqual(result["overall_overlap_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
