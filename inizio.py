a = 10
b = 20
c = int(input("Inserisci un numero "))
print(a+b+c);
print("ciaooo");
if(c>=18):
    print("maggiore di 18")
else:
    print(f"eta{c}")
for i in range(0,5):
    print(i)
def funzione(cane):
    print(f"il tuo cane è {cane}")
a,b = b,a
print(a,b);
funzione("marco")
arr = [a,b,c] #lista,mutabile
def scorriArray(array):
    n = len(array)
    for i in range(0,n):
        print(array[i])
scorriArray(arr)
miaTupla = ("cane","gatto","pane")#tupla immutabile
scorriArray(miaTupla)
mioSet = {"pollo","pippo","pelle"}#set mutabile non ammette duplicati
#no scorri array perchè non ha indici
mio_dict = {"nome": "Luca", "età": 25, "città": "Roma"}#dizionario coppia di valori chiave:valore
print(mio_dict["nome"]) 
mio_dict["età"] = 26 
mio_dict["professione"] = "Dog Trainer"