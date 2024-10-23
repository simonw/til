# Running prompts against images and PDFs with Google Gemini

I'm still working towards adding multi-modal support to my [LLM](https://llm.datasette.io/) tool. In the meantime, here are notes on running prompts against images and PDFs from the command-line using the [Google Gemini](https://ai.google.dev/gemini-api) family of models.

## Using curl

Here's the initial recipe I figured out using `curl`.

The Gemini models take a JSON document sent via POST that looks like this:

```json
{
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": "Extract text from this image"
        },
        {
          "inlineData": {
            "data": "... base 64 encoded image data ...",
            "mimeType": "image/png"
          }
        }
      ]
    }
  ]
}
```
So the first challenge is to construct that document, including the base64 encoded image.

On macOS you can encode a file using `base64 -i image.png`. On other platforms you may not need the `-i` option.

So we can create the JSON document like this:

```bash
cat <<EOF > input.json
{
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": "Extract text from this image"
        },
        {
          "inlineData": {
            "data": "$(base64 -i image.png)",
            "mimeType": "image/png"
          }
        }
      ]
    }
  ]
}
EOF
```

This creates a `input.json` file containing the base64 encoded image, ready to be sent to the Gemini API.

Now we can send it using `curl`:

```bash
export GOOGLE_API_KEY='... your key here ...'

curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-8b-latest:generateContent?key=$GOOGLE_API_KEY" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d @input.json
```

The model name goes in the URL - here I'm using `gemini-1.5-flash-8b-latest`, Google's cheapest and fastest model.

Model values you can use are:

- `gemini-1.5-flash-8b-latest` - the cheapest and fastest model, $0.04/million input tokens, 0.001 cents per image
- `gemini-1.5-flash-latest` - the one in the middle, $0.07/million input tokens, 0.0019 cents per image
- `gemini-1.5-pro-latest` - the most powerful model, $1.25/million input tokens, 0.0323 cents per image

It's hard to overestimate how _cheap_ these models are. An input image is charged at 258 tokens. That means the price per image processed is measured in fraction of a cent - those numbers above really are correct, an image even through Gemini Pro will cost less than 1/30th of a cent, and the other two models are even cheaper.

