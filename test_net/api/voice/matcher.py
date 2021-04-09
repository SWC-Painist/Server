from api.note import pianoNote
from api.graph.note_coloring import ColorNote
from api.voice.noteFilter import ShortEventFilter


class picthOnlyMatch:
    '''
    for preview mode
    '''

    def __init__(self,__ref : list):
        self.current = 0
        self.windowCnt = 0
        self.reference = __ref
        self.window = []
        self.NextWindow()
        self.windowCnt = 0

    def NextWindow(self) -> int:
        self.current += self.window.__len__()
        self.windowCnt += 1

        if self.current >= self.reference.__len__():
            return self.current

        self.window.clear()
        for i in range(self.current,self.reference.__len__()):
            n = self.reference[i]
            n : pianoNote
            if n.chord != 'n':
                self.window.append([n,False])
                if n.chord == 'e':
                    break
            else :
                break
        if self.window.__len__() == 0:
            self.window.append([self.reference[self.current],False])
        
        return self.current

    def SegmentMatch(self, notes : list) -> int:
        '''
        return how much notes has been played correct
        '''
        
        for n in notes:
            n : pianoNote
            com = 0
            for index,refn in enumerate(self.window):
                if n.SamePitch(refn[0]) and refn[1] == False:
                    com += 1
                    self.window[index][1] = True
            if com == self.window.__len__():
                self.NextWindow()
        
        return self.current
    

    def End(self) -> bool:
        return self.current == self.reference.__len__()

class Matcher :
    '''
    for segment match
    '''
    def __init__(self,__ref : list):
        self.reference = [[i,-1] for i in __ref]
    
    def pretreatment(self, played : list) -> tuple:
        played = ShortEventFilter(played)
        if played.__len__() == 0:
            return(1,1,[])
        start_note = played[0]
        start_note : pianoNote
        start_time = start_note.start
        for index,n in enumerate(played):
            played[index].start = n.start - start_time
            played[index].end = n.end - start_time
            played[index] = [played[index],-1]
        
        end_time = played[-1][0].start 

        if end_time == 0:
            return (1.0,1.0,played)
        tempo_rate =  self.reference[-1][0].start / end_time

        return (tempo_rate, 1.0,played)

    def match(self, played : list) -> list:
        tempo_rate,velo_rate,played = self.pretreatment(played)
        #print(played)
        for i,ref_note_tp in enumerate(self.reference):
            marked = -1
            for j, played_note_tp in enumerate(played):
                if played_note_tp[1] == -1 and ref_note_tp[0].SamePitch(played_note_tp[0]):
                    if marked == -1:
                        marked = j
                    elif abs(ref_note_tp[0].start - played[marked][0].start*tempo_rate) > abs(ref_note_tp[0].start - played_note_tp[0].start*tempo_rate):
                        marked = j

            if marked != -1:
                self.reference[i][1] = marked
                played[marked][1] = i
        
        back_index = self.reference.__len__() - 1
        while back_index > 0:
            if self.reference[back_index][1] != -1:
                back_index -= 1
                continue
            search_index = back_index - 1
            while search_index >= 0:
                if self.reference[search_index][1] == -1 or (not self.reference[back_index][0].SamePitch(self.reference[search_index][0])) :
                    search_index -= 1
                    continue

                current_played = self.reference[search_index][1]
                current_diff = abs(self.reference[search_index][0].start - played[current_played][0].start*tempo_rate)
                new_diff     = abs(self.reference[back_index][0].start - played[current_played][0].start*tempo_rate)
                if new_diff < current_diff:
                    self.reference[search_index][1] = -1
                    self.reference[back_index][1] = current_played
                    played[current_played][1] = back_index
                    break
                search_index -= 1
            back_index -= 1
        
        res_list = []
        for ele in self.reference:
            if ele[1] != -1:
                if ele[0].chord == 'y' :
                    res_list.append(3)
                elif ele[0].chord == 'e':
                    res_list.append(5)
                else:
                    res_list.append(1)
            else:
                if ele[0].chord == 'y':
                    res_list.append(2)
                elif ele[0].chord == 'e':
                    res_list.append(4)
                else:
                    res_list.append(0) 
        return res_list

