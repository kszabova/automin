import re
import string


class EntitiesSynchronizer:
    '''
    Synchronizes transcript entities with those in annotation.
    '''
    def __init__(self, transcript, annotation):
        '''
        Constructor.
        Accepts the transcript and annotation to sync.
        '''
        self.__transcript = transcript
        self.__annotation = annotation

        self.__patterns = [
            'PERSON[0-9]{1,2}', 'Person[0-9]{1,2}', 'person[0-9]{1,2}',
            'ORGANIZATION[0-9]{1,2}', 'Organization[0-9]{1,2}', 'organization[0-9]{1,2}',
            'LOCATION[0-9]{1,2}', 'Location[0-9]{1,2}', 'location[0-9]{1,2}',
            'PROJECT[0-9]{1,2}', 'Project[0-9]{1,2}', 'project[0-9]{1,2}',
            'OTHER[0-9]{1,2}', 'Other[0-9]{1,2}', 'other[0-9]{1,2}'
        ]

    def match(self):
        self.__annotation_to_transcript()
        self.__transcript_to_annotation()

        return re.sub(' +', ' ', self.__annotation).strip() 

    def __annotation_to_transcript(self):
        '''
        Matches annotation with transcript.
        '''
        for pattern in self.__patterns:
            if not self.__match_found_in_transcript(re.findall(pattern, self.__annotation)):
                self.__annotation = re.sub(pattern, '', self.__annotation)

    def __match_found_in_transcript(self, matches):
        for mtch in matches:
            if mtch not in self.__transcript:
                return False
        return True

    def __transcript_to_annotation(self):
        '''
        Matches transcript items with annotation.
        '''
        for pattern in self.__patterns:
            if self.__match_found_in_annotation(re.findall(pattern, self.__transcript)):
                occurrences = re.finditer(pattern, self.__transcript)

                for occurrence in occurrences:
                    ostart = occurrence.start()
                    oend = occurrence.end()

                    start = self.__transcript[:ostart].rfind('.')
                    if start < 0:
                        start = 0

                    sentence = self.__transcript[start + 1:ostart]
                    sentence += ' ' + occurrence.group() + ' '

                    end = self.__transcript[oend:].find('.')
                    if end < 0:
                        sentence += self.__transcript[oend + 1:]
                    else:
                        sentence += self.__transcript[oend + 1: oend + end + 1]

                    self.__annotation = self.__annotation[:-1]
                    self.__annotation += ' ' + sentence + '\n'                

    def __match_found_in_annotation(self, matches):
        for mtch in matches:
            if mtch not in self.__annotation:
                return True

        return False
