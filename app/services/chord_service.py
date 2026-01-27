import librosa
import numpy as np
import os
import json

import librosa
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

class ChordService:
    def __init__(self):
        self.chroma_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.templates = self._build_templates()

    def _build_templates(self):
        templates = {}
        for i, name in enumerate(self.chroma_names):
            # Major: 0, 4, 7
            major = np.zeros(12)
            major[i] = 1
            major[(i + 4) % 12] = 1
            major[(i + 7) % 12] = 1
            templates[f"{name}"] = major / np.linalg.norm(major)
            
            # Minor: 0, 3, 7
            minor = np.zeros(12)
            minor[i] = 1
            minor[(i + 3) % 12] = 1
            minor[(i + 7) % 12] = 1
            templates[f"{name}m"] = minor / np.linalg.norm(minor)
        return templates

    def detect_chords(self, file_path):
        """
        Analyzes an audio file and returns a list of chords with timestamps.
        """
        logger.info(f"[CHORD] Starting analysis for: {file_path}")
        if not os.path.exists(file_path):
            logger.error(f"[CHORD] File not found: {file_path}")
            return []

        try:
            # Load audio (mono, 22050Hz)
            y, sr = librosa.load(file_path, sr=22050)
            logger.info(f"[CHORD] Audio loaded. Duration: {len(y)/sr:.2f}s")
            
            # Compute chroma cens (more robust to dynamics and timbre)
            chroma = librosa.feature.chroma_cens(y=y, sr=sr)
            logger.info(f"[CHORD] Chroma computed. Shape: {chroma.shape}")
            
            # Estimate chords per frame
            chord_sequence = []
            hop_length = 512
            times = librosa.frames_to_time(np.arange(chroma.shape[1]), sr=sr, hop_length=hop_length)
            
            last_chord = None
            
            for i in range(chroma.shape[1]):
                frame_chroma = chroma[:, i]
                norm = np.linalg.norm(frame_chroma)
                if norm > 0:
                    frame_chroma = frame_chroma / norm
                
                best_chord = "Unknown"
                best_sim = -1
                
                for name, template in self.templates.items():
                    sim = np.dot(frame_chroma, template)
                    if sim > best_sim:
                        best_sim = sim
                        best_chord = name
                
                if best_chord != last_chord:
                    chord_sequence.append({
                        "time": round(float(times[i]), 2),
                        "chord": best_chord
                    })
                    last_chord = best_chord
            
            # Remove short flickers
            refined_sequence = []
            if chord_sequence:
                refined_sequence.append(chord_sequence[0])
                for i in range(1, len(chord_sequence)):
                    duration = chord_sequence[i]['time'] - chord_sequence[i-1]['time']
                    if duration > 0.3: # Increased threshold slightly
                        refined_sequence.append(chord_sequence[i])
            
            logger.info(f"[CHORD] Analysis complete. Found {len(refined_sequence)} chord changes.")
            return refined_sequence

        except Exception as e:
            logger.error(f"[CHORD] Detection error: {str(e)}")
            raise e

chord_service = ChordService()
