import tempfile
import unittest
from pathlib import Path
from unittest import mock

from local_llama_voiceover import VoiceoverService, render_page


class VoiceoverServiceTests(unittest.TestCase):
    def test_build_character_prompt_keeps_character_and_text(self):
        service = VoiceoverService(output_dir=Path(tempfile.mkdtemp()))
        prompt = service.build_character_prompt("Halo dunia", "Narator hangat")

        self.assertIn("Narator hangat", prompt)
        self.assertIn("Halo dunia", prompt)

    def test_refine_script_falls_back_to_original_text_when_ollama_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = VoiceoverService(
                output_dir=Path(tmp_dir),
                urlopen=mock.Mock(side_effect=OSError("offline")),
            )

            refined = service.refine_script("Teks awal", "Narator tegas")

        self.assertEqual(refined, "Teks awal")

    def test_safe_audio_path_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = VoiceoverService(output_dir=Path(tmp_dir))
            audio_file = Path(tmp_dir) / "hasil.wav"
            audio_file.write_bytes(b"voice")

            resolved = service.safe_audio_path("../hasil.wav")

        self.assertEqual(resolved, audio_file.resolve())

    def test_render_page_shows_audio_player_when_result_exists(self):
        html = render_page(
            result={
                "character": "Narator natural",
                "refined_script": "Selamat datang",
                "audio_file": "hasil.wav",
                "audio_path": "/tmp/hasil.wav",
            }
        )

        self.assertIn("<audio controls", html)
        self.assertIn("Selamat datang", html)


if __name__ == "__main__":
    unittest.main()
