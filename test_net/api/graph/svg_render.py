from api.note import pianoNote

def LineToNote(line : str) -> list:
    str_list = line.split(' ')
    nott_list = []
    modify_map = {}
    on_chord = 'n'
    for s in str_list:
        if s == '':
            continue
        n_not = pianoNote(0,0,0,50)
        new_chord = on_chord
        if s[0] == '{':
            on_chord = 'y'
            new_chord = 'y'
            s = s[1:]
        elif s[-1] == '}':
            new_chord = 'n'
            on_chord  = 'e'
            s = s[:-1]
        
        n_not.fromStr(s)

        pure_name = n_not.name[0] + n_not.name[-1]
        if modify_map.get(pure_name,'') !='' and n_not.Modifier != '':
            if n_not.Modifier == 'n':
                modify_map.pop(pure_name)
            else : 
                modify_map.update({pure_name : n_not.Modifier})
        elif modify_map.get(pure_name,'') =='' and n_not.Modifier != '' and n_not.Modifier != 'n':
            modify_map.update({pure_name : n_not.Modifier})
        elif modify_map.get(pure_name,'') != '' and n_not.Modifier == '' :
            n_not.setModifier(modify_map.get(pure_name,''))
            n_not.Modifier = ''

        n_not.setChord(on_chord)
        on_chord = new_chord
        nott_list.append(n_not)

    return nott_list

def NoteNameToVex(n : str):
    return n[0:-1] + '/' + n[-1]

def SetOneNote(chord_str : str, chord_time : int, chord_m : list, chord_dot : int, clef : str) -> str:
    n_str = 'new Vex.Flow.StaveNote({{clef: "{}", keys: [{}], duration: "{}" }})'
    if chord_time == 2 : 
        chord_time = 'h'
    elif chord_time == 1 :
        chord_time = 'w'
    elif chord_time == 4 :
        chord_time = 'q'
    else:
        chord_time = str(chord_time)
    chord_time = chord_time + chord_dot*'d'
    n_str = n_str.format(clef,chord_str,chord_time)
    for ii,mm in enumerate(chord_m) : 
        if mm != '':
            n_str = n_str + ('.addAccidental({}, new VF.Accidental("{}"))'.format(ii,mm))
    for i in range(chord_dot):
        n_str = n_str + '.addDotToAll()'
    return n_str

def OneLineVexFlow(note_list : list, clef : str) -> list:
    chord_str = ''
    chord_time = 0
    chord_m = []
    chord_dot = 0
    ans_str = []
    for n in note_list:
        n : pianoNote
        if n.chord != 'n':
            chord_str = chord_str + ("\"{}\"".format(NoteNameToVex(n.name))) + ','
            chord_time = n.TimeDiv
            chord_dot = n.dot
            chord_m.append(n.Modifier)
            if n.chord != 'e':
                continue
        if chord_str != '':
            ans_str.append(SetOneNote(chord_str[0:-1],chord_time,chord_m,chord_dot,clef))
            chord_str = ''
            chord_time = 0
            chord_m = []
            chord_dot = 0
            if n.chord == 'e':
                continue

        new_single = SetOneNote("\""+NoteNameToVex(n.name)+"\"",n.TimeDiv,[n.Modifier],n.dot,clef)
        ans_str.append(new_single)

    return ans_str


def WirteScriptToFile(file_name : str, note_lists : list, meters : list, clefs : list):
    f = open(file_name,'wt',encoding='utf-8')
    f.write('''<!DOCTYPE html>
<head>
    <meta charset="UTF-8">
    <script src="vexflow-min.js"></script>
</head>
<body>
    <div id="boo"></div>
    <script>
        VF = Vex.Flow;

var div = document.getElementById("boo")
var renderer = new VF.Renderer(div, VF.Renderer.Backends.SVG);

renderer.resize(800, 600);
var context = renderer.getContext();
context.setFont("Arial", 10, "").setBackgroundFillStyle("#eed");
    ''')

    for i in range(note_lists.__len__()):
        if i == 0:
            stave_str = 'var stave{} = new VF.Stave(10, 40, 800);'.format(i)
        else:
            stave_str = 'var stave{} = new VF.Stave(stave{}.x, stave{}.y+stave{}.height, 800);'.format(i,i-1,i-1,i-1)
        stave_str = stave_str + ('\nstave{}.addClef("{}").addTimeSignature("{}/{}");'.format(i,clefs[i],meters[i][0],meters[i][1]))
        stave_str = stave_str + ('\nstave{}.setContext(context).draw();\n'.format(i))
        start = 'var notes{} = ['.format(i)
        ll = OneLineVexFlow(note_lists[i],clefs[i])
        for j,s in enumerate(ll):
            start = start + '\n' + s
            if j != ll.__len__()-1:
                start+=','
        start = start+'\n];'
        tail = '''
        var beams{} = VF.Beam.generateBeams(notes{});
Vex.Flow.Formatter.FormatAndDraw(context, stave{}, notes{});
beams{}.forEach(function(b) {{b.setContext(context).draw()}})\n
        '''.format(i,i,i,i,i)
        f.write(stave_str)
        f.write(start)
        f.write(tail)
    f.write('''
    </script>
</body>
    ''')

def TextFileAna(file_name : str) -> dict:
    file_content = []
    with open(file_name,'rt',encoding='utf-8') as f:
        file_content = f.readlines()
    
    meters     = []
    clefs      = []
    note_lists = []

    for line in file_content:
        is_voice = line.find('[')
        if is_voice != -1:
            beg = is_voice+1
            has_clef = line.find("\\clef")
            if has_clef != -1:
                beg_clef = line.find('<')
                end_clef = line.find('>')
                clefs.append(line[beg_clef+1 : end_clef])
                beg = end_clef + 1
            else:
                clefs.append("treble")
            has_meter = line.find("\\meter")
            if has_meter != -1 :
                end_met = line.find('>',has_meter)
                meters.append(line[has_meter : end_met + 1])
                beg = end_met + 1
            else : 
                meters.append('')
            note_lists.append(LineToNote(line[beg:line.rfind(']')]))
    
    return {'meters' : meters, 'clefs' : clefs, 'note_lists' : note_lists}


def SvgRender(file_name : str):
    f_content = TextFileAna(file_name)

    meters     = f_content['meters']
    clefs      = f_content['clefs']
    note_lists = f_content['note_lists']

    for i in range(0,meters.__len__()):
        if meters[i] == '':
            meters[i] = ()
            continue
        beg = meters[i].find('\"')
        end = meters[i].find("\"",beg+1)
        num_str = meters[i][beg+1:end].split('/')
        meters[i] = (int(num_str[0]),int(num_str[1]))

    WirteScriptToFile(file_name+'.html',note_lists,meters,clefs)


if __name__ == '__main__':
    SvgRender('./data/trans_1.txt')
