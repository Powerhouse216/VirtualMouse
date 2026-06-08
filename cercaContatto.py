def aggiungi(rubrica):
    name = str(input("Inserisci il nome"))
    name = name.lower()
    numero = str(input("Inserisci il numero di telefono"))
    if("+" not in numero):
        numero = "+39"+numero
    if numero not in rubrica:
        rubrica[numero] = name
        print(f"il numero {numero}, è stato aggiunto alla rubrica\n")
    else:
        print(f"il numero {numero}, è già presente nella rubrica\n")
def stampa(rubrica):
    for numero,nome in rubrica.items():
        print(f"Nome: {nome}, Numero:{numero}\n")
def cerca(rubrica):
    numero = str(input("Inserisci il numero di telefono da cercare "))
    if("+39" not in numero):
        numero = "+39"+numero
    for telefono,nome in rubrica.items():
        if(telefono==numero):
            print(f"Nome associato al numero: {nome}")
            return 0;
    return 1;
contatti = {"+393516317964":"matteo"}
running = True;
while(running):
    scelta = -1
    while(scelta<0 or scelta>3):
        scelta = int(input("1)Aggiungi 2)Cerca 3)Mostra tutti 0)Esci"))
    match scelta:
        case 1:
            aggiungi(contatti)
        case 2:
            x = cerca(contatti)
            if(x==1):
                print("Numero non trovato")
        case 3:
            stampa(contatti)
        case 0:
            running = False