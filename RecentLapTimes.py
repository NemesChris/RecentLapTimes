import os
import sys
import ac
import acsys

from sim_info import info

# maximum korok szama, amit mutasson az app
maxLaps = 10


l_lapcount = 0
l_besttext = 0
l_besttime = 0
lapcount = 0
l_laptime = 0
l_lastlaptime = 0
l_korszam = 1
lapList = []
korList = []
kiirasHelyek = []
korHelyek = []
palyanev = ""
kocsinev = ""
idodirectory = ""
besttime = 99999999
invalidlap = False
lapTipusokList = []  # 0 - piros, 1 - sima, 2 - rekord


def acMain(ac_version):
    global l_lapcount, l_laptime, l_lastlaptime, l_korszam, l_besttext, l_besttime
    global maxLaps
    global kiirasHelyek
    global palyanev
    global kocsinev
    global korHelyek
    global besttime
    global idodirectory
    global invalidlap
    global rekord

    palyanev = ac.getTrackName(0)
    kocsinev = ac.getCarName(0)

    # legjobb ido betoltese palya+kocsi szerint
    iniDirectory = os.path.dirname(os.path.abspath(__file__))
    iniDirectory = iniDirectory + "/records/"
    idodirectory = iniDirectory + "/" + palyanev + "/" + kocsinev + "/"

    if not os.path.exists(idodirectory):
        ac.log('ini directory ' + iniDirectory + ' does not exist, try to create it')
        os.makedirs(idodirectory)
    try:
        with open(idodirectory + 'record.txt') as f:
            lines = f.readlines()
            besttime = int(lines[0])
            ac.log("record.txt tartalma: " + str(lines))
    except Exception as e:
        ac.log("Meg nincs rekord kor ezzel az osszeallitassal: " + str(palyanev) + "/" + str(kocsinev))
        ac.log(str(e))
        f = open(idodirectory + "record.txt", "w+")
        f.write("99999999")
        f.close()
        besttime = 99999999

    # Eredmeny-doboz beallitasa
    appWindow = ac.newApp("RecentLapTimes")
    ac.setSize(appWindow, 250, 65 + maxLaps * 30 + 110)
    ac.setBackgroundOpacity(appWindow, 0)
    ac.drawBorder(appWindow, 0)

    # cimkek felul
    l_lapcount = ac.addLabel(appWindow, "Laps:              Times:")
    ac.setPosition(l_lapcount, 5, 35)
    ac.setCustomFont(l_lapcount, "Formula", 0, 0)
    ac.setFontSize(l_lapcount, 18)
    ac.setFontColor(l_lapcount, 0.7, 0.7, 0.7, 1)

    # Rekord kor szoveg
    l_besttext = ac.addLabel(appWindow, "All Time Best:")
    ac.setPosition(l_besttext, 5, 65 + maxLaps * 30 + 45)
    ac.setCustomFont(l_besttext, "Formula", 0, 0)
    ac.setFontSize(l_besttext, 16)
    ac.setFontColor(l_besttext, 0.7, 0.7, 0.7, 1)


    # REKORD KoR
    if besttime == 99999999:
        l_besttime = ac.addLabel(appWindow, "-:--.---")
    else:
        l_besttime = ac.addLabel(appWindow, time_to_string(besttime, True))
    ac.setPosition(l_besttime, 90, 65 + maxLaps * 30 + 80)
    ac.setCustomFont(l_besttime, "Formula", 0, 0)
    ac.setFontSize(l_besttime, 14)
    ac.setFontColor(l_besttime, 0.7, 0.7, 0.7, 1)

    ac.log("Max Laps: " + str(maxLaps))

    # 0 - maxLaps-1
    for i in range(0, maxLaps):
        l_lastlaptime = ac.addLabel(appWindow, "")
        ac.setCustomFont(l_lastlaptime, "Formula", 0, 0)
        ac.setFontSize(l_lastlaptime, 14)
        ac.setFontColor(l_lastlaptime, 0.7, 0.7, 0.7, 1)

        l_korszam = ac.addLabel(appWindow, "")
        ac.setCustomFont(l_korszam, "Formula", 0, 0)
        ac.setFontSize(l_korszam, 15)
        ac.setFontColor(l_korszam, 0.7, 0.7, 0.7, 1)

        kiirasHelyek.append(l_lastlaptime)
        korHelyek.append(l_korszam)

    z = 0
    ac.log("Letrejott kiirashelyek: " + str(len(kiirasHelyek)) + "   (vart: " + str(maxLaps) + ")")
    for kiiras in kiirasHelyek:
        ac.setPosition(kiiras, 110, 65 + (30 * z))
        z += 1

    z = 0
    for szamhely in korHelyek:
        ac.setPosition(szamhely, 20, 65 + (30 * z))
        z += 1

    ac.log("Generalas kesz.")
    return "RecentLapTimes"


