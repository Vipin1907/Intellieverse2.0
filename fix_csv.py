# Ward data
wards = """zone,ward_nos,population,area_sqkm,density_per_sqkm,source
Hazratganj,1-5,48320,2.1,23009,Census 2011
Aminabad,6-12,71840,3.4,21129,Census 2011
Gomti Nagar,13-22,98450,8.2,12006,Census 2011
Alambagh,23-31,78320,5.6,13986,Census 2011
Chowk,32-38,61240,2.8,21871,Census 2011
Aliganj,39-47,82150,6.1,13467,Census 2011
Indira Nagar,48-58,105320,9.4,11204,Census 2011
Rajajipuram,59-65,54180,4.2,12900,Census 2011"""

# Hospital data
hospitals = """name,zone,lat,lon,type,beds,icu_beds,source
King George Medical University,Chowk,26.8629,80.9162,Government,3500,120,NHP India
Ram Manohar Lohia Hospital,Hazratganj,26.8501,80.9391,Government,650,40,NHP India
Balrampur Hospital,Chowk,26.8578,80.9134,Government,700,35,NHP India
Civil Hospital Aliganj,Aliganj,26.8891,80.9612,Government,200,15,NHP India
Sahara Hospital,Gomti Nagar,26.8467,80.9956,Private,350,45,Google Maps
Medanta Hospital,Gomti Nagar,26.8523,80.9934,Private,450,60,Google Maps
Apollo Clinic,Indira Nagar,26.8734,80.9978,Private,80,10,Google Maps
Vivekananda Hospital,Alambagh,26.8198,80.9187,Government,180,12,NHP India
District Hospital Rajajipuram,Rajajipuram,26.8312,80.8989,Government,250,18,NHP India"""

open('data/lucknow_wards.csv',    'w', encoding='utf-8', newline='').write(wards)
open('data/lucknow_hospitals.csv', 'w', encoding='utf-8', newline='').write(hospitals)
print('Done! Dono CSV files ready.')