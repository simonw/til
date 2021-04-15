# Listing files uploaded to Cloud Build

Today while running `datasette publish cloudrun ...` I noticed the following:

```
Uploading tarball of [.] to [gs://datasette-222320_cloudbuild/source/1618465936.523167-939ed21aedff4cb8a2c914c099fb48cd.tgz]
```
`gs://` indicates a Google Cloud Storage bucket. Can I see what's in that `datasette-222320_cloudbuild` bucket?

Turns out I can:

```
~ % gsutil ls -l gs://datasette-222320_cloudbuild/source/ | head -n 10
     36929  2019-05-03T13:18:35Z  gs://datasette-222320_cloudbuild/source/1556889512.4-7ffeb30ed7bc4173a8101cc3e7d6e12e.tgz
     36929  2019-05-03T13:20:06Z  gs://datasette-222320_cloudbuild/source/1556889605.56-5a5251a73b9646cca36b9afef8e578fd.tgz
     36928  2019-05-03T13:20:23Z  gs://datasette-222320_cloudbuild/source/1556889623.22-5ccfa45f935e4810ac322c15593233dc.tgz
     36927  2019-05-03T13:21:33Z  gs://datasette-222320_cloudbuild/source/1556889692.37-44759f37332047d9849cfb3773ef5b28.tgz
     36962  2019-05-03T14:01:14Z  gs://datasette-222320_cloudbuild/source/1556892073.6-d99f13f412054e13b4fb36670f454e50.tgz
```
The `-l` option adds the size information.

Mine has 7438 objects in it! I panicked a bit when I saw this at the end:

```
~ % gsutil ls -l gs://datasette-222320_cloudbuild/source/ | tail -n 10
 152553673  2021-04-15T01:41:32Z  gs://datasette-222320_cloudbuild/source/1618450815.99-26109d7f15bc478d999423e993091fd0.tgz
   1283564  2021-04-15T02:23:47Z  gs://datasette-222320_cloudbuild/source/1618453427.2-0e6193003ae14bff8be813f734b038b2.tgz
   1284121  2021-04-15T03:11:09Z  gs://datasette-222320_cloudbuild/source/1618456268.44-11595af453a74c9fb122b818e56d152e.tgz
  18660297  2021-04-15T03:37:24Z  gs://datasette-222320_cloudbuild/source/1618457837.52-71dfc8e6527042c6ba7b25afe91d006c.tgz
   1283482  2021-04-15T04:10:28Z  gs://datasette-222320_cloudbuild/source/1618459828.02-db9803983d024e7da2593a8db4c87b65.tgz
   3654810  2021-04-15T04:39:26Z  gs://datasette-222320_cloudbuild/source/1618461564.31-a9cff151b6bd4baba4ce68972bef4549.tgz
   1283746  2021-04-15T05:11:01Z  gs://datasette-222320_cloudbuild/source/1618463460.43-b65504ef3f9243a4acd2e07f6c7e9f63.tgz
 152748131  2021-04-15T05:19:52Z  gs://datasette-222320_cloudbuild/source/1618463900.76-1b829400ac3644b69dc5554d56dc3eab.tgz
 845871549  2021-04-15T06:05:49Z  gs://datasette-222320_cloudbuild/source/1618465936.523167-939ed21aedff4cb8a2c914c099fb48cd.tgz
TOTAL: 7438 objects, 273755828462 bytes (254.95 GiB)
```
But... since storage costs $0.020 per GB per month that quarter of a TB is costing me only $5/month. Phew!
