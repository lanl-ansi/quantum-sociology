From:	Roberts, Randy Mark
Sent:	Wednesday, September 20, 2017 3:36 PM
To:	Sims, Benjamin Hayden; Ambrosiano, John Joseph
Subject:	Re: D-Wave Results
Attachments:	results.json

I’ve run the problem the way you suggested.  I’ve committed the code and the results to the 
repository.  I’ve attached the results to this email for convenience.

The delta value of -999 means that there were no unbroken results for those runs.  When I run the 
problem in the d-wave simulator it returns unbroken solutions with delta = 0.0.

R^2

From: "Sims, Benjamin Hayden" <bsims@lanl.gov> 
Date: Tuesday, September 19, 2017 at 6:39 PM 
To: "Ambrosiano, John Joseph" <ambro@lanl.gov> 
Cc: Randy Roberts <rsqrd@lanl.gov> 
Subject: Re: D-Wave Results

Thanks Randy! Well that matches our intuition about the role of the Islamic State, the Hezbollah thing is 
somewhat unexpected though. I don’t know if there’s room for any further analysis, but I would be 
curious to see what the delta looks over time without Islamic State. If we could compare that to the 
delta over time with Islamic State included, that would give a nice view of IS as an instigator of 
imbalance. 

As far as interpretation, I will try to write something up but that will probably have to wait until next 
week.

Ben


 
Benjamin Sims, PhD ~ Sociologist 
Statistical Sciences Group (CCS-6) 
Los Alamos National Laboratory 
Los Alamos, NM 87544 
bsims@lanl.gov ~ (505) 667-5508 
http://public.lanl.gov/bsims 

On Sep 19, 2017, at 3:18 PM, Ambrosiano, John Joseph <ambro@lanl.gov> wrote:

How do you like them apples?
 
From: Roberts, Randy Mark  
Sent: Tuesday, September 19, 2017 3:10 PM 
To: Ambrosiano, John Joseph <ambro@lanl.gov>; Sims, Benjamin Hayden 
<bsims@lanl.gov> 
Subject: Re: D-Wave Results Immanent
 
/usr/local/bin/python2 /Users/rsqrd/PycharmProjects/d-wave/sensitivity.py
LANL-2690b414a0be9fc9af1d82d00bfe1ef23936c99e
syria_graph_2016-10-00.graphml initial problem solved, delta = 9.0
syria_graph_2016-10-00.graphml node Kata'ib al-Imam Ali removed: problem solved, 
delta = 9.0
syria_graph_2016-10-00.graphml node Jund al-Aqsa removed: problem solved, delta = 
8.0
syria_graph_2016-10-00.graphml node Kata’ib Sayyid al-Shuhada removed: problem 
solved, delta = 9.0
syria_graph_2016-10-00.graphml node Ansar al-Sham removed: problem solved, delta = 
9.0
syria_graph_2016-10-00.graphml node Jaysh al-Sanadeed removed: problem solved, 
delta = 9.0
syria_graph_2016-10-00.graphml node Hezbollah removed: problem solved, delta = 5.0
syria_graph_2016-10-00.graphml node Jabhat Fatah al-Sham (Formerly Jabhat al-Nusra) 
removed: problem solved, delta = 8.0
syria_graph_2016-10-00.graphml node Al Qaeda removed: problem solved, delta = 9.0
syria_graph_2016-10-00.graphml node Suqour al-Sham removed: problem solved, delta 
= 8.0
syria_graph_2016-10-00.graphml node The Islamic State removed: problem solved, 
delta = 1.0
syria_graph_2016-10-00.graphml node Harakat Nour al-Din al-Zenki removed: problem 
solved, delta = 9.0
syria_graph_2016-10-00.graphml node Liwa al-Tawhid removed: problem solved, delta 
= 8.0
syria_graph_2016-10-00.graphml node Liwa al-Islam removed: problem solved, delta = 
9.0
syria_graph_2016-10-00.graphml node Ahrar al-Sham removed: problem solved, delta = 
9.0
syria_graph_2016-10-00.graphml node Jaysh al-Islam removed: problem solved, delta = 
8.0
syria_graph_2016-10-00.graphml node Jaysh al-Sham removed: problem solved, delta = 
9.0
syria_graph_2016-10-00.graphml node Liwa al-Haqq removed: problem solved, delta = 
9.0
syria_graph_2016-10-00.graphml node Al-Fawj Al-Awl removed: problem solved, delta = 
8.0
syria_graph_2016-10-00.graphml node Harakat al-Nujaba removed: problem solved, 
delta = 9.0
syria_graph_2016-10-00.graphml node Asa'ib Ahl al-Haq removed: problem solved, 
delta = 9.0
syria_graph_2016-10-00.graphml node Faylaq al-Rahman removed: problem solved, 
delta = 7.0
syria_graph_2016-10-00.graphml node Kata'ib Hezbollah removed: problem solved, 
delta = 8.0
syria_graph_2016-10-00.graphml node Peoples Protection Units removed: problem 
solved, delta = 9.0
syria_graph_2016-10-00.graphml node Free Syrian Army removed: problem solved, 
delta = 8.0
syria_graph_2016-10-00.graphml node Kurdish Islamic Front removed: problem solved, 
delta = 9.0
syria_graph_2016-10-00.graphml node The Southern Front  removed: problem solved, 
delta = 8.0
syria_graph_2016-10-00.graphml node The Levantine Front  removed: problem solved, 
delta = 9.0
syria_graph_2016-10-00.graphml node The Ajnad al-Sham Islamic Union removed: 
problem solved, delta = 9.0
syria_graph_2016-10-00.graphml node Badr Organization of Reconstruction and 
Development removed: problem solved, delta = 9.0
 
Process finished with exit code 0
 
 
From: "Ambrosiano, John Joseph" <ambro@lanl.gov> 
Date: Tuesday, September 19, 2017 at 2:20 PM 
To: "Sims, Benjamin Hayden" <bsims@lanl.gov> 
Cc: Randy Roberts <rsqrd@lanl.gov> 
Subject: D-Wave Results Immanent
 
Ben,
 
Randy’s made good progress in modifying our original code to evaluate network 
imbalance with one member at a time removed. He’s chasing down one remaining 
discrepancy in the scaling of results. We hope to be able to send you a table of member 
removed and resulting imbalance by tomorrow. Then you can deal with the hard part - 
explaining it.
 
 

