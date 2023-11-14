from matplotlib import pyplot as plt
"""
----------------------------------------------------------------------------------------------------------------------
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|Tipo de Suelo | 	S	 |	To(s) |	 T'(s) |   n   |	p	 | Zona Sísmica |   A_o(g)|	Cat Edificio |   	I(num)	 |
| 	   A	   |   0.90  |	0.15  |	 0.20  |  1.00 |   2.00  |		1		|   0.20  |		  1		 |		0.8      |	 	
| 	   B	   |   1.00  |	0.30  |	 0.35  |  1.33 |   1.50  |		2		|   0.30  |		  2		 |		1.0      |
|	   C	   |   1.05  |	0.40  |	 0.45  |  1.40 |   1.60  |		3 		|	0.40  |		  3		 |		1.2      |
|	   D	   |   1.20  |	0.75  |	 0.85  |  1.80 |   1.00  |				|		  |		  4		 |		1.2      |
|	   E	   |   1.30  |	1.20  |	 1.35  |  1.80 |   1.00  |				|		  | 			 |			     |
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||	
----------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------------------
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|PROYECTO DE NORMA – prNCh2369																															|	
|08 de agosto de 2022 - Versión Final Comité prNCh2369 - ST Carlos Peña L. 45																			|
|Sistema resistente 																															|R|  ξ  |
|6. Estructuras de hormigón armado																												| |		|
|6.1 Edificio y estructuras de marcos resistentes a momento con elementos no estructurales dilatados 											|5| 0,05|
|6.2 Edificios y estructuras de marcos resistentes a momento con elementos no estructurales no dilatados e incorporados en el modelo estructural|3| 0,05|
|6.3 Edificios y estructuras de hormigón armado, con muros de corte 																			|5| 0,05|
|6.4 Edificios industriales de un piso, con o sin puente grúa, y con arriostramiento continuo de techo 											|5| 0,05|
|6.5 Edificios industriales de un piso, sin puente grúa, sin arriostramiento continuo de techo 													|3| 0,05|
---------------------------------------------------------------------------------------------------------------------------------------------------------
|															 |
|**Tipo de suelo A, Zona sísmica 2, Categoría de edificio 2**|
|															 |
--------------------------------------------------------------														
"""
import numpy as np
def Espectro2369_Actual(S,To,Tprima,n,p,Ao,I,R,Rv,chi,chiv):
	Th = np.linspace(0,5.,2000)
	Tv = np.linspace(0,5.,2000)
	Sah = np.zeros(2000)
	Sav = np.zeros(2000)

	for i in range(len(Th)):
		
		th = Th[i]
		tv = Tv[i]

		sah = 1.4*S*Ao*( (1+4.5*(th/To)**p)/(1+(th/To)**3) )
		sav = S*Ao*( (1+4.5*(1.7*tv/To)**p)/(1+(1.7*tv/To)**3) ) 

		Sah[i] = 0.7*(I*sah/R)*(0.05/chi)**0.4
		Sav[i] = 0.7*(I*sav/Rv)*(0.05/chiv)**0.4

	return Sah,Sav

def Espectro433(S,Ao,R,I,To,p):
	T = np.linspace(0,5.,2000)
	Sah = np.zeros(2000)
	Sav = np.zeros(2000)

	for i in range(2000):
		tn = T[i]
		alpha = (1 + 4.5*(tn/To)**p)/(1 +(tn/To)**3)
		Sah[i] = S*Ao*alpha/(R/I)
		Sav[i] = 2/3 * S*Ao*alpha/(R/I)

	return T,Sah,Sav
"""
S = 0.9
To = 0.15 #[s]
p = 2
Ao = 0.3 *9.81 
I = 1.2
R = 1

T,Sah,Sav = Espectro433(S,Ao,R,I,To,p)

plt.plot(T,Sah)
plt.grid()
plt.show()
"""
