import queue
#   Mapping of letter grades to numerical grades
letters = {"A+":4, "A":4, "A-":3.66667, "B+":3.33333, "B":3, "B-":2.66667,
           "C+":2.33333, "C":2, "C-":1.66667, "D+":1.33333, "D":1, "D-":0.66667,
           "CR":0, "NC":0, "IC":0, "W":0, "R":0}
#   Mapping of subjects to codes (i.e. Engineering to ENGR) and vice-versa
subjects = {}
codes = {}
#   List of all course options for the upcoming semester and their weights
weights = queue.PriorityQueue()
#   Fetches, contains, and prints out data relevant to student's report
class Student:
#   Constructor for Student class
    def __init__(self, page):
        self.page = page
        self.name = page[5][1][0]
        self.transcript = []
        self.year = int(page[5][-1][0])
        self.credits = 0
        self.majors = self.getMajors()
        self.terms = self.getTerms()
        self.gpa = self.getCumulGPA()
        self.courses = self.getCourses()
        self.attrs = self.getAttrs()
#   Returns major(s) (and minor(s)) in 2 lists of strings, 1 per subject
    def getMajors(self):
        majors = [[], []]
        for i in range(0, 2):
            string = ""
            if len(self.page[i+6]) < 2:
                continue
            for j in range(len(self.page[i+6][1])):
                if j > 0:
                    string += " "
                string += self.page[i+6][1][j]
            majors[i] = string.split(", ")
        return majors
#   Collects the student's terms and builds up their complete transcript
    def getTerms(self):
        terms = []
        for i in range(13, len(self.page)):
            if self.page[i][0][0] == "Term:":
                load = float(self.page[i][0][-1])
                self.credits += load*(load < 10)
                terms.append(Term(self.page[i], self.getTermGPA(i+2, load)))
        return terms
#   Returns the GPA for a term given the index of its first course
    def getTermGPA(self, i, load):
        if self.page[i][0][0] == '-':
            return [-1, 0]
        gpa = 0
        while i < len(self.page):
            if self.page[i][0][0] == "Term:":
                break
            self.transcript.append(Course(self.page[i]))
            if self.transcript[-1].grade == 0 \
                and self.transcript[-1].line[3][0] != 'R' \
                and self.transcript[-1].dept != "PHED":
                load -= self.transcript[-1].weight
            gpa += self.transcript[-1].grade
            i += 1
        if load == 0:
            return [0, load]
        else:
            return [gpa/load, load]
#   Returns the student's cumulative GPA over all terms
    def getCumulGPA(self):
        gpa = 0.0
        load = 0.0
        for term in self.terms:
            gpa += term.gpa*term.load
            load += term.load
        return gpa/load
#   Returns the student's GPA for a given major (or any subject)
    def getMajorGPA(self, major):
        gpa = 0
        load = 0
        if major in subjects:
            code = subjects[major]
        else:
            return -1
        for course in self.transcript:
            if course.dept == code and course.grade > 0:
                gpa += course.grade
                load += course.weight
        if load > 0:
            return gpa/load
        else:
            return -1
