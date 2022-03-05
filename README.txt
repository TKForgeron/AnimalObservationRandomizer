Prerequisites:
	- Windows

How do I use this tool?
Every working day do the following:
1. Double-click 'update_schedule.exe'
2. At the start of your day, check 'daily_schedule_*.csv' to see which animals are to be observed in which timeslot that day
3. At the end of your day, fill out your excel file: 'true_observations.xlsx' and use the sheet tabs 'apenheul', 'gaiazoo', and 'dierenrijk'

Notes
1. 'Animal' moet iets ingevuld hebben. De volgende notaties zijn toegestaan: 
        ['KE', 'FA', 'MU', 'NO', 'SW', 'SG', 'SA', 'HA', 'BI', 'KA', 'TU', 'AS', 'TA']
2. 'Timeslot' moet iets ingevuld hebben. De volgende notaties zijn toegestaan: 
        ['EM', 'LM', 'EA', 'LA']
3. 'Time (s)' moet iets ingevuld hebben. De volgende notaties zijn toegestaan: 
        ['18' alsin 18 minuten en 0 seconden, '15.33' alsin 15 minuten en 33 seconden,
         '13.' alsin 13 minuten, '.4' alsin 4 seconden, '234.900' alsin 234 minuten en 900 seconden]
        kortom, gebruik:
            - alleen getallen om minuten aan te geven, of;
            - een punt om minuten van seconden te scheiden, waarbij het getal voor de punt minuten zijn en na de punt seconden.
4. Deze 3 kolomnamen moeten minimaal bestaan in de werkbladen:
        ['apenheul', 'gaiazoo', 'dierenrijk'] (pas deze namen niet aan)
3. Alle rijen die niet aan bovenstaande punten voldoet, worden niet meegenomen in 'update_schedule.exe'.