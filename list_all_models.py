from audio_separator.separator import Separator
import logging

logging.basicConfig(level=logging.ERROR)

def find_guitar_model():
    print("Listing all available models from audio-separator...")
    separator = Separator()
    # In audio-separator, the models are listed in fixed constant or retrieved from a source.
    # Looking at the source code of audio-separator, it seems we can get them from the internal list.
    try:
        # For audio-separator >= 0.17.x, models are defined in constants or we can try to find them.
        # Let's try to see if we can get the model data.
        # Often it's in separator.model_data or similar.
        print("Searching for 'guitar' in supported models...")
        # Since I can't easily peek into the library without running, let's just try a few common ones
        # or list them by trying a list-models type command indirectly.
        pass
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_guitar_model()