class MactherMiddleware:
    def __init__(self, __refs : list):
        self.left  = []
        self.right = []
        self.resault = []

        for i in range(0,__refs.__len__()):
            for j in range(1,__refs[i].__len__()):
                if __refs[i][j].chord !='n' and __refs[i][j-1].chord == 'y':
                    __refs[i][j].start = __refs[i][j-1].start
                    __refs[i][j].end = __refs[i][j-1].end
                else :
                    __refs[i][j].start += __refs[i][j-1].end
                    __refs[i][j].end   += __refs[i][j-1].end
        
        combined_list = []
        left_index,right_index = 0,0
        while left_index != __refs[1].__len__() or right_index != __refs[0].__len__():
            if left_index == __refs[1].__len__():
                cur_index = combined_list.__len__()
                combined_list.extend(__refs[0][right_index : ])
                end_index = combined_list.__len__()
                self.right.extend([i for i in range(cur_index,end_index)])
                break

            elif right_index == __refs[0].__len__() :
                cur_index = combined_list.__len__()
                combined_list.extend(__refs[1][left_index : ])
                end_index = combined_list.__len__()
                self.left.extend([i for i in range(cur_index,end_index)])

                break
            elif __refs[0][right_index].start <= __refs[1][left_index].start :
                combined_list.append( __refs[0][right_index])
                self.right.append(combined_list.__len__() - 1)
                right_index += 1
            else:
                combined_list.append( __refs[1][left_index])
                self.left.append(combined_list.__len__() - 1)
                left_index += 1
        
        self.matcher = Matcher(combined_list)

    def macth(self,played:list):
        self.resault = self.matcher.match(played)
    
    def RendSingleHand(self, hand : list, line_index : int) -> list:
        rendlist = []

        correct_color = "#dcdcdc"
        incorrect_color   = "#fe4354"
        half_correct  = "#ff7f24"

        rend_index = 0
        chord_status = "unset"

        for index,note_in_res in enumerate(hand):
            code = self.resault[note_in_res]
            if code == 0:
                rendlist.append((line_index,rend_index,incorrect_color))
                rend_index+=1
            elif code == 1:
                rendlist.append((line_index,rend_index,correct_color))
                rend_index+=1
            elif code == 2:
                if chord_status == "unset":
                    chord_status = "incorrect"
                elif chord_status == "correct":
                    chord_status = "half_correct"

            elif code == 3:
                if chord_status == "unset":
                    chord_status = "correct"
                elif chord_status == "incorrect":
                    chord_status = "half_correct"

            elif code == 4:
                if chord_status == "unset":
                    chord_status = "incorrect"
                elif chord_status == "correct":
                    chord_status = "half_correct"
                
                if chord_status == "correct":
                    rendlist.append((line_index,rend_index,correct_color))
                elif chord_status == "half_correct":
                    rendlist.append((line_index,rend_index,half_correct))
                else :
                    rendlist.append((line_index,rend_index,incorrect_color))
                
                rend_index += 1

            elif code == 5:
                if chord_status == "unset":
                    chord_status = "correct"
                elif chord_status == "incorrect":
                    chord_status = "half_correct"
                
                if chord_status == "correct":
                    rendlist.append((line_index,rend_index,correct_color))
                elif chord_status == "half_correct":
                    rendlist.append((line_index,rend_index,half_correct))
                else :
                    rendlist.append((line_index,rend_index,incorrect_color))
                
                rend_index += 1
        return rendlist
        

    def RendResault(self,path : str):
        renddict = []

        renddict.extend(self.RendSingleHand(self.right,0))
        renddict.extend(self.RendSingleHand(self.left,1))

        ColorNote(path,renddict,path+".res.html","#dcdcdc")

    def GetScore(self):
        correct = 0
        chord_num, chord_correct = 0,0
        for code in self.resault:
            if code in [1,3,5]:
                correct += 1
            if code in [2,3,4,5]:
                chord_num += 1
            if code in [3,5]:
                chord_correct += 1
        
        right_score = 0
        for note_index in self.right :
            if note_index >= self.resault.__len__():
                continue
            if self.resault[note_index] in [1,3,5]:
                right_score += 1

        left_score = 0
        for note_index in self.left :
            if note_index >= self.resault.__len__():
                continue
            if self.resault[note_index] in [1,3,5]:
                left_score += 1
        if chord_num == 0:
            chord_num,chord_correct = 1,1
        return {"right" : right_score * 100 / self.right.__len__(), 
                "left"  : left_score * 100 / self.left.__len__(),
                "chord" : chord_correct * 100 / chord_num,
                "total" : correct * 100 / self.resault.__len__()}

class pitchOnlyMiddleWare:
    def __init__(self,__ref : list, line_index : int, from_index = 0):
        self.matcher = picthOnlyMatch(__ref[line_index])
        self.last_rend_index = 0
        self.exe_line = line_index
        for i in range(from_index):
            self.matcher.NextWindow()

    def InitExe(self,path : str) :
        ColorNote(path,[(self.exe_line,0,"#00bfff")],path+".exe.html",False)
        self.Rend(path+".exe.html")

    def match(self,played : list):
        self.matcher.SegmentMatch(played)

    def Rend(self,path : str):
        if self.matcher.windowCnt == self.last_rend_index:
            return
        rendlist = [(self.exe_line, i, "#dcdcdc") for i in range(self.last_rend_index,self.matcher.windowCnt)]
        if not self.matcher.End():
            rendlist.append((self.exe_line,self.matcher.windowCnt,"#00bfff"))
            
        self.last_rend_index = self.matcher.windowCnt
        ColorNote(path,rendlist,path,False)

    def GetShouldPlayed(self):
        return self.matcher.windowCnt
    
    def End(self):
        return self.matcher.End()


if __name__ == "__main__" :
    from svg_render import TextFileAna
    f_content = TextFileAna(r'D:\VS_Progs\__CODE__PY\Painist\backend\data\trans_1.txt')
    mw = pitchOnlyMiddleWare(f_content['note_lists'],0)
    mw.InitExe(r"D:\VS_Progs\__CODE__PY\Painist\backend\data\trans_1.txt.html")
    mw.match([pianoNote(72,0,250,50),pianoNote(72,0,250,50)])
    mw.Rend(r'D:\VS_Progs\__CODE__PY\Painist\backend\data\trans_1.txt.html.exe.html')
    mw.match([pianoNote(72,0,250,50),pianoNote(79,0,250,50)])
    mw.Rend(r'D:\VS_Progs\__CODE__PY\Painist\backend\data\trans_1.txt.html.exe.html')
    print("finish")