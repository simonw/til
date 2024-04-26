# Transcribing MP3s with whisper-cpp on macOS

I asked [on Twitter](https://twitter.com/simonw/status/1783520794754318600) for tips about running Whisper transcriptions in the CLI on my Mac. Werner Robitza [pointed me](https://twitter.com/slhck/status/1783556354487034146) to Homebrew's [whisper-cpp](https://formulae.brew.sh/formula/whisper-cpp) formula, and when I complained that it didn't have quite enough documentation for me to know how to use it [got a PR accepted](https://github.com/Homebrew/homebrew-core/pull/170148) adding the missing details.

Here's my recipe for using it to transcribe an MP3 file.

1. Install `whisper-cpp`:
    
    ```bash
    brew install whisper-cpp
    ```
    This gave me a `/opt/homebrew/bin/whisper-cpp`, added to my `PATH` as `whisper-cpp`

2. Download a Whisper model file. These are available [on Hugging Face](https://huggingface.co/ggerganov/whisper.cpp/tree/main) - there are a bunch of options, I decided to go for `ggml-large-v3-q5_0.bin` ([direct download link](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-q5_0.bin?download=true), 1GB) because it looked like it might offer right balance of file size to quality.
3. Convert the MP3 file to the 16khz WAV file needed by Whisper:
    ```bash
    ffmpeg -i input.mp3 -ar 16000 input.wav
    ````
4. Run the transcription:
    ```bash
    whisper-cpp -m ggml-large-v3-q5_0.bin input.wav --output-txt out.txt
    ```

This output a whole bunch of information, including the transcript, and saved that transcript to `out.txt`.

## How I figured out the 16khz MP3 conversion

When I realized Whisper needed WAV and not MP3 I used my [llm cmd](https://simonwillison.net/2024/Mar/26/llm-cmd/) command to figure out how to run that conversion:

```bash
llm cmd convert input.mp3 to .wav
```
It suggested this command, which I ran:
```bash
ffmpeg -i input.mp3 input.wav
```
But when I ran the resulting file through Whisper I got this error:
```
...
read_wav: WAV file '/tmp/input.wav' must be 16 kHz
error: failed to read WAV file '/tmp/input.wav'
```
So I ran `llm cmd` again:
```bash
llm cmd convert input.mp3 to .wav must be 16khz
```
And  this time it gave me:
```bash
ffmpeg -i input.mp3 -ar 16000 input.wav
```
Which produced a file that worked in Whisper.

## whisper-cpp has a bunch more options

Here's the full `whisper-cpp --help` output. I have not spent any time exploring these options beyond `--output-txt`:

```
usage: whisper-cpp [options] file0.wav file1.wav ...

options:
  -h,        --help              [default] show this help message and exit
  -t N,      --threads N         [4      ] number of threads to use during computation
  -p N,      --processors N      [1      ] number of processors to use during computation
  -ot N,     --offset-t N        [0      ] time offset in milliseconds
  -on N,     --offset-n N        [0      ] segment index offset
  -d  N,     --duration N        [0      ] duration of audio to process in milliseconds
  -mc N,     --max-context N     [-1     ] maximum number of text context tokens to store
  -ml N,     --max-len N         [0      ] maximum segment length in characters
  -sow,      --split-on-word     [false  ] split on word rather than on token
  -bo N,     --best-of N         [5      ] number of best candidates to keep
  -bs N,     --beam-size N       [5      ] beam size for beam search
  -wt N,     --word-thold N      [0.01   ] word timestamp probability threshold
  -et N,     --entropy-thold N   [2.40   ] entropy threshold for decoder fail
  -lpt N,    --logprob-thold N   [-1.00  ] log probability threshold for decoder fail
  -debug,    --debug-mode        [false  ] enable debug mode (eg. dump log_mel)
  -tr,       --translate         [false  ] translate from source language to english
  -di,       --diarize           [false  ] stereo audio diarization
  -tdrz,     --tinydiarize       [false  ] enable tinydiarize (requires a tdrz model)
  -nf,       --no-fallback       [false  ] do not use temperature fallback while decoding
  -otxt,     --output-txt        [false  ] output result in a text file
  -ovtt,     --output-vtt        [false  ] output result in a vtt file
  -osrt,     --output-srt        [false  ] output result in a srt file
  -olrc,     --output-lrc        [false  ] output result in a lrc file
  -owts,     --output-words      [false  ] output script for generating karaoke video
  -fp,       --font-path         [/System/Library/Fonts/Supplemental/Courier New Bold.ttf] path to a monospace font for karaoke video
  -ocsv,     --output-csv        [false  ] output result in a CSV file
  -oj,       --output-json       [false  ] output result in a JSON file
  -ojf,      --output-json-full  [false  ] include more information in the JSON file
  -of FNAME, --output-file FNAME [       ] output file path (without file extension)
  -ps,       --print-special     [false  ] print special tokens
  -pc,       --print-colors      [false  ] print colors
  -pp,       --print-progress    [false  ] print progress
  -nt,       --no-timestamps     [false  ] do not print timestamps
  -l LANG,   --language LANG     [en     ] spoken language ('auto' for auto-detect)
  -dl,       --detect-language   [false  ] exit after automatically detecting language
             --prompt PROMPT     [       ] initial prompt
  -m FNAME,  --model FNAME       [models/ggml-base.en.bin] model path
  -f FNAME,  --file FNAME        [       ] input WAV file path
  -oved D,   --ov-e-device DNAME [CPU    ] the OpenVINO device used for encode inference
  -ls,       --log-score         [false  ] log best decoder scores of tokens
  -ng,       --no-gpu            [false  ] disable GPU
```
