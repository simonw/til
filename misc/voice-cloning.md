# Cloning my voice with ElevenLabs

Charlie Holtz published [an astonishing demo](https://twitter.com/charliebholtz/status/1724815159590293764) today, where he hooked together GPT-Vision and a text-to-speech model trained on his own voice to produce a video of Sir David Attenborough narrating his life as observed through his webcam.

It honestly has to be seen to be believed. It's incredible and awful  at the same time. The simulated voice is pitch-perfect.

Charlie [released his code](https://github.com/cbh123/narrator) but did not release the cloned voice model, which is definitely for the best.

I decided to see how hard it was to clone my own voice using [ElevenLabs](https://elevenlabs.io/), the tool Charlie had used for the speech synthesis part of his demo.

The answer is _shockingly easy_.

## Starting with a sample

The ElevenLabs "Instant Voice Cloning" feature needs just a five minute sample of your voice.

I tried a couple of samples, but by far the best result I got was using the audio from my recent [10 minute talk](https://simonwillison.net/2023/Nov/10/universe/) at GitHub Universe. This isn't surprising: the Universe A/V team are extremely good at their jobs.

I already had a copy of the video downloaded from YouTube (using [yt-dlp](https://github.com/yt-dlp/yt-dlp). I opened it up in QuickTime Player on macOS, trimmed it to just the ten minutes of my speaking and used `File -> Export As -> Audio Only...` to extract a 9m40s 8.5MB `.m4a` file.

You can listen to that here:

https://static.simonwillison.net/static/2023/github-universe-simon-audio-only.m4a

## Creating the voice

In ElevenLabs, I clicked "Instant Voice Cloning" and uploaded my file.

I also set the description field to "40 year old British male, enthusiastic, technical". I don't think this description has any impact on the voice generation, I think it's just metadata for your own library of voices.

I agreed to the terms:

> I hereby confirm that I have all necessary rights or consents to upload and clone these voice samples and that I will not use the platform-generated content for any illegal, fraudulent, or harmful purpose

And clicked "Add Voice".

![The Add Voice form. I have set the name, uploaded a single 8.5MB audio file, set a description and clicked the checkbox. The Add Voice button at the bottom of the form is highlighted.](https://static.simonwillison.net/static/2023/add-voice.jpg)

It only took a few seconds and my cloned voice was ready to use.

## Using the voice

I clicked "use" and navigated to the Speech Synthesis page, with my cloned voice pre-selected.

![The Speech Synthesis form. Unleash the power of our cutting-edge technology to generate realistic, captivating speech in a wide range of languages. Voice is set to Simon Willison. I've pasted in four paragraphs of text. The bottom reads 699 / 5000 - Total quota remaining: 28410 - then a Generate button.](https://static.simonwillison.net/static/2023/use-voice.jpg)

I pasted in the following text from [my latest blog entry](https://simonwillison.net/2023/Nov/15/gpts/):

> The biggest announcement from last week’s OpenAI DevDay (and there were a LOT of announcements) was GPTs. Users of ChatGPT Plus can now create their own, custom GPT chat bots that other Plus subscribers can then talk to.
>
> My initial impression of GPTs was that they’re not much more than ChatGPT in a trench coat—a fancy wrapper for standard GPT-4 with some pre-baked prompts.
>
> Now that I’ve spent more time with them I’m beginning to see glimpses of something more than that. The combination of features they provide can add up to some very interesting results.
>
> As with pretty much everything coming out of these modern AI companies, the documentation is thin. Here’s what I’ve figured out so far.

## The resulting audio

Here's the resulting generated audio:

https://static.simonwillison.net/static/2023/simon-cloned-voice-demo.mp3

It's not perfect. It feels like there's a bit of a regional accent mixed in there that's not my own? But it's still ferociously impressive for the amount of time I spent creating this.

I ran the text through Google Translate to get a Spanish version:

> El anuncio más importante del OpenAI DevDay de la semana pasada (y hubo MUCHOS anuncios) fueron los GPT. Los usuarios de ChatGPT Plus ahora pueden crear sus propios bots de chat GPT personalizados con los que otros suscriptores de Plus pueden hablar.
>
> Mi impresión inicial de los GPT fue que no son mucho más que ChatGPT con una gabardina: un elegante envoltorio para el GPT-4 estándar con algunas indicaciones predefinidas.
>
> Ahora que he pasado más tiempo con ellos, empiezo a vislumbrar algo más que eso. La combinación de características que proporcionan puede generar resultados muy interesantes.
>
> Como ocurre con casi todo lo que surge de estas empresas modernas de inteligencia artificial, la documentación es escasa. Esto es lo que he descubierto hasta ahora.

Here's what that sounds like after running it through the voice generator with my voice:

https://static.simonwillison.net/static/2023/simon-generated-voice-spanish.mp3

This feels slightly less likely to confuse people who know me, though that's partly because I'm not remotely fluent in Spanish!