# acsys.CS.LapCount
# acsys.CS.BestLap
# acsys.CS.LastLap
# acsys.CS.LapTime


def acUpdate(deltaT):
    global l_lapcount, lapcount, l_laptime, l_lastlaptime, l_besttext, l_besttime
    global lapList
    global kiirasHelyek, korHelyek
    global maxLaps
    global l_korszam
    global korList
    global besttime
    global idodirectory
    global invalidlap
    global lapTipusokList

    laps = ac.getCarState(0, acsys.CS.LapCount)    

    if laps <= lapcount and laps > 0:
        if int(info.physics.numberOfTyresOut) > 3:            
            invalidlap = True

    if laps > lapcount:
        lapcount = laps
        ac.log("------------------------------")
        ac.log("------------------------------")
        ac.log("UJ KOR (" + str(lapcount) + ".) BEFEJEZVE")
        ac.log("------------------------------")
        rekord = False

        if lapcount == 1:
            # első, felvezető kör volt
            invalidlap = True

        ac.log("LAP WAS INVALID? " + str(invalidlap))

        ac.log("{} laps completed".format(lapcount))
        ac.console("{} laps completed".format(lapcount))

        lastlaptime = ac.getCarState(0, acsys.CS.LastLap)
        # jobb volt, mint a rekord?
        ac.log("Rekordkor eddig: " + str(besttime))
        ac.log("Mostani kor meg: " + str(lastlaptime))
        if besttime > lastlaptime and lastlaptime != 0:
            ac.log("UJ REKORD (elvileg)!")
            rekord = True
            besttime = lastlaptime

        lastlaptime = str(time_to_string(lastlaptime, True))

        lapList.append(lastlaptime)
        korList.append(str(lapcount))
        ac.log("Uj kor hozzaadva a listahoz: " + str(lastlaptime))

        ac.log("Eddig ennyi kor van bejegyezve: " + str(len(lapList)))
        if len(lapList) > maxLaps:
            lapList.pop(0)
            kibaszottKor = korList.pop(0)

            ac.log("Sok kor volt mar, az eddigi elsot(" + str(kibaszottKor) + ".) kibasszuk!")          

        # elobb a nullazas
        z = 0
        for hely in kiirasHelyek:
            ac.setFontColor(kiirasHelyek[z],  0.7, 0.7, 0.7, 1)
            ac.setFontColor(korHelyek[z], 0.7, 0.7, 0.7, 1)
            z += 1
        ac.log("Az UTOLSO teljesitett: " + str(lapcount) + ". kor volt")
        if rekord == True:
            # kellene tudni, hogy a rekord az hanyas helyre kerul, de mindig az utolsohoz...
            # ha eddig mashol volt, az torolni (vissza feherre) kell!

            # ha szabalyos kor volt
            if invalidlap == True:
                # majd az utolsot lilara
                ac.log("Rekord, de invalid lett [0]")
                lapTipusokList.append(0)
            else:               
                # majd az utolsot lilara
                ac.log("Rekord lett szabalyosan [2]")
                ac.log("Bekerul a mentesbe is!")
                lapTipusokList.append(2)
                ac.setText(l_besttime, lastlaptime)
                try:
                    f = open(idodirectory + "record.txt", "w+")
                    f.write(str(besttime))
                    f.close()
                    pass
                except Exception as e:
                    ac.log(str(e))
        else:
            # nem rekord kor, csak sima
            if invalidlap == True:
                # majd az utolsot lilara
                ac.log("Sima kor volt csak, de invalid is [0]")
                lapTipusokList.append(0)
            else:
                # majd az utolsot lilara
                ac.log("Sima kor volt csak [1]")
                lapTipusokList.append(1)

        # meg be kell tenni a megfelelot a megfelelo helyre
        z = 0
        for kiiras in lapList:
            ac.setText(kiirasHelyek[z], lapList[z])
            z += 1

        z = 0
        for kor in korList:
            ac.setText(korHelyek[z], str(korList[z]) + ".")
            z += 1

        ac.log("------------")
        ac.log("Szinezes")
        ac.log("------------")
        # meg be kell szinezni a szinertekek alapjan
        voltmarrekord = False
        if lapcount > 0:
            ac.log("Eddig teljesitett korok szama: " + str(lapcount ))
            ac.log("Tipusok: eddig" + str(lapTipusokList))

            if len(lapTipusokList) > maxLaps:
                toroltlap = lapTipusokList.pop(0)
                ac.log("Sok tipus volt, az elsot (" + str(toroltlap) + ") toroltuk")            
            for i in range(len(lapTipusokList)-1,-1,-1):
                ac.log("Ez a kor van soron szinezesben: " + str(i+1))
                ac.log("Tipusa: " + str(lapTipusokList[i]))
                if lapTipusokList[i] == 0:
                    # piros lap
                    # 0, 1 volt, es most a 3. korben a 3-1-edikre akarja betenni
                    # de ott csak 0 es 1 hely van, mert osszesen a MaxLaps az ebben az esetben 2
                    # tehat, ha mar tobb kor van, mint a maxlaps, akkor csak a maxlaps-nyi hely van
                    ac.setFontColor(kiirasHelyek[i], 1, 0, 0, 1)
                    ac.setFontColor(korHelyek[i], 1, 0, 0, 1)
                    ac.log("Ez invalid volt [0] >>> piros")
                    ac.log("Helye: a listaban: " + str(i+1))
                elif lapTipusokList[i] == 1:
                    # sima lap
                    ac.setFontColor(kiirasHelyek[i], 0.7, 0.7, 0.7, 1)
                    ac.setFontColor(korHelyek[i], 0.7, 0.7, 0.7, 1)
                    ac.log("Ez sima lap volt [1] >>> feher")
                    ac.log("Helye: a listaban: " + str(i+1))
                elif lapTipusokList[i] == 2:
                    # rekord lap
                    if voltmarrekord == False:
                        ac.setFontColor(kiirasHelyek[i], 1, 0, 1, 1)
                        ac.setFontColor(korHelyek[i], 1, 0, 1, 1)
                        ac.log("Ez rekord kor volt [2] >>> lila")
                        ac.log("Helye: a listaban: " + str(i+1))
                        voltmarrekord = True
                    else:
                        ac.setFontColor(kiirasHelyek[i], 0.7, 0.7, 0.7, 1)
                        ac.setFontColor(korHelyek[i], 0.7, 0.7, 0.7, 1)
                        ac.log("Ez sima lap volt, mert mar volt rekord kesobb [2 > 1] >>> feher")
                        ac.log("Helye: a listaban: " + str(i+1))
                ac.log("--------")
        invalidlap = False

# + legjobb korido betoltes mentes milliszekundban!
# nem merheto kort ne szamolja, es legyen piros
# korido-ujraszinezesnel vegye figyelembe, hogy volt mar szines elotte


def time_to_string(t, include_ms=True):
    try:
        hours, x = divmod(int(t), 3600000)
        mins, x = divmod(x, 60000)
        secs, ms = divmod(x, 1000)
        if not include_ms:
            return '%d:%02d' % (mins, secs)
        return '%d.%03d' % (secs, ms) if mins == 0 else '%d:%02d.%03d' % (mins, secs, ms)
    except Exception:
        return '--:--.---'


def acShutdown():
    ac.log("RecentLapTimes is closing now...")
    return


# fent meg kell adni, mennyi legyen a max lap, amit néz
# ha a felvezető piros,
# akkor ő beteszi pirosnak az első kört is!
# vajon az hanyadik körnek van véve?