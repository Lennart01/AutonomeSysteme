---
title: UPPAAL Labor
description: Martin Sulzmann
---

## 

UPPAAL ist frei verfügbar (akademische Lizenz): http://www.uppaal.org/

Die grundlegenden Elemente von UPPAAL werden in der Vorlesung erklärt.
Unten finden Sie eine Reihe von Beispielen als auch Aufgaben die Sie im
Labor bearbeiten sollen.

Weitere Hilfestellungen finden Sie hier:
http://www.it.uu.se/research/group/darts/uppaal/small\_tutorial.pdf
Allgemein ist UPPAAL "einfach erlernbar" und viele Fragen lassen sich
via der Online Hilfe beantworten.

Eine trickreiche Sache ist die Einstellung des "proxies", falls Sie
UPPAAL innerhalb der HS KA benutzen wollen. (FYI, UPPAAL benötigt eine
Verbindung zu dem Lizenzserver). Hilfestellung zum "proxy" finden Sie
hier (siehe Punkt 15):
http://www.uppaal.com/index.php?sida=201&rubrik=95

\[EDIT:\] Auf meinem Mac scheint eine extra Konfiguration wegen proxy
aktuell nicht mehr notwendig.

[Übungsblatts](./uebung-uppaal.pdf)

## Beispiele

xml das Modell und q die Spezifikation ("queries"), jeweils
herunterladen via folgenden links

Kaffeemaschine [xml](./src/uppaal/coffeeMachineWithUser.xml)
[q](./src/uppaal/coffeeMachineWithUser.q)

Hirte [xml](./src/uppaal/hirte.xml) [q](./src/uppaal/hirte.q)

Bankkonto [xml](./src/uppaal/userAccount.xml)
[q](./src/uppaal/userAccount.q)

Lampe [xml](./src/uppaal/lamp.xml) Modellierung einer Tischlampe mit
Helligkeit

SendReceive [xml](./src/uppaal/sndRcv.xml) Modellierung von
Nachrichtenbasierter Kommunikation

## Muserlösungen

### Kaffeemaschine (mit Münzen)

[xml](./src/uppaal/Coffeemachine.xml) [q](./src/uppaal/Coffeemachine.q)

Folgendes Verhalten lässt sich beobachten (via Simulator)

1.  User1: Wirft 3 Euro ein, bekommt Kaffee
2.  User2: Bekommt Kaffee!
3.  Sprich, User1 bezahlt für User2

Beachte: Die Aufgabenbeschreibung sagt nichts gegenteiliges aus. Vorteil
der formalen Modellierung Wir können dieses Verhalten im Modell genau
nachvollziehen (bevor man viel Arbeit in die eigentliche Implementierung
steckt)

Aufgabe: Wie könnte man durch eine geeignete Query (TCTL Formel) obigen
Ablauf herauskriegen?

### Sleeping Barber

[xml](./src/uppaal/SleepingBarber.xml)

Sehr einfach gehalten. Als Erweiterung könnten Sie (eine endliche
Anzahl) von Wartestühlen modellieren Beachte: Die Modellierung im
Übungsblatt (2-uebung-state-cfa) unterscheidet sich dadurch, dass ein
Kunde entweder direkt zum Barbier geht oder zuerst auf einem Stuhl Platz
nimmt.

### Hirte mit Randbedingung

[xml](./src/uppaal/hirteMitBedingung.xml)
[q](./src/uppaal/hirteMitBedingung.q)

In UPPAAL können wir leider nicht direkt den aktiven Zustand eines
Automaten abfragen. Wir führen deshalb (globale) Variablen ein, die den
aktuellen Zustand repräsentieren Transitionen bekommen guards
(Randbedingungen) die garantieren, dass z.B. der Wolf nicht alleine mit
der Ziege auf einer Seite des Ufers bleibt
