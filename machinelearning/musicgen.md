# Trying out the facebook/musicgen-small sound generation model

Facebook's [musicgen](https://huggingface.co/facebook/musicgen-small) is a model that generates snippets of audio from a text description - it's effectively a Stable Diffusion for music.

It turns out it's pretty easy to run it using Python, thanks to the Hugging Face [transformers](https://pypi.org/project/transformers/) library.

Here's the code that worked for me. First, install the dependencies:
```
pip install scipy transformers
```
The following will download the small model - around 2GB - and store it in `~/.cache/huggingface/hub/models--facebook--musicgen-small` the first time you run it.

```python
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy

processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")

def save(prompt, filename, num_tokens=1503):
    inputs = processor(
        text=[prompt],
        padding=True,
        return_tensors="pt",
    )
    audio_values = model.generate(**inputs, max_new_tokens=num_tokens)
    sampling_rate = model.config.audio_encoder.sampling_rate
    scipy.io.wavfile.write(filename, rate=sampling_rate, data=audio_values[0, 0].numpy())
```
Then you can use that `save()` function like this to generate and save an audio sample:
```python
save("trumpet mariachi frenetic excitement", "trumpet_mariachi.wav")
```
Here's the audio that generated:

https://static.simonwillison.net/static/2023/trumpet_mariachi.wav
