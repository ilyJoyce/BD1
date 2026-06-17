# BD1-Pi

### Aufbau

Der Pi wird über das GPIO mit dem Motor-Controller verbunden:  

- IN1 = 17
- IN2 = 22
- IN3 = 23
- IN4 = 24

- ENA = 18
- ENB = 19

Siehe https://pinout.xyz/ für die Pin Nummern am Pi.  
Der Motor Controller (L298N Standard Controller Board) steuert die 4 Motoren über die Out 1 - Out 4 Schnittstellen an, Da ein Motor an Out 1 **UND** Out 2 bzw. Out 3 **UND** Out 4 angeschlossen werden *muss*, müssen die jeweils an der gleichen Seite montierten (links oder rechts) an die gleichen 2 Schnittstellen angeschlossen werden. (eg. Motor links vorne und Motor links hinten beide an Out 1 und Out 2)  

#### Spannungsquellen

Der Motor Controller wird über einen T-Connector mit einer LiPo Batterie verbunden, dessen Daten wie folgt lauten:  

- Hersteller: Gens ace
- Konfiguration: 3S, 25C
- Spannung: 11,1V
- Größe: 800mAh

### Steuerung

bei Nutzung eines Xbox Series S/X Controllers über Bluetooth (dieser muss manuell **einmalig** über bluetoothctl direkt über den Pi verbunden werden) funktioniert die Steuerung wie gewünscht:  
- Rechter Trigger: Vorwärts
- Linker Trigger: Rückwärts
- Linker Stick: Links und Rechts

### Liste der Elektronik-Komponenten

- Allgemeine Steuerungseinheit: Rasperry Pi3
- Motorsteuerung: L298N Motorcontroller modul
- Lidarsensor: TF Luna LiDar "single Point Lidar von Youyeeto
- Motoren: 4x DC-Getriebemotoren mit jeweils einem Reifen "4pcs DC3V-12V DC Gear Motoren for 4-wheel drive Toy Car" von Amazin(Gebildet)
- Batterie(Lastkreis): LiPo 11,1V (3S) auf Amazon
- Batterie(logikkreis): jegliche herkömmliche Powerbanks funktionieren solange sie in das Gehäuse passt
- Verkabelung: Jumper wire cables(10cm) von amazon


