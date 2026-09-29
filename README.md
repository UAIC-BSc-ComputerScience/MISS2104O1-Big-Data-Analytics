# MISS2104O1 — Big Data Analytics

Course materials from [UAIC's Big Data Analytics page](https://edu.info.uaic.ro/big-data-analytics/), downloaded on 29 September 2026 using the supplied course login. See [the course index](COURSE_INDEX.md) for assessment details and external reading.

## Materials

| Section | Files |
| --- | --- |
| Lecture slides | [Introduction](courses/1.%20Intro.pdf), [Hadoop](courses/2.%20Hadoop.pdf), [Recommender systems](courses/9.%20Recommender%20systems.pdf), [Graph clustering](courses/10.Graph%20clustering.pdf), [Locality sensitive hashing](courses/11-12.LSH.pdf) |
| Lab sheets | [HDFS](lab/Homework_Labs_Lecture01.pdf), [Run MapReduce](lab/Homework_Labs_Lecture02.pdf), [Java MapReduce](lab/Homework_Labs_Lecture03.pdf), [Combiners](lab/Homework_Labs_Lecture04.pdf), [Partitioner](lab/Homework_Labs_Lecture06.pdf) |
| Other course document | [University Training Options (2022)](resources/University%20Training%20Options_2022.pdf) |

[materials-manifest.json](materials-manifest.json) records the source URL, file size, and SHA-256 digest of each of the 11 PDFs. Source filenames are preserved. The linked Cloudera VM ZIP was excluded because it is a large software image, not a course PDF.

## Refreshing the material

Run `python3 download_materials.py` for active PDF links. It prompts for the course username and password, then writes to an ignored `materials/` folder. The broader `scripts/scrape_course.py` crawler also exists for local use and writes to ignored `course-materials/`. Neither script stores the login in Git.
