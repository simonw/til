# Calculating the size of all LFS files in a repo

I wanted to know how large the [deepseek-ai/DeepSeek-V3-Base](https://huggingface.co/deepseek-ai/DeepSeek-V3-Base) repo on Hugging Face was without actually downloading all of the files.

With [some help from Claude](https://gist.github.com/simonw/9d2b780a39e58a230a0cee18452ec9d0), here's the recipe that worked.

First, clone the repo without having Git LFS download the files:

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/deepseek-ai/DeepSeek-V3-Base
cd DeepSeek-V3-Base
```
The `git lfs ls-files -s` command lists the files along with their sizes:

```bash
git lfs ls-files -s
```
```
3f4e5fcec2 - model-00001-of-000163.safetensors (5.2 GB)
4fb0c2abdd - model-00002-of-000163.safetensors (4.3 GB)
...
```
Then I used this `awk` recipe to add up those numbers:
```bash
git lfs ls-files -s | grep -o '[0-9.]\+ GB' | awk '{sum += $1} END {print sum " GB"}'
```
Output:
```
687.9 GB
```
Since this only counts lines with `GB` in them I asked Claude for a longer one-liner for handling other units as well. This appears to work but I haven't verified it in depth yet, so use with caution:

```bash
git lfs ls-files -s | grep -o '[0-9.]\+ [KMGT]B' | awk '{ 
    split($0, a, " "); 
    size=a[1]; 
    unit=a[2]; 
    if(unit=="KB") size*=1024; 
    else if(unit=="MB") size*=1024^2; 
    else if(unit=="GB") size*=1024^3; 
    else if(unit=="TB") size*=1024^4; 
    total+=size
} END { 
    if(total<1024) print total " B";
    else if(total<1024^2) print total/1024 " KB";
    else if(total<1024^3) print total/1024^2 " MB";
    else if(total<1024^4) print total/1024^3 " GB";
    else print total/1024^4 " TB"
}'
```
