# Generating a calendar week grid with the Python Calendar module

I needed to generate a grid calendar that looks like this (design [by Natalie Downe](https://github.com/natbat/pillarpointstewards/issues/23)):

<img alt="A calendar grid showing April with rows for each week, starting 28th March and finishing 1st May" src="https://user-images.githubusercontent.com/9599/161109554-b10c3aaa-57b3-4de5-8cae-84c88536ab24.png" width="600">

The Python standard library [calendar](https://docs.python.org/3/library/calendar.html) module has a utility function that really helps here:

```python
import calendar

cal = calendar.Calendar()
list(cal.monthdatescalendar(2022, 4))
```
Outputs:
```python
[[datetime.date(2022, 3, 28),
  datetime.date(2022, 3, 29),
  datetime.date(2022, 3, 30),
  datetime.date(2022, 3, 31),
  datetime.date(2022, 4, 1),
  datetime.date(2022, 4, 2),
  datetime.date(2022, 4, 3)],
 [datetime.date(2022, 4, 4),
  datetime.date(2022, 4, 5),
  datetime.date(2022, 4, 6),
  datetime.date(2022, 4, 7),
  datetime.date(2022, 4, 8),
  datetime.date(2022, 4, 9),
  datetime.date(2022, 4, 10)],
 [datetime.date(2022, 4, 11),
  datetime.date(2022, 4, 12),
  datetime.date(2022, 4, 13),
  datetime.date(2022, 4, 14),
  datetime.date(2022, 4, 15),
  datetime.date(2022, 4, 16),
  datetime.date(2022, 4, 17)],
 [datetime.date(2022, 4, 18),
  datetime.date(2022, 4, 19),
  datetime.date(2022, 4, 20),
  datetime.date(2022, 4, 21),
  datetime.date(2022, 4, 22),
  datetime.date(2022, 4, 23),
  datetime.date(2022, 4, 24)],
 [datetime.date(2022, 4, 25),
  datetime.date(2022, 4, 26),
  datetime.date(2022, 4, 27),
  datetime.date(2022, 4, 28),
  datetime.date(2022, 4, 29),
  datetime.date(2022, 4, 30),
  datetime.date(2022, 5, 1)]]
```

