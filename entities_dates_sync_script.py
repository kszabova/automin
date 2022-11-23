import re
import string

import datefinder


class AnnotationParser:
    '''
    Parses an initial annotation and retrieves its date, atttendees list and items.
    '''
    def __init__(self, filename):
        '''
        Constructor.
        Accepts the name of file with annotation to parse as parameter.
        '''
        self.__filename = filename
        self.__annotation = None
        self.__date = None
        self.__attendees = []
        self.__items = []

    def date(self):
        return self.__date

    def attendees_list(self):
        return self.__attendees

    def annotation(self):
        return self.__annotation

    def all_items(self):
        return self.__items

    def parse(self):
        '''
        Parses an initial annotation and retrieves its date, atttendees list and items.
        '''
        with open(self.__filename) as f:
            self.__annotation = f.readlines()

            if self.__annotation:
                start, line_to_add = False, ''

                for line in self.__annotation:
                    line = line.strip()

                    if 'DATE :' in line:
                        self.__date = line
                        continue

                    if 'ATTENDEES :' in line:
                        self.__attendees = line
                        continue

                    if 'SUMMARY' in line: start = True
                    elif start:
                        if line.strip() == 'Minuted by: Team ABC':
                            continue

                        if line_to_add == '':
                            line_to_add = line.strip()
                        elif len(line) > 0 and line[0] == '-':
                            if len(line_to_add) > 0:
                                self.__items.append(line_to_add)
                            line_to_add = line
                        elif len(line) > 0:
                            line_to_add += ' ' + line

                if len(line_to_add) > 0:
                    self.__items.append(line_to_add)


class AnnotationToTranscriptMatcher:
    '''
    Selects annotation items that contain no made-up entities, i.e. only
    those entities that exist in the transcript.
    '''
    def __init__(self, transcript, annotation_items):
        '''
        Constructor.
        Accepts the transcript to match against
        and the list of annotation items as parameters.
        '''
        self.__transcript = "\n".join(transcript)
        self.__annotation_items = annotation_items

        self.__patterns = [
            'PERSON[0-9]{1,2}', 'Person[0-9]{1,2}', 'person[0-9]{1,2}',
            'ORGANIZATION[0-9]{1,2}', 'Organization[0-9]{1,2}', 'organization[0-9]{1,2}',
            'LOCATION[0-9]{1,2}', 'Location[0-9]{1,2}', 'location[0-9]{1,2}',
            'PROJECT[0-9]{1,2}', 'Project[0-9]{1,2}', 'project[0-9]{1,2}',
            'OTHER[0-9]{1,2}', 'Other[0-9]{1,2}', 'other[0-9]{1,2}',
            'ANNOTATOR[0-9]{1,2}', 'Annotator[0-9]{1,2}', 'annotator[0-9]{1,2}',
            'URL[0-9]{1,2}', 'Url[0-9]{1,2}', 'url[0-9]{1,2}',
            'NUMBER[0-9]{1,2}', 'Number[0-9]{1,2}', 'number[0-9]{1,2}',
            'PASSWORD[0-9]{1,2}', 'Password[0-9]{1,2}', 'password[0-9]{1,2}',
            'PHONE[0-9]{1,2}', 'Phone[0-9]{1,2}', 'phone[0-9]{1,2}',
            'PATH[0-9]{1,2}', 'Path[0-9]{1,2}', 'path[0-9]{1,2}',
            'EMAIL[0-9]{1,2}', 'Email[0-9]{1,2}', 'email[0-9]{1,2}'
        ]

    def match(self):
        '''
        Matches annotation items with transcript.
        '''
        result = []

        for item in self.__annotation_items:
            made_up = False

            for pattern in self.__patterns:
                if not self.__match_found(re.findall(pattern, item)):
                    made_up = True
                    break

            if not made_up:
                result.append(item)

        return result

    def __match_found(self, matches):
        for mtch in matches:
            if mtch not in self.__transcript:
                return False
        return True


