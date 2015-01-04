# Course Browser Scraper
# Samantha Voigt

from bs4 import BeautifulSoup as bs
import urllib2
import ast

def getAllCourses(): 
    '''Scrapes all course information from the Wellesley College Course Browser and 
    returns a list of dictionaries corresponding to each course'''
    listOfCourses = []
    page = urllib2.urlopen('http://courses.wellesley.edu/')
    soup = bs(page)
    tableContent = soup.find('tbody')
    cellNames = ['CRN', 'Course', 'Title', 'Current Enrollment', 'Seats Available', \
    'Location(s)', 'Meeting Time(s)', 'Days(s)', 'Instructor', 'Additional Instructor(s)', \
    'Distribution(s)', 'Description', 'Prerequisites']
    
    for row in tableContent.find_all('tr'):
        indivClassDict = {}
        cellNum = 0
        for cell in row.find_all('th'): #every loop is a new if statement that corresponds to cellNum
           
            if cell.contents != []:     
                if cellNum == 0 or cellNum == 2 or cellNum == 3 or cellNum == 6 or cellNum == 10: 
                    #strip for CRN, Title, Current Enrollment, meeting times, and distribution
                    indivClassDict[cellNames[cellNum]] = str(unicode(cell.string))
                    
                    if cellNum == 10 and len(cell.contents) > 1: #when there are more than 1 distribution 
                        distList = []
                        for dist in cell.text.split('\n'):
                            distList.append(str(unicode(dist)))
                        indivClassDict[cellNames[cellNum]] = distList                     
                        
                elif cellNum == 1 or cellNum == 5 or cellNum == 8 or cellNum == 9: 
                    #strip for Course, Location(s), and Instructor and Additional Instructor
                    indivClassDict[cellNames[cellNum]] = str(unicode(cell.find('a').string))
                
                elif cellNum == 4 or cellNum == 7: 
                    #strip for Seats Available and Day(s)
                    indivClassDict[cellNames[cellNum]] = str(unicode(cell.next.next.next.string.strip('\n')))
                
                #need to get the description and the prereqs from the second link
                elif cellNum == 11: 
                    linkTag = str(cell.find('a'))
                    linkPt2 = linkTag[linkTag.find('=')+2:linkTag.find(' onclick')-1]
                    moreLink = ('http://courses.wellesley.edu/' + linkPt2).replace('&amp;','&')
                    page2 = urllib2.urlopen(moreLink)
                    soup2 = bs(page2)     
                    
                    #get description:
                    descStr = ''
                    for string in soup2.find(text="Description").next.next.stripped_strings:
                        descStr = descStr + ' ' + str(unicode(string))
                    indivClassDict[cellNames[cellNum]] = descStr
                    
                    #get prereqs:
                    print indivClassDict["CRN"]
                    try:
                        prereqStr = str(unicode(soup2.find(text="Prerequisite(s)").next.next.string))
                    except AttributeError: 
                        prereqStr = 'Not provided'
                    indivClassDict['Prerequisite(s)'] = prereqStr
            
            #needs to be a separate if statement, not an elif 
            if cellNum <= len(cellNames):
                cellNum += 1
    
        listOfCourses.append(indivClassDict) #should go inside the first loop, but outside the second
        print indivClassDict
    return listOfCourses
    
# semester should be in the format of 'FA14', 'SP15', etc...
        
def writeListFile(L, semester):
    '''Given a list of courses and the semester, writes a file with the list as 
    a string named according to the semester name given'''
    filename = semester + 'coursesFile.txt'
    courseFile = open(filename,'w')
    courseFile.write(str(L))
    courseFile.close()
    
def readCourseFile(filename): 
    '''Takes in a local filename and reads the string inside of the file into a basic 
    Python type (in this case, a list of dictionaries), and returns it.'''
    s = open(filename, 'r').read()
    return ast.literal_eval(s)
    
def updateCourseInfo(semester): 
    '''When a new file of course info needs to get written (or re-written), this 
    funtion will either update the file or write a new one. Will also return the list 
    of courses for immediate use. Semester should be formatted like 'FA14' or 'SP15' '''
    listOfCourses = getAllCourses()
    writeListFile(listOfCourses, semester)
    return listOfCourses

# Should only ever need to call 2 functions (readCourseFile and updateCourseInfo) when using this program
#   use readCourseFile when the course info doesn't need to be updated
#   use updateCourseInfo when the course info does need to be updated
#       both will return a usable list of courses