#   Prints the output seen by the user, which includes all relevant info
    def display(self):
        print("\n\n\n\n\n\n\n\nHello %s!" % (self.name))
        print("It looks like you started in %s and have %.1f credits." %
             (self.terms[-1].name, self.credits))
        if len(self.majors) > 0:
            printMajors(self.majors)
        else:
            print("You don't have a major yet, \
                   so you'll only have a cumulative GPA.")
        print("\nHere are your grades for each term:")
        for term in self.terms:
            if term.gpa != 0 and term.gpa != -1:
                print("%15s: %.2f" % (term.name, term.gpa))
            elif term.gpa == 0:
                print("%15s: Woohoo! Pass-fail!" % term.name)
            else:
                print("%15s: Leave of absence" % term.name)
        print("\nYour cumulative GPA is %.2f." % self.gpa)
        for major in self.majors[0]:
            gpa = self.getMajorGPA(major)
            if gpa == -1:
                print("Your %s GPA is unavailable at the moment."
                      % major)
            else:
                print("Your %s GPA is %.2f." % (major, gpa))
        print("\nHere are some suggestions for courses to take in Fall 2021:")
        recs = [[], []]
        while (len(recs[0]) < 10 or len(recs[1]) < 10):
            rec = weights.get()[1]
            if (codes[rec[0:4]] in self.majors[0]
                or codes[rec[0:4]] in self.majors[1]) and len(recs[0]) < 10:
                recs[0].append(rec)
            elif codes[rec[0:4]] not in self.majors[0] \
                  and codes[rec[0:4]] not in self.majors[1] \
                  and len(recs[1]) < 10:
                recs[1].append(rec)
        print("\nFor making progress on your majors/minors:\n")
        for i in range(10):
            print(recs[0][10-i-1])
        print("\nFor enjoyment and fulfilling graduation requirements:\n")
        for i in range(10):
            print(recs[1][10-i-1])
        print("\nThe suggestions are based on classes you've taken before, so" \
              " keep in mind it won't list many courses you're unfamiliar with!")
        print('\n')
#   Groups the student's courses according to department and returns a
#   dictionary mapping departments to a pair consisting of an array of
#   course codes and courses taken.
#   e.g. If I took CPSC 21, 31 and ENGR 11, it returns the following:
#        {"CPSC":[["21", "31"], 2], "ENGR":[[11], 1]}
    def getCourses(self):
        courses = {}
        for course in self.transcript:
            if course.dept not in courses:
                courses[course.dept] = [[],0]
            courses[course.dept][0].append(course.code)
            courses[course.dept][1] += course.weight
            if course.dept == "PHED" and int(course.line[3][0]) == 1:
                courses[course.dept][1] += 1
        return courses
#   Returns a dictionary of attributes (NS/SS/W/PE/etc) mapping to booleans of
#   whether or not they have been completed
    def getAttrs(self):
        attrs = {"NS":0, "SS":0, "HU":0, "W":0, "NSEP":0, "PE":0}
        required = [3, 3, 3, 3, 1, 4]
        divisions = ["NS", "SS", "HU", "W"]
        for division in divisions:
            fulfill = {}
            for course in self.transcript:
                if division in course.attrs and course.weight >= 1 \
                and course.line[3][0] != "R":
                    if course.dept not in fulfill:
                        fulfill[course.dept] = course.weight
                        attrs[division] += course.weight
                    elif fulfill[course.dept] < 2:
                        fulfill[course.dept] += course.weight
                        attrs[division] += course.weight
        for course in self.transcript:
            if "NSEP" in course.attrs and course.weight >= 1 \
            and course.line[3][0] != "R":
                attrs["NSEP"] += course.weight
        attrs["PE"] = self.courses["PHED"][1]
        for division in divisions:
            if attrs[division] >= 3:
                attrs[division] = True
            else:
                attrs[division] = False
        if attrs["NSEP"] >= 1:
            attrs["NSEP"] = True
        else:
            attrs["NSEP"] = False
        if attrs["PE"] >= 4:
            attrs["PE"] = True
        else:
            attrs["PE"] = False
        return attrs
#   Fetches and contains info on a term from a line passed if __name__ == '__main__':
class Term:
    def __init__(self, line, pair):
        self.name = "%s %s" % (line[0][1], line[0][2])
        self.credits = float(line[-1][-1])
        self.gpa = pair[0]
        self.load = pair[1]
#   Fetches and contains info on a course from a line passed in
class Course:
#   Constructor for Course class
    def __init__(self, line):
        self.line = line
        self.dept = line[0][0]
        self.code = line[0][1]
        self.weight = float(self.line[2][0])
        if self.weight != 0:
            self.grade = letters[self.line[3][0]]
        else:
            self.grade = 0
        self.attrs = set()
        for attr in self.line[4]:
            self.attrs.add(attr.replace(',', ''))
