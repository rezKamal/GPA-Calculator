# GPA-Calculator

This repo contains a script which scrapes a student's unofficial Swarthmore College grade report to obtain data about their progress, calculate their cumulative and term-by-term GPA, and list some suggestions as to which courses they should take in subsequent semesters.

The suggestions for future courses are based on an algorithm which weighs courses depending on their relation to the student's major and the student's past "interests," i.e. the number of similar classes they have taken before.

**script.py**: Python script that calculates GPA and suggests courses to enroll in next semester.

**grade_report.txt**: Sample unofficial grade report scraped from mySwarthmore website.

**fall_2021.txt**: List of course offerings for Fall 2021 obtained from Swarthmore website.

**subjects.txt**: List of subject codes and what majors they map to at Swarthmore.
