NUM_NOTENAME_LIST = ['Not Piano Key' for i in range(0,109)]
TELVE_TONE_TEMPERAMENT = ['c_','c#_/db_,','d_','d#_/eb_','e_','f_','f#_/gb_','g_','g#_/ab_','a_','a#_/bb_','b_']

#Generate Notename List
for i in range(0,109):
    if i < 24 : 
        continue
    else:
        octa,num = int((i-24)/12), ((i-24)%12)
        NUM_NOTENAME_LIST[i] = TELVE_TONE_TEMPERAMENT[num].replace('_',str(octa+1))

NUM_NOTENAME_LIST[21] = 'c0'
NUM_NOTENAME_LIST[22] = 'a#0/bb0'
NUM_NOTENAME_LIST[23] = 'b0'


STR_TO_MIDI_MAP = {}

for i,s in enumerate(NUM_NOTENAME_LIST)  :
    if s == 'Not Piano Key':
        continue
    if s.find('/') != -1:
        s = s.split('/')
        STR_TO_MIDI_MAP.update({s[0]:i,s[1]:i})
    else:
        STR_TO_MIDI_MAP.update({s:i})
        

class pianoNote:
    '''
    Note class.
    contains pitch time(length) velocity and name
    '''

    def __init__(self, __mNum : int, __start : int, __end, __velo : int):
        '''
        Args:
        __mNum  : midi node number
        __start : time start
        __end   : time end
        __velo  : note velocity

        constructor for midi event
        '''
        self.MidiNum  = __mNum
        self.start    = __start
        self.end      = __end
        self.velocity = __velo

        self.TimeDiv = 0
        self.chord = 'n'
        self.Modifier = ''
        self.dot = 0
        self.name = NUM_NOTENAME_LIST[self.MidiNum]

    def find_modifier(self, note_str : str):
        sharp = note_str.find('#')
        flat = note_str.find('&')
        if sharp != -1:
            if note_str.find('##') != -1:
                return '##'
            else: 
                return '#'
        elif flat != -1:
            if note_str.find('&&') != -1:
                return 'bb'
            else: 
                return 'b'
        elif note_str.find('n') != -1:
            return 'n'

        return ''

    def fromStr(self, from_str : str):
        back_index = from_str.__len__() - 1
        while back_index >= 0 and from_str[back_index] == '.':
            self.dot = self.dot + 1
            back_index = back_index - 1

        from_str = from_str[0:back_index+1].split('/')

        self.TimeDiv = int(from_str[1])
        note_len = 1000/self.TimeDiv
        note_len = note_len * 1.5**self.dot
        self.end = self.start + note_len

        self.Modifier = self.find_modifier(from_str[0])
        if self.Modifier == '##':
            self.name = from_str[0][0] + self.Modifier + from_str[0][-1]
            fake_name = self.name[0]+self.name[-1]
            self.MidiNum = STR_TO_MIDI_MAP.get(fake_name) + 2
        elif self.Modifier == 'bb':
            self.name = from_str[0][0] + self.Modifier + from_str[0][-1]
            fake_name = self.name[0]+self.name[-1]
            self.MidiNum = STR_TO_MIDI_MAP.get(fake_name) - 2
        elif self.Modifier == 'n':
            self.name = from_str[0][0] + from_str[0][-1]
            self.MidiNum = STR_TO_MIDI_MAP.get(self.name)
        else :
            self.name = from_str[0][0] + self.Modifier + from_str[0][-1]
            self.MidiNum = STR_TO_MIDI_MAP.get(self.name)


    def setChord(self,flag : str):
        self.chord = flag
    
    def setModifier(self,modifier : str):
        if self.Modifier == modifier:
            return

        #remove old
        if self.Modifier == '#' :
            self.MidiNum = self.MidiNum - 1
        elif self.Modifier == '##':
            self.MidiNum = self.MidiNum - 2
        elif self.Modifier == 'b' :
            self.MidiNum = self.MidiNum + 1
        elif self.Modifier == 'bb':
            self.MidiNum = self.MidiNum + 2
        
        #set new
        if modifier == '#' :
            self.MidiNum = self.MidiNum + 1
        elif modifier == '##':
            self.MidiNum = self.MidiNum + 2
        elif modifier == 'b' :
            self.MidiNum = self.MidiNum - 1
        elif modifier == 'bb':
            self.MidiNum = self.MidiNum - 2
        self.Modifier = modifier
        self.name = self.name[0] + modifier + self.name[-1]

    def __eq__(self, __rhs) -> bool:
        '''
        operator=.
        true only if this two notes has same pitch, same length, same velocity
        '''
        return self.MidiNum == __rhs.MidiNum and self.start == __rhs.start and self.end == __rhs.end and self.velocity == __rhs.length
        
    
    def SamePitch(self, __cmp) -> bool:
        '''
        true if this two notes has same pitch
        '''
        return self.MidiNum == __cmp.MidiNum
    
    def __str__(self) -> str:
        return('Note: {}, Name: {}, Start: {}ms, End: {}ms, Velo: {}'.format(self.MidiNum,self.name,self.start,self.end,self.velocity))
    
if __name__ == '__main__':
    print('not the main module only for temperament check')
    for i in NUM_NOTENAME_LIST:
        print(i,end=', ')
   