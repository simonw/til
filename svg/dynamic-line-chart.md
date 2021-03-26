# Creating a dynamic line chart with SVG

I helped build the tide chart visualizations for [Rocky Beaches](https://www.rockybeaches.com/).

I wanted to generate an SVG line representing 24 hours of tide levels. I had 240 points per day of level data, imported from the NOAA Tides & Currents API. That data looked [like this](https://www.rockybeaches.com/data/tide_predictions):

| station_id | datetime | mllw_feet |
| --- | --- | --- |
| 9414131 | 2020-08-19 00:00 | 5.913 |
| 9414131 | 2020-08-19 00:06 | 5.822 |
| 9414131 | 2020-08-19 00:12 | 5.726 |
| 9414131 | 2020-08-19 00:18 | 5.623 |
| 9414131 | 2020-08-19 ... | ... |

I started with [this line chart example](https://css-tricks.com/how-to-make-charts-with-svg/#line-charts) from CSS-Tricks:

```svg
<svg viewBox="0 0 500 100">
  <polyline
     fill="none"
     stroke="#0074d9"
     stroke-width="3"
     points="
       0,120
       20,60
       40,80
       60,20"/>
</svg>
```
A few things to note:

- The SVG coordinate system starts at the top left - so '0,120' means 0 units along, 120 units down.
- The `viewBox` attribute specifies `min-x min-y width height` - so `0 0 500 100` specifies a box that is 500 units wide and 100 units high.

The dynamic data can be contained entirely in that single `points=` attribute on the `polyline`.

## Prototyping using SQL

I posted my working [in this issue](https://github.com/natbat/rockybeaches/issues/31), including prototyping the polyline using a SQL query that generated the `x1,y1 x2,y2` pairs. That query looked like this:

```sql
with today_points as (
  select
    datetime,
    mllw_feet
  from
    tide_predictions
  where
    date("datetime") = :p0
    and "station_id" = :p1
),
min_max as (
  select
    min(mllw_feet) as min_feet,
    max(mllw_feet) as max_feet
  from
    today_points
),
points as (
  select
    RANK () OVER (
      ORDER BY
        datetime
    ) -1 as rank,
    min_max.min_feet,
    min_max.max_feet,
    mllw_feet,
    (
      100 * (mllw_feet - min_max.min_feet) / (min_max.max_feet - min_max.min_feet)
    ) as line_height_pct
  from
    tide_predictions,
    min_max
  where
    date("datetime") = :p0
    and "station_id" = :p1
  order by
    datetime
)
select
  group_concat(rank || ',' || line_height_pct, ' ')
from
  points
```
[Try that here](https://www.rockybeaches.com/data?sql=with+today_points+as+%28%0D%0A++select+datetime%2C+mllw_feet%0D%0A++from+tide_predictions%0D%0A++where%0D%0A++date%28%22datetime%22%29+%3D+%3Ap0%0D%0A++and+%22station_id%22+%3D+%3Ap1%0D%0A%29%2C+min_max+as+%28select+min%28mllw_feet%29+as+min_feet%2C+max%28mllw_feet%29+as+max_feet+from+today_points%29%2C+points+as+%28select%0D%0A++RANK+%28%29+OVER+%28%0D%0A++++ORDER+BY%0D%0A++++++datetime%0D%0A++%29+-1+as+rank%2C%0D%0A+min_max.min_feet%2C+min_max.max_feet%2C++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++mllw_feet%2C%0D%0A++%28100+*+%28mllw_feet+-+min_max.min_feet%29+%2F+%28min_max.max_feet+-+min_max.min_feet%29%29+as+line_height_pct%0D%0Afrom%0D%0A++tide_predictions%2C+min_max%0D%0Awhere%0D%0A++date%28%22datetime%22%29+%3D+%3Ap0%0D%0A++and+%22station_id%22+%3D+%3Ap1%0D%0Aorder+by%0D%0A++datetime%29%0D%0Aselect+group_concat%28rank+%7C%7C+%27%2C%27+%7C%7C+line_height_pct%2C+%27+%27%29+from+points&p0=2020-08-21&p1=9414131)

I then pasted the results into the SVG and previewed it by pasting it into https://htmledit.squarefree.com/

```html
<svg style="border: 1px solid red; width: 40%; height: 60px" viewBox="0 -2 240 104" preserveAspectRatio="none">
  <polyline
     fill="none"
     stroke="#0074d9"
     stroke-width="2"
     points="0,0.543825975687781 1,0.255918106206011 2,0.0799744081893721 3,1.4210854715202e-14 4,0.0159948816378659 5,0.159948816378744 6,0.383877159309023 7,0.71976967370442 8,1.16762635956493 9,1.71145233525272 10,2.36724248240563 11,3.11900191938578 12,3.98272552783109 13,4.94241842610363 14,5.99808061420346 15,7.16570697376839 16,8.4133077415227 17,9.75687779910427 18,11.1804222648752 19,12.6999360204734 20,14.3154190658989 21,15.9948816378759 22,17.7543186180422 23,19.5937300063979 24,21.4971209213052 25,23.4644913627639 26,25.4958413307741 27,27.5911708253359 28,29.7344849648113 29,31.9097888675624 30,34.149072296865 31,36.4203454894434 32,38.7236084452975 33,41.0428662827895 34,43.3941138835573 35,45.7613563659629 36,48.1445937300064 37,50.5278310940499 38,52.9270633397313 39,55.3103007037748 40,57.6775431861804 41,60.0287907869482 42,62.3640435060781 43,64.6673064619322 44,66.9385796545106 45,69.1618682021753 46,71.3371721049264 47,73.4804862444018 48,75.5598208573257 49,77.575175943698 50,79.5265515035189 51,81.4139475367882 52,83.2213691618682 53,84.9488163787588 54,86.59628918746 55,88.1637875879719 56,89.6513115802943 57,91.0268714011516 58,92.3224568138196 59,93.5220729366603 60,94.6257197696737 61,95.6333973128599 62,96.5291106845809 63,97.3288547664747 64,98.0326295585413 65,98.6244401791427 66,99.104286628279 67,99.488163787588 68,99.7600767754319 69,99.9360204734485 70,100.0 71,99.9520153550864 72,99.7920665387076 73,99.5361484325016 74,99.1682661548304 75,98.6884197056942 76,98.0966090850928 77,97.4088291746641 78,96.6250799744082 79,95.7293666026871 80,94.7376839411388 81,93.6340371081254 82,92.4344209852847 83,91.1548304542546 84,89.7792706333973 85,88.3077415227127 86,86.7562380038388 87,85.1247600767754 88,83.4133077415227 89,81.6218809980806 90,79.7824696097249 91,77.8630838131798 92,75.9117082533589 93,73.8963531669866 94,71.8330134357006 95,69.7376839411388 96,67.5943698016635 97,65.4350607805502 98,63.2597568777991 99,61.0684580934101 100,58.8611644273832 101,56.6538707613564 102,54.4625719769674 103,52.2552783109405 104,50.0799744081894 105,47.9206653870761 106,45.7773512476008 107,43.6660268714011 108,41.5866922584773 109,39.5393474088292 110,37.5399872040947 111,35.5886116442738 112,33.6692258477287 113,31.829814459373 114,30.022392834293 115,28.2949456174024 116,26.6154830454255 117,25.0159948816379 118,23.4804862444018 119,22.0089571337172 120,20.6333973128599 121,19.3218170185541 122,18.1062060140755 123,16.9705694177863 124,15.9149072296865 125,14.9552143314139 126,14.0914907229686 127,13.3237364043506 128,12.635956493922 129,12.0601407549584 130,11.5802943058221 131,11.212412028151 132,10.9245041586692 133,10.7485604606526 134,10.6685860524632 135,10.7005758157389 136,10.828534868842 137,11.0524632117722 138,11.3723608445297 139,11.7882277671145 140,12.3000639795265 141,12.9078694817658 142,13.5956493921945 143,14.3793985924504 144,15.2431222008957 145,16.2028150991683 146,17.2264875239923 147,18.3301343570058 148,19.4977607165707 149,20.745361484325 150,22.0409468969929 151,23.4005118362124 152,24.8240563019834 153,26.2955854126679 154,27.7991042866283 155,29.3666026871401 156,30.9660908509277 157,32.5815738963532 158,34.2450415866923 159,35.9245041586692 160,37.6199616122841 161,39.3474088291747 162,41.0588611644274 163,42.786308381318 164,44.5137555982086 165,46.2412028150992 166,47.9526551503519 167,49.6481126039667 168,51.3275751759437 169,52.9750479846449 170,54.5905310300704 171,56.1740243122201 172,57.725527831094 173,59.2130518234165 174,60.6685860524632 175,62.0761356365963 176,63.40371081254 177,64.6992962252079 178,65.9149072296865 179,67.0665387076136 180,68.1541906589891 181,69.1618682021753 182,70.10556621881 183,70.9692898272553 184,71.7530390275112 185,72.4408189379399 186,73.064619321817 187,73.6084452975048 188,74.0563019833653 189,74.4241842610365 190,74.7120921305182 191,74.9040307101727 192,75.0159948816379 193,75.0319897632758 194,74.9520153550864 195,74.8080614203455 196,74.5521433141395 197,74.2162507997441 198,73.8003838771593 199,73.2885476647473 200,72.680742162508 201,72.0089571337172 202,71.2412028150992 203,70.3774792066539 204,69.4497760716571 205,68.4420985284709 206,67.3544465770953 207,66.1868202175304 208,64.9552143314139 209,63.6436340371081 210,62.2840690978887 211,60.8445297504799 212,59.3730006397953 213,57.8214971209213 214,56.2380038387716 215,54.6225207933461 216,52.9430582213691 217,51.2476007677543 218,49.5201535508637 219,47.7767114523352 220,46.0172744721689 221,44.2418426103647 222,42.4664107485605 223,40.6749840051184 224,38.8995521433141 225,37.1401151631478 226,35.3806781829814 227,33.6532309660909 228,31.9417786308381 229,30.2623160588612 230,28.61484325016 231,26.9993602047345 232,25.4318618042226 233,23.9123480486244 234,22.424824056302 235,21.001279590531 236,19.6257197696737 237,18.3141394753679 238,17.0665387076136 239,15.8829174664107"/>
</svg>
```
## Scaling the image with preserveAspectRatio="none"

I wanted to scale the SVG image to fit the div it was overlayed onto - which had a fixed height of 60px but a variable width.

[How to Scale SVG](https://css-tricks.com/scale-svg/) was useful for understanding the options here.

SVG images maintain their aspect ratio by default. Adding `preserveAspectRatio="none"` changed this, so the image could be distorted to fit the shape.

Unfortunately this has a visual impact on the line of the graph - causing it to be wider and narrower at different angles. We decided that this brush-stroke effect was actually OK for our purposes.

<img src="https://user-images.githubusercontent.com/9599/90821264-7a930680-e2e7-11ea-83a2-3003cf08877f.png" alt="Distorted line">

## Tweaking the viewBox

My chart was drawn be 240 units wide (covering 24 hours of the day with 10 units per hour) and 100 units high.

Using this as the exact viewBox dimensions caused the top and bottom of the line peaks to be truncated. I fixed that by tweaking the viewBox a bit to add some breathing room:

    viewBox="0 -2 240 104"

## Generating the data using Python

Here's [the final Python code](https://github.com/natbat/rockybeaches/blob/70039f18b3d3823a4f069deca513e950a3aaba4f/plugins/template_vars.py#L148-L156) I used to generate the points:

```python
# Calculate SVG points, refs https://github.com/natbat/rockybeaches/issues/31
min_feet = min(h["feet"] for h in heights[1:-1])
max_feet = max(h["feet"] for h in heights[1:-1])
feet_delta = max_feet - min_feet
svg_points = []
for i, height in enumerate(heights[1:-1]):
    ratio = (height["feet"] - min_feet) / feet_delta
    line_height_pct = 100 - (ratio * 100)
    svg_points.append((i, line_height_pct))
# ...
points = " ".join("{},{:.2f}".format(i, pct) for i, pct in svg_points)
```
I used `{:.2f}` to truncate the floating point represention to just two decimal places, which knocked 100KB off the total page size due to the number of charts being displayed!

Finished result can be seen here: https://www.rockybeaches.com/us/pillar-point#when-to-visit
