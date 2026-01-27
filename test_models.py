from audio_separator.separator import Separator
import os

def list_models():
    separator = Separator()
    # Looking at the source of audio-separator, it doesn't have a direct "list_models" method on Separator class 
    # but it downloads models from a certain source.
    # However, I'll try to load a likely name and see if it errors with suggestions or something.
    # Actually, let's just use a common one: UVR-MDX-NET-Guitar
    print("Trying to find Guitar models...")
    # Based on research, UVR-MDX-NET-Guitar is the standard.
    
if __name__ == "__main__":
    list_models()