class TranscriptToAnnotationMatcher:
    '''
    Selects transcript items that contain entities, missing in the annotation.
    '''
    def __init__(self, transcript, annotation_items):
        '''
        Constructor.
        Accepts the transcript to match against
        and the list of annotation items as parameters.
        '''
        self.__transcript = transcript
        self.__annotation = annotation_items
        self.__annotation_as_str = "\n".join(annotation_items)
        self.__existing_dates = []

        self.__patterns = [
            'PERSON[0-9]{1,2}', 'Person[0-9]{1,2}', 'person[0-9]{1,2}',
            'ORGANIZATION[0-9]{1,2}', 'Organization[0-9]{1,2}', 'organization[0-9]{1,2}',
            'LOCATION[0-9]{1,2}', 'Location[0-9]{1,2}', 'location[0-9]{1,2}',
            'PROJECT[0-9]{1,2}', 'Project[0-9]{1,2}', 'project[0-9]{1,2}',
            'OTHER[0-9]{1,2}', 'Other[0-9]{1,2}', 'other[0-9]{1,2}',
            'ANNOTATOR[0-9]{1,2}', 'Annotator[0-9]{1,2}', 'annotator[0-9]{1,2}',
            'URL[0-9]{1,2}', 'Url[0-9]{1,2}', 'url[0-9]{1,2}',
            'NUMBER[0-9]{1,2}', 'Number[0-9]{1,2}', 'number[0-9]{1,2}',
            'PASSWORD[0-9]{1,2}', 'Password[0-9]{1,2}', 'password[0-9]{1,2}',
            'PHONE[0-9]{1,2}', 'Phone[0-9]{1,2}', 'phone[0-9]{1,2}',
            'PATH[0-9]{1,2}', 'Path[0-9]{1,2}', 'path[0-9]{1,2}',
            'EMAIL[0-9]{1,2}', 'Email[0-9]{1,2}', 'email[0-9]{1,2}'
        ]

        self.__find_existing_date_specifications()

    def match(self):
        '''
        Matches transcript items with annotation.
        '''
        result = []

        for line in self.__transcript:
            not_found = False

            if len(line.strip()) > 0:
                for pattern in self.__patterns:
                    if self.__match_not_found(re.findall(pattern, line)):
                        not_found = True
                        break

                if not_found:
                    result.append('-' + line[:-1])
                else:
                    found_dates = self.__missing_date_specification(line)

                    if len(found_dates) > 0:
                        result.append(line)

        return result

    def __find_existing_date_specifications(self):
        '''
        Iterates over annotation lines without made up entities 
        and returns those that contain any date specifications.
        '''
        for item in self.__annotation:
            found_dates = [match for match in datefinder.find_dates(item)]

            if len(found_dates) > 0:
                self.__existing_dates.extend(found_dates)

    def __match_not_found(self, matches):
        for mtch in matches:
            if mtch not in self.__annotation_as_str:
                return True

        return False

    def __missing_date_specification(self, line):
        '''
        We inspect a transcript whether it contains any date relevant information
        that was missed in annotation.
        '''
        return [d for d in datefinder.find_dates(line) if d not in self.__existing_dates]


def main():
    '''
    Main function.
    '''
    def store_output_as_file(filename, _output):
        '''
        Writes output to .txt file
        '''
        with open(filename, 'w') as outputfile:
            print(_output, file = outputfile)


    with open('in.txt') as f:
        transcript = f.readlines()

        antn_parser = AnnotationParser('out.txt')
        antn_parser.parse()

        att = AnnotationToTranscriptMatcher(transcript, antn_parser.all_items())
        existing_items = att.match()

        tta = TranscriptToAnnotationMatcher(transcript, existing_items)
        missing_items = tta.match()

        output = antn_parser.date() + "\n"
        output += antn_parser.attendees_list() + "\n\n\nSUMMARY-\n"
        output += "\n".join(existing_items + missing_items)
        output +="\n\n\nMinuted by: Team ABC"

        store_output_as_file('new_annotation.txt', output)


if __name__ == '__main__':
    main()
