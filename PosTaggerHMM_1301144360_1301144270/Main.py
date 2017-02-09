States = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'HYPH', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NN', 'NNS', 'NNP', 'NNPS', 'PDT',
          'POS', 'PP', 'PP$', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', '.', '\'\'', ':', '``', ',', 'SYM', 'TO',
          'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB']

probabilitas_awal = {}
probabilitas_transisi = {}
probabilitas_emisi = {}

for i in range(len(States)):
    probabilitas_transisi[States[i]] = {}
    probabilitas_awal[States[i]] = 0
    probabilitas_emisi[States[i]] = {}
    for j in range(len(States)):
        probabilitas_transisi[States[i]][States[j]] = 0

def Learn_Param(filetraining):
    ftrain = open(filetraining, 'r')
    kata_baru = True
    hitung_awal = 0.0
    kata_sebelumnya = ''
    for baris in ftrain.readlines():
        if (baris.strip() != ''):
            cek_baris = baris.replace(' ', '\t')
            kata_kata = cek_baris.split('\t')
            tag = kata_kata[1].strip('\r\n')
            if (States.count(tag) == 0):
                tag = 'SYM'
            if (kata_baru == True):
                hitung_awal += 1
                probabilitas_awal[tag] += 1
                kata_sebelumnya = tag
                kata_baru = False
            elif (tag == '.'):
                kata_baru = True
                probabilitas_transisi[kata_sebelumnya]['.'] += 1
                kata_sebelumnya = ''
            else:
                if (probabilitas_transisi[kata_sebelumnya].has_key(tag) == False):
                    probabilitas_transisi[kata_sebelumnya]['SYM'] += 1
                    kata_sebelumnya = 'SYM'
                else:
                    probabilitas_transisi[kata_sebelumnya][tag] += 1
                    kata_sebelumnya = tag
            probabilitas_emisi[tag].setdefault(kata_kata[0], 0)
            probabilitas_emisi[tag][kata_kata[0]] += 1
        else:
            kata_baru = True
    ftrain.close()

    for i in range(len(States)):
        hitung = 0.0
        for j in range(len(States)):
            hitung += probabilitas_transisi[States[i]][States[j]]
            if (hitung_awal > 1):
                probabilitas_awal[States[i]] /= hitung_awal
        for j in range(len(States)):
            if (hitung > 0):
                probabilitas_transisi[States[i]][States[j]] /= hitung
            else:
                break
    return 0

def Viterbi(Observasi, states, start, trans, emission):
    V = [{}]
    path = {}
    final_path = ''
    final_tag = ''
    for tag in states:
        try:
            V[0][tag] = start[tag] * emission[tag][Observasi[0]]
            path[tag] = tag
        except KeyError:
            try:
                V[0][tag] = start[tag] * emission[tag][Observasi[0].lower()]  #cek lowercase
                path[tag] = tag
            except KeyError:
                try:
                    V[0][tag] = start[tag] * emission[tag][
                        Observasi[0][0:1].upper() + Observasi[0][1:-1]]  #cek uppercase
                    path[tag] = tag
                except KeyError:
                    V[0][tag] = 0
    for i in range(1, len(Observasi)):
        V.append({})
        max_tag = ''
        max_prob = 0.0
        for tag1 in states:
            path_probs = []
            for tag2 in states:
                try:
                    path_probs.append(V[i - 1][tag2] * emission[tag1][Observasi[i]] * trans[tag2][tag1])
                except KeyError:
                    try:
                        path_probs.append(V[i - 1][tag2] * emission[tag1][Observasi[i].lower()] * trans[tag2][tag1])  #cek lowercase
                    except KeyError:
                        try:
                            path_probs.append(V[i - 1][tag2] * emission[tag1][Observasi[i][0:1].upper() + Observasi[i][1:-1]] * trans[tag2][tag1])  #cek uppercase
                        except KeyError:
                            path_probs.append(0)
                if (path_probs[-1] > max_prob):
                    max_tag = tag2
                    max_prob = path_probs[-1]

            V[i][tag1] = max(path_probs)
            if (i == len(Observasi) - 1):
                if (final_tag == ''):
                    final_tag = tag1
                elif (V[i][tag1] > V[i][final_tag]):
                    final_tag = tag1

        if (max_tag == ''):
            max_emission = 0.0
            for t in range(len(states)):
                try:
                    if (emission[states[t]][O[i]] > max_emission):
                        max_emission = emission[states[t]][O[i]]
                        max_tag = states[t]
                except KeyError:
                    try:
                        if (emission[states[t]][O[i].lower()] > max_emission):
                            max_emission = emission[states[t]][O[i].lower()]
                            max_tag = states[t]
                    except KeyError:
                        try:
                            if (emission[states[t]][O[i][0:1].upper() + O[i][1:-1]] > max_emission):
                                max_emission = emission[states[t]][O[i][0:1].upper() + O[i][1:-1]]
                                max_tag = states[t]
                        except KeyError:
                            continue
        if (final_path != ''):
            final_path = final_path + "-->" + max_tag
        else:
            final_path = max_tag

    final_path = final_path + "-->" + final_tag

    return final_path

def perataankamus(d):
    values = []
    for value in d.itervalues():
        if isinstance(value, dict):
            values.extend(perataankamus(value))
        else:
            values.append(value)
    return values

def Testing(filetesting):
    ftest = open(filetesting, 'r')
    tag = {}
    observasi = {}
    prediksi = []
    hitung = 0
    for baris in ftest.readlines():
        if (baris.strip() != ''):
            cek_baris = baris.replace(' ', '\t')
            kata_kata = cek_baris.split('\t')
            tag[hitung] = kata_kata[1].strip('\r\n')
            observasi[hitung] = kata_kata[0]
            if (States.count(tag[hitung]) == 0):
                tag[hitung] = 'SYM'
            if (tag[hitung] == '.'):
                print "Urutan tag yang di prediksi: " + Viterbi(observasi, States, probabilitas_awal, probabilitas_transisi, probabilitas_emisi)
                print "Urutan tag sebenarnya: " + '-->'.join(perataankamus(tag))
                print ""
                predicted = Viterbi(observasi, States, probabilitas_awal, probabilitas_transisi, probabilitas_emisi).split('-->')
                for t in range(hitung):
                    if (t<len(predicted) and t<len(tag)):
                        prediksi.append(predicted[t] == tag[t])
                hitung = 0
                tag.clear()
                observasi.clear()
            else:
                hitung += 1
        else:
            hitung = 0

    hitung_benar = 0.0
    for i in range(len(prediksi)):
        if (prediksi[i]):
            hitung_benar += 1

    print ""
    return 100*hitung_benar / float(len(prediksi))


print "----- TRAINING POS.TRAIN.TXT -----"
Learn_Param("pos.train.txt")
print "Transition"
for keys, values in probabilitas_transisi.items():
    print keys
    for items in values.items():
        print "\t" + str(items[0]) + "\t\t" + str(items[1])
    print " "
print ""

print "Emission"
for keys, values in probabilitas_emisi.items():
    print keys
    for items in values.items():
        print "\t" + str(items[1]) + "\t\t" + str(items[0])
    print " "
print ""

print "----- TESTING POS.TEST.TXT -----"
recall = Testing("pos.train.txt")
precision = Testing("pos.test.txt")

print "Recall: " + str(recall) + "%"
print "Precision: " + str(precision) + "%"
print "Akurasi Total: " + str(precision) + "%"