#   Prints the student's majors/minors in a readable format
def printMajors(majors):
    s = "You are majoring in " + majors[0][0]
    if len(majors[0]) > 1:
        s += " & " + majors[0][1]
    if len(majors[1]) > 0:
        s += " and minoring in " + majors[1][0]
        if len(majors[1]) > 1:
            s += " & " + majors[1][1]
    return s
#   Parses student report into a list of lines, each line into a tab-separated
#   section, and each section into a list of space-separated words.
#   Below is an example of what will be stored for a short sample page.
#   ----------  SAMPLE PAGE ----------
#   Name:  	Rezhwan Amanj Kamal	Class Year:  	2023
#   Majors:  	Engineering, Computer Science
#   ----------  TO RETURN   ----------
#   [[["Name"], ["Rezhwan","Amanj","Kamal"], ["Class", "Year:"], ["2023"]],
#    [["Majors:"], ["Engineering,", "Computer", "Science"]]]
def parseFile(filename):
   page = []
   myfile = open(filename, "r")
   for line in myfile:
      row = []
      sections = line.split('\t')
      for section in sections:
          words = section.strip().split(' ')
          row.append(words)
      page.append(row)
   return page
#  Parses a txt file to create a global mapping of subjects to 4-letter codes
def getAllSubjects():
    myfile = open("subjects.txt", "r")
    for line in myfile:
        line = line.strip().split(',')
        codes[line[0]] = line[1]
        subjects[line[1]] = line[0]
#   Populates the globally declared options() priority queue with courses,
#   then adds their respective weights
def getOptions(page, student):
    prev = set()
    for line in page:
        code = line[3][0] + " " + line[4][0]
        if code not in prev:
            if line[3][0] in student.courses:
                if line[4][0] in student.courses[line[3][0]]:
                    continue
            name = code + ":   "
            for word in line[10]:
                name += " " + word
            weights.put((getWeight(line, student), name))
            prev.add(code)
#   Gets the weight of a course offering, or how much the student is predicted
#   to want to take the course, by starting from 0 and adding or subtracting
#   based on the following algorithm:
#   +8 if subject is the student's major
#   	reduce to +6 if student already has 6+ credits for major
#   +5 if subject is the student's minor
#	    reduce to +3 if student already has 3+ credits for minor
#   +3 for each attribute the subject has that the student needs (SS/HU/NS/etc)
#       double this weight if the student is an upperclassman
#       multiply by zero if the course is worth less than 1.0 credits
#   +1 for each course the student has taken in that subject
#   -3 if student has taken a course in that subject and the course is numbered
#   lower than 10
#   -3 if the course is worth less than 1.0 credits
def getWeight(line, student):
    reqs = {"SS", "HU", "NS", "NSEP"}
    weight = 0
    depts = [line[1][0], line[3][0]]
    number = line[4][0]
    attrs = []
    if depts[1] in student.courses:
        if number in student.courses[depts[1]][0]:
            return 50
    if ("FYS" in line[10] and len(student.majors[0]) > 0) or \
    "Thesis" in line[10] or "Comprehensive" in line[10] or "DirRdg" in line[10]\
    or "Senior" in line[10]:
        return 50
    for dept in depts:
        if dept in codes:
            if codes[dept] in student.majors[0]:
                weight -= 6 + 2*(len(student.courses[line[3][0]][0]) < 6)
            elif codes[dept] in student.majors[1]:
                weight -= 3 + 2*(len(student.courses[line[3][0]][0]) < 3)
            break
    if depts[1] in student.courses:
        weight -= 1*(len(student.courses[line[3][0]][0]))
        if ord(number[1]) < 72:
            weight += 3*(int(number[1]) < 1 or int(number[1]) > 8)
    weight += 3*(float(line[11][0]) < 1)
    for req in reqs:
        for section in line:
            if req in section:
                weight -= (2 + 2*(len(student.majors[0]) > 0)) \
                *(student.attrs[req] == False)
    return weight
def main():
    getAllSubjects()
    user = Student(parseFile("malhar_report.txt"))
    getOptions(parseFile("fall_2021.txt"), user)
    user.display()

main()
