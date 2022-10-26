import os
import sys
import ac
import acsys

from sim_info import info

# maximum körök száma, amit mutasson az app
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

    # legjobb idő betöltése pálya+kocsi szerint
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
        ac.log("Még nincs rekord kör ezzel az összeállítással: " + str(palyanev) + "/" + str(kocsinev))
        ac.log(str(e))
        f = open(idodirectory + "record.txt", "w+")
        f.write("99999999")
        f.close()
        besttime = 99999999

    # Eredmény-doboz beállítása
    appWindow = ac.newApp("RecentLapTimes")
    ac.setSize(appWindow, 250, maxLaps * 80)
    ac.setBackgroundOpacity(appWindow, 0)
    ac.drawBorder(appWindow, 0)


    l_lapcount = ac.addLabel(appWindow, "Laps:           Times:")
    ac.setPosition(l_lapcount, 5, 30)
    ac.setCustomFont(l_lapcount, "Formula", 0, 0)
    ac.setFontSize(l_lapcount, 22)
    ac.setFontColor(l_lapcount, 1, 1, 1, 1)

    l_besttext = ac.addLabel(appWindow, "All Time Best:")
    ac.setPosition(l_besttext, 5, maxLaps * 65 + 45)
    ac.setCustomFont(l_besttext, "Formula", 0, 0)
    ac.setFontSize(l_besttext, 22)
    ac.setFontColor(l_besttext, 1, 1, 1, 1)



    if besttime == 99999999:
        l_besttime = ac.addLabel(appWindow, "-:--.---")
    else:
        l_besttime = ac.addLabel(appWindow, time_to_string(besttime, True))
    ac.setPosition(l_besttime, 90, maxLaps * 65 + 80)
    ac.setCustomFont(l_besttime, "Formula", 0, 0)
    ac.setFontSize(l_besttime, 18)
    ac.setFontColor(l_besttime, 1, 1, 1, 1)


    ac.log("Max Laps: " + str(maxLaps))
    for i in range(0, maxLaps):
        l_lastlaptime = ac.addLabel(appWindow, "")
        ac.setCustomFont(l_lastlaptime, "Formula", 0, 0)
        ac.setFontSize(l_lastlaptime, 18)
        ac.setFontColor(l_lastlaptime, 1, 1, 1, 1)

        l_korszam = ac.addLabel(appWindow, "")
        ac.setCustomFont(l_korszam, "Formula", 0, 0)
        ac.setFontSize(l_korszam, 20)
        ac.setFontColor(l_korszam, 1, 1, 1, 1)

        kiirasHelyek.append(l_lastlaptime)
        korHelyek.append(l_korszam)
        # ac.log("i generálás: " + str(i))

    z = 0
    ac.log("létrejött kiíráshelyek: " + str(len(kiirasHelyek)))
    for kiiras in kiirasHelyek:
        ac.setPosition(kiiras, 90, 60 + (40 * z))
        z += 1

    z = 0
    for szamhely in korHelyek:
        ac.setPosition(szamhely, 20, 60 + (40 * z))
        z += 1

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

    if laps <= lapcount:
        if int(info.physics.numberOfTyresOut) > 3:
            invalidlap = True

    if laps > lapcount:
        lapcount = laps
        ac.log("------------------------------")
        ac.log("ÚJ KÖR (" + str(lapcount) + ".) BEFEJEZVE")
        ac.log("------------------------------")
        rekord = False
        ac.log("LAP INVALID? " + str(invalidlap))

        ac.log("{} laps completed".format(lapcount))
        ac.console("{} laps completed".format(lapcount))

        lastlaptime = ac.getCarState(0, acsys.CS.LastLap)
        # jobb volt, mint a rekord?
        ac.log("Rekordkör eddig: " + str(besttime))
        ac.log("Mostani kör meg: " + str(lastlaptime))
        if besttime > lastlaptime:
            ac.log("ÚJ REKORD (elvileg)!")
            rekord = True
            besttime = lastlaptime

        lastlaptime = str(time_to_string(lastlaptime, True))

        lapList.append(lastlaptime)
        korList.append(str(lapcount))
        ac.log("Új kör hozzáadva: " + str(lastlaptime))

        if len(lapList) > maxLaps:
            lapList.pop(0)
            ac.log("Sok kör volt már, az utolsót kibasszuk")

        if len(korList) > maxLaps:
            korList.pop(0)

        # előbb a nullázás
        z = 0
        for hely in kiirasHelyek:
            ac.setFontColor(kiirasHelyek[z], 1, 1, 1, 1)
            ac.setFontColor(korHelyek[z], 1, 1, 1, 1)
            z += 1
        ac.log("AZ UTOLSÓ teljesített: " + str(lapcount))
        if rekord == True:
            # kellene tudni, hogy a rekord az hanyas helyre kerül, de mindig az utolsóhoz...
            # ha eddig máshol volt, az törölni (vissza fehérre) kell!

            # ha szabályos kör volt
            if invalidlap == True:
                # majd az utolsót lilára
                ac.log("Rekord, de invalid [0]")
                lapTipusokList.append(0)
            else:
                ac.log("AZ UTOLSÓ: " + str(lapcount))
                # majd az utolsót lilára
                ac.log("rekord lett [2]")
                ac.log("Bekerül a mentésbe!")
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
            # nem rekord kör, csak sima
            if invalidlap == True:
                # majd az utolsót lilára
                ac.log("Sima, de invalid [0]")
                lapTipusokList.append(0)
            else:
                # majd az utolsót lilára
                ac.log("Szimpla fehér [1]")
                lapTipusokList.append(1)

        # még be kell tenni a megfelelőt a megfelelő helyre
        z = 0
        for kiiras in lapList:
            ac.setText(kiirasHelyek[z], lapList[z])
            z += 1

        z = 0
        for kor in korList:
            ac.setText(korHelyek[z], str(korList[z]) + ".")
            z += 1



        ac.log("------------")
        # még be kell színezni a színértékek alapján
        voltmarrekord = False
        if lapcount > 0:
            ac.log("Teljesített körök száma: " + str(lapcount ))
            ac.log("Típusok: eddig" + str(lapTipusokList))

            if len(lapTipusokList) > maxLaps:
                lapTipusokList.pop(0)
                ac.log("Sok típus volt, az elsőt töröltük")
            ac.log("Színezés...")
            for i in range(len(lapTipusokList)-1,-1,-1):
                ac.log("Ez a kör van soron: " + str(i))
                ac.log("típusa: " + str(lapTipusokList[i]))
                if lapTipusokList[i] == 0:
                    # piros lap
                    # 0, 1 volt, és most a 3. körben a 3-1-edikre akarja betenni
                    # de ott csak 0 és 1 hely van, mert összesen a MaxLaps az ebben az esetben 2
                    # tehát, ha már több kör van, mint a maxlaps, akkor csak a maxlaps-nyi hely van
                    ac.setFontColor(kiirasHelyek[i], 1, 0, 0, 1)
                    ac.setFontColor(korHelyek[i], 1, 0, 0, 1)
                    ac.log(" ez invalid volt [0] >>> piros")
                    ac.log("Helye: " + str(i))
                elif lapTipusokList[i] == 1:
                    # sima lap
                    ac.setFontColor(kiirasHelyek[i], 1, 1, 1, 1)
                    ac.setFontColor(korHelyek[i], 1, 1, 1, 1)
                    ac.log("ez sima lap volt [1] >>> fehér")
                    ac.log("Helye: " + str(i))
                elif lapTipusokList[i] == 2:
                    # rekord lap
                    if voltmarrekord == False:
                        ac.setFontColor(kiirasHelyek[i], 1, 0, 1, 1)
                        ac.setFontColor(korHelyek[i], 1, 0, 1, 1)
                        ac.log("ez rekord kor volt [2] >>> lila")
                        ac.log("Helye: " + str(i))
                        voltmarrekord = True
                    else:
                        ac.setFontColor(kiirasHelyek[i], 1, 1, 1, 1)
                        ac.setFontColor(korHelyek[i], 1, 1, 1, 1)
                        ac.log("ez sima lap volt, mert már volt rekord később [2 > 1] >>> fehér")
                        ac.log("Helye: " + str(i))
                ac.log("--------")
        invalidlap = False

# + legjobb köridő betöltés mentés milliszekundban!
# nem mérhető kört ne számolja, és legyen piros
# köridő-újraszínezésnél vegye figyelembe, hogy volt már színes előtte


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
    ac.log("Chris's first app is closing now...")
    return