You get charged for output tokens too, which vary depending on the length of the response. Use [my LLM pricing calculator](https://tools.simonwillison.net/llm-prices) to explore those.

The output of a prompt includes a usage section that shows you exactly how many tokens you spent. Here's example output for the prompt "extract text from this image" against this image:

![Rough handwriting black marker on white card, it reads Example handwriting Let's try this out](https://github.com/user-attachments/assets/b0e18d6e-eca5-4a7a-bed8-7ffb0f0d9c68)


```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "Example handwriting\nLet's try this out"
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "safetyRatings": [
        {
          "category": "HARM_CATEGORY_HATE_SPEECH",
          "probability": "NEGLIGIBLE"
        },
        {
          "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
          "probability": "NEGLIGIBLE"
        },
        {
          "category": "HARM_CATEGORY_HARASSMENT",
          "probability": "NEGLIGIBLE"
        },
        {
          "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
          "probability": "NEGLIGIBLE"
        }
      ],
      "avgLogprobs": -0.000025986179631824296
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 264,
    "candidatesTokenCount": 9,
    "totalTokenCount": 273
  },
  "modelVersion": "gemini-1.5-flash-8b-001"
}
```
Total cost: 0.0011 cents.

## Using a Bash script

I got Claude to write me a script to automate this process. Here's how you can use it:

```bash
export GOOGLE_API_KEY='... your key here ...'

prompt-gemini 'extract text from this image' example-handwriting.jpg
```
It accepts PNG, JPG, GIF or PDF files, automatically sending the correct `mimeType` to the API. Note that PDFs with multiple pages are charged differently - I tried a 19 page PDF and it cost 12842 tokens, suggesting around 675 tokens per page.

You can also add a `-m` option to specify a different model:

```bash
prompt-gemini 'extract text from this image' example-handwriting.jpg -m pro
```
Shortcuts `pro`, `flash` and `8b` are supported - it defaults to the cheapest 8b model.

By default it outputs the full JSON response, so you can see things like the `"usageMetadata"` block. To output just the raw returned text add `-r`:

```bash
prompt-gemini 'extract text from this image' example-handwriting.jpg -r
```
```
Example handwriting
Let's try this out
```

Here's the script - save it somewhere on your path and run `chmod 755 prompt-gemini` to make it executable:

```bash
#!/bin/bash

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY environment variable is not set" >&2
    exit 1
fi

# Default model and options
model="8b"
prompt=""
image_file=""
jq_filter="."

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m)
            model="$2"
            shift 2
            ;;
        -r)
            jq_filter=".candidates[0].content.parts[0].text"
            shift
            ;;
        *)
            if [ -z "$prompt" ]; then
                prompt="$1"
            elif [ -z "$image_file" ]; then
                image_file="$1"
            fi
            shift
            ;;
    esac
done

# Validate prompt
if [ -z "$prompt" ]; then
    echo "Error: No prompt provided" >&2
    echo "Usage: prompt-gemini \"prompt\" [image_file] [-m model] [-r]" >&2
    exit 1
fi

# Map model names to full model strings
case $model in
    "8b"|"flash-8b")
        model_string="gemini-1.5-flash-8b-latest"
        ;;
    "flash")
        model_string="gemini-1.5-flash-latest"
        ;;
    "pro")
        model_string="gemini-1.5-pro-latest"
        ;;
    *)
        model_string="gemini-1.5-$model"
        ;;
esac

# Create temporary file
temp_file=$(mktemp)
trap 'rm -f "$temp_file"' EXIT

# Determine mime type if image file is provided
if [ -n "$image_file" ]; then
    if [ ! -f "$image_file" ]; then
        echo "Error: File '$image_file' not found" >&2
        exit 1
    fi

    # Get file extension and convert to lowercase
    ext=$(echo "${image_file##*.}" | tr '[:upper:]' '[:lower:]')
    
    case $ext in
        png)
            mime_type="image/png"
            ;;
        jpg|jpeg)
            mime_type="image/jpeg"
            ;;
        gif)
            mime_type="image/gif"
            ;;
        pdf)
            mime_type="application/pdf"
            ;;
        *)
            echo "Error: Unsupported file type .$ext" >&2
            exit 1
            ;;
    esac

    # Create JSON with image data
    cat <<EOF > "$temp_file"
{
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": "$prompt"
        },
        {
          "inlineData": {
            "data": "$(base64 -i "$image_file")",
            "mimeType": "$mime_type"
          }
        }
      ]
    }
  ]
}
EOF
else
    # Create JSON without image data
    cat <<EOF > "$temp_file"
{
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": "$prompt"
        }
      ]
    }
  ]
}
EOF
fi

# Make API request with jq filter
curl -s "https://generativelanguage.googleapis.com/v1beta/models/$model_string:generateContent?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d @"$temp_file" | jq "$jq_filter" -r
```

## How I got Claude to write the Bash script

Here's the prompt I fed to Claude to create this, starting with the Bash + `curl` recipe I had already figured out:


> ```bash
> cat <<EOF > input.json
> {
>   "contents": [
>     {
>       "role": "user",
>       "parts": [
>         {
>           "text": "Extract text from this imaage"
>         },
>         {
>           "inlineData": {
>             "data": "$(base64 -i output_0.png)",
>             "mimeType": "image/png"
>           }
>         }
>       ]
>     }
>   ]
> }
> EOF
> 
> curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-8b-latest:generateContent?key=$GOOGLE_API_KEY" \
>   -H 'Content-Type: application/json' \
>   -X POST \
>   -d @input.json | jq
> ```
> Turn this into a Bash script that runs like this:
> ```bash
> prompt-gemini "this is the prompt"
> prompt-gemini "This is the prompt" blah.png
> prompt-gemini "This is the prompt" blah.pdf
> prompt-gemini "this is the prompt" -m pro
> ```
> It should exit with an error if `GOOGLE_API_KEY` is not set
> 
> It should use a temporary file for input.json which is deleted on completion
> 
> If no file was provided it should skip the inlineData bit
> 
> It should use the correct mimeType for PNG or PDF or JPG or JPEG or GIF depending on the file extension
> 
> The -m option should follow the following rules: it defaults to 8b, or it can be:
> 
> 8b => gemini-1.5-flash-8b-latest (the default)
> flash-8b => gemini-1.5-flash-8b-latest
> flash => gemini-1.5-flash-latest
> pro => gemini-1.5-pro-latest
> 
> Any other value should be passed used directly in the `gemini-1.5-flash:generateContent` portion of the URL

Here's [the full Claude transcript](https://gist.github.com/simonw/7cc2a9c3e612a8af502d733ff619e066).

Then I added the `-r` option by pasting in the previous script and prompting:

> Modify this script to add an extra `-r` option which, if present, causes the final line to pipe through `jq` like this:
>
> ```
> ... | jq '.candidates[0].content.parts[0].text' -r
> ```

[Claude transcript here](https://gist.github.com/simonw/b1bffe54ebdf3583ec4e3639fb535567).
