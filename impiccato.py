import random
soluzioni = ("pesce","cane","losco","supercalifragili","apelle figlia di apollo fece la palla di pelle di pollo")
i = random.randint(0,len(soluzioni)-1)
sol = soluzioni[i]
lunghezza = len(sol)
attempt = 0
running = True
show = ["_"]*lunghezza   
while(running):
    prova = False  
    print("".join(show))
    x = str(input("Inserisci la lettera "))
    x = x.lower()
    x = x[0]
    for i in range(0,lunghezza):
        if(sol[i]==x):
            show[i] = x
            prova = True
    if(prova == False):
        attempt+=1
        print(f"tentativi: {attempt}")
    if(sol == "".join(show)):
        print("hai vinto")
        running = False
    if(attempt == 10):
        print("hai perso")
        running = False
